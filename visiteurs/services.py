import os 
import time
import requests
from flask import current_app, session,flash
import re 
from ext import get_db_connection
from admin.models import Message
from auth.models import User



def envoyer_email(name, email, subject, message):
    url = "https://api.brevo.com/v3/smtp/email"
    api_key= os.getenv("BREVO_API_KEY")

    if not api_key:
        current_app.logger.error("La clé API Brevo n'est pas définie dans les variables d'environnement.")
        return False
    
    payload = {
        "sender": {"name": "Contact Site", "email": os.getenv("MAIL_USERNAME")},
        "to": [{"email": os.getenv("MAIL_USERNAME")}],
        "replyTo": {"name": name, "email": email},
        "subject": subject,
        "htmlContent": f"""
        <p>Vous avez reçu un nouveau message de <strong>{name}</strong> ({email}).</p>
        <p><strong>Message :</strong></p>
        <p>{message}</p>"""
    }
    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers = headers)
        if response.status_code == 201:
            current_app.logger.info("Email envoyé avec succès via Brevo.")
            return True
        else:
            current_app.logger.error(f"Erreur lors de l'envoi de l'email via Brevo: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        current_app.logger.error(f"Exception lors de l'envoi de l'email via Brevo: {str(e)}")
        return False


def process_contact_form(name, email, subject, message):
    """
    1. Enregistre le message dans la base de données.
    2. Envoie une notification par e-mail à tous les administrateurs.
    """
    try:
        # 1. Enregistrer le message
        Message.create(name, email, subject, message)
        current_app.logger.info(f"Nouveau message enregistré en BDD.")

        # 2. Envoyer la notification aux administrateurs
        admins = User.get_all_admins()
        if not admins:
            current_app.logger.warning("Aucun administrateur trouvé pour l'envoi de la notification.")
            return True # Le message est enregistré, c'est le principal

        url = "https://api.brevo.com/v3/smtp/email"
        api_key = os.getenv("BREVO_API_KEY")
        
        payload = {
            "sender": {"name": "Site Autisme HDF", "email": os.getenv("MAIL_USERNAME")},
            "to": [{"email": admin.email} for admin in admins],
            "subject": f"Nouveau message de {name}",
            "htmlContent": f"""
            <p>Bonjour,</p>
            <p>Vous avez reçu un nouveau message de <strong>{name}</strong> via le formulaire de contact du site.</p>
            <p><strong>Sujet :</strong> {subject}</p>
            <p>Connectez-vous à votre tableau de bord pour le consulter et y répondre.</p>
            """
        }
        headers = {"api-key": api_key, "Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() # Lèvera une exception si le statut n'est pas 2xx
        current_app.logger.info(f"Notification de nouveau message envoyée aux administrateurs avec succès.")
        return True

    except Exception as e:
        current_app.logger.error(f"Erreur lors du traitement du formulaire de contact: {str(e)}")
        return False

def send_admin_reply(recipient_name, recipient_email, subject, message):
    """
    Envoie la réponse d'un administrateur à un visiteur.
    """
    try:
        url = "https://api.brevo.com/v3/smtp/email"
        api_key = os.getenv("BREVO_API_KEY")
        
        payload = {
            "sender": {"name": "Support Autisme HDF", "email": os.getenv("MAIL_USERNAME")},
            "to": [{"name": recipient_name, "email": recipient_email}],
            "subject": subject,
            "htmlContent": f"""
            <p>Bonjour {recipient_name},</p>
            <p>Voici une réponse de notre équipe concernant votre message :</p>
            <div style="border-left: 2px solid #e0f2fe; padding-left: 1rem; margin: 1rem 0;">
                <p>{message}</p>
            </div>
            <p>Cordialement,<br>L'équipe d'Autisme Hauts-de-France</p>
            """
        }
        headers = {"api-key": api_key, "Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        current_app.logger.info(f"Réponse envoyée avec succès à {recipient_email}.")
        return True
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de la réponse admin à {recipient_email}: {str(e)}")
        return False