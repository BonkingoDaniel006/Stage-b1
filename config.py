import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

import os
from datetime import timedelta

class Config:
    # 1. Sécurité & Clé secrète (Génère une clé par défaut si absente du .env pour éviter le crash)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'votre_cle_secrete_par_defaut_a_changer')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # 2. Protection CSRF & Configuration des Cookies de Session (Crucial pour Render)
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True       # Oblige l'envoi des cookies uniquement via HTTPS
    SESSION_COOKIE_HTTPONLY = True     # Empêche le JavaScript d'accéder au cookie de session
    SESSION_COOKIE_SAMESITE = 'Lax'    # 'Lax' si front & back sont sur le même domaine, 'None' si front séparé
    
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30) # Déconnexion après 30 minutes
    
    # 3. Base de données
    DB_HOST = os.environ.get('DB_HOST')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')

    # 4. Redis pour le rate limiting
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

    # 5. Configuration des Mails
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'True').lower() in ('true', '1', 't')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'False').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # 6. Clés API Stripe
    STRIPE_PUBLIC_KEY = os.environ.get('public_stripe')
    STRIPE_SECRET_KEY = os.environ.get('secret_stripe')