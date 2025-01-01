from app import db
from app.user import bp
from app.user.forms import LoginForm, RegistrationForm
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
