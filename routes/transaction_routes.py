from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from models.__init__ import db
from models.transaction import Transaction
from models.category import Category
from models.tag import Tag

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/')
def index():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('transactions/index.html', transactions=transactions)

@transaction_bp.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        transaction_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        type = request.form['type']
        category_id = request.form['category_id']
        amount = float(request.form['amount'])
        description = request.form['description']
        
        transaction = Transaction(
            date=transaction_date,
            type=type,
            category_id=category_id,
            amount=amount,
            description=description
        )
        
        # Tag'leri ekle
        tag_ids = request.form.getlist('tags')
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            transaction.tags = tags
        
        db.session.add(transaction)
        db.session.commit()
        flash('İşlem başarıyla eklendi!', 'success')
        return redirect(url_for('transaction.index'))
    
    categories = Category.query.all()
    tags = Tag.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('transactions/add.html', categories=categories, tags=tags, today=today)

@transaction_bp.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    if request.method == 'POST':
        transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        transaction.type = request.form['type']
        transaction.amount = float(request.form['amount'])
        transaction.description = request.form['description']
        transaction.category_id = request.form['category_id']

        # Tag'leri güncelle
        tag_ids = request.form.getlist('tags')
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            transaction.tags = tags
        else:
            transaction.tags = []

        db.session.commit()
        flash('İşlem başarıyla güncellendi!', 'success')
        return redirect(url_for('transaction.index'))

    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('transactions/edit.html', transaction=transaction, categories=categories, tags=tags)

@transaction_bp.route('/delete_transaction/<int:id>')
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem başarıyla silindi!', 'success')
    return redirect(url_for('transaction.index')) 