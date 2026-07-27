from ext import get_db_connection
import os
import uuid

class Event:
    def __init__(self, id, title, description, event_date, location, organizer, price_info, tag, image_url, max_attendees, **kwargs):
        self.id = id
        self.title = title
        self.description = description
        self.event_date = event_date
        self.location = location
        self.organizer = organizer
        self.price_info = price_info
        self.tag = tag
        self.image_url = image_url
        self.max_attendees = max_attendees

        # Accepte d'autres champs pour une utilisation future
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """Convertit l'objet Event en dictionnaire pour l'API JSON."""
        data = self.__dict__
        # Formate la date en chaîne ISO pour le JSON et les inputs HTML
        if 'event_date' in data and hasattr(data['event_date'], 'isoformat'):
            # Le format doit être compatible avec <input type="datetime-local">
            data['event_date'] = data['event_date'].strftime('%Y-%m-%dT%H:%M')
        return data



    @staticmethod
    def get_all():
        """Récupère tous les événements de la base de données, triés par date."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM evenements ORDER BY event_date DESC")
        events_data = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Crée une liste d'objets Event à partir des données de la BDD
        return [Event(**data) for data in events_data]

    @staticmethod
    def get_by_id(event_id):
        """Récupère un événement par son ID."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM evenements WHERE id = %s", (event_id,))
        event_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if event_data:
            return Event(**event_data)
        return None

    @staticmethod
    def create(data):
        """Crée un nouvel événement dans la base de données et retourne son ID."""
        # Champs obligatoires pour la création
        if not data.get('title') or not data.get('event_date'):
            raise ValueError("Le titre et la date de l'événement sont obligatoires.")

        # Liste des champs autorisés pour l'insertion
        allowed_fields = ['title', 'description', 'event_date', 'location', 'organizer', 'price_info', 'tag', 'image_url', 'max_attendees']
        
        # Filtrer les données pour ne garder que les champs autorisés et non vides
        event_data = {field: (data[field] if data[field] != '' else None) for field in allowed_fields if field in data}

        if not event_data:
            return None # Rien à insérer

        fields_to_insert = [f"`{field}`" for field in event_data.keys()]
        placeholders = ['%s'] * len(event_data)
        values = list(event_data.values())

        query = f"INSERT INTO evenements ({', '.join(fields_to_insert)}) VALUES ({', '.join(placeholders)})"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        new_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return new_id

    def update(self, data):
        """Met à jour l'événement dans la base de données avec les nouvelles données."""
        if not self.id:
            return

        # Liste des champs autorisés à la mise à jour
        allowed_fields = ['title', 'description', 'event_date', 'location', 'organizer', 'price_info', 'tag', 'image_url', 'max_attendees']
        
        # Construction dynamique de la requête SQL
        update_data = {
            field: (data[field] if data[field] != '' else None)
            for field in allowed_fields
            if field in data and data[field] is not None
        }

        if not update_data:
            return # Rien à mettre à jour
        
        fields_to_update = [f"`{field}` = %s" for field in update_data.keys()]
        values = list(update_data.values()) + [self.id]
        query = f"UPDATE evenements SET {', '.join(fields_to_update)} WHERE id = %s"

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit()
        cursor.close()
        conn.close()

    def delete(self):
        """Supprime l'événement de la base de données."""
        if not self.id:
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM evenements WHERE id = %s", (self.id,))
        conn.commit()
        cursor.close()
        conn.close()



class Message:
    def __init__(self, **kwargs):
        """Initialise dynamiquement les attributs à partir des données de la BDD."""
        # Assure que tous les champs de la BDD deviennent des attributs de l'objet
        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def get_all():
        """Récupère tous les messages de la base de données, les plus récents en premier."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Renommer les colonnes pour correspondre aux attributs de l'objet
        cursor.execute("""
            SELECT id, sender_name, sender_email, subject, content, is_read, created_at 
            FROM messages 
            ORDER BY created_at DESC
        """)
        messages_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return [Message(**data) for data in messages_data]

    @staticmethod
    def get_by_id(message_id):
        """Récupère un message par son ID."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM messages WHERE id = %s", (message_id,))
        message_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if message_data:
            return Message(**message_data)
        return None


    @staticmethod
    def get_conversation(message_id):
        """Récupère le message original et toutes ses réponses."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Le message original est celui où l'ID et le conversation_id sont identiques
        # Les réponses ont le même conversation_id
        cursor.execute("""
            SELECT * FROM messages WHERE conversation_id = (SELECT conversation_id FROM messages WHERE id = %s)
            ORDER BY created_at ASC
        """, (message_id,))
        messages_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return [Message(**data) for data in messages_data]

    @staticmethod
    def create(name, email, subject, message_content):
        """Crée un nouveau message dans la base de données."""
        query = """
            INSERT INTO messages (sender_name, sender_email, subject, content, is_read) 
            VALUES (%s, %s, %s, %s, FALSE)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (name, email, subject, message_content))
            new_id = cursor.lastrowid
            # Le premier message définit l'ID de la conversation
            cursor.execute("UPDATE messages SET conversation_id = %s WHERE id = %s", (new_id, new_id))
            conn.commit()
            return new_id
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def reply(conversation_id, admin_user, recipient_email, subject, content):
        """Enregistre la réponse d'un administrateur."""
        query = """
            INSERT INTO messages (conversation_id, sender_name, sender_email, subject, content, sender_type) 
            VALUES (%s, %s, %s, %s, %s, 'admin')
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (conversation_id, admin_user.username, admin_user.email, subject, content))
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    def mark_as_read(self):
        """Marque le message comme lu dans la base de données."""
        if not self.id:
            return
        query = "UPDATE messages SET is_read = TRUE WHERE id = %s"
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (self.id,))
            conn.commit()
            self.is_read = True
        finally:
            cursor.close()
            conn.close()

    def to_dict(self):
        """Convertit l'objet en dictionnaire pour l'API JSON."""
        # Récupérer tous les attributs de l'instance
        data = self.__dict__.copy()
        return {
            "id": self.id,
            "name": self.sender_name,
            "email": self.sender_email,
            "subject": self.subject,
            "message": self.content,
            "is_read": self.is_read,
            "date": self.created_at.isoformat(),
            "sender_type": data.get('sender_type', 'visitor') # Assurer une valeur par défaut
        }


