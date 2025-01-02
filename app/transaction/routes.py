from app import db
from app.transaction import bp
from app.transaction.forms import TransactionForm
from app.models import Transaction, Category, Brand
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import sqlalchemy as sa
from datetime import datetime, timezone


@bp.route('/transaction')
@login_required
def list_transaction():
    transactions = db.session.scalars(
        sa.select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .join(Transaction.brand)
        .execution_options(fresh_metadata=True)
    ).all()
    db.session.expire_all()
    return render_template('list_transaction.html', title='Transactions', transactions=transactions)


@bp.route('/transaction/add', methods=['GET', 'POST'], endpoint='add_transaction')
@login_required
def add_transaction():
    form = TransactionForm()
    form.category_id.choices = [(c.id, f'{c.name} [{c.type}]') for c in Category.query.filter_by(
        user_id=current_user.id, is_deleted=False).all()]
    form.brand_id.choices = [(b.id, b.name) for b in Brand.query.filter_by(
        user_id=current_user.id, is_deleted=False).all()]

    if form.validate_on_submit():
        transaction = Transaction(
            user_id=current_user.id,
            category_id=form.category_id.data,
            brand_id=form.brand_id.data,
            name=form.name.data,
            amount=form.amount.data,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f'Transaction "{transaction.name}" has been added successfully.', 'success')
        return redirect(url_for('transaction.list_transaction'))
    return render_template('addit_transaction.html', title='Add New Transaction', form=form)


@bp.route('/transaction/<int:id>/delete', methods=['POST'])
@login_required
def delete_transaction(id):
    transaction = db.first_or_404(sa.select(Transaction).where(
        Transaction.id == id, Transaction.user_id == current_user.id))
    db.session.delete(transaction)
    db.session.commit()
    flash(f'Transaction "{transaction.name}" has been deleted successfully.', 'info')
    return redirect(url_for('transaction.list_transaction'))


@bp.route('/transaction/<int:id>/edit', methods=['GET', 'POST'], endpoint='edit_transaction')
@login_required
def edit_transaction(id):
    transaction = db.first_or_404(sa.select(Transaction).where(
        Transaction.id == id,
        Transaction.user_id == current_user.id
    ))
    form = TransactionForm(obj=transaction)

    # Aktif kategorileri al
    active_categories = Category.query.filter_by(
        user_id=current_user.id, is_deleted=False).all()
    current_category = transaction.category

    # Mevcut kategori silinmişse onu da ekle
    category_choices = [(c.id, f'{c.name} [{c.type}]')
                        for c in active_categories]
    if current_category.is_deleted and (current_category.id, f'{current_category.name} [{current_category.type}]') not in category_choices:
        category_choices.append(
            (current_category.id, f'{current_category.name} [{current_category.type}]'))

    form.category_id.choices = category_choices

    # Brand seçenekleri için benzer işlem
    active_brands = Brand.query.filter_by(
        user_id=current_user.id, is_deleted=False).all()
    current_brand = transaction.brand

    brand_choices = [(b.id, b.name) for b in active_brands]
    if current_brand.is_deleted and (current_brand.id, current_brand.name) not in brand_choices:
        brand_choices.append((current_brand.id, current_brand.name))

    form.brand_id.choices = brand_choices

    if form.validate_on_submit():
        transaction.category_id = form.category_id.data
        transaction.brand_id = form.brand_id.data
        transaction.name = form.name.data
        transaction.amount = form.amount.data
        transaction.timestamp = datetime.now(timezone.utc)
        db.session.commit()
        flash(f'Transaction "{transaction.name}" has been updated successfully.', 'success')
        return redirect(url_for('transaction.list_transaction'))
    return render_template('addit_transaction.html', title='Edit Transaction', form=form)
