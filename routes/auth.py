from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    # If already logged in, redirect to home
    if current_user.is_authenticated:
        return redirect(url_for('cashflow.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False) == 'on'
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            logger.info(f'User {username} logged in successfully from {request.remote_addr}')
            
            # Redirect to the page they were trying to access, or home
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('cashflow.index'))
        else:
            logger.warning(f'Failed login attempt for username: {username} from {request.remote_addr}')
            flash('Invalid username or password', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    username = current_user.username
    logout_user()
    logger.info(f'User {username} logged out')
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
