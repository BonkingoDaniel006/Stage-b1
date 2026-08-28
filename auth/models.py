from flask_login import UserMixin
from ext import get_db_connection, bcrypt, login_manager

class User(UserMixin):
    def __init__(self, id, email, password_hash, username=None, identity_verified=False):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.username = username or email.split('@')[0]
        self.identity_verified = identity_verified

    def set_password(self, password):
        """Crée un hash du mot de passe."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

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
            # On charge maintenant la valeur de identity_verified depuis la BDD
            return User(id=user_data['id'], email=user_data['email'], password_hash=user_data['password'], username=user_data.get('username'), identity_verified=user_data.get('identity_verified', False))
        return None

    def set_identity_verified(self): # <--- Cette méthode met à jour la colonne
        """Marque l'identité de l'utilisateur comme vérifiée dans la base de données."""
        if not self.id:
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET identity_verified = TRUE WHERE id = %s", (self.id,))
            conn.commit()
            self.identity_verified = True
        finally:
            cursor.close()
            conn.close()

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
            return User(id=user_data['id'], email=user_data['email'], password_hash=user_data['password'], username=user_data.get('username'), identity_verified=user_data.get('identity_verified', False))
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
                (username, self.email, self.password_hash)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all_admins():
        """Récupère tous les administrateurs de la base de données."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users_data = cursor.fetchall()
        cursor.close()
        conn.close() # On charge aussi le statut de vérification ici
        return [User(id=user_data['id'], email=user_data['email'], password_hash=user_data['password'], username=user_data.get('username'), identity_verified=user_data.get('identity_verified', False)) for user_data in users_data]
    


@login_manager.user_loader
def load_user(user_id):
    """Fonction requise par Flask-Login pour charger un utilisateur à partir de la session."""
    return User.get(user_id)