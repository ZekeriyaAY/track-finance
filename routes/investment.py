from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_babel import _
from models.__init__ import db
from models.investment import InvestmentTransaction, InvestmentType
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

investment_bp = Blueprint('investment', __name__, url_prefix='/investments')

@investment_bp.route('/')
def index():
    transactions = InvestmentTransaction.query.order_by(InvestmentTransaction.transaction_date.desc()).all()
    return render_template('investment/index.html', transactions=transactions)

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
            flash(_('Investment transaction added successfully!'), 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding investment transaction: {str(e)}')
            flash(_('An error occurred while adding the investment transaction.'), 'error')
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
            flash(_('Investment transaction updated successfully!'), 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating investment transaction: {str(e)}')
            flash(_('An error occurred while updating the investment transaction.'), 'error')
        return redirect(url_for('investment.index'))
    
    investment_types = InvestmentType.query.all()
    return render_template('investment/form.html', transaction=transaction, types=investment_types)

@investment_bp.route('/delete/<int:id>', methods=['POST'])
def delete_investment(id):
    transaction = InvestmentTransaction.query.get_or_404(id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash(_('Investment transaction deleted successfully.'), 'success')
        logger.info(f"Investment transaction deleted: {transaction.description}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting investment transaction: {str(e)}")
        flash(_('An error occurred while deleting the investment transaction.'), 'error')
    return redirect(url_for('investment.index')) 