import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, redirect, url_for, request, session, g
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from models.__init__ import db
from flask_wtf import CSRFProtect
from config import config
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Trust proxy headers if behind reverse proxy (nginx, traefik, etc.)
    if os.environ.get('BEHIND_PROXY', 'False').lower() == 'true':
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=1,
            x_proto=1,
            x_host=1,
            x_prefix=1
        )
    
    # Configure logging
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    log_format = app.config.get('LOG_FORMAT')
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # File handler with rotation (10MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(
        'logs/track-finance.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set Flask app logger
    app.logger.setLevel(log_level)
    if not app.logger.handlers:
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models.user import User
        return User.query.get(int(user_id))
    
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
    
    # Require authentication for all routes except auth and health
    @app.before_request
    def require_login():
        # Allow access to auth routes, static files, and health check
        allowed_endpoints = ['auth.login', 'auth.logout', 'static', 'health_check']
        if request.endpoint and request.endpoint not in allowed_endpoints:
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
    
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
    def inject_external_urls():
        from models.settings import Settings
        pgadmin_url = Settings.get_setting('pgadmin_url', 'http://localhost:5050')
        return dict(pgadmin_url=pgadmin_url)

    # Import blueprints
    from routes.cashflow import cashflow_bp
    from routes.category import category_bp
    from routes.tag import tag_bp
    from routes.investment import investment_bp
    from routes.investment_type import investment_type_bp
    from routes.settings import settings_bp
    from routes.auth import auth_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(cashflow_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(investment_bp)
    app.register_blueprint(investment_type_bp)
    app.register_blueprint(settings_bp)
    
    # Create default admin user on first run (after migrations)
    @app.before_request
    def ensure_admin_user():
        """Create default admin user if none exists (runs once)"""
        if getattr(app, '_admin_user_checked', False):
            return
        app._admin_user_checked = True
        
        try:
            from models.user import User
            if User.query.count() == 0:
                admin_user = User.create_default_user(
                    username=app.config.get('ADMIN_USERNAME', 'admin'),
                    password=app.config.get('ADMIN_PASSWORD', 'changeme123')
                )
                if admin_user:
                    app.logger.info(f'Created default admin user: {admin_user.username}')
        except Exception as e:
            # Table might not exist yet (before migrations)
            app.logger.debug(f'Could not check/create admin user: {e}')
    
    @app.route('/')
    def index():
        return redirect(url_for('cashflow.index'))
    
    @app.route('/health')
    def health_check():
        """Health check endpoint for load balancers"""
        from sqlalchemy import text
        try:
            # Test database connectivity
            db.session.execute(text('SELECT 1'))
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