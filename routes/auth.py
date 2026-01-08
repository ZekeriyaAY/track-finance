from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from models.__init__ import db
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
            flash('Invalid username or password.', 'danger')
    
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


@auth_bp.route('/account')
@login_required
def account():
    """Account settings page"""
    return render_template('auth/account.html')


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Handle password change"""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    # Validate current password
    if not current_user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect(url_for('auth.account'))
    
    # Validate new password
    if len(new_password) < 6:
        flash('New password must be at least 6 characters.', 'danger')
        return redirect(url_for('auth.account'))
    
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('auth.account'))
    
    # Update password
    current_user.set_password(new_password)
    db.session.commit()
    
    logger.info(f'User {current_user.username} changed password')
    flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.account'))


@auth_bp.route('/change-username', methods=['POST'])
@login_required
def change_username():
    """Handle username change"""
    new_username = request.form.get('new_username', '').strip()
    password = request.form.get('password', '')
    
    # Validate password
    if not current_user.check_password(password):
        flash('Password is incorrect.', 'danger')
        return redirect(url_for('auth.account'))
    
    # Validate new username
    if len(new_username) < 3:
        flash('Username must be at least 3 characters.', 'danger')
        return redirect(url_for('auth.account'))
    
    if new_username == current_user.username:
        flash('New username is the same as current.', 'danger')
        return redirect(url_for('auth.account'))
    
    # Update username
    old_username = current_user.username
    current_user.username = new_username
    db.session.commit()
    
    logger.info(f'User {old_username} changed username to {new_username}')
    flash('Username changed successfully!', 'success')
    return redirect(url_for('auth.account'))
