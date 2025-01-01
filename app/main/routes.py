from app.main import bp
from flask import redirect, url_for, render_template
from flask_login import login_required, current_user


@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    return render_template('landing.html', title='Welcome')
