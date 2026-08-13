import os
import secrets
import time
import requests
from flask import current_app, session, flash
from flask_login import login_user
import re
from auth.models import User
from ext import bcrypt, redis_client


def _generer_code_verification(longueur=6):
    """Génère un code de vérification numérique sécurisé."""
    return "".join(secrets.choice("0123456789") for _ in range(longueur))


def _envoyer_otp_brevo(email_destinataire, prenom, code_otp):
    """Fonction utilitaire pour envoyer l'OTP via l'API HTTP de Brevo"""
    url = "https://api.brevo.com/v3/smtp/email"
    api_key = os.getenv("BREVO_API_KEY")
    if not api_key:
        current_app.logger.error("La variable d'environnement BREVO_API_KEY n'est pas configurée.")
        return False

    greeting = f"Bonjour {prenom}," if prenom else "Bonjour,"
    payload = {
        "sender": {"name": "Autisme-hf Connect", "email": os.getenv("MAIL_USERNAME")},
        "to": [{"email": email_destinataire}],
        "subject": "Code de vérification Autisme-hf",
        "htmlContent": f"""
            <h3>{greeting}</h3>
            <p>Votre code de vérification unique est : <strong>{code_otp}</strong></p>
            <p>Ce code expirera dans 20 minutes.</p>
        """
    }
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 201:
            current_app.logger.info(f"OTP envoyé avec succès à {email_destinataire}")
            return True
        else:
            current_app.logger.error(f"Erreur de l'API Brevo lors de l'envoi d'OTP à {email_destinataire}. Status: {response.status_code}")
            return False
    except Exception as e:
        current_app.logger.error(f"Exception lors de l'envoi HTTP à Brevo : {str(e)}")
        return False
    
def _envoyer_email_alerte(sujet, contenu_html):
    """Envoie un email d'alerte à l'administrateur."""
    url = "https://api.brevo.com/v3/smtp/email"
    api_key = os.getenv("BREVO_API_KEY")
    admin_email = os.getenv("ADMIN_EMAIL_ALERT")

    if not api_key:
        current_app.logger.error("BREVO_API_KEY n'est pas configurée.")
        return

    payload = {
        "sender": {"name": "Alerte Sécurité Autisme-hf", "email": os.getenv("MAIL_USERNAME")},
        "to": [{"email": admin_email}],
        "subject": sujet,
        "htmlContent": contenu_html
    }
    headers = {"api-key": api_key, "content-type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code != 201:
            current_app.logger.error(f"Erreur API Brevo pour alerte admin ({response.status_code}): {response.text}")
    except Exception as e:
        current_app.logger.error(f"Exception lors de l'envoi de l'alerte admin: {str(e)}")

def check_login_lockout(email):
    """Vérifie si un email est verrouillé."""
    if not redis_client:
        current_app.logger.warning("Redis client not available. Skipping login lockout check.")
        return False
    lockout_key = f"lockout:{email}"
    ttl = redis_client.ttl(lockout_key)
    if ttl > 0:
        minutes = (ttl // 60) + 1 # Arrondi à la minute supérieure
        flash(f"Trop de tentatives de connexion échouées. Veuillez réessayer dans {minutes} minute(s).", "warning")
        return True
    return False

def handle_failed_login(email):
    """Gère une tentative de connexion échouée."""
    if not redis_client:
        current_app.logger.warning("Redis client not available. Skipping failed login handling.")
        flash('Connexion échouée. Veuillez vérifier votre e-mail et mot de passe.', 'danger')
        return
    attempts_key = f"failed_attempts:{email}"
    attempts = redis_client.incr(attempts_key)
    redis_client.expire(attempts_key, 900) # Le compteur se réinitialise après 15 minutes

    if attempts >= 3:
        lockout_key = f"lockout:{email}"
        redis_client.setex(lockout_key, 300, "locked") # Verrouillage pour 5 minutes (300s)
        redis_client.delete(attempts_key) # On supprime le compteur une fois le verrouillage actif
        
        # Envoi de l'email d'alerte
        sujet = "Alerte de sécurité : Compte verrouillé"
        contenu = f"<p>Le compte associé à l'email <strong>{email}</strong> a été temporairement verrouillé pour 5 minutes suite à 3 tentatives de connexion infructueuses.</p><p>Veuillez vérifier l'activité suspecte.</p>"
        _envoyer_email_alerte(sujet, contenu)
        
        flash("Trop de tentatives de connexion échouées. Votre compte est temporairement verrouillé pour 5 minutes.", "danger")
    else:
        flash('Connexion échouée. Veuillez vérifier votre e-mail et mot de passe.', 'danger')

def start_otp_verification(user):
    """
    Génère un code OTP, l'envoie par e-mail et initialise la session pour la vérification.
    """
    if not user:
        return False

    code_otp = _generer_code_verification()
    prenom = user.username or user.email.split('@')[0]

    if _envoyer_otp_brevo(user.email, prenom, code_otp):
        session['otp_login'] = {'code': code_otp, 'expires_at': time.time() + 1200, 'attempts': 0} # 20 minutes
        session['user_id_to_verify'] = user.id
        current_app.logger.info(f"Démarrage de la vérification OTP pour l'utilisateur {user.id}")
        return True
    
    return False

def process_registration(form_data):
    if User.find_by_email(form_data['email']):
        flash("Cet email est déjà utilisé. Veuillez en choisir un autre.", "error")
        return False
    verification_code = _generer_code_verification()
    if not _envoyer_otp_brevo(form_data['email'], form_data['prenom'], verification_code):
        flash("Une erreur est survenue lors de l'envoi de l'OTP. Veuillez réessayer plus tard.", "error")
        return False
    session['otp'] = {'code': verification_code, 'expires_at': time.time() + 1200, 'attempts': 0}
    session['pending_user'] = form_data
    return True # Signifie "succès"


def process_login(submitted_code):
    """Traite la soumission du code OTP pour la connexion."""
    otp_data = session.get('otp_login')
    user_id = session.get('user_id_to_verify')

    if not otp_data or not user_id:
        return "invalid_session"
    
    if time.time() > otp_data['expires_at'] or otp_data['attempts'] >= 3:
        session.pop('otp_login', None)
        session.pop('user_id_to_verify', None)
        return "expired_or_max_attempts"

    if submitted_code == otp_data['code']:
        user = User.get(user_id)
        if user:
            login_user(user, remember=False)
        session.pop('otp_login', None)
        session.pop('user_id_to_verify', None)
        return "success"
    
    otp_data['attempts'] += 1
    session['otp_login'] = otp_data
    return "incorrect_code"