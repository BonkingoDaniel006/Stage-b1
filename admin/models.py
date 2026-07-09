from ext import get_db_connection
from flask import current_app

class Event:
    def __init__(self, id, title, description, event_date, location, image_url=None):
        self.id = id
        self.title = title
        self.description = description
        self.event_date = event_date
        self.location = location
        self.image_url = image_url

    @staticmethod
    def get_all():
        """Récupère tous les événements de la base de données."""
        events = []
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, title, description, event_date, location, image_url FROM events ORDER BY event_date DESC")
            for row in cursor.fetchall():
                events.append(Event(**row))
            return events
        except Exception as e:
            current_app.logger.error(f"Erreur lors de la récupération des événements: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def save(self):
        """Sauvegarde l'événement (création ou mise à jour)."""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if self.id: # Mise à jour
                sql = "UPDATE events SET title = %s, description = %s, event_date = %s, location = %s WHERE id = %s"
                cursor.execute(sql, (self.title, self.description, self.event_date, self.location, self.id))
            else: # Création
                sql = "INSERT INTO events (title, description, event_date, location) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (self.title, self.description, self.event_date, self.location))
                self.id = cursor.lastrowid
            conn.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Erreur lors de la sauvegarde de l'événement: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def delete(event_id):
        """Supprime un événement par son ID."""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
            conn.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Erreur lors de la suppression de l'événement {event_id}: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()