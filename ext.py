from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
import mysql.connector.pooling
import redis

# Instanciation des extensions Flask
# Cela permet d'éviter les importations circulaires
bcrypt = Bcrypt()
csrf = CSRFProtect()

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

    # Création du pool de connexions à la base de données
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="autisme_hf_pool",
        pool_size=5,
        host=app.config['DB_HOST'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME']
    )