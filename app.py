import os
from flask import Flask, redirect, url_for, request, session, g
from flask_migrate import Migrate
from models.__init__ import db
from flask_wtf import CSRFProtect
from flask_babel import Babel
from config import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    
    # Babel Configuration
    def get_locale():
        # First check session, then check browser language
        lang = session.get('lang')
        if lang in ['en', 'tr']:
            return lang
        return 'en'

    babel = Babel(app, locale_selector=get_locale)

    @app.before_request
    def set_lang_code():
        g.lang_code = get_locale()

    @app.context_processor
    def inject_locale():
        return dict(get_locale=get_locale, lang_code=g.get('lang_code', 'en'))

    # Import blueprints
    from routes.cashflow import cashflow_bp
    from routes.category import category_bp
    from routes.tag import tag_bp
    from routes.investment import investment_bp
    from routes.investment_type import investment_type_bp
    from routes.settings import settings_bp

    # Register blueprints
    app.register_blueprint(cashflow_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(investment_bp)
    app.register_blueprint(investment_type_bp)
    app.register_blueprint(settings_bp)
    
    @app.route('/')
    def index():
        return redirect(url_for('cashflow.index'))
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Production configuration for Docker
    app.run(host='0.0.0.0', port=5000, debug=False)