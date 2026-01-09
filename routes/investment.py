from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.investment import InvestmentTransaction, InvestmentType
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

investment_bp = Blueprint('investment', __name__, url_prefix='/investments')

@investment_bp.route('/')
def index():
    # Get filter parameters
    investment_type_id = request.args.get('investment_type_id', type=int)
    transaction_type = request.args.get('transaction_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Build query with filters
    query = InvestmentTransaction.query
    
    if investment_type_id:
        # Include subtypes as well
        inv_type = InvestmentType.query.get(investment_type_id)
        if inv_type:
            type_ids = [investment_type_id]
            # Add subtype IDs if this is a parent type
            subtypes = InvestmentType.query.filter_by(parent_id=investment_type_id).all()
            type_ids.extend([sub.id for sub in subtypes])
            query = query.filter(InvestmentTransaction.investment_type_id.in_(type_ids))
    
    if transaction_type in ['buy', 'sell']:
        query = query.filter(InvestmentTransaction.transaction_type == transaction_type)
    
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(InvestmentTransaction.transaction_date >= date_from_parsed)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(InvestmentTransaction.transaction_date <= date_to_parsed)
        except ValueError:
            pass
    
    transactions = query.order_by(InvestmentTransaction.transaction_date.desc()).all()
    
    # Get all investment types for filter dropdown
    investment_types = InvestmentType.query.filter_by(parent_id=None).all()
    
    return render_template('investment/index.html',
                           transactions=transactions,
                           investment_types=investment_types,
                           selected_type=investment_type_id,
                           selected_transaction_type=transaction_type,
                           selected_date_from=date_from,
                           selected_date_to=date_to)

@investment_bp.route('/add', methods=['GET', 'POST'])
def add_investment():
    if request.method == 'POST':
        investment_type_id = request.form['investment_type_id']
        transaction_date = datetime.strptime(request.form['transaction_date'], '%Y-%m-%d')
        transaction_type = request.form['transaction_type']
        price = float(request.form['price'])
        quantity = float(request.form['quantity'])
        description = request.form['description']
        
        try:
            transaction = InvestmentTransaction(
                investment_type_id=investment_type_id,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                price=price,
                quantity=quantity,
                description=description
            )
            db.session.add(transaction)
            db.session.commit()
            flash('Investment transaction added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding investment transaction: {str(e)}')
            flash('An error occurred while adding the investment transaction.', 'error')
        return redirect(url_for('investment.index'))
    
    investment_types = InvestmentType.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('investment/form.html', types=investment_types, today=today)

@investment_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_investment(id):
    transaction = InvestmentTransaction.query.get_or_404(id)
    if request.method == 'POST':
        try:
            transaction.investment_type_id = request.form['investment_type_id']
            transaction.transaction_date = datetime.strptime(request.form['transaction_date'], '%Y-%m-%d')
            transaction.transaction_type = request.form['transaction_type']
            transaction.price = float(request.form['price'])
            transaction.quantity = float(request.form['quantity'])
            transaction.description = request.form['description']
            
            db.session.commit()
            flash('Investment transaction updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating investment transaction: {str(e)}')
            flash('An error occurred while updating the investment transaction.', 'error')
        return redirect(url_for('investment.index'))
    
    investment_types = InvestmentType.query.all()
    return render_template('investment/form.html', transaction=transaction, types=investment_types)

@investment_bp.route('/delete/<int:id>', methods=['POST'])
def delete_investment(id):
    transaction = InvestmentTransaction.query.get_or_404(id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash('Investment transaction deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting investment transaction: {str(e)}")
        flash('An error occurred while deleting the investment transaction.', 'error')
    return redirect(url_for('investment.index')) 