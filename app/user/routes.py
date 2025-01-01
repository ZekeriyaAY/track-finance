from app import db
from app.user import bp
from app.models import User, Transaction, Category, Brand
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
import sqlalchemy as sa
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_seen()
