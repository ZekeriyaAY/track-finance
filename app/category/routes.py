from app import db
from app.category import bp
from app.category.forms import CategoryForm
from app.models import Category
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import sqlalchemy as sa


@bp.route('/category/add', methods=['GET', 'POST'], endpoint='add_category')
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(user_id=current_user.id, name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added. {}#{}'.format(category.name, category.id))
        return redirect(url_for('category.add_category'))
    return render_template('addit_category.html', form=form)


@bp.route('/category/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    category = db.first_or_404(sa.select(Category).where(
        Category.id == id, Category.user_id == current_user.id))
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted. {}#{}'.format(category.name, category.id))
    return redirect(url_for('category.list_category'))


@bp.route('/category')
@login_required
def list_category():
    categories = db.session.scalars(
        sa.select(Category).where(Category.user_id == current_user.id))
    return render_template('list_category.html', categories=categories)


@bp.route('/category/<int:id>/edit', methods=['GET', 'POST'], endpoint='edit_category')
@login_required
def edit_category(id):
    category = db.first_or_404(sa.select(Category).where(
        Category.id == id, Category.user_id == current_user.id))
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated. {}#{}'.format(category.name, category.id))
        return redirect(url_for('category.list_category'))
    return render_template('addit_category.html', form=form)
