from app import db
from app.category import bp
from app.category.forms import CategoryForm
from app.models import Category, Transaction
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import sqlalchemy as sa
from datetime import datetime, timezone


@bp.route('/category')
@login_required
def list_category():
    result = db.session.execute(
        sa.select(
            Category,
            sa.func.count(Transaction.id).label('transaction_count')
        )
        .where(
            Category.user_id == current_user.id,
            Category.is_deleted == False
        )
        .join(Category.transactions, isouter=True)
        .group_by(Category.id)
    ).all()
    return render_template('list_category.html', title='Categories', categories=result)


@bp.route('/category/add', methods=['GET', 'POST'], endpoint='add_category')
@login_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        # Aynı isim ve type kontrolü
        existing_category = Category.query.filter_by(
            user_id=current_user.id,
            name=form.name.data,
            type=form.type.data,
            is_deleted=False
        ).first()

        if existing_category:
            flash(f'Category "{form.name.data}" with type "{form.type.data}" already exists.', 'danger')
            return redirect(url_for('category.list_category'))

        # Silinmiş category kontrolü
        deleted_category = Category.query.filter_by(
            user_id=current_user.id,
            original_name=form.name.data,
            type=form.type.data,
            is_deleted=True
        ).first()

        if deleted_category:
            try:
                deleted_category.restore()
                db.session.commit()
                flash(
                    f'Category "{deleted_category.name}" has been restored successfully.',
                    'success'
                )
            except ValueError as e:
                flash(str(e), 'danger')
        else:
            category = Category(
                user_id=current_user.id,
                name=form.name.data,
                type=form.type.data,
                timestamp=datetime.now(timezone.utc)
            )
            db.session.add(category)
            db.session.commit()
            flash(f'Category "{category.name}" has been added successfully.', 'success')

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
        flash(f'Category "{category.name}" has been deleted successfully.', 'info')
    except ValueError as e:
        flash('This category has already been deleted', 'danger')

    return redirect(url_for('category.list_category'))


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
        deleted_same_category = Category.query.filter_by(
            user_id=current_user.id,
            original_name=form.name.data,
            type=form.type.data,
            is_deleted=True
        ).first()

        if deleted_same_category:
            try:
                deleted_same_category.restore()
                transactions = db.session.scalars(
                    sa.select(Transaction).where(
                        Transaction.category_id == category.id)
                ).all()

                for transaction in transactions:
                    transaction.category_id = deleted_same_category.id

                category.soft_delete()
                db.session.commit()
                flash(
                    f'Category "{deleted_same_category.name}" has been restored and transactions transferred',
                    'success'
                )
            except ValueError as e:
                flash(str(e), 'danger')
        else:
            category.name = form.name.data
            category.type = form.type.data
            category.timestamp = datetime.now(timezone.utc)
            db.session.commit()
            flash(f'Category "{category.name}" has been updated successfully.', 'success')

        db.session.expire_all()
        return redirect(url_for('category.list_category'))
    return render_template('addit_category.html', title='Edit Category', form=form)
