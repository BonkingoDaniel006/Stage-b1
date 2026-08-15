from flask import Blueprint, render_template, redirect, url_for,flash, request, current_app, session
from visiteurs.model import Event
from visiteurs.model import Details_event
from visiteurs.model import Reservation
import re # Import pour le parsing des prix
import stripe

index_bp = Blueprint('index', __name__)

# Fonction utilitaire pour parser le prix en centimes
def parse_price_to_cents(price_str):
    if not price_str:
        return 0
    price_str = price_str.lower().replace(' ', '').replace(',', '.')
    if 'gratuit' in price_str:
        return 0
    # Supprimer les symboles monétaires et autres caractères non numériques
    price_str = re.sub(r'[^\d.]', '', price_str)
    try:
        return int(float(price_str) * 100)
    except ValueError:
        return 0 # Retourne 0 si le parsing échoue


@index_bp.route('/')
def index():
    return render_template('index.html')


@index_bp.route('/evenements')
def evenements():
    events = Event.get_all_events()
    return render_template('evenements.html', events=events)

@index_bp.route('/mentions-legales')
def legal():
    """Affiche la page des mentions légales."""
    return render_template('legal.html')

@index_bp.route('/politique-de-confidentialite')
def privacy_policy():
    """Affiche la page de politique de confidentialité."""
    return render_template('privacy.html')

@index_bp.route('/evenements/<int:event_id>')
def evenement(event_id):
    details = Details_event.get_event_by_id(event_id)
    if details is None:
        flash("Événement introuvable.", "error")
        return redirect(url_for('index.evenements'))
    return render_template('evenement.html', details=details)

@index_bp.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # Validation simple côté serveur
    if not all([name, email, subject, message]):
        flash("Tous les champs sont requis.", "error")
        return redirect(url_for('index.index') + '#contact')

    # Importer ici pour éviter les dépendances circulaires potentielles
    from visiteurs.services import process_contact_form

    if process_contact_form(name, email, subject, message):
        flash("Votre message a été envoyé avec succès.", "success")
    else:
        flash("Une erreur est survenue lors de l'envoi de votre message. Veuillez réessayer plus tard.", "error")
    
    return redirect(url_for('index.index') + '#contact')

# --- Routes pour le paiement (Stripe) ---

@index_bp.route('/don')
def don():
    """Affiche la page de don pour les visiteurs."""
    return render_template('paiement_public.html', stripe_public_key=current_app.config.get('STRIPE_PUBLIC_KEY'))

@index_bp.route('/create-donation-checkout-session', methods=['POST'])
def create_donation_checkout_session():
    """Crée une session de paiement Stripe Checkout pour les visiteurs."""
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': 'Don à l\'association Autisme HDF',
                        },
                        'unit_amount': 2000, # Montant en centimes (ex: 20.00€)
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=url_for('index.payment_success', _external=True),
            cancel_url=url_for('index.payment_cancel', _external=True), # Pas d'event_id pour un don générique
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création de la session Stripe: {e}")
        flash("Une erreur est survenue lors de la redirection vers la page de paiement. Veuillez réessayer.", "error")
        return redirect(url_for('index.don'))

@index_bp.route('/reserver-evenement/<int:event_id>', methods=['GET', 'POST'])
def reserver_evenement(event_id):
    """Gère le processus de réservation en deux étapes : collecte d'infos puis confirmation."""
    event = Details_event.get_event_by_id(event_id)
    if not event:
        flash("Événement introuvable.", "error")
        return redirect(url_for('index.evenements'))

    if request.method == 'POST':
        # Étape 2 : L'utilisateur a soumis le formulaire d'informations
        nom_complet = request.form.get('nom_complet')
        email = request.form.get('email')
        age = request.form.get('age')

        if not all([nom_complet, email, age]):
            flash("Tous les champs sont obligatoires.", "error")
            return render_template('participant_info.html', event=event)

        # Stocker les informations dans la session pour les récupérer après le paiement
        session['participant_info'] = {
            'nom_complet': nom_complet,
            'email': email,
            'age': age,
            'id_evenement': event_id
        }

        # Afficher la page de confirmation de paiement
        return render_template('reserver_evenement.html', event=event, stripe_public_key=current_app.config.get('STRIPE_PUBLIC_KEY'))

    # Étape 1 : Afficher le formulaire pour collecter les informations du participant
    return render_template('participant_info.html', event=event)

