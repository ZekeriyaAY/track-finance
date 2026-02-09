from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g
from models.__init__ import db
from models.settings import Settings
from models.bank_connection import BankConnection
from utils.data_utils import create_dummy_data, create_default_categories, create_default_tags, create_default_investment_types
from utils.bank_sync import get_available_banks, get_adapter, BankSyncError
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
    bank_connections = BankConnection.query.order_by(BankConnection.created_at.desc()).all()
    available_banks = get_available_banks()
    return render_template('settings/index.html',
                           pgadmin_url=pgadmin_url,
                           bank_connections=bank_connections,
                           available_banks=available_banks)

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

@settings_bp.route('/bank-connections/add', methods=['POST'])
def add_bank_connection():
    bank_code = request.form.get('bank_code', '').strip()
    client_id = request.form.get('client_id', '').strip()
    client_secret = request.form.get('client_secret', '').strip()
    account_id = request.form.get('account_id', '').strip() or None

    if not bank_code or not client_id or not client_secret:
        flash('Bank, Client ID, and Client Secret are required.', 'error')
        return redirect(url_for('settings.index'))

    try:
        available = dict(get_available_banks())
        bank_name = available.get(bank_code)
        if not bank_name:
            flash('Invalid bank selection.', 'error')
            return redirect(url_for('settings.index'))

        conn = BankConnection(bank_code=bank_code, bank_name=bank_name, account_id=account_id)
        conn.set_client_id(client_id)
        conn.set_client_secret(client_secret)
        db.session.add(conn)
        db.session.commit()
        flash(f'{bank_name} connection added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error adding bank connection: {e}')
        flash('An error occurred while adding bank connection.', 'error')

    return redirect(url_for('settings.index'))


@settings_bp.route('/bank-connections/delete/<int:id>', methods=['POST'])
def delete_bank_connection(id):
    conn = BankConnection.query.get_or_404(id)
    try:
        db.session.delete(conn)
        db.session.commit()
        flash(f'{conn.bank_name} connection deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting bank connection: {e}')
        flash('An error occurred while deleting bank connection.', 'error')
    return redirect(url_for('settings.index'))


@settings_bp.route('/bank-connections/toggle/<int:id>', methods=['POST'])
def toggle_bank_connection(id):
    conn = BankConnection.query.get_or_404(id)
    try:
        conn.is_active = not conn.is_active
        db.session.commit()
        status = 'activated' if conn.is_active else 'deactivated'
        flash(f'{conn.bank_name} connection {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error toggling bank connection: {e}')
        flash('An error occurred.', 'error')
    return redirect(url_for('settings.index'))


@settings_bp.route('/bank-connections/test/<int:id>', methods=['POST'])
def test_bank_connection(id):
    conn = BankConnection.query.get_or_404(id)
    try:
        adapter_cls = get_adapter(conn.bank_code)
        adapter = adapter_cls(
            client_id=conn.get_client_id(),
            client_secret=conn.get_client_secret(),
            account_id=conn.account_id,
        )
        if adapter.test_connection():
            flash(f'{conn.bank_name} connection test successful!', 'success')
        else:
            flash(f'{conn.bank_name} connection test failed. Check your credentials.', 'error')
    except BankSyncError as e:
        flash(f'Connection test failed: {e}', 'error')
    except Exception as e:
        logger.error(f'Error testing bank connection: {e}')
        flash(f'Connection test error: {e}', 'error')
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
            "DELETE FROM bank_connection",
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
                "ALTER SEQUENCE bank_connection_id_seq RESTART WITH 1",
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