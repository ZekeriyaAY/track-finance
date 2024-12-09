from app import db
from app.main import bp
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


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html', title='Home')
