from flask import Flask, render_template
from config import Config
from ext import init_extensions

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
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/evenements')
    def evenements():
        return render_template('evenements.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()