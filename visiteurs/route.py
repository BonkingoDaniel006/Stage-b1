from flask import Blueprint, render_template, redirect, url_for,flash, request, current_app
from visiteurs.model import Event
from visiteurs.model import Details_event
import stripe

index_bp = Blueprint('index', __name__)


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

@index_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
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
            cancel_url=url_for('index.payment_cancel', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la création de la session Stripe: {e}")
        flash("Une erreur est survenue lors de la redirection vers la page de paiement. Veuillez réessayer.", "error")
        return redirect(url_for('index.don'))

@index_bp.route('/don/succes')
def payment_success():
    """Page affichée après un paiement réussi."""
    return render_template('payment_success.html')

@index_bp.route('/don/annulation')
def payment_cancel():
    """Page affichée après une annulation de paiement."""
    return render_template('payment_cancel.html')