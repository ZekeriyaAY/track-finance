from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.investment import Investment
from models.investment_type import InvestmentType

investment_bp = Blueprint('investment', __name__)

@investment_bp.route('/investments')
def index():
    investments = Investment.query.all()
    return render_template('investments/index.html', investments=investments)

@investment_bp.route('/add_investment', methods=['GET', 'POST'])
def add_investment():
    if request.method == 'POST':
        name = request.form['name']
        type_id = request.form['type_id']
        amount = float(request.form['amount'])
        description = request.form['description']
        
        investment = Investment(
            name=name,
            type_id=type_id,
            amount=amount,
            description=description
        )
        
        db.session.add(investment)
        db.session.commit()
        flash('Yatırım başarıyla eklendi!', 'success')
        return redirect(url_for('investment.index'))
    
    investment_types = InvestmentType.query.all()
    return render_template('investments/add.html', investment_types=investment_types)

@investment_bp.route('/edit_investment/<int:id>', methods=['GET', 'POST'])
def edit_investment(id):
    investment = Investment.query.get_or_404(id)
    if request.method == 'POST':
        investment.name = request.form['name']
        investment.type_id = request.form['type_id']
        investment.amount = float(request.form['amount'])
        investment.description = request.form['description']
        
        db.session.commit()
        flash('Yatırım başarıyla güncellendi!', 'success')
        return redirect(url_for('investment.index'))
    
    investment_types = InvestmentType.query.all()
    return render_template('investments/edit.html', investment=investment, investment_types=investment_types)

@investment_bp.route('/delete_investment/<int:id>')
def delete_investment(id):
    investment = Investment.query.get_or_404(id)
    db.session.delete(investment)
    db.session.commit()
    flash('Yatırım başarıyla silindi!', 'success')
    return redirect(url_for('investment.index')) 