@index_bp.route('/create-event-checkout-session/<int:event_id>', methods=['POST'])
def create_event_checkout_session(event_id):
    """Crée une session de paiement Stripe Checkout pour la réservation d'un événement."""
    try:
        event = Details_event.get_event_by_id(event_id)
        if not event:
            flash("Événement introuvable pour la réservation.", "error")
            return redirect(url_for('index.evenements'))

        unit_amount_cents = parse_price_to_cents(event.price_info)
        if unit_amount_cents == 0:
            flash(f"L'événement '{event.title}' est gratuit. Pas de paiement nécessaire.", "info")
            return redirect(url_for('index.evenement', event_id=event_id))

        # Récupérer les infos du participant depuis la session
        participant_info = session.get('participant_info')
        if not participant_info or participant_info.get('id_evenement') != event_id:
            flash("Les informations du participant sont manquantes. Veuillez recommencer.", "error")
            return redirect(url_for('index.reserver_evenement', event_id=event_id))

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': f'Réservation: {event.title}',
                            'description': f'Réservation pour l\'événement "{event.title}" le {event.event_date.strftime("%d/%m/%Y")}.',
                        },
                        'unit_amount': unit_amount_cents,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            # Passer l'email du client à Stripe et les infos en métadonnées
            customer_email=participant_info.get('email'),
            metadata={
                'id_evenement': event_id,
                'nom_complet': participant_info.get('nom_complet'),
                'age': participant_info.get('age')
            },
            success_url=url_for('index.payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('index.payment_cancel', event_id=event_id, _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création de la session Stripe: {e}")
        flash("Une erreur est survenue lors de la redirection vers la page de paiement. Veuillez réessayer.", "error")
        return redirect(url_for('index.reserver_evenement', event_id=event_id))

@index_bp.route('/don/succes')
@index_bp.route('/reservation/succes')
def payment_success():
    """Page affichée après un paiement réussi."""
    session_id = request.args.get('session_id')
    event = None

    if session_id:
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            metadata = checkout_session.metadata.to_dict()
            id_evenement = metadata.get('id_evenement')

            if id_evenement:
                event = Details_event.get_event_by_id(id_evenement)
                nom_complet = metadata.get('nom_complet', '').split(' ', 1)
                prenom = nom_complet[0]
                nom = nom_complet[1] if len(nom_complet) > 1 else ''
                
                # Récupérer l'email du client depuis les détails de la session de paiement
                email = checkout_session.customer_details.email
               
                # Enregistrer la réservation dans la base de données
                try:
                    Reservation.create(
                        nom=nom,
                        prenom=prenom,
                        age=metadata.get('age'),
                        id_evenement=id_evenement,
                        email=email,
                    )
                except Exception as e:
                    current_app.logger.error(f"Erreur lors de l'enregistrement de la réservation en BDD : {e}")
                # Nettoyer la session
                session.pop('participant_info', None)
        except Exception as e:
            current_app.logger.error(f"Erreur lors du traitement du succès de paiement Stripe : {e}")

    return render_template('payment_success.html', event=event)

@index_bp.route('/don/annulation')
@index_bp.route('/reservation/annulation/<int:event_id>')
def payment_cancel(event_id=None):
    """Page affichée après une annulation de paiement."""
    event = None
    if event_id:
        event = Details_event.get_event_by_id(event_id)
    return render_template('payment_cancel.html', event=event)

@index_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """
    Écoute les événements de Stripe pour confirmer les paiements de manière fiable.
    C'est la méthode de production recommandée.
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET') # À ajouter dans vos variables d'environnement

    if not endpoint_secret:
        current_app.logger.error("Le secret du webhook Stripe n'est pas configuré.")
        return 'Webhook secret non configuré', 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Payload invalide
        return 'Payload invalide', 400
    except stripe.error.SignatureVerificationError as e:
        # Signature invalide
        return 'Signature invalide', 400

    # Gérer l'événement checkout.session.completed
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        metadata = session.get('metadata')

        if metadata and 'id_evenement' in metadata:
            nom_complet = metadata.get('nom_complet', '').split(' ', 1)
            prenom = nom_complet[0]
            nom = nom_complet[1] if len(nom_complet) > 1 else ''
            email = session.get('customer_details', {}).get('email')

            # Crée la réservation (le même code que dans payment_success)
            Reservation.create(nom=nom, prenom=prenom, age=metadata.get('age'), id_evenement=metadata.get('id_evenement'), email=email)

    return 'OK', 200