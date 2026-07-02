from flask import Flask, render_template
from config import Config
from ext import init_extensions
from visiteurs.route import index_bp
import os

def create_app(config_class=Config):
    """
    Application Factory: Crée et configure l'application Flask.
    """
    app = Flask(__name__)
    
    # 1. Charger la configuration
    app.config.from_object(config_class)
    
    # 2. Initialiser les extensions (DB pool, LoginManager, etc.)
    with app.app_context():
        init_extensions(app)

    # 3. Définir les routes
    app.register_blueprint(index_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)