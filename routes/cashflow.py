from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models.__init__ import db
from models.cashflow import CashflowTransaction
from models.category import Category
from models.tag import Tag
import logging
import os
import tempfile
from werkzeug.utils import secure_filename
from utils.bank_configs import get_bank_config
from utils.excel_processor import process_excel_data, ExcelImportError

logger = logging.getLogger(__name__)

cashflow_bp = Blueprint('cashflow', __name__, url_prefix='/cashflow')

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cashflow_bp.route('/')
def index():
    transactions = CashflowTransaction.query.order_by(CashflowTransaction.date.desc()).all()
    return render_template('cashflow/index.html', transactions=transactions)

@cashflow_bp.route('/add', methods=['GET', 'POST'])
def add_cashflow():
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        amount = float(request.form['amount'])
        type = request.form['type']
        category_id = int(request.form['category_id'])
        tag_ids = request.form.getlist('tags')
        description = request.form['description']

        try:
            transaction = CashflowTransaction(
                date=date,
                amount=amount,
                type=type,
                category_id=category_id,
                description=description
            )
            if tag_ids:
                tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                transaction.tags = tags
            db.session.add(transaction)
            db.session.commit()
            flash('Transaction added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding transaction: {str(e)}')
            flash('An error occurred while adding the transaction.', 'error')
        return redirect(url_for('cashflow.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('cashflow/form.html', categories=categories, tags=tags, today=today)

@cashflow_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_cashflow(id):
    transaction = CashflowTransaction.query.get_or_404(id)
    if request.method == 'POST':
        try:
            transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            transaction.amount = float(request.form['amount'])
            transaction.type = request.form['type']
            transaction.category_id = int(request.form['category_id'])
            transaction.description = request.form['description']

            tag_ids = request.form.getlist('tags')
            transaction.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
            db.session.commit()
            flash('Transaction updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating transaction: {str(e)}')
            flash('An error occurred while updating the transaction.', 'error')
        return redirect(url_for('cashflow.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    return render_template('cashflow/form.html', transaction=transaction, categories=categories, tags=tags)

@cashflow_bp.route('/delete/<int:id>', methods=['POST'])
def delete_cashflow(id):
    transaction = CashflowTransaction.query.get_or_404(id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting transaction: {str(e)}')
        flash('An error occurred while deleting the transaction.', 'error')
    return redirect(url_for('cashflow.index'))

@cashflow_bp.route('/import', methods=['GET', 'POST'])
def import_excel():
    """Import transactions from Excel file"""
    
    if request.method == 'GET':
        return render_template('cashflow/import.html')
    
    try:
        # File check
        if 'excel_file' not in request.files:
            flash('Please select an Excel file.', 'error')
            return render_template('cashflow/import.html')
        
        file = request.files['excel_file']
        
        if file.filename == '':
            flash('Please select an Excel file.', 'error')
            return render_template('cashflow/import.html')
        
        if not allowed_file(file.filename):
            flash('Only Excel files (.xlsx, .xls, .csv) are supported.', 'error')
            return render_template('cashflow/import.html')
        
        # Bank selection check
        bank_code = request.form.get('bank_code')
        if not bank_code:
            flash('Please select a bank.', 'error')
            return render_template('cashflow/import.html')
        
        # Create temporary file
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        try:
            # Process Excel directly
            result = process_excel_data(temp_path, bank_code)
            
            # Save transactions to database
            saved_count = 0
            
            # Create/find default category (Import)
            import_category = Category.query.filter_by(name='Import').first()
            if not import_category:
                import_category = Category(name='Import')
                db.session.add(import_category)
                db.session.flush()  # Get ID
            
            # Create/find tag for selected bank
            bank_config = get_bank_config(bank_code)
            bank_tag = Tag.query.filter_by(name=bank_config['name']).first()
            if not bank_tag:
                bank_tag = Tag(name=bank_config['name'])
                db.session.add(bank_tag)
                db.session.flush()  # Get ID
            
            for transaction_data in result['transactions']:
                try:
                    transaction = CashflowTransaction(
                        date=transaction_data['date'],  # Already converted to date in excel_processor
                        amount=abs(transaction_data['amount']),  # Amount is always positive
                        type=transaction_data['type'],  # income or expense
                        category_id=import_category.id,
                        description=transaction_data['description'],
                        tags = [bank_tag]
                    )
                    
                    db.session.add(transaction)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"Error saving transaction: {str(e)}")
                    continue
            
            db.session.commit()
            
            # Success message
            success_msg = f'{saved_count} transactions imported successfully.'
            if result.get('failed', 0) > 0:
                success_msg += f' {result["failed"]} transactions failed.'
            flash(success_msg, 'success')
            
            # Show errors if any
            if result.get('errors'):
                error_details = []
                for error in result['errors'][:5]:  # Show first 5 errors
                    error_details.append(f"Row {error['row']}: {error['error']}")
                flash('Errors: ' + '; '.join(error_details), 'warning')
            
        finally:
            # Remove temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        return redirect(url_for('cashflow.index'))
    
    except ExcelImportError as e:
        logger.error(f"ExcelImportError: {str(e)}")
        flash(f'Excel import error: {str(e)}', 'error')
    except Exception as e:
        logger.error(f'Import error: {str(e)}', exc_info=True)
        flash('An unexpected error occurred.', 'error')
    
    return render_template('cashflow/import.html')

