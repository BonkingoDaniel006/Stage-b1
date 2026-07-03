# Autisme Hauts-de-France - Site Web de l'Association

Ce projet est le site web de l'association "Autisme Hauts-de-France". Il a pour but de présenter la mission de l'association, ses actions, de fournir des ressources et de permettre aux visiteurs de prendre contact ou de consulter les événements à venir.

> **Tagline :** Ensemble, chaque différence a sa place.

## Table des matières
1.  [Stack Technique](#stack-technique)
2.  [Structure du Projet](#structure-du-projet)
3.  [Installation et Lancement](#installation-et-lancement)
4.  [Variables d'Environnement](#variables-denvironnement)
5.  [Conventions de Code](#conventions-de-code)

---

## Stack Technique

*   **Backend :**
    *   **Framework :** [Flask](https://flask.palletsprojects.com/)
    *   **Langage :** Python 3.12+
    *   **Base de données :** MySQL
    *   **Envoi d'e-mails :** API [Brevo](https://www.brevo.com/) (via la librairie `requests`)
*   **Frontend :**
    *   HTML5 / CSS3
    *   JavaScript (ES6+)
*   **Dépendances Python principales :**
    *   `flask`: Le framework web.
    *   `mysql-connector-python`: Pour la connexion à la base de données MySQL.
    *   `python-dotenv`: Pour la gestion des variables d'environnement.
    *   `requests`: Pour effectuer des appels à l'API Brevo.
    *   `flask-wtf`: Pour la gestion des formulaires et la protection CSRF.

## Structure du Projet

Le projet suit le modèle **Application Factory** et utilise des **Blueprints** pour organiser le code.

```
/
├── app.py                  # Point d'entrée, contient la factory create_app()
├── config.py               # Classes de configuration (charge les .env)
├── ext.py                  # Initialisation des extensions Flask (DB, CSRF...)
├── static/                 # Fichiers statiques (CSS, JS, images)
│   ├── css/style.css
│   └── js/main.js
├── templates/              # Templates Jinja2
│   ├── index.html
│   └── ...
├── visiteurs/              # Blueprint pour les routes publiques
│   ├── __init__.py
│   ├── route.py            # Définition des routes (/contact, /evenements...)
│   ├── model.py            # Modèles de données (classes interagissant avec la BDD)
│   └── services.py         # Logique métier (ex: envoi d'email)
├── .env.example            # Fichier d'exemple pour les variables d'environnement
└── README.md               # Ce fichier
```

## Installation et Lancement

1.  **Cloner le dépôt :**
    ```bash
    git clone <url-du-repo>
    cd STAGE-B1
    ```

2.  **Créer et activer un environnement virtuel :**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurer les variables d'environnement :**
    Copiez le fichier `.env.example` vers un nouveau fichier nommé `.env` et remplissez les valeurs requises (voir section ci-dessous).
    ```bash
    cp .env.example .env
    ```

5.  **Lancer l'application :**
    ```bash
    flask run
    ```
    L'application sera accessible à l'adresse `http://127.0.0.1:5000`.

## Variables d'Environnement

Ces variables doivent être définies dans le fichier `.env` à la racine du projet.

```ini
# Clé secrète pour Flask (sessions, signatures...)
# Générer avec : python -c 'import secrets; print(secrets.token_hex())'
SECRET_KEY=

# Configuration de la base de données
DB_HOST=localhost
DB_USER=
DB_PASSWORD=
DB_NAME=

# Configuration pour l'envoi d'e-mails via Brevo
BREVO_API_KEY=
MAIL_USERNAME= # L'adresse e-mail utilisée pour envoyer et recevoir les messages du formulaire
```

## Conventions de Code

*   **Python :** Le code suit la convention PEP 8.
*   **Gestion des connexions BDD :** Utiliser `get_db_connection()` depuis `ext.py` pour obtenir une connexion depuis le pool. Penser à fermer la connexion et le curseur après usage.
*   **Sécurité :** La protection CSRF est gérée par `Flask-WTF`. Elle est actuellement désactivée pour le développement (`WTF_CSRF_ENABLED = False` dans `config.py`). Elle devra être réactivée en production.