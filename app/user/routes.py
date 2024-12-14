from app import db
from app.user import bp
from app.user.forms import EditProfileForm
from app.models import User
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
import sqlalchemy as sa
from datetime import datetime, timezone


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('user.html', title=username, user=user)


@bp.route('/profile')
@login_required
def profile():
    user = db.first_or_404(sa.select(User).where(
        User.username == current_user.username))
    return render_template('profile.html', title='Profile', user=user)


@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('user.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
