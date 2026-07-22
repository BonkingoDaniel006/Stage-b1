from ext import get_db_connection

class Event:
    def __init__(self, id, title, event_date, location, **kwargs):
        self.id = id
        self.title = title
        self.event_date = event_date
        self.location = location
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

    def update(self, data):
        """Met à jour l'événement avec les nouvelles données."""
        if not self.id:
            return

        # Mettre à jour les attributs de l'objet
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        conn = get_db_connection()
        cursor = conn.cursor()
        # Note: Cette requête est un exemple. Pour une application en production,
        # il serait préférable de construire la requête dynamiquement pour ne mettre
        # à jour que les champs modifiés.
        query = """
            UPDATE evenements SET title=%s, description=%s, event_date=%s, location=%s, organizer=%s, price_info=%s, tag=%s, max_attendees=%s, image_url=%s
            WHERE id=%s
        """
        cursor.execute(query, (self.title, self.description, self.event_date, self.location, self.organizer, self.price_info, self.tag, self.max_attendees, self.image_url, self.id))
        conn.commit()
        cursor.close()
        conn.close()