from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db
from models.category import Category
import logging

logger = logging.getLogger(__name__)

category_bp = Blueprint('category', __name__, url_prefix='/categories')

@category_bp.route('/')
def index():
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('category/index.html', categories=categories)

@category_bp.route('/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        parent_id = request.form['parent_id'] if request.form['parent_id'] else None
        
        if Category.query.filter_by(name=name, parent_id=parent_id).first():
            flash('This category already exists!', 'error')
            return redirect(url_for('category.add_category'))
        
        try:
            category = Category(name=name, parent_id=parent_id)
            db.session.add(category)
            db.session.commit()
            flash('Category added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding category: {str(e)}')
            flash('An error occurred while adding the category.', 'error')
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
            flash('This category already exists!', 'error')
            return redirect(url_for('category.edit_category', id=id))
        
        try:
            category.name = name
            category.parent_id = parent_id
            db.session.commit()
            flash('Category updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating category: {str(e)}')
            flash('An error occurred while updating the category.', 'error')
        return redirect(url_for('category.index'))
    
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('category/form.html', category=category, categories=categories)

@category_bp.route('/delete/<int:id>', methods=['POST'])
def delete_category(id):
    category = db.get_or_404(Category, id)
    if category.subcategories:
        flash('This category has subcategories. You must delete them first!', 'error')
        return redirect(url_for('category.index'))
    if category.transactions:
        flash('This category has associated transactions and cannot be deleted.', 'error')
        return redirect(url_for('category.index'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting category: {str(e)}')
        flash('An error occurred while deleting the category.', 'error')
    return redirect(url_for('category.index')) 