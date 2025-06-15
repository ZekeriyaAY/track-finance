from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.investment import Investment
from models.investment_type import InvestmentType
from models.investment_history import InvestmentHistory
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

investment_bp = Blueprint('investment', __name__, url_prefix='/investments')

@investment_bp.route('/')
def index():
    investments = Investment.query.all()
    return render_template('investments/index.html', investments=investments)

@investment_bp.route('/add', methods=['GET', 'POST'])
def add_investment():
    if request.method == 'POST':
        type_id = request.form['type_id']
        purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d')
        purchase_price = float(request.form['purchase_price'])
        current_price = float(request.form['current_price'])
        quantity = float(request.form['quantity'])
        description = request.form['description']
        
        investment = Investment(
            type_id=type_id,
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            current_price=current_price,
            quantity=quantity,
            description=description
        )
        
        db.session.add(investment)
        db.session.commit()
        flash('Yatırım başarıyla eklendi!', 'success')
        return redirect(url_for('investment.index'))
    
    investment_types = InvestmentType.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('investments/form.html', types=investment_types, today=today)

@investment_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_investment(id):
    investment = Investment.query.get_or_404(id)
    if request.method == 'POST':
        investment.type_id = request.form['type_id']
        investment.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d')
        investment.purchase_price = float(request.form['purchase_price'])
        investment.current_price = float(request.form['current_price'])
        investment.quantity = float(request.form['quantity'])
        investment.description = request.form['description']
        
        db.session.commit()
        flash('Yatırım başarıyla güncellendi!', 'success')
        return redirect(url_for('investment.index'))
    
    investment_types = InvestmentType.query.all()
    return render_template('investments/form.html', investment=investment, types=investment_types)

@investment_bp.route('/delete/<int:id>', methods=['POST'])
def delete_investment(id):
    """Yatırımı siler."""
    investment = Investment.query.get_or_404(id)
    
    try:
        # Önce ilişkili geçmiş kayıtlarını sil
        InvestmentHistory.query.filter_by(investment_id=id).delete()
        # Sonra yatırımı sil
        db.session.delete(investment)
        db.session.commit()
        flash('Yatırım başarıyla silindi.', 'success')
        logger.info(f"Yatırım silindi: {investment.name}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Yatırım silinirken bir hata oluştu: {str(e)}")
        flash('Yatırım silinirken bir hata oluştu.', 'error')
    
    return redirect(url_for('investment.index')) 