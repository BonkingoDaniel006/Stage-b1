from flask import jsonify, request, render_template
from flask_login import login_required
from . import admin_bp
from .models import Event

# --- Page principale du tableau de bord ---
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    events = Event.get_all()
    return render_template('dashboard.html', events=events)

# --- API pour le CRUD des événements ---

@admin_bp.route('/events/add', methods=['POST'])
@login_required
def add_event():
    data = request.get_json()
    if not all(k in data for k in ['title', 'description', 'event_date', 'location']):
        return jsonify({'success': False, 'message': 'Données manquantes.'}), 400

    event = Event(id=None, **data)
    if event.save():
        return jsonify({'success': True, 'message': 'Événement ajouté avec succès.'})
    else:
        return jsonify({'success': False, 'message': "Erreur lors de l'ajout de l'événement."}), 500

@admin_bp.route('/events/update/<int:event_id>', methods=['POST'])
@login_required
def update_event(event_id):
    data = request.get_json()
    if not all(k in data for k in ['title', 'description', 'event_date', 'location']):
        return jsonify({'success': False, 'message': 'Données manquantes.'}), 400

    event = Event(id=event_id, **data)
    if event.save():
        return jsonify({'success': True, 'message': 'Événement mis à jour avec succès.'})
    else:
        return jsonify({'success': False, 'message': "Erreur lors de la mise à jour de l'événement."}), 500

@admin_bp.route('/events/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    if Event.delete(event_id):
        return jsonify({'success': True, 'message': 'Événement supprimé avec succès.'})
    else:
        return jsonify({'success': False, 'message': "Erreur lors de la suppression de l'événement."}), 500