from flask_login import UserMixin
from ext import get_db_connection, bcrypt, login_manager

class User(UserMixin):
    def __init__(self, id, email, password_hash, username=None):
        self.id = id
        self.email = email
        self.password = password_hash
        self.username = username or self.email.split('@')[0]

    def set_password(self, password):
        """Crée un hash du mot de passe."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash."""
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def find_by_email(email):
        """Trouve un utilisateur par son email."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_data:
            return User(id=user_data['id'], email=user_data['email'], password_hash=user_data['password'], username=user_data.get('username'))
        return None

    @staticmethod
    def get(user_id):
        """Trouve un utilisateur par son ID (requis par Flask-Login)."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_data:
            return User(id=user_data['id'], email=user_data['email'], password_hash=user_data['password'], username=user_data.get('username'))
        return None

    def save(self):
        """Sauvegarde un nouvel utilisateur dans la base de données."""
        conn = get_db_connection()
        cursor = conn.cursor()
        # Le nom d'utilisateur est défini comme la partie locale de l'email pour satisfaire la contrainte de la BDD
        username = self.email.split('@')[0]
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, self.email, self.password)
            )
            conn.commit()
            cursor.close()
            conn.close()
        finally:
            pass # La connexion est déjà gérée dans le bloc try


@login_manager.user_loader
def load_user(user_id):
    """Fonction requise par Flask-Login pour charger un utilisateur à partir de la session."""
    return User.get(user_id)