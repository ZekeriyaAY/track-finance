from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.investment import InvestmentType
import logging

logger = logging.getLogger(__name__)

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
            flash('This investment type already exists!', 'error')
            return redirect(url_for('investment_type.add_investment_type'))
        
        try:
            type = InvestmentType(
                name=name,
                code=code,
                icon=icon,
                color=color,
                parent_id=parent_id
            )
            db.session.add(type)
            db.session.commit()
            flash('Investment type added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding investment type: {str(e)}')
            flash('An error occurred while adding the investment type.', 'error')
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
            flash('This investment type already exists!', 'error')
            return redirect(url_for('investment_type.edit_investment_type', id=id))
        
        try:
            type.name = name
            type.code = code
            type.icon = icon
            type.color = color
            type.parent_id = parent_id
            db.session.commit()
            flash('Investment type updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating investment type: {str(e)}')
            flash('An error occurred while updating the investment type.', 'error')
        return redirect(url_for('investment_type.index'))
    
    types = InvestmentType.query.filter_by(parent_id=None).all()
    return render_template('investment_type/form.html', type=type, types=types)

@investment_type_bp.route('/delete/<int:id>', methods=['POST'])
def delete_investment_type(id):
    type = InvestmentType.query.get_or_404(id)
    if type.children:
        flash('This investment type has subtypes. You must delete them first!', 'error')
        return redirect(url_for('investment_type.index'))
    if type.investments:
        flash('This investment type has associated investments and cannot be deleted.', 'error')
        return redirect(url_for('investment_type.index'))
    
    try:
        db.session.delete(type)
        db.session.commit()
        flash('Investment type deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting investment type: {str(e)}')
        flash('An error occurred while deleting the investment type.', 'error')
    return redirect(url_for('investment_type.index')) 