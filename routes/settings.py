from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import db
from models.settings import Settings
from utils.data_utils import create_dummy_data, create_default_categories, create_default_tags
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/update-pgadmin-url', methods=['POST'])
def update_pgadmin_url():
    pgadmin_url = request.form.get('pgadmin_url', '').strip()
    
    if not pgadmin_url:
        flash('PgAdmin URL cannot be empty.', 'error')
        return redirect(url_for('settings.index'))
    
    # Validate URL format
    if not pgadmin_url.startswith(('http://', 'https://')):
        pgadmin_url = 'http://' + pgadmin_url
    
    try:
        # Update PgAdmin URL in database
        Settings.set_setting('pgadmin_url', pgadmin_url)
        flash('PgAdmin URL saved.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating PgAdmin URL: {str(e)}")
        flash('Something went wrong. Please try again.', 'error')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/update-currency', methods=['POST'])
def update_currency():
    currency_symbol = request.form.get('currency_symbol', '').strip()

    if not currency_symbol:
        flash('Currency symbol cannot be empty.', 'error')
        return redirect(url_for('settings.index'))

    try:
        Settings.set_setting('currency_symbol', currency_symbol)
        flash('Currency updated!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating currency: {str(e)}")
        flash('Something went wrong. Please try again.', 'error')

    return redirect(url_for('settings.index'))

@settings_bp.route('/')
def index():
    pgadmin_url = Settings.get_setting('pgadmin_url', 'http://localhost:5050')
    currency_symbol = Settings.get_setting('currency_symbol', '₺')
    return render_template('settings/index.html',
                           pgadmin_url=pgadmin_url,
                           currency_symbol=currency_symbol)

@settings_bp.route('/create-dummy-data', methods=['POST'])
def create_dummy_data_route():
    try:
        create_dummy_data()
        flash('Sample data ready!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating dummy data: {str(e)}")
        flash('Something went wrong. Please try again.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-categories', methods=['POST'])
def create_default_categories_route():
    try:
        create_default_categories()
        flash('Default categories created!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default categories: {str(e)}")
        flash('Something went wrong. Please try again.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-tags', methods=['POST'])
def create_default_tags_route():
    try:
        create_default_tags()
        flash('Default tags created!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default tags: {str(e)}")
        flash('Something went wrong. Please try again.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/reset-database', methods=['POST'])
def reset_database():
    try:
        # Clear all data from tables (but keep table structure)
        # Order is critical: junction tables first, then child tables, then parent tables
        
        statements = [
            "DELETE FROM cashflow_transaction_tags",
            "DELETE FROM cashflow_transaction",
            "DELETE FROM tag",
            "DELETE FROM category"
        ]
        
        for sql in statements:
            db.session.execute(text(sql))
        
        # Reset auto-increment counters (PostgreSQL uses SEQUENCE)
        try:
            # PostgreSQL: Reset sequences for auto-increment columns
            sequences = [
                "ALTER SEQUENCE cashflow_transaction_id_seq RESTART WITH 1",
                "ALTER SEQUENCE tag_id_seq RESTART WITH 1",
                "ALTER SEQUENCE category_id_seq RESTART WITH 1"
            ]
            
            for seq_sql in sequences:
                db.session.execute(text(seq_sql))
                
        except Exception as e:
            # If sequence reset fails, just log and continue
            logger.warning(f"Could not reset auto-increment sequences: {str(e)}")
            
        db.session.commit()
        
        flash('All data cleared.', 'success')
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"An error occurred while clearing database data: {str(e)}"
        flash('Something went wrong while clearing data.', 'error')
        logger.error(error_msg)
    
    return redirect(url_for('settings.index'))