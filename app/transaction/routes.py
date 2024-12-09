from app import db
from app.transaction import bp
from app.transaction.forms import TransactionForm
from app.models import Transaction, Category, Brand
from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
import sqlalchemy as sa
from datetime import datetime, timezone


@bp.route('/transaction/add', methods=['GET', 'POST'], endpoint='add_transaction')
@login_required
def add_transaction():
    form = TransactionForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.filter_by(
        user_id=current_user.id).all()]
    form.brand.choices = [(b.id, b.name) for b in Brand.query.filter_by(
        user_id=current_user.id).all()]
    if form.validate_on_submit():
        transaction = Transaction(user_id=current_user.id, category_id=form.category.data, brand_id=form.brand.data,
                                  name=form.name.data, amount=form.amount.data, timestamp=datetime.now(timezone.utc))
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added. {}#{}'.format(
            transaction.name, transaction.id))
        return redirect(url_for('transaction.add_transaction'))
    return render_template('addit_transaction.html', title='Add New Transaction', form=form)


@bp.route('/transaction/<int:id>/delete', methods=['POST'])
@login_required
def delete_transaction(id):
    transaction = db.first_or_404(sa.select(Transaction).where(
        Transaction.id == id, Transaction.user_id == current_user.id))
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted. {}#{}'.format(
        transaction.name, transaction.id))
    return redirect(url_for('transaction.list_transaction'))


@bp.route('/transaction')
@login_required
def list_transaction():
    transactions = db.session.scalars(
        sa.select(Transaction).where(Transaction.user_id == current_user.id))
    return render_template('list_transaction.html', title='Transactions', transactions=transactions)


@bp.route('/transaction/<int:id>/edit', methods=['GET', 'POST'], endpoint='edit_transaction')
@login_required
def edit_transaction(id):
    transaction = db.first_or_404(sa.select(Transaction).where(
        Transaction.id == id, Transaction.user_id == current_user.id))
    form = TransactionForm(obj=transaction)
    form.category.choices = [(c.id, c.name) for c in Category.query.filter_by(
        user_id=current_user.id).all()]
    form.brand.choices = [(b.id, b.name) for b in Brand.query.filter_by(
        user_id=current_user.id).all()]
    if form.validate_on_submit():
        transaction.category_id = form.category.data
        transaction.brand_id = form.brand.data
        transaction.name = form.name.data
        transaction.amount = form.amount.data
        db.session.commit()
        flash('Transaction updated. {}#{}'.format(
            transaction.name, transaction.id))
        return redirect(url_for('transaction.list_transaction'))
    return render_template('addit_transaction.html', title='Edit Transaction', form=form)
