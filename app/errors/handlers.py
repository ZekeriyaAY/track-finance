from app import db
from app.errors import bp
from flask import render_template


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@bp.app_errorhandler(Exception)
def handle_exception(error):
    # Here, you can catch other types of errors and send them to the generic error page
    print(error)
    return render_template('error.html', error=error), 500
