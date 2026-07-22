from flask import render_template, abort, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from . import admin_bp
from .models import Event

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Affiche le tableau de bord principal."""
    # Récupère tous les événements depuis la base de données
    events = Event.get_all()
    # Passe la liste des événements au template
    return render_template('dashboard.html', events=events)

@admin_bp.route('/event/<int:event_id>')
@login_required
def view_event(event_id):
    """Affiche les détails d'un événement spécifique."""
    event_to_view = Event.get_by_id(event_id)
    if not event_to_view:
        # Si l'événement n'est pas trouvé, renvoie une erreur 404
        abort(404)
    
    # On récupère aussi la liste de tous les événements pour la table en arrière-plan
    all_events = Event.get_all()
    
    return render_template('dashboard.html', events=all_events, event_to_view=event_to_view)

@admin_bp.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    """Supprime un événement après vérification du mot de passe."""
    password = request.json.get('password')

    # 1. Vérifier le mot de passe de l'utilisateur courant
    if not password or not current_user.check_password(password):
        return jsonify({'success': False, 'message': 'Mot de passe incorrect.'}), 403

    # 2. Récupérer et supprimer l'événement
    event = Event.get_by_id(event_id)
    if not event:
        return jsonify({'success': False, 'message': 'Événement non trouvé.'}), 404
    
    event.delete()
    
    return jsonify({'success': True, 'message': 'Événement supprimé avec succès.'})

@admin_bp.route('/api/event/<int:event_id>', methods=['GET'])
@login_required
def get_event_data(event_id):
    """Fournit les données d'un événement en format JSON."""
    event = Event.get_by_id(event_id)
    if not event:
        return jsonify({'success': False, 'message': 'Événement non trouvé.'}), 404
    return jsonify(event.to_dict())

@admin_bp.route('/event/<int:event_id>/update', methods=['POST'])
@login_required
def update_event(event_id):
    """Met à jour un événement."""
    event = Event.get_by_id(event_id)
    if not event:
        return jsonify({'success': False, 'message': 'Événement non trouvé.'}), 404

    data = request.form.to_dict()
    # Convertir les champs numériques si nécessaire
    if 'max_attendees' in data and data['max_attendees']:
        data['max_attendees'] = int(data['max_attendees'])

    event.update(data)
    return jsonify({'success': True, 'message': 'Événement mis à jour avec succès.'})