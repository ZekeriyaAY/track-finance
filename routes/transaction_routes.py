from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from models.__init__ import db
from models.transaction import Transaction
from models.category import Category
from models.tag import Tag

transaction_bp = Blueprint('transaction', __name__, url_prefix='/transactions')

@transaction_bp.route('/')
def index():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('transactions/index.html', transactions=transactions)

@transaction_bp.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        amount = float(request.form['amount'])
        type = request.form['type']
        category_id = int(request.form['category_id'])
        description = request.form['description']
        tag_ids = request.form.getlist('tags')

        transaction = Transaction(
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
        return redirect(url_for('transaction.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('transactions/form.html', categories=categories, tags=tags, today=today)

@transaction_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
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
        return redirect(url_for('transaction.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    return render_template('transactions/form.html', transaction=transaction, categories=categories, tags=tags)

@transaction_bp.route('/delete/<int:id>', methods=['POST'])
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem başarıyla silindi!', 'success')
    return redirect(url_for('transaction.index')) 