from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func, exists
from models import db
from models.tag import Tag
from models.cashflow import CashflowTransaction, cashflow_transaction_tags
import logging

logger = logging.getLogger(__name__)

tag_bp = Blueprint('tag', __name__, url_prefix='/tags')

@tag_bp.route('/')
def index():
    tags = Tag.query.order_by(Tag.name).all()

    # Single aggregation query for all tag counts (replaces N+1 model methods)
    raw_counts = db.session.query(
        cashflow_transaction_tags.c.tag_id,
        CashflowTransaction.type,
        func.count(CashflowTransaction.id)
    ).join(
        CashflowTransaction,
        cashflow_transaction_tags.c.cashflow_transaction_id == CashflowTransaction.id
    ).group_by(cashflow_transaction_tags.c.tag_id, CashflowTransaction.type).all()

    tag_counts = {}
    for tag_id, txn_type, count in raw_counts:
        if tag_id not in tag_counts:
            tag_counts[tag_id] = {'income': 0, 'expense': 0}
        tag_counts[tag_id][txn_type] = count

    return render_template('tag/index.html', tags=tags, tag_counts=tag_counts)

@tag_bp.route('/add', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        name = request.form['name']
        
        if Tag.query.filter_by(name=name).first():
            flash('A tag with that name already exists.', 'error')
            return redirect(url_for('tag.add_tag'))
        
        try:
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.commit()
            flash('Tag added!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding tag: {str(e)}')
            flash('Something went wrong. Please try again.', 'error')
        return redirect(url_for('tag.index'))
    return render_template('tag/form.html')

@tag_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_tag(id):
    tag = db.get_or_404(Tag, id)
    if request.method == 'POST':
        name = request.form['name']

        existing = Tag.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash('A tag with that name already exists.', 'error')
            return redirect(url_for('tag.edit_tag', id=id))
        
        try:
            tag.name = name
            db.session.commit()
            flash('Tag updated!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating tag: {str(e)}')
            flash('Something went wrong. Please try again.', 'error')
        return redirect(url_for('tag.index'))
    return render_template('tag/form.html', tag=tag)

@tag_bp.route('/delete/<int:id>', methods=['POST'])
def delete_tag(id):
    tag = db.get_or_404(Tag, id)
    if db.session.query(exists().where(cashflow_transaction_tags.c.tag_id == id)).scalar():
        flash("Can't delete — this tag has linked transactions.", 'error')
        return redirect(url_for('tag.index'))

    try:
        db.session.delete(tag)
        db.session.commit()
        flash('Tag removed.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting tag: {str(e)}')
        flash('Something went wrong. Please try again.', 'error')
    return redirect(url_for('tag.index'))