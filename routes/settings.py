from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g
from flask_babel import _
from models.__init__ import db
from models.settings import Settings
from utils.data_utils import create_dummy_data, create_default_categories, create_default_tags, create_default_investment_types
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/change-language', methods=['POST'])
def change_language():
    lang = request.form.get('language')
    if lang in ['en', 'tr']:
        session['lang'] = lang
    return redirect(url_for('settings.index'))

@settings_bp.route('/update-grafana-url', methods=['POST'])
def update_grafana_url():
    grafana_url = request.form.get('grafana_url', '').strip()
    
    if not grafana_url:
        flash(_('Grafana URL cannot be empty.'), 'error')
        return redirect(url_for('settings.index'))
    
    # URL formatını kontrol et
    if not grafana_url.startswith(('http://', 'https://')):
        grafana_url = 'http://' + grafana_url
    
    try:
        # Veritabanında Grafana URL'sini güncelle
        Settings.set_setting('grafana_url', grafana_url)
        flash(_('Grafana URL updated successfully.'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating Grafana URL: {str(e)}")
        flash(_('An error occurred while updating Grafana URL.'), 'error')
    
    return redirect(url_for('settings.index'))

@settings_bp.route('/')
def index():
    # Veritabanından Grafana URL'sini al, yoksa varsayılan değeri kullan
    grafana_url = Settings.get_setting('grafana_url', 'http://localhost:3000')
    return render_template('settings/index.html', grafana_url=grafana_url)

@settings_bp.route('/create-dummy-data', methods=['POST'])
def create_dummy_data_route():
    try:
        create_dummy_data()
        flash(_('Dummy data created successfully.'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating dummy data: {str(e)}")
        flash(_('An error occurred while creating dummy data.'), 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-categories', methods=['POST'])
def create_default_categories_route():
    try:
        create_default_categories()
        flash(_('Default categories created successfully.'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default categories: {str(e)}")
        flash(_('An error occurred while creating default categories.'), 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-tags', methods=['POST'])
def create_default_tags_route():
    try:
        create_default_tags()
        flash(_('Default tags created successfully.'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default tags: {str(e)}")
        flash(_('An error occurred while creating default tags.'), 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-investment-types', methods=['POST'])
def create_default_investment_types_route():
    try:
        create_default_investment_types()
        flash(_('Default investment types created successfully.'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default investment types: {str(e)}")
        flash(_('An error occurred while creating default investment types.'), 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/reset-database', methods=['POST'])
def reset_database():
    try:
        # Clear all data from tables (but keep table structure)
        # Order is critical: junction tables first, then child tables, then parent tables
        
        # SQLite requires each statement to be executed separately
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
        
        # SQLite uses AUTOINCREMENT instead of SEQUENCE
        # Reset auto-increment counters by updating sqlite_sequence if it exists
        try:
            # Check if sqlite_sequence table exists
            check_sequence_table = "SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'"
            result = db.session.execute(text(check_sequence_table)).fetchone()
            
            if result:
                # Simple approach: just delete all entries and they'll be recreated with seq=1
                db.session.execute(text("DELETE FROM sqlite_sequence WHERE name IN ('investment_transaction', 'cashflow_transaction', 'investment_type', 'tag', 'category')"))
                
        except Exception as e:
            # If sqlite_sequence operations fail, just log and continue
            logger.warning(f"Could not reset auto-increment counters: {str(e)}")
            
        db.session.commit()
        
        flash(_('Database data cleared successfully.'), 'success')
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"An error occurred while clearing database data: {str(e)}"
        flash(_('Error clearing database data.'), 'error')
        logger.error(error_msg)
    
    return redirect(url_for('settings.index'))