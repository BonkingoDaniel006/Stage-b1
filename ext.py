from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_login import LoginManager
import mysql.connector.pooling
import redis

# Instanciation des extensions Flask
# Cela permet d'éviter les importations circulaires
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()


# Redirection automatique si un utilisateur non connecté tente d'accéder à une page protégée
login_manager.login_view = 'auth.connexion'
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
login_manager.login_message_category = "info"


#initialisation du client Redis
redis_client = None
#initialisation du pool de connexion (une seule connexion sera utilisée pour toutes les requêtes)
db_pool = None

def init_extensions(app):
    """Initialise les extensions Flask et le pool de connexions."""
    global db_pool
    
    # Initialisation des extensions avec l'application Flask
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    try:
        # Création du pool de connexions à la base de données
        db_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="autisme_hf_pool",
            pool_size=5,
            host=app.config['DB_HOST'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            database=app.config['DB_NAME']
        )
        app.logger.info("Database connection pool created successfully.")
    except mysql.connector.Error as err:
        app.logger.error(f"Failed to create database connection pool: {err}")
        app.logger.error("The application will start, but database functionality will be unavailable until the connection is resolved.")
        db_pool = None


def get_db_connection():
    if db_pool is None:
        raise Exception("Database connection pool is not available.")
    return db_pool.get_connection()