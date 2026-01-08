from models.__init__ import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """Single user model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def get_admin_user():
        """Get the single admin user, create if doesn't exist"""
        return User.query.first()
    
    @staticmethod
    def create_default_user(username, password):
        """Create the default admin user if none exists"""
        if User.query.count() == 0:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user
        return None
    
    def __repr__(self):
        return f'<User {self.username}>'
