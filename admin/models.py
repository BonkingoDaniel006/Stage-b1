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

        # Liste des champs autorisés à l'insertion
        allowed_fields = ['title', 'description', 'event_date', 'location', 'organizer', 'price_info', 'tag', 'image_url', 'max_attendees']
        
        fields_to_insert = []
        values = []
        placeholders = []

        for field in allowed_fields:
            if field in data:
                fields_to_insert.append(f"`{field}`")
                placeholders.append('%s')
                # Gère le cas où un champ non obligatoire est vide (ex: max_attendees)
                values.append(data[field] if data[field] != '' else None)

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
        fields_to_update = []
        values = []
        for field in allowed_fields:
            if field in data:
                fields_to_update.append(f"{field} = %s")
                values.append(data[field])

        if not fields_to_update:
            return # Rien à mettre à jour

        values.append(self.id)
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