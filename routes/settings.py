from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g
from models.__init__ import db
from models.settings import Settings
from utils.data_utils import create_dummy_data, create_default_categories, create_default_tags, create_default_investment_types
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
    
    # URL formatını kontrol et
    if not pgadmin_url.startswith(('http://', 'https://')):
        pgadmin_url = 'http://' + pgadmin_url
    
    try:
        # Veritabanında PgAdmin URL'sini güncelle
        Settings.set_setting('pgadmin_url', pgadmin_url)
        flash('PgAdmin URL updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating PgAdmin URL: {str(e)}")
        flash('An error occurred while updating PgAdmin URL.', 'error')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/')
def index():
    # Veritabanından URL'leri al, yoksa varsayılan değerleri kullan
    pgadmin_url = Settings.get_setting('pgadmin_url', 'http://localhost:5050')
    return render_template('settings/index.html', pgadmin_url=pgadmin_url)

@settings_bp.route('/create-dummy-data', methods=['POST'])
def create_dummy_data_route():
    try:
        create_dummy_data()
        flash('Dummy data created successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating dummy data: {str(e)}")
        flash('An error occurred while creating dummy data.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-categories', methods=['POST'])
def create_default_categories_route():
    try:
        create_default_categories()
        flash('Default categories created successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default categories: {str(e)}")
        flash('An error occurred while creating default categories.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-tags', methods=['POST'])
def create_default_tags_route():
    try:
        create_default_tags()
        flash('Default tags created successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default tags: {str(e)}")
        flash('An error occurred while creating default tags.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-investment-types', methods=['POST'])
def create_default_investment_types_route():
    try:
        create_default_investment_types()
        flash('Default investment types created successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default investment types: {str(e)}")
        flash('An error occurred while creating default investment types.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/reset-database', methods=['POST'])
def reset_database():
    try:
        # Clear all data from tables (but keep table structure)
        # Order is critical: junction tables first, then child tables, then parent tables
        
        statements = [
            "DELETE FROM cashflow_transaction_tags",
            "DELETE FROM investment_transaction", 
            "DELETE FROM cashflow_transaction",
            "DELETE FROM investment_type",
            "DELETE FROM tag",
            "DELETE FROM category"
        ]
        
        for sql in statements:
            db.session.execute(text(sql))
        
        # Reset auto-increment counters (PostgreSQL uses SEQUENCE)
        try:
            # PostgreSQL: Reset sequences for auto-increment columns
            sequences = [
                "ALTER SEQUENCE investment_transaction_id_seq RESTART WITH 1",
                "ALTER SEQUENCE cashflow_transaction_id_seq RESTART WITH 1",
                "ALTER SEQUENCE investment_type_id_seq RESTART WITH 1",
                "ALTER SEQUENCE tag_id_seq RESTART WITH 1",
                "ALTER SEQUENCE category_id_seq RESTART WITH 1"
            ]
            
            for seq_sql in sequences:
                db.session.execute(text(seq_sql))
                
        except Exception as e:
            # If sequence reset fails, just log and continue
            logger.warning(f"Could not reset auto-increment sequences: {str(e)}")
            
        db.session.commit()
        
        flash('Database data cleared successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"An error occurred while clearing database data: {str(e)}"
        flash('Error clearing database data.', 'error')
        logger.error(error_msg)
    
    return redirect(url_for('settings.index'))