from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

# Import des routes pour qu'elles soient associées au blueprint
from . import routes