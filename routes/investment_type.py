from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.investment import InvestmentType

investment_type_bp = Blueprint('investment_type', __name__, url_prefix='/investment-types')

@investment_type_bp.route('/')
def index():
    types = InvestmentType.query.filter_by(parent_id=None).all()
    return render_template('investment_type/index.html', types=types)

@investment_type_bp.route('/add', methods=['GET', 'POST'])
def add_investment_type():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        icon = request.form['icon']
        color = request.form['color']
        parent_id = request.form['parent_id'] if request.form['parent_id'] else None
        
        if InvestmentType.query.filter_by(name=name).first():
            flash('Bu yatırım türü zaten mevcut!', 'error')
            return redirect(url_for('investment_type.add_investment_type'))
        
        type = InvestmentType(
            name=name,
            code=code,
            icon=icon,
            color=color,
            parent_id=parent_id
        )
        db.session.add(type)
        db.session.commit()
        flash('Yatırım türü başarıyla eklendi!', 'success')
        return redirect(url_for('investment_type.index'))
    
    types = InvestmentType.query.filter_by(parent_id=None).all()
    return render_template('investment_type/form.html', types=types)

@investment_type_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_investment_type(id):
    type = InvestmentType.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        icon = request.form['icon']
        color = request.form['color']
        parent_id = request.form['parent_id'] if request.form['parent_id'] else None
        
        existing = InvestmentType.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash('Bu yatırım türü zaten mevcut!', 'error')
            return redirect(url_for('investment_type.edit_investment_type', id=id))
        
        type.name = name
        type.code = code
        type.icon = icon
        type.color = color
        type.parent_id = parent_id
        db.session.commit()
        flash('Yatırım türü başarıyla güncellendi!', 'success')
        return redirect(url_for('investment_type.index'))
    
    types = InvestmentType.query.filter_by(parent_id=None).all()
    return render_template('investment_type/form.html', type=type, types=types)

@investment_type_bp.route('/delete/<int:id>', methods=['POST'])
def delete_investment_type(id):
    type = InvestmentType.query.get_or_404(id)
    
    # Check if type has children or investments
    if type.children:
        flash('Bu yatırım türünün alt türleri var. Önce alt türleri silmelisiniz!', 'error')
        return redirect(url_for('investment_type.index'))
    if type.investments:
        flash('Bu yatırım türüne ait yatırımlar var. Önce yatırımları silmelisiniz!', 'error')
        return redirect(url_for('investment_type.index'))
    
    db.session.delete(type)
    db.session.commit()
    flash('Yatırım türü başarıyla silindi!', 'success')
    return redirect(url_for('investment_type.index')) 