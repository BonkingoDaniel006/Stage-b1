from flask import render_template, abort, request, jsonify, redirect, url_for, flash, current_app
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

@admin_bp.route('/event/new', methods=['GET', 'POST'])
@login_required
def new_event():
    """Affiche le formulaire de création d'un événement et traite la soumission."""
    if request.method == 'POST':
        # 1. Récupérer les données du formulaire
        data = request.form.to_dict()

        # 2. Validation simple (les champs requis sont gérés par le formulaire HTML)
        if not data.get('title') or not data.get('event_date'):
            flash('Le titre et la date sont obligatoires.', 'error')
            all_events = Event.get_all()
            return render_template('dashboard.html', events=all_events, event_to_create=True, form_data=data)

        # 3. Insérer dans la base de données
        new_event_id = Event.create(data)
        
        # 4. Rediriger vers la page du nouvel événement avec un message de succès
        flash('Événement créé avec succès !', 'success')
        return redirect(url_for('admin.view_event', event_id=new_event_id))

    # Si GET, on affiche le formulaire de création
    all_events = Event.get_all()
    return render_template('dashboard.html', events=all_events, event_to_create=True, form_data={})

@admin_bp.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """Affiche le formulaire de modification d'un événement et traite la soumission."""
    event_to_edit = Event.get_by_id(event_id)
    if not event_to_edit:
        abort(404)

    if request.method == 'POST':
        # 1. Récupérer les données du formulaire
        data = request.form.to_dict()
        
        # 2. Mettre à jour l'événement
        event_to_edit.update(data)
        
        # 3. Rediriger vers la page de vue avec un message de succès
        flash('Événement mis à jour avec succès.', 'success')
        return redirect(url_for('admin.view_event', event_id=event_id))

    # Si GET, on affiche le formulaire de modification
    all_events = Event.get_all()
    return render_template('dashboard.html', events=all_events, event_to_edit=event_to_edit)


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