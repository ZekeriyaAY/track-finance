from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, extract, case
from sqlalchemy.orm import joinedload
from models import db
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

def calculate_moving_average(data_list, window=7):
    """Calculate moving average for a list of values."""
    result = []
    for i in range(len(data_list)):
        if i < window - 1:
            result.append(sum(data_list[:i+1]) / (i+1))
        else:
            result.append(sum(data_list[i-window+1:i+1]) / window)
    return result


def calc_pct_change(current, previous):
    """Calculate percentage change between current and previous values."""
    if previous == 0:
        return None
    return ((current - previous) / abs(previous)) * 100


@cashflow_bp.route('/dashboard')
def dashboard():
    # Date filter — default current month
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    today = date.today()
    if date_from:
        try:
            d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            d_from = today.replace(day=1)
    else:
        d_from = today.replace(day=1)

    if date_to:
        try:
            d_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            d_to = today
    else:
        d_to = today

    # Swap if date_from is after date_to
    if d_from > d_to:
        d_from, d_to = d_to, d_from

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

    # Previous period comparison
    period_days = (d_to - d_from).days
    prev_d_to = d_from - relativedelta(days=1)
    prev_d_from = prev_d_to - relativedelta(days=period_days)

    prev_income = db.session.query(func.coalesce(func.sum(CashflowTransaction.amount), 0)).filter(
        CashflowTransaction.date >= prev_d_from, CashflowTransaction.date <= prev_d_to,
        CashflowTransaction.type == 'income'
    ).scalar()
    prev_expense = db.session.query(func.coalesce(func.sum(CashflowTransaction.amount), 0)).filter(
        CashflowTransaction.date >= prev_d_from, CashflowTransaction.date <= prev_d_to,
        CashflowTransaction.type == 'expense'
    ).scalar()
    prev_net_savings = prev_income - prev_expense

    income_change = calc_pct_change(total_income, prev_income)
    expense_change = calc_pct_change(total_expense, prev_expense)
    savings_change = calc_pct_change(net_savings, prev_net_savings)

    # Monthly income vs expense (uses filter dates, with minimum 4-month window)
    default_monthly_from = today - relativedelta(months=3)
    monthly_from = min(d_from, default_monthly_from)
    monthly_to = max(d_to, today)

    monthly_data = db.session.query(
        extract('year', CashflowTransaction.date).label('year'),
        extract('month', CashflowTransaction.date).label('month'),
        CashflowTransaction.type,
        func.sum(CashflowTransaction.amount).label('total')
    ).filter(
        CashflowTransaction.date >= monthly_from, CashflowTransaction.date <= monthly_to
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

    # Category expense breakdown (parent view - aggregates child categories)
    parent_categories = Category.query.filter_by(parent_id=None).options(
        joinedload(Category.subcategories)
    ).all()
    category_result = []
    for parent in parent_categories:
        category_ids = [parent.id] + [c.id for c in parent.subcategories]
        total = db.session.query(func.coalesce(func.sum(CashflowTransaction.amount), 0)).filter(
            CashflowTransaction.date >= d_from,
            CashflowTransaction.date <= d_to,
            CashflowTransaction.type == 'expense',
            CashflowTransaction.category_id.in_(category_ids)
        ).scalar()
        if total > 0:
            category_result.append({
                'name': parent.name,
                'total': float(total),
                'id': parent.id,
                'has_children': len(parent.subcategories) > 0
            })
    category_result.sort(key=lambda x: x['total'], reverse=True)

    category_labels = [r['name'] for r in category_result]
    category_values = [r['total'] for r in category_result]
    category_ids = [r['id'] for r in category_result]
    category_has_children = [r['has_children'] for r in category_result]

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

    # Fill all days between d_from and d_to (no gaps in the chart x-axis)
    sorted_days = []
    current_day = d_from
    while current_day <= d_to:
        key = current_day.isoformat()
        if key not in daily_map:
            daily_map[key] = {'income': 0, 'expense': 0}
        sorted_days.append(key)
        current_day += timedelta(days=1)

    daily_labels = sorted_days
    daily_income = [daily_map[d]['income'] for d in sorted_days]
    daily_expense = [daily_map[d]['expense'] for d in sorted_days]

    # Calculate 7-day moving averages
    daily_income_ma = calculate_moving_average(daily_income, window=7)
    daily_expense_ma = calculate_moving_average(daily_expense, window=7)

    return render_template('cashflow/dashboard.html',
        total_income=total_income,
        total_expense=total_expense,
        net_savings=net_savings,
        transaction_count=transaction_count,
        income_change=income_change,
        expense_change=expense_change,
        savings_change=savings_change,
        monthly_labels=monthly_labels,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        monthly_net=monthly_net,
        category_labels=category_labels,
        category_values=category_values,
        category_ids=category_ids,
        category_has_children=category_has_children,
        top10_labels=top10_labels,
        top10_values=top10_values,
        daily_labels=daily_labels,
        daily_income=daily_income,
        daily_expense=daily_expense,
        daily_income_ma=daily_income_ma,
        daily_expense_ma=daily_expense_ma,
        date_from=d_from.isoformat(),
        date_to=d_to.isoformat(),
        server_today=today.isoformat(),
    )

CASHFLOW_PER_PAGE = 25


@cashflow_bp.route('/')
def index():
    # Get filter parameters
    category_id = request.args.get('category_id', type=int)
    tag_id = request.args.get('tag_id', type=int)
    type_filter = request.args.get('type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)

    # Build query with filters
    query = CashflowTransaction.query

    if search:
        query = query.filter(CashflowTransaction.description.ilike(f'%{search}%'))

    if category_id:
        # Include subcategories as well
        category = db.session.get(Category, category_id)
        if category:
            category_ids = [category_id]
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

    # Summary totals from full filtered query in a single pass
    filtered_ids = query.with_entities(CashflowTransaction.id)
    totals = db.session.query(
        func.coalesce(func.sum(case((CashflowTransaction.type == 'income', CashflowTransaction.amount), else_=0)), 0),
        func.coalesce(func.sum(case((CashflowTransaction.type == 'expense', CashflowTransaction.amount), else_=0)), 0),
    ).filter(CashflowTransaction.id.in_(filtered_ids)).one()
    total_income, total_expense = totals

    # Paginate with eager loading (avoid N+1 for category/parent/tags)
    pagination = query.order_by(CashflowTransaction.date.desc()).options(
        joinedload(CashflowTransaction.category).joinedload(Category.parent),
        joinedload(CashflowTransaction.tags),
    ).paginate(
        page=page, per_page=CASHFLOW_PER_PAGE, error_out=False
    )

    # Get all categories and tags for filter dropdowns
    categories = Category.query.filter_by(parent_id=None).options(
        joinedload(Category.subcategories)
    ).all()
    tags = Tag.query.all()

    return render_template('cashflow/index.html',
                           transactions=pagination.items,
                           pagination=pagination,
                           total_income=total_income,
                           total_expense=total_expense,
                           categories=categories,
                           tags=tags,
                           selected_category=category_id,
                           selected_tag=tag_id,
                           selected_type=type_filter,
                           selected_date_from=date_from,
                           selected_date_to=date_to,
                           selected_search=search)

@cashflow_bp.route('/add', methods=['GET', 'POST'])
def add_cashflow():
    if request.method == 'POST':
        try:
            date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            amount = float(request.form['amount'])
            category_id = int(request.form['category_id'])
        except (ValueError, KeyError):
            flash('Please check date, amount, and category.', 'danger')
            return redirect(url_for('cashflow.add_cashflow'))

        type = request.form['type']
        if type not in ('income', 'expense'):
            flash('Invalid transaction type.', 'danger')
            return redirect(url_for('cashflow.add_cashflow'))
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
            flash('Transaction added!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding transaction: {str(e)}')
            flash('Something went wrong. Please try again.', 'error')
        return redirect(url_for('cashflow.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('cashflow/form.html', categories=categories, tags=tags, today=today)

@cashflow_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_cashflow(id):
    transaction = db.get_or_404(CashflowTransaction, id)
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
            flash('Changes saved!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating transaction: {str(e)}')
            flash('Something went wrong. Please try again.', 'error')
        return redirect(url_for('cashflow.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    return render_template('cashflow/form.html', transaction=transaction, categories=categories, tags=tags)

@cashflow_bp.route('/delete/<int:id>', methods=['POST'])
def delete_cashflow(id):
    transaction = db.get_or_404(CashflowTransaction, id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction removed.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting transaction: {str(e)}')
        flash('Something went wrong. Please try again.', 'error')
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
            
            # Load active categorization rules for auto-categorization
            from models.categorization_rule import CategorizationRule
            active_rules = CategorizationRule.query.filter_by(is_active=True).order_by(
                CategorizationRule.priority.asc()
            ).all()

            for transaction_data in result['transactions']:
                try:
                    # Apply categorization rules (first match wins)
                    matched_category_id = import_category.id
                    matched_tags = [bank_tag]
                    matched_type = transaction_data['type']

                    for rule in active_rules:
                        if rule.matches(transaction_data.get('description', '')):
                            matched_category_id = rule.category_id
                            matched_tags = [bank_tag] + list(rule.tags)
                            if rule.type_override:
                                matched_type = rule.type_override
                            break

                    transaction = CashflowTransaction(
                        date=transaction_data['date'],
                        amount=abs(transaction_data['amount']),
                        type=matched_type,
                        category_id=matched_category_id,
                        description=transaction_data['description'],
                        source='excel_import',
                        tags=matched_tags,
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
        flash('Something unexpected happened. Please try again.', 'error')
    
    return render_template('cashflow/import.html')


@cashflow_bp.route('/bulk-edit', methods=['POST'])
def bulk_edit():
    transaction_ids = request.form.getlist('transaction_ids[]', type=int)
    category_id = request.form.get('category_id', type=int)
    tag_ids = request.form.getlist('tags[]', type=int)
    tag_mode = request.form.get('tag_mode', 'replace')

    if not transaction_ids:
        flash('No transactions selected.', 'error')
        return redirect(url_for('cashflow.index'))

    try:
        transactions = CashflowTransaction.query.filter(CashflowTransaction.id.in_(transaction_ids)).all()

        for txn in transactions:
            if category_id:
                txn.category_id = category_id
            if tag_ids:
                new_tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
                if tag_mode == 'add':
                    existing_ids = {t.id for t in txn.tags}
                    for tag in new_tags:
                        if tag.id not in existing_ids:
                            txn.tags.append(tag)
                else:
                    txn.tags = new_tags

        db.session.commit()
        flash(f'{len(transactions)} transaction(s) updated.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Bulk edit error: {str(e)}')
        flash('Something went wrong during bulk edit.', 'error')

    # Preserve filter params
    redirect_params = {}
    for key in ('category_id', 'tag_id', 'type', 'date_from', 'date_to', 'search'):
        val = request.form.get(f'filter_{key}')
        if val:
            redirect_params[key] = val
    return redirect(url_for('cashflow.index', **redirect_params))


@cashflow_bp.route('/api/category-data')
def category_data_api():
    """API endpoint for category data with drill-down support."""
    view_mode = request.args.get('view_mode', 'parent')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')

    today = date.today()
    if date_from:
        try:
            d_from = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            d_from = today.replace(day=1)
    else:
        d_from = today.replace(day=1)

    if date_to:
        try:
            d_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            d_to = today
    else:
        d_to = today

    # Swap if date_from is after date_to
    if d_from > d_to:
        d_from, d_to = d_to, d_from

    if view_mode == 'parent':
        # Parent categories with aggregated child totals
        parent_categories = Category.query.filter_by(parent_id=None).options(
            joinedload(Category.subcategories)
        ).all()
        result = []
        for parent in parent_categories:
            cat_ids = [parent.id] + [c.id for c in parent.subcategories]
            total = db.session.query(func.coalesce(func.sum(CashflowTransaction.amount), 0)).filter(
                CashflowTransaction.date >= d_from,
                CashflowTransaction.date <= d_to,
                CashflowTransaction.type == 'expense',
                CashflowTransaction.category_id.in_(cat_ids)
            ).scalar()
            if total > 0:
                result.append({
                    'name': parent.name,
                    'total': float(total),
                    'id': parent.id,
                    'has_children': len(parent.subcategories) > 0
                })
        result.sort(key=lambda x: x['total'], reverse=True)
        labels = [r['name'] for r in result]
        values = [r['total'] for r in result]
        cat_ids_list = [r['id'] for r in result]
        has_children = [r['has_children'] for r in result]
        return jsonify({'labels': labels, 'values': values, 'category_ids': cat_ids_list, 'has_children': has_children})

    elif view_mode == 'children_of':
        parent_id = request.args.get('parent_id', type=int)
        if not parent_id:
            return jsonify({'labels': [], 'values': [], 'category_ids': [], 'has_children': []})

        parent = db.session.get(Category, parent_id)
        if not parent:
            return jsonify({'labels': [], 'values': [], 'category_ids': [], 'has_children': []})

        result = []
        # Subcategory totals
        for child in parent.subcategories:
            total = db.session.query(func.coalesce(func.sum(CashflowTransaction.amount), 0)).filter(
                CashflowTransaction.date >= d_from,
                CashflowTransaction.date <= d_to,
                CashflowTransaction.type == 'expense',
                CashflowTransaction.category_id == child.id
            ).scalar()
            if total > 0:
                result.append({'name': child.name, 'total': float(total), 'id': child.id, 'has_children': False})

        # Direct transactions on parent
        direct_total = db.session.query(func.coalesce(func.sum(CashflowTransaction.amount), 0)).filter(
            CashflowTransaction.date >= d_from,
            CashflowTransaction.date <= d_to,
            CashflowTransaction.type == 'expense',
            CashflowTransaction.category_id == parent_id
        ).scalar()
        if direct_total > 0:
            result.append({'name': f'{parent.name} (Direct)', 'total': float(direct_total), 'id': parent_id, 'has_children': False})

        result.sort(key=lambda x: x['total'], reverse=True)
        labels = [r['name'] for r in result]
        values = [r['total'] for r in result]
        cat_ids_list = [r['id'] for r in result]
        has_children_list = [r['has_children'] for r in result]
        return jsonify({'labels': labels, 'values': values, 'parent_name': parent.name, 'category_ids': cat_ids_list, 'has_children': has_children_list})

    else:
        # Child categories only
        category_data = db.session.query(
            Category.name,
            func.sum(CashflowTransaction.amount).label('total')
        ).join(Category, CashflowTransaction.category_id == Category.id).filter(
            CashflowTransaction.date >= d_from,
            CashflowTransaction.date <= d_to,
            CashflowTransaction.type == 'expense',
            Category.parent_id.isnot(None)
        ).group_by(Category.name).order_by(func.sum(CashflowTransaction.amount).desc()).all()

        labels = [r.name for r in category_data]
        values = [float(r.total) for r in category_data]

    return jsonify({'labels': labels, 'values': values})

