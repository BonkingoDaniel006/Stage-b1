import time
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from .forms import LoginForm, RegistrationForm
from .models import User
from .services import _generer_code_verification, _envoyer_otp_brevo, process_login, check_login_lockout, handle_failed_login

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
        email = form.email.data
        # 1. Vérifier si le compte est verrouillé AVANT toute chose
        if check_login_lockout(email):
            return render_template('connexion.html', form=form)

        user = User.find_by_email(email)
        if user and user.check_password(form.password.data):
            # Ne pas connecter l'utilisateur tout de suite.
            # Générer et envoyer l'OTP.
            verification_code = _generer_code_verification()
            if not _envoyer_otp_brevo(user.email, None, verification_code):
                flash("Une erreur est survenue lors de l'envoi de l'e-mail de vérification. Veuillez réessayer.", "error")
                return render_template('connexion.html', form=form)

            # Stocker les informations nécessaires dans la session
            session['otp_login'] = {'code': verification_code, 'expires_at': time.time() + 1200, 'attempts': 0} # 20 minutes
            session['user_id_to_verify'] = user.id

            flash('Un code de vérification a été envoyé à votre adresse e-mail.', 'info')
            return redirect(url_for('auth.verification'))
        else:
            # 2. Gérer la tentative échouée
            handle_failed_login(email)
    
    return render_template('connexion.html', form=form)
# ici la fonctionalité de verification
@auth_bp.route('/verification', methods=['GET', 'POST'])
def verification():
    if request.method == 'POST':
        submitted_code = request.form.get('code')
        result = process_login(submitted_code)

        if result == "success":
            flash('Vérification réussie. Vous êtes maintenant connecté.', 'success')
            return redirect(url_for('auth.dashboard'))
        elif result == "incorrect_code":
            flash('Code de vérification incorrect. Veuillez réessayer.', 'danger')
        elif result == "expired_or_max_attempts":
            flash('Le code de vérification a expiré ou vous avez atteint le nombre maximum de tentatives. Veuillez vous reconnecter.', 'warning')
            return redirect(url_for('auth.connexion'))
        else: # "redirect_register" ou autre cas
            flash('Session de vérification invalide. Veuillez vous reconnecter.', 'danger')
            return redirect(url_for('auth.connexion'))

    # Si la session n'existe pas, on ne devrait pas être sur cette page
    if 'otp_login' not in session or 'user_id_to_verify' not in session:
        flash('Session de vérification invalide. Veuillez vous reconnecter.', 'danger')
        return redirect(url_for('auth.connexion'))

    # Récupérer l'utilisateur à partir de l'ID stocké dans la session
    user = User.get(session.get('user_id_to_verify'))
    if not user:
        flash('Utilisateur de vérification introuvable. Veuillez vous reconnecter.', 'danger')
        return redirect(url_for('auth.connexion'))

    return render_template('verification.html', email=user.email)


@auth_bp.route('/deconnexion')
@login_required
def deconnexion():
    logout_user()
    return redirect(url_for('auth.connexion'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
