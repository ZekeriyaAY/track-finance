from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, extract
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

@cashflow_bp.route('/dashboard')
def dashboard():
    # Date filter — default last 12 months
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    today = date.today()
    if date_from:
        try:
            d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            d_from = today - relativedelta(months=12)
    else:
        d_from = today - relativedelta(months=12)

    if date_to:
        try:
            d_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            d_to = today
    else:
        d_to = today

    base_q = CashflowTransaction.query.filter(
        CashflowTransaction.date >= d_from,
        CashflowTransaction.date <= d_to,
    )

    # KPI
    total_income = db.session.query(func.coalesce(func.sum(CashflowTransaction.amount), 0)).filter(
        CashflowTransaction.date >= d_from, CashflowTransaction.date <= d_to,
        CashflowTransaction.type == 'income'
    ).scalar()
    total_expense = db.session.query(func.coalesce(func.sum(CashflowTransaction.amount), 0)).filter(
        CashflowTransaction.date >= d_from, CashflowTransaction.date <= d_to,
        CashflowTransaction.type == 'expense'
    ).scalar()
    transaction_count = base_q.count()
    net_savings = total_income - total_expense

    # Monthly income vs expense
    monthly_data = db.session.query(
        extract('year', CashflowTransaction.date).label('year'),
        extract('month', CashflowTransaction.date).label('month'),
        CashflowTransaction.type,
        func.sum(CashflowTransaction.amount).label('total')
    ).filter(
        CashflowTransaction.date >= d_from, CashflowTransaction.date <= d_to
    ).group_by('year', 'month', CashflowTransaction.type).order_by('year', 'month').all()

    monthly_map = {}
    for row in monthly_data:
        key = f"{int(row.year)}-{int(row.month):02d}"
        if key not in monthly_map:
            monthly_map[key] = {'income': 0, 'expense': 0}
        monthly_map[key][row.type] = float(row.total)

    sorted_months = sorted(monthly_map.keys())
    monthly_labels = sorted_months
    monthly_income = [monthly_map[m]['income'] for m in sorted_months]
    monthly_expense = [monthly_map[m]['expense'] for m in sorted_months]
    monthly_net = [monthly_map[m]['income'] - monthly_map[m]['expense'] for m in sorted_months]

    # Category expense breakdown
    category_data = db.session.query(
        Category.name,
        func.sum(CashflowTransaction.amount).label('total')
    ).join(Category, CashflowTransaction.category_id == Category.id).filter(
        CashflowTransaction.date >= d_from, CashflowTransaction.date <= d_to,
        CashflowTransaction.type == 'expense'
    ).group_by(Category.name).order_by(func.sum(CashflowTransaction.amount).desc()).all()

    category_labels = [r.name for r in category_data]
    category_values = [float(r.total) for r in category_data]

    # Top 10 expense categories (for horizontal bar)
    top10_labels = category_labels[:10]
    top10_values = category_values[:10]

    # Daily trend
    daily_data = db.session.query(
        CashflowTransaction.date,
        CashflowTransaction.type,
        func.sum(CashflowTransaction.amount).label('total')
    ).filter(
        CashflowTransaction.date >= d_from, CashflowTransaction.date <= d_to
    ).group_by(CashflowTransaction.date, CashflowTransaction.type).order_by(CashflowTransaction.date).all()

    daily_map = {}
    for row in daily_data:
        key = row.date.isoformat()
        if key not in daily_map:
            daily_map[key] = {'income': 0, 'expense': 0}
        daily_map[key][row.type] = float(row.total)

    sorted_days = sorted(daily_map.keys())
    daily_labels = sorted_days
    daily_income = [daily_map[d]['income'] for d in sorted_days]
    daily_expense = [daily_map[d]['expense'] for d in sorted_days]

    return render_template('cashflow/dashboard.html',
        total_income=total_income,
        total_expense=total_expense,
        net_savings=net_savings,
        transaction_count=transaction_count,
        monthly_labels=monthly_labels,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        monthly_net=monthly_net,
        category_labels=category_labels,
        category_values=category_values,
        top10_labels=top10_labels,
        top10_values=top10_values,
        daily_labels=daily_labels,
        daily_income=daily_income,
        daily_expense=daily_expense,
        date_from=d_from.isoformat(),
        date_to=d_to.isoformat(),
    )

@cashflow_bp.route('/')
def index():
    # Get filter parameters
    category_id = request.args.get('category_id', type=int)
    tag_id = request.args.get('tag_id', type=int)
    type_filter = request.args.get('type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query with filters
    query = CashflowTransaction.query
    
    if category_id:
        # Include subcategories as well
        category = Category.query.get(category_id)
        if category:
            category_ids = [category_id]
            # Add subcategory IDs if this is a parent category
            subcategories = Category.query.filter_by(parent_id=category_id).all()
            category_ids.extend([sub.id for sub in subcategories])
            query = query.filter(CashflowTransaction.category_id.in_(category_ids))
    
    if tag_id:
        query = query.filter(CashflowTransaction.tags.any(Tag.id == tag_id))
    
    if type_filter in ['income', 'expense']:
        query = query.filter(CashflowTransaction.type == type_filter)
    
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(CashflowTransaction.date >= date_from_parsed)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(CashflowTransaction.date <= date_to_parsed)
        except ValueError:
            pass
    
    transactions = query.order_by(CashflowTransaction.date.desc()).all()
    
    # Get all categories and tags for filter dropdowns
    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    
    return render_template('cashflow/index.html', 
                           transactions=transactions,
                           categories=categories,
                           tags=tags,
                           selected_category=category_id,
                           selected_tag=tag_id,
                           selected_type=type_filter,
                           selected_date_from=date_from,
                           selected_date_to=date_to)

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

