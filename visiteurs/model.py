from ext import get_db_connection
from flask import current_app
from datetime import datetime

class Event:
    def __init__(self, id, title, description, event_date,location, organizer, price_info, tag, image_url, max_attendees, created_at=None):
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
        self.created_at = created_at


    @classmethod
    def get_all_events(cls):

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM evenements ORDER BY event_date DESC")
        events_data = cursor.fetchall()
        cursor.close()
        conn.close()
        if events_data:
            return [cls(**event) for event in events_data]
        else:
            return []
        


class Details_event:
    def __init__(self, id, title, description, event_date, location, organizer, price_info, tag, image_url, max_attendees, created_at=None):
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
        self.created_at = created_at

    @classmethod
    def get_event_by_id(cls, event_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM evenements WHERE id = %s", (event_id,))
        event_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if event_data:
            return cls(**event_data)
        else:
            return None

class Reservation:
    @staticmethod
    def create(nom, prenom, age, id_evenement, email):
        """Crée une nouvelle réservation dans la base de données."""
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO reservations (nom, prenom, age, id_evenement, email, date_reservation)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                """
                # Utiliser la date et l'heure actuelles pour la réservation
                date_reservation = datetime.now()
                cursor.execute(sql, (nom, prenom, age, id_evenement, email))
            connection.commit()
            current_app.logger.info(f"Nouvelle réservation créée pour l'événement {id_evenement} par {prenom} {nom}.")
            return cursor.lastrowid
        except Exception as e:
            connection.rollback()
            current_app.logger.error(f"Erreur lors de la création de la réservation : {e}")
            return None
        finally:
            if connection.is_connected():
                connection.close()