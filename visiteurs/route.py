from flask import Blueprint, render_template, redirect, url_for,flash, request, current_app
from visiteurs.model import Event
from visiteurs.model import Details_event

index_bp = Blueprint('index', __name__)


@index_bp.route('/')
def index():
    return render_template('index.html')


@index_bp.route('/evenements')
def evenements():
    events = Event.get_all_events()
    return render_template('evenements.html', events=events)

@index_bp.route('/evenements/<int:event_id>')
def evenement(event_id):
    details = Details_event.get_event_by_id(event_id)
    if details is None:
        flash("Événement introuvable.", "error")
        return redirect(url_for('index.evenements'))
    return render_template('evenement.html', details=details)