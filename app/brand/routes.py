from app import db
from app.brand import bp
from app.brand.forms import BrandForm
from app.models import Brand, Transaction
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import sqlalchemy as sa


@bp.route('/brand/add', methods=['GET', 'POST'], endpoint='add_brand')
@login_required
def add_brand():
    form = BrandForm()
    if form.validate_on_submit():
        # Önce aktif veya silinmiş aynı isimli brand var mı kontrol et
        existing_brand = Brand.query.filter_by(
            user_id=current_user.id,
            name=form.name.data,
            is_deleted=False
        ).first()

        if existing_brand:
            flash(f'Error: Brand "{form.name.data}" already exists.', 'danger')
            return redirect(url_for('brand.list_brand'))

        # Silinmiş brand'i kontrol et
        deleted_brand = Brand.query.filter_by(
            user_id=current_user.id,
            original_name=form.name.data,
            is_deleted=True
        ).first()
        
        if deleted_brand:
            # Varsa geri getir
            try:
                deleted_brand.restore()
                db.session.flush()  # Değişiklikleri hemen uygula
                db.session.refresh(deleted_brand)  # Brand'i yenile
                db.session.commit()
                flash(f'Brand restored: {deleted_brand.name}#{deleted_brand.id}', 'success')
            except ValueError as e:
                flash(f'Error: {str(e)}', 'danger')
        else:
            # Yoksa yeni ekle
            brand = Brand(user_id=current_user.id, name=form.name.data)
            db.session.add(brand)
            db.session.commit()
            flash(f'Brand added: {brand.name}#{brand.id}', 'success')
        
        db.session.expire_all()  # Tüm objeleri yenile
        return redirect(url_for('brand.list_brand'))
    return render_template('addit_brand.html', title='Add New Brand', form=form)


@bp.route('/brand/<int:id>/delete', methods=['POST'])
@login_required
def delete_brand(id):
    brand = db.first_or_404(sa.select(Brand).where(
        Brand.id == id, 
        Brand.user_id == current_user.id,
        Brand.is_deleted == False  # Sadece silinmemiş brand'leri getir
    ))
    
    try:
        brand.soft_delete()
        db.session.commit()
        flash('Brand deleted. {}#{}'.format(brand.name, brand.id), 'success')
    except ValueError as e:
        flash('Error: Brand is already deleted.', 'danger')
    
    return redirect(url_for('brand.list_brand'))


@bp.route('/brand')
@login_required
def list_brand():
    brands = db.session.scalars(
        sa.select(Brand).where(
            Brand.user_id == current_user.id,
            Brand.is_deleted == False
        )
    )
    return render_template('list_brand.html', title='Brands', brands=brands)


@bp.route('/brand/<int:id>/edit', methods=['GET', 'POST'], endpoint='edit_brand')
@login_required
def edit_brand(id):
    brand = db.first_or_404(sa.select(Brand).where(
        Brand.id == id, 
        Brand.user_id == current_user.id,
        Brand.is_deleted == False
    ))
    form = BrandForm(obj=brand)
    if form.validate_on_submit():
        # Eğer silinmiş aynı isimli brand varsa
        deleted_same_brand = Brand.query.filter_by(
            user_id=current_user.id,
            original_name=form.name.data,
            is_deleted=True
        ).first()
        
        if deleted_same_brand:
            try:
                # Silinmiş brand'i restore et
                deleted_same_brand.restore()
                
                # Transaction'ları güncelle
                transactions = db.session.scalars(
                    sa.select(Transaction).where(Transaction.brand_id == brand.id)
                ).all()
                
                for transaction in transactions:
                    transaction.brand_id = deleted_same_brand.id
                
                # Mevcut brand'i sil
                brand.soft_delete()
                db.session.commit()
                flash(f'Brand restored and transactions transferred: {deleted_same_brand.name}#{deleted_same_brand.id}', 'success')
            except ValueError as e:
                flash(f'Error: {str(e)}', 'danger')
        else:
            # Normal güncelleme
            brand.name = form.name.data
            db.session.commit()
            flash('Brand updated. {}#{}'.format(
                brand.name, brand.id), 'success')
        
        db.session.expire_all()
        return redirect(url_for('brand.list_brand'))
    return render_template('addit_brand.html', title='Edit Brand', form=form)