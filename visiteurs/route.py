from flask import Blueprint, render_template, redirect, url_for,flash, request, current_app
from visiteurs.model import Event
from visiteurs.model import Details_event
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

@index_bp.route('/reserver-evenement/<int:event_id>')
def reserver_evenement(event_id):
    """Affiche la page de réservation pour un événement spécifique."""
    event = Details_event.get_event_by_id(event_id)
    if not event:
        flash("Événement introuvable.", "error")
        return redirect(url_for('index.evenements'))

    # Si l'événement est gratuit, pas besoin de passer par Stripe
    if parse_price_to_cents(event.price_info) == 0:
        flash(f"L'événement '{event.title}' est gratuit. Votre réservation est enregistrée.", "success")
        # Ici, vous pourriez ajouter une logique pour enregistrer la "réservation gratuite"
        return redirect(url_for('index.evenement', event_id=event_id))

    return render_template('reserver_evenement.html',
                           event=event,
                           stripe_public_key=current_app.config.get('STRIPE_PUBLIC_KEY'))

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
            success_url=url_for('index.payment_success', event_id=event_id, _external=True),
            cancel_url=url_for('index.payment_cancel', event_id=event_id, _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création de la session Stripe: {e}")
        flash("Une erreur est survenue lors de la redirection vers la page de paiement. Veuillez réessayer.", "error")
        return redirect(url_for('index.reserver_evenement', event_id=event_id))

@index_bp.route('/don/succes')
@index_bp.route('/reservation/succes/<int:event_id>')
def payment_success(event_id=None):
    """Page affichée après un paiement réussi."""
    event = None
    if event_id:
        event = Details_event.get_event_by_id(event_id)
    return render_template('payment_success.html', event=event)

@index_bp.route('/don/annulation')
@index_bp.route('/reservation/annulation/<int:event_id>')
def payment_cancel(event_id=None):
    """Page affichée après une annulation de paiement."""
    event = None
    if event_id:
        event = Details_event.get_event_by_id(event_id)
    return render_template('payment_cancel.html', event=event)