import os 
import time
import requests
from flask import current_app, session,flash
import re 
from ext import redis_client, get_db_connection




def envoyer_email(name, email, subject, message):
    """
    Envoie un email en utilisan Brevo.
    """
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