from app import db
from app.category import bp
from app.category.forms import CategoryForm
from app.models import Category, Transaction
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import sqlalchemy as sa


@bp.route('/category/add', methods=['GET', 'POST'], endpoint='add_category')
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        # Aynı isim ve type kontrolü
        existing_category = Category.query.filter_by(
            user_id=current_user.id,
            name=form.name.data,
            type=form.type.data,  # Type kontrolü eklendi
            is_deleted=False
        ).first()

        if existing_category:
            flash(f'Error: Category "{form.name.data}" with type "{form.type.data}" already exists.', 'danger')
            return redirect(url_for('category.list_category'))

        # Silinmiş category'i kontrol et (aynı isim ve type için)
        deleted_category = Category.query.filter_by(
            user_id=current_user.id,
            original_name=form.name.data,
            type=form.type.data,  # Aynı type'a sahip olanı ara
            is_deleted=True
        ).first()
        
        if deleted_category:
            # Varsa geri getir
            try:
                deleted_category.restore()
                db.session.commit()
                flash(f'Category restored: {deleted_category.name}#{deleted_category.id}', 'success')
            except ValueError as e:
                flash(f'Error: {str(e)}', 'danger')
        else:
            # Yoksa yeni ekle
            category = Category(
                user_id=current_user.id,
                name=form.name.data,
                type=form.type.data
            )
            db.session.add(category)
            db.session.commit()
            flash(f'Category added: {category.name}#{category.id}', 'success')
        
        db.session.expire_all()
        return redirect(url_for('category.list_category'))
    return render_template('addit_category.html', title='Add New Category', form=form)


@bp.route('/category/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = db.first_or_404(sa.select(Category).where(
        Category.id == id, 
        Category.user_id == current_user.id,
        Category.is_deleted == False
    ))
    
    try:
        category.soft_delete()
        db.session.commit()
        flash('Category deleted. {}#{}'.format(category.name, category.id), 'success')
    except ValueError as e:
        flash('Error: Category is already deleted.', 'danger')
    
    return redirect(url_for('category.list_category'))


@bp.route('/category')
@login_required
def list_category():
    categories = db.session.scalars(
        sa.select(Category)
        .where(
            Category.user_id == current_user.id,
            Category.is_deleted == False
        )
    ).all()
    return render_template('list_category.html', title='Categories', categories=categories)


@bp.route('/category/<int:id>/edit', methods=['GET', 'POST'], endpoint='edit_category')
@login_required
def edit_category(id):
    category = db.first_or_404(sa.select(Category).where(
        Category.id == id, 
        Category.user_id == current_user.id,
        Category.is_deleted == False
    ))
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        # Eğer silinmiş aynı isimli ve yeni type'a sahip category varsa
        deleted_same_category = Category.query.filter_by(
            user_id=current_user.id,
            original_name=form.name.data,
            type=form.type.data,
            is_deleted=True
        ).first()
        
        if deleted_same_category:
            try:
                # Silinmiş category'i restore et
                deleted_same_category.restore()
                
                # Transaction'ları güncelle
                transactions = db.session.scalars(
                    sa.select(Transaction).where(Transaction.category_id == category.id)
                ).all()
                
                for transaction in transactions:
                    transaction.category_id = deleted_same_category.id
                
                # Mevcut category'i sil
                category.soft_delete()
                db.session.commit()
                flash(f'Category restored and transactions transferred: {deleted_same_category.name}#{deleted_same_category.id}', 'success')
            except ValueError as e:
                flash(f'Error: {str(e)}', 'danger')
        else:
            # Normal güncelleme
            category.name = form.name.data
            category.type = form.type.data
            db.session.commit()
            flash('Category updated. {}#{}'.format(
                category.name, category.id), 'success')
        
        db.session.expire_all()  # Cache'i temizle
        return redirect(url_for('category.list_category'))
    return render_template('addit_category.html', title='Edit Category', form=form)
