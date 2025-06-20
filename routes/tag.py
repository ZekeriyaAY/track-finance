from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.tag import Tag
from flask_babel import _
import logging

logger = logging.getLogger(__name__)

tag_bp = Blueprint('tag', __name__, url_prefix='/tags')

@tag_bp.route('/')
def index():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('tag/index.html', tags=tags)

@tag_bp.route('/add', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        name = request.form['name']
        
        if Tag.query.filter_by(name=name).first():
            flash(_('This tag already exists!'), 'error')
            return redirect(url_for('tag.add_tag'))
        
        try:
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.commit()
            flash(_('Tag added successfully!'), 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding tag: {str(e)}')
            flash(_('An error occurred while adding the tag.'), 'error')
        return redirect(url_for('tag.index'))
    return render_template('tag/form.html')

@tag_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form['name']
        
        existing = Tag.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash(_('This tag already exists!'), 'error')
            return redirect(url_for('tag.edit_tag', id=id))
        
        try:
            tag.name = name
            db.session.commit()
            flash(_('Tag updated successfully!'), 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating tag: {str(e)}')
            flash(_('An error occurred while updating the tag.'), 'error')
        return redirect(url_for('tag.index'))
    return render_template('tag/form.html', tag=tag)

@tag_bp.route('/delete/<int:id>', methods=['POST'])
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    if tag.transactions:
        flash(_('This tag has associated transactions and cannot be deleted.'), 'error')
        return redirect(url_for('tag.index'))

    try:
        db.session.delete(tag)
        db.session.commit()
        flash(_('Tag deleted successfully!'), 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting tag: {str(e)}')
        flash(_('An error occurred while deleting the tag.'), 'error')
    return redirect(url_for('tag.index'))