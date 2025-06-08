from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.investment_type import InvestmentType

investment_type_bp = Blueprint('investment_type', __name__)

@investment_type_bp.route('/investment_types')
def index():
    types = InvestmentType.query.order_by(InvestmentType.name).all()
    return render_template('investment_types/index.html', types=types)

@investment_type_bp.route('/add_investment_type', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        icon = request.form.get('icon', 'fas fa-chart-pie')  # Default icon if not provided
        color = request.form.get('color', '#3B82F6')  # Default color if not provided
        parent_id = request.form['parent_id'] if request.form['parent_id'] else None

        if InvestmentType.query.filter_by(code=code).first():
            flash('Bu kod zaten kullanılıyor!', 'error')
            return redirect(url_for('investment_type.add'))

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

    types = InvestmentType.query.filter_by(parent_id=None).order_by(InvestmentType.name).all()
    return render_template('investment_types/form.html', types=types)

@investment_type_bp.route('/edit_investment_type/<int:id>', methods=['GET', 'POST'])
def edit(id):
    type = InvestmentType.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        code = request.form['code']
        icon = request.form.get('icon', 'fas fa-chart-pie')  # Default icon if not provided
        color = request.form.get('color', '#3B82F6')  # Default color if not provided
        parent_id = request.form['parent_id'] if request.form['parent_id'] else None

        existing = InvestmentType.query.filter_by(code=code).first()
        if existing and existing.id != id:
            flash('Bu kod zaten kullanılıyor!', 'error')
            return redirect(url_for('investment_type.edit', id=id))

        type.name = name
        type.code = code
        type.icon = icon
        type.color = color
        type.parent_id = parent_id
        db.session.commit()
        flash('Yatırım türü başarıyla güncellendi!', 'success')
        return redirect(url_for('investment_type.index'))

    types = InvestmentType.query.filter_by(parent_id=None).order_by(InvestmentType.name).all()
    return render_template('investment_types/form.html', type=type, types=types)

@investment_type_bp.route('/delete_investment_type/<int:id>')
def delete(id):
    type = InvestmentType.query.get_or_404(id)
    
    # Check if type has children
    if type.children:
        flash('Bu türün alt türleri var. Önce alt türleri silmelisiniz!', 'error')
        return redirect(url_for('investment_type.index'))
    
    # Check if type has investments
    if type.investments:
        flash('Bu türe ait yatırımlar var. Önce yatırımları silmelisiniz!', 'error')
        return redirect(url_for('investment_type.index'))
    
    db.session.delete(type)
    db.session.commit()
    flash('Yatırım türü başarıyla silindi!', 'success')
    return redirect(url_for('investment_type.index')) 