import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'very-secret-key')
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Database - PostgreSQL configuration  
    DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'change_me')
    DB_HOST = os.environ.get('POSTGRES_HOST', 'db')  # localhost in dev, db in Docker
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://track_finance_user:{DB_PASSWORD}@{DB_HOST}:5432/track_finance'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300
    }
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    
    def __init__(self):
        super().__init__()
        if self.SECRET_KEY == 'very-secret-key':
            raise ValueError("Production requires a secure SECRET_KEY! Use: openssl rand -hex 32")

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
