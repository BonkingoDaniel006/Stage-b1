# Autisme Hauts-de-France - Site Web & Administration

Ce projet contient le code source du site vitrine et du panneau d'administration de l'association "Autisme Hauts-de-France". Il a pour but de présenter la mission de l'association, de gérer ses événements et de fournir une interface sécurisée pour son administration.

---

## 1. Stack Technique

Le projet est construit sur une stack moderne et robuste, choisie pour sa flexibilité, sa sécurité et sa maintenabilité.

*   **Backend :**
    *   **Framework :** Flask (Python) - Un micro-framework puissant et flexible, idéal pour des projets de cette taille.
    *   **Base de données :** MySQL - Un SGBD relationnel fiable et largement utilisé. La connexion est gérée via un pool pour optimiser les performances (`mysql-connector-python`).
    *   **Cache & Tâches en mémoire :** Redis - Utilisé pour les fonctionnalités de sécurité critiques comme le suivi des tentatives de connexion et le verrouillage de comptes.
    *   **Authentification :** `Flask-Login` pour la gestion des sessions, `Flask-Bcrypt` pour le hachage sécurisé des mots de passe.
    *   **Emails Transactionnels :** API HTTP de Brevo - Pour l'envoi des codes de vérification (OTP) et des alertes de sécurité, déchargeant la complexité de la délivrabilité email.

*   **Frontend :**
    *   **Site Vitrine :** HTML5, CSS3 (méthodologie BEM), JavaScript (ES6+).
    *   **Panneau d'Administration :** Tailwind CSS pour un développement rapide de l'interface, combiné à du JavaScript pour l'interactivité (navigation par onglets, modales).

---

## 2. Architecture du Projet

L'architecture a été pensée pour être modulaire, évolutive et facile à maintenir, en suivant les meilleures pratiques de l'écosystème Flask.

*   **Application Factory (`create_app` dans `app.py`) :** Le projet utilise le pattern *Application Factory*. Cela permet de créer des instances de l'application avec différentes configurations, ce qui est essentiel pour les tests et les déploiements multiples (développement, production).

*   **Blueprints :** Le code est organisé en `Blueprints`, qui sont des "mini-applications" Flask. Chaque blueprint correspond à une section logique du site :
    *   `visiteurs/` : Routes publiques du site vitrine (accueil, contact, événements...).
    *   `admin/` : Le panneau d'administration et l'API pour gérer le contenu.
    *   `auth/` : Routes et logique pour l'inscription, la connexion, la déconnexion et la vérification 2FA.

*   **Séparation des Responsabilités (SoC) :** Au sein de chaque blueprint, les fichiers sont organisés par fonction :
    *   `routes.py` : Gère les points d'entrée HTTP (les vues).
    *   `models.py` : Définit les structures de données et les interactions avec la base de données (ex: `User`, `Event`).
    *   `services.py` : Contient la logique métier complexe (ex: envoi d'emails, gestion du processus de connexion 2FA). Cela permet de garder les routes légères et lisibles.
    *   `forms.py` : Définit les formulaires avec `Flask-WTF`, gérant la validation et la protection CSRF.

*   **Gestion Centralisée des Extensions (`ext.py`) :** Toutes les extensions Flask (Bcrypt, LoginManager, etc.) et les clients (pool de BDD, Redis) sont initialisés dans `ext.py`. Cela évite les importations circulaires et centralise la configuration des services partagés.

---

## 3. Mesures de Sécurité

La sécurité est un aspect central de ce projet, en particulier pour la partie administration.

1.  **Authentification à Deux Facteurs (2FA / OTP) :**
    *   La connexion administrateur ne se fait pas seulement avec un mot de passe. Après une première validation réussie, un **code à usage unique (OTP)** est envoyé par email (via Brevo).
    *   Ce code a une durée de vie limitée (20 minutes) et un nombre de tentatives restreint (3 essais) pour être validé.
    *   *Fichiers concernés : `auth/routes.py`, `auth/services.py`.*

2.  **Protection contre les Attaques par Force Brute :**
    *   Le système utilise **Redis** pour suivre les tentatives de connexion échouées par adresse email.
    *   Après **3 tentatives infructueuses**, le compte est **verrouillé pendant 5 minutes**. Toute nouvelle tentative de connexion durant cette période est immédiatement rejetée.
    *   *Fichiers concernés : `auth/services.py` (fonctions `check_login_lockout` et `handle_failed_login`).*

3.  **Alertes de Sécurité :**
    *   Lorsqu'un compte est verrouillé suite à trop de tentatives, un **email d'alerte est automatiquement envoyé** à l'administrateur principal du site.
    *   *Fichier concerné : `auth/services.py` (fonction `_envoyer_email_alerte`).*

4.  **Hachage Sécurisé des Mots de Passe :**
    *   Les mots de passe ne sont **jamais stockés en clair**. Ils sont hachés et salés à l'aide de l'algorithme **Bcrypt**, qui est robuste et lent, le rendant résistant aux attaques par force brute sur la base de données.
    *   *Fichiers concernés : `ext.py`, `auth/models.py` (méthodes `set_password` et `check_password`).*

5.  **Protection contre les Failles CSRF (Cross-Site Request Forgery) :**
    *   L'extension `Flask-WTF` est utilisée pour générer et valider des jetons CSRF sur tous les formulaires et les requêtes `POST` sensibles (ajout/modification/suppression d'événements).
    *   **Note :** Cette protection est désactivée en mode développement (`WTF_CSRF_ENABLED = False` dans `config.py`) mais doit impérativement être activée en production.

6.  **Gestion des Secrets et Variables d'Environnement :**
    *   Aucune information sensible (clés d'API, identifiants de base de données, `SECRET_KEY` de Flask) n'est écrite en dur dans le code.
    *   Toutes ces informations sont chargées depuis un fichier `.env` à la racine du projet, qui ne doit **jamais** être versionné avec Git.

---

## 4. Installation et Lancement

Suivez ces étapes pour mettre en place un environnement de développement local.

1.  **Cloner le dépôt :**
    ```bash
    git clone <url-du-repo>
    cd STAGE-B1
    ```

2.  **Créer et activer un environnement virtuel :**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Sur Windows: venv\Scripts\activate
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurer les variables d'environnement :**
    *   Copiez le fichier d'exemple : `cp .env.example .env`
    *   Ouvrez le fichier `.env` et remplissez toutes les valeurs requises (voir section ci-dessous).

5.  **Lancer l'application :**
    ```bash
    flask run
    ```
    L'application sera accessible à l'adresse `http://127.0.0.1:5000`.

---

## 5. Variables d'Environnement (`.env`)

Ces variables sont nécessaires au bon fonctionnement de l'application.

```ini
# Clé secrète pour Flask (sessions, signatures, CSRF)
# Générer une clé robuste avec : python -c 'import secrets; print(secrets.token_hex())'
SECRET_KEY=

# Configuration de la base de données MySQL
DB_HOST=localhost
DB_USER=votre_utilisateur_mysql
DB_PASSWORD=votre_mot_de_passe_mysql
DB_NAME=autisme_hdf_db

# Configuration pour l'envoi d'e-mails via Brevo
BREVO_API_KEY=votre_cle_api_brevo
MAIL_USERNAME=adresse_email_expediteur@domaine.com

# Configuration de Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```