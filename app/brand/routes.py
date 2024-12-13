from app import db
from app.brand import bp
from app.brand.forms import BrandForm
from app.models import Brand
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import sqlalchemy as sa


@bp.route('/brand/add', methods=['GET', 'POST'], endpoint='add_brand')
@login_required
def add_brand():
    form = BrandForm()
    if form.validate_on_submit():
        brand = Brand(user_id=current_user.id, name=form.name.data)
        db.session.add(brand)
        db.session.commit()
        flash('Brand added. {}#{}'.format(brand.name, brand.id))
        return redirect(url_for('brand.list_brand'))
    return render_template('addit_brand.html', title='Add New Brand' , form=form)


@bp.route('/brand/<int:id>/delete', methods=['POST'])
@login_required
def delete_brand(id):
    brand = db.first_or_404(sa.select(Brand).where(
        Brand.id == id, Brand.user_id == current_user.id))
    db.session.delete(brand)
    db.session.commit()
    flash('Brand deleted. {}#{}'.format(brand.name, brand.id))
    return redirect(url_for('brand.list_brand'))


@bp.route('/brand')
@login_required
def list_brand():
    brands = db.session.scalars(
        sa.select(Brand).where(Brand.user_id == current_user.id))
    return render_template('list_brand.html', title='Brands', brands=brands)


@bp.route('/brand/<int:id>/edit', methods=['GET', 'POST'], endpoint='edit_brand')
@login_required
def edit_brand(id):
    brand = db.first_or_404(sa.select(Brand).where(
        Brand.id == id, Brand.user_id == current_user.id))
    form = BrandForm(obj=brand)
    if form.validate_on_submit():
        brand.name = form.name.data
        db.session.commit()
        flash('Brand updated. {}#{}'.format(brand.name, brand.id))
        return redirect(url_for('brand.list_brand'))
    return render_template('addit_brand.html', title='Edit Brand', form=form)