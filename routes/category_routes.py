from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.category import Category
from models.transaction import Transaction

category_bp = Blueprint('category', __name__)

@category_bp.route('/categories')
def index():
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/index.html', categories=categories)

@category_bp.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        parent_id = request.form.get('parent_id')
        
        if parent_id == '':
            parent_id = None
        else:
            parent_id = int(parent_id)
            
        category = Category(name=name, parent_id=parent_id)
        db.session.add(category)
        db.session.commit()
        flash('Kategori başarıyla eklendi!', 'success')
        return redirect(url_for('category.index'))
    
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/add.html', categories=categories)

@category_bp.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form['name']
        parent_id = request.form.get('parent_id')
        
        if parent_id == '':
            parent_id = None
        else:
            parent_id = int(parent_id)
            
        # Eğer kategori kendisini üst kategori olarak seçmeye çalışıyorsa engelle
        if parent_id == category.id:
            flash('Bir kategori kendisini üst kategori olarak seçemez!', 'error')
            return redirect(url_for('category.edit_category', id=id))
            
        # Eğer seçilen üst kategori bir alt kategori ise engelle
        if parent_id:
            parent = Category.query.get(parent_id)
            if parent and parent.is_subcategory():
                flash('Alt kategoriler üst kategori olamaz!', 'error')
                return redirect(url_for('category.edit_category', id=id))
            
        category.parent_id = parent_id
        db.session.commit()
        flash('Kategori başarıyla güncellendi!', 'success')
        return redirect(url_for('category.index'))
    
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/edit.html', category=category, categories=categories)

@category_bp.route('/delete_category/<int:id>')
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Kategoriye bağlı işlemleri kontrol et
    transactions = Transaction.query.filter_by(category_id=id).all()
    if transactions:
        flash('Bu kategoriye bağlı işlemler var. Önce bu işlemleri başka bir kategoriye taşıyın veya silin.', 'error')
        return redirect(url_for('category.index'))
    
    # Alt kategorileri kontrol et
    subcategories = Category.query.filter_by(parent_id=id).all()
    if subcategories:
        flash('Bu kategorinin alt kategorileri var. Önce alt kategorileri silin.', 'error')
        return redirect(url_for('category.index'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Kategori başarıyla silindi!', 'success')
    return redirect(url_for('category.index')) 