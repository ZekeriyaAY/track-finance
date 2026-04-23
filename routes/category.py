from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func, exists
from models import db
from models.category import Category
from models.cashflow import CashflowTransaction
import logging

logger = logging.getLogger(__name__)

category_bp = Blueprint('category', __name__, url_prefix='/categories')

@category_bp.route('/')
def index():
    categories = Category.query.filter_by(parent_id=None).all()

    # Single aggregation query for all category counts (replaces N+1 model methods)
    raw_counts = db.session.query(
        CashflowTransaction.category_id,
        CashflowTransaction.type,
        func.count(CashflowTransaction.id)
    ).group_by(CashflowTransaction.category_id, CashflowTransaction.type).all()

    per_cat = {}
    for cat_id, txn_type, count in raw_counts:
        if cat_id not in per_cat:
            per_cat[cat_id] = {'income': 0, 'expense': 0}
        per_cat[cat_id][txn_type] = count

    # Build final counts: parent totals include subcategory totals
    category_counts = {}
    for parent in categories:
        parent_income = per_cat.get(parent.id, {}).get('income', 0)
        parent_expense = per_cat.get(parent.id, {}).get('expense', 0)
        for sub in parent.subcategories:
            sub_income = per_cat.get(sub.id, {}).get('income', 0)
            sub_expense = per_cat.get(sub.id, {}).get('expense', 0)
            category_counts[sub.id] = {'income': sub_income, 'expense': sub_expense}
            parent_income += sub_income
            parent_expense += sub_expense
        category_counts[parent.id] = {'income': parent_income, 'expense': parent_expense}

    return render_template('category/index.html', categories=categories, category_counts=category_counts)

@category_bp.route('/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        parent_id = request.form['parent_id'] if request.form['parent_id'] else None
        
        if Category.query.filter_by(name=name, parent_id=parent_id).first():
            flash('A category with that name already exists.', 'error')
            return redirect(url_for('category.add_category'))
        
        try:
            category = Category(name=name, parent_id=parent_id)
            db.session.add(category)
            db.session.commit()
            flash('Category added!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding category: {str(e)}')
            flash('Something went wrong. Please try again.', 'error')
        return redirect(url_for('category.index'))
    
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('category/form.html', categories=categories)

@category_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = db.get_or_404(Category, id)
    if request.method == 'POST':
        name = request.form['name']
        parent_id = request.form['parent_id'] if request.form['parent_id'] else None

        existing = Category.query.filter_by(name=name, parent_id=parent_id).first()
        if existing and existing.id != id:
            flash('A category with that name already exists.', 'error')
            return redirect(url_for('category.edit_category', id=id))
        
        try:
            category.name = name
            category.parent_id = parent_id
            db.session.commit()
            flash('Category updated!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating category: {str(e)}')
            flash('Something went wrong. Please try again.', 'error')
        return redirect(url_for('category.index'))
    
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('category/form.html', category=category, categories=categories)

@category_bp.route('/delete/<int:id>', methods=['POST'])
def delete_category(id):
    category = db.get_or_404(Category, id)
    if db.session.query(exists().where(Category.parent_id == id)).scalar():
        flash('Remove subcategories first before deleting this category.', 'error')
        return redirect(url_for('category.index'))
    if db.session.query(exists().where(CashflowTransaction.category_id == id)).scalar():
        flash("Can't delete — this category has linked transactions.", 'error')
        return redirect(url_for('category.index'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category removed.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting category: {str(e)}')
        flash('Something went wrong. Please try again.', 'error')
    return redirect(url_for('category.index')) 