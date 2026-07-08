from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .forms import LoginForm, RegistrationForm
from .models import User

@auth_bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(id=None, email=form.email.data, password_hash=None)
        user.set_password(form.password.data)
        user.save()
        flash('Votre compte a été créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('auth.connexion'))
    
    # Pour réutiliser le template existant sans le modifier
    return render_template('inscription.html', form=form)

@auth_bp.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Connexion échouée. Veuillez vérifier votre email et mot de passe.', 'danger')
    
    return render_template('connexion.html', form=form)

@auth_bp.route('/deconnexion')
@login_required
def deconnexion():
    logout_user()
    return redirect(url_for('auth.connexion'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')