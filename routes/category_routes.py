from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.category import Category
from models.transaction import Transaction

category_bp = Blueprint('category', __name__, url_prefix='/categories')

@category_bp.route('/')
def index():
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/index.html', categories=categories)

@category_bp.route('/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        parent_id = request.form['parent_id'] if request.form['parent_id'] else None
        
        if Category.query.filter_by(name=name, parent_id=parent_id).first():
            flash('Bu kategori zaten mevcut!', 'error')
            return redirect(url_for('category.add_category'))
        
        category = Category(name=name, parent_id=parent_id)
        db.session.add(category)
        db.session.commit()
        flash('Kategori başarıyla eklendi!', 'success')
        return redirect(url_for('category.index'))
    
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/form.html', categories=categories)

@category_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form['name']
        parent_id = request.form['parent_id'] if request.form['parent_id'] else None
        
        existing = Category.query.filter_by(name=name, parent_id=parent_id).first()
        if existing and existing.id != id:
            flash('Bu kategori zaten mevcut!', 'error')
            return redirect(url_for('category.edit_category', id=id))
        
        category.name = name
        category.parent_id = parent_id
        db.session.commit()
        flash('Kategori başarıyla güncellendi!', 'success')
        return redirect(url_for('category.index'))
    
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/form.html', category=category, categories=categories)

@category_bp.route('/delete/<int:id>')
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Check if category has subcategories or transactions
    if category.subcategories:
        flash('Bu kategorinin alt kategorileri var. Önce alt kategorileri silmelisiniz!', 'error')
        return redirect(url_for('category.index'))
    if category.transactions:
        flash('Bu kategoriye ait işlemler var. Önce işlemleri silmelisiniz!', 'error')
        return redirect(url_for('category.index'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Kategori başarıyla silindi!', 'success')
    return redirect(url_for('category.index')) 