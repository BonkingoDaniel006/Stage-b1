from flask import render_template, abort, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user 
from . import admin_bp
from .models import Event, Message
import os
import uuid
from werkzeug.utils import secure_filename

# Configuration pour l'upload de fichiers
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024 # 5 MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Affiche le tableau de bord principal."""
    # Récupère les données pour les différents onglets
    events = Event.get_all()
    messages = Message.get_all()
    # Passe les listes au template
    return render_template('dashboard.html', events=events, messages=messages)

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
    all_messages = Message.get_all()
    
    return render_template('dashboard.html', events=all_events, messages=all_messages, event_to_view=event_to_view)

def _save_image(file):
    """Sécurise et sauvegarde un fichier image, puis retourne son chemin relatif."""
    # 1. Vérifier si un fichier est présent et si son nom n'est pas vide
    if not file or file.filename == '':
        return None

    # 2. Vérifier l'extension et la taille du fichier
    if not allowed_file(file.filename):
        flash("Type de fichier non autorisé.", "error")
        return None

    # Vérification de la taille (nécessite de lire le fichier, attention à la performance)
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > MAX_FILE_SIZE:
        flash(f"Le fichier est trop volumineux (max {MAX_FILE_SIZE/1024/1024:.0f}MB).", "error")
        return None
    file.seek(0) # Revenir au début du fichier pour la sauvegarde


    # 3. Sécurise le nom du fichier
    filename = secure_filename(file.filename)
    # Crée un nom de fichier unique pour éviter les conflits
    extension = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{extension}"
    
    # Chemin de sauvegarde
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(save_path)
    
    # Retourne le chemin relatif pour le stocker en BDD
    return os.path.join('uploads', unique_filename)

@admin_bp.route('/event/new', methods=['GET', 'POST'])
@login_required
def new_event():
    """Affiche le formulaire de création d'un événement et traite la soumission."""
    if request.method == 'POST':
        # 1. Récupérer les données du formulaire
        data = request.form.to_dict()

        # 2. Gérer le téléversement de l'image
        image_file = request.files.get('image_file')
        if image_file:
            data['image_url'] = _save_image(image_file)

        # 2. Validation simple (les champs requis sont gérés par le formulaire HTML)
        if not data.get('title') or not data.get('event_date'):
            flash('Le titre et la date sont obligatoires.', 'error')
            all_events = Event.get_all()
            all_messages = Message.get_all()
            return render_template('dashboard.html', events=all_events, messages=all_messages, event_to_create=True, form_data=data)

        # 3. Insérer dans la base de données
        new_event_id = Event.create(data)
        
        # 4. Rediriger vers la page du nouvel événement avec un message de succès
        flash('Événement créé avec succès !', 'success')
        return redirect(url_for('admin.view_event', event_id=new_event_id))

    # Si GET, on affiche le formulaire de création
    all_events = Event.get_all()
    all_messages = Message.get_all()
    return render_template('dashboard.html', events=all_events, messages=all_messages, event_to_create=True, form_data={})

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
        image_file = request.files.get('image_file')
        old_image_path = event_to_edit.image_url

        # 2. Gérer la mise à jour de l'image
        if image_file:
            # Une nouvelle image est uploadée, on la sauvegarde
            data['image_url'] = _save_image(image_file)
            # Et on supprime l'ancienne si elle existe
            if old_image_path:
                try:
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    image_path_to_delete = os.path.join(upload_folder, os.path.basename(old_image_path))
                    # Vérifier que le chemin est bien dans le dossier d'uploads
                    if os.path.commonpath([image_path_to_delete, upload_folder]) == upload_folder:
                        if os.path.exists(image_path_to_delete):
                            os.remove(image_path_to_delete)
                except OSError as e:
                    current_app.logger.error(f"Erreur lors de la suppression de l'ancienne image {old_image_path}: {e}")
        elif 'remove_image' in data:
            # La case "Supprimer l'image" est cochée
            data['image_url'] = None
            if old_image_path:
                try:
                    upload_folder = current_app.config['UPLOAD_FOLDER']
                    image_path_to_delete = os.path.join(upload_folder, os.path.basename(old_image_path))
                    if os.path.commonpath([image_path_to_delete, upload_folder]) == upload_folder:
                        if os.path.exists(image_path_to_delete):
                            os.remove(image_path_to_delete)
                except OSError as e:
                    current_app.logger.error(f"Erreur lors de la suppression de l'image {old_image_path}: {e}")
        
        # 3. Mettre à jour l'événement en base de données
        event_to_edit.update(data)
        
        # 3. Rediriger vers la page de vue avec un message de succès
        flash('Événement mis à jour avec succès.', 'success')
        return redirect(url_for('admin.view_event', event_id=event_id))

    # Si GET, on affiche le formulaire de modification
    all_events = Event.get_all()
    all_messages = Message.get_all()
    return render_template('dashboard.html', events=all_events, messages=all_messages, event_to_edit=event_to_edit)


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
    
    # 3. Supprimer l'image associée s'il y en a une
    if event.image_url:
        try:
            # Sécurisation contre le Path Traversal
            upload_folder = current_app.config['UPLOAD_FOLDER']
            image_path = os.path.join(upload_folder, os.path.basename(event.image_url))
            
            # Vérifier que le chemin est bien dans le dossier d'uploads
            if os.path.commonpath([image_path, upload_folder]) == upload_folder:
                if os.path.exists(image_path):
                    os.remove(image_path)
        except OSError as e:
            current_app.logger.error(f"Erreur lors de la suppression de l'image {event.image_url}: {e}")

    event.delete()
    
    return jsonify({'success': True, 'message': 'Événement supprimé avec succès.'})

@admin_bp.route('/message/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_as_read(message_id):
    """Marque un message comme lu."""
    message = next((m for m in Message.get_all() if m.id == message_id), None)
    if not message:
        return jsonify({'success': False, 'message': 'Message non trouvé.'}), 404
    
    if not message.is_read:
        message.mark_as_read()
        return jsonify({'success': True, 'message': 'Message marqué comme lu.'})
    
    return jsonify({'success': True, 'message': 'Message déjà lu.'})

@admin_bp.route('/message/<int:message_id>/conversation', methods=['GET'])
@login_required
def get_conversation(message_id):
    """Récupère tous les messages d'une conversation."""
    conversation = Message.get_conversation(message_id)
    if not conversation:
        return jsonify({'success': False, 'message': 'Conversation non trouvée.'}), 404
    
    # Convertir les objets en dictionnaires pour la réponse JSON
    return jsonify({
        'success': True,
        'conversation': [msg.to_dict() for msg in conversation]
    })

@admin_bp.route('/message/<int:message_id>/reply', methods=['POST'])
@login_required
def reply_to_message(message_id):
    """Enregistre et envoie la réponse à un message."""
    data = request.json
    reply_content = data.get('reply_content')

    if not reply_content:
        return jsonify({'success': False, 'message': 'La réponse ne peut pas être vide.'}), 400

    original_message = Message.get_by_id(message_id)
    if not original_message:
        return jsonify({'success': False, 'message': 'Message original non trouvé.'}), 404

    # Importer ici pour éviter la dépendance circulaire
    from visiteurs.services import send_admin_reply

    # 1. Enregistrer la réponse en BDD
    subject = f"Re: {original_message.subject}"
    Message.reply(original_message.conversation_id, current_user, original_message.sender_email, subject, reply_content)

    # 2. Envoyer la réponse par email au visiteur
    send_admin_reply(original_message.sender_name, original_message.sender_email, subject, reply_content)

    return jsonify({'success': True, 'message': 'Réponse envoyée avec succès.'})