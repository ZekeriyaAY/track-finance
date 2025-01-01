from app import db
from app.user import bp
from app.user.forms import LoginForm, RegistrationForm, ProfileForm, ChangePasswordForm
from app.models import User, Transaction, Category, Brand
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required, login_user, logout_user
import sqlalchemy as sa
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from urllib.parse import urlsplit


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_seen()


@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('user.login'))
        login_user(user, remember=form.remember_me.data)
        flash(f'Welcome back, {user.username}!', 'success')
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations! Your registration was successful.', 'success')
        return redirect(url_for('user.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html',
                           title='Profile',
                           user=current_user)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    profile_form = ProfileForm(
        form_type="profile",
        original_username=current_user.username,
        original_email=current_user.email,
        obj=current_user
    )
    password_form = ChangePasswordForm(form_type="password")

    if request.form.get('form_type') == 'profile' and profile_form.validate_on_submit():
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        db.session.commit()
        flash('Your profile has been updated successfully.', 'success')
        return redirect(url_for('user.profile'))

    if request.form.get('form_type') == 'password' and password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Your password has been changed successfully.', 'success')
            return redirect(url_for('user.settings'))
        else:
            flash('Invalid current password.', 'error')

    return render_template('settings.html',
                           title='Settings',
                           profile_form=profile_form,
                           password_form=password_form)
