from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from models.__init__ import db
from models.cashflow import CashflowTransaction
from models.category import Category
from models.tag import Tag

cashflow_bp = Blueprint('cashflow', __name__, url_prefix='/cashflow')

@cashflow_bp.route('/')
def index():
    transactions = CashflowTransaction.query.order_by(CashflowTransaction.date.desc()).all()
    return render_template('cashflow/index.html', transactions=transactions)

@cashflow_bp.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        amount = float(request.form['amount'])
        type = request.form['type']
        category_id = int(request.form['category_id'])
        description = request.form['description']
        tag_ids = request.form.getlist('tags')

        transaction = CashflowTransaction(
            date=date,
            amount=amount,
            type=type,
            category_id=category_id,
            description=description
        )

        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            transaction.tags = tags

        db.session.add(transaction)
        db.session.commit()
        flash('İşlem başarıyla eklendi!', 'success')
        return redirect(url_for('cashflow.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('cashflow/form.html', categories=categories, tags=tags, today=today)

@cashflow_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = CashflowTransaction.query.get_or_404(id)
    if request.method == 'POST':
        transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        transaction.amount = float(request.form['amount'])
        transaction.type = request.form['type']
        transaction.category_id = int(request.form['category_id'])
        transaction.description = request.form['description']
        
        # Update tags
        tag_ids = request.form.getlist('tags')
        transaction.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all() if tag_ids else []

        db.session.commit()
        flash('İşlem başarıyla güncellendi!', 'success')
        return redirect(url_for('cashflow.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    return render_template('cashflow/form.html', transaction=transaction, categories=categories, tags=tags)

@cashflow_bp.route('/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    transaction = CashflowTransaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem başarıyla silindi!', 'success')
    return redirect(url_for('cashflow.index')) 