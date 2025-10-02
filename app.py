import os
import logging
from flask import Flask, redirect, url_for, request, session, g
from flask_migrate import Migrate
from models.__init__ import db
from flask_wtf import CSRFProtect
from config import config

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
        format=app.config.get('LOG_FORMAT')
    )
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    
    # Security headers middleware
    @app.after_request
    def add_security_headers(response):
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Only send referrer for same-origin requests
        response.headers['Referrer-Policy'] = 'same-origin'
        
        # HTTPS enforcement in production
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    # Request logging for production
    @app.before_request
    def log_request_info():
        if not app.debug:
            app.logger.info(f'{request.method} {request.url} - {request.remote_addr}')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        app.logger.warning(f'404 error: {request.url} - {request.remote_addr}')
        return redirect(url_for('cashflow.index'))
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'500 error: {error} - {request.url} - {request.remote_addr}')
        return redirect(url_for('cashflow.index'))
    
    @app.context_processor
    def inject_grafana_url():
        from models.settings import Settings
        grafana_url = Settings.get_setting('grafana_url', 'http://localhost:3000')
        return dict(grafana_url=grafana_url)

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
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancers"""
        try:
            # Test database connectivity
            db.session.execute('SELECT 1')
            return {'status': 'healthy', 'service': 'track-finance', 'database': 'connected'}, 200
        except Exception as e:
            app.logger.error(f'Health check failed: {e}')
            return {'status': 'unhealthy', 'service': 'track-finance', 'error': str(e)}, 503
    
    app.logger.info(f'Track Finance app created with config: {config_name}')
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Development server only - production uses Gunicorn
    # Debug mode is automatically determined by FLASK_ENV in config
    app.run(host='127.0.0.1', port=5000)