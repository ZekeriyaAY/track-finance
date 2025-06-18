from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.tag import Tag
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
            flash('Bu tag zaten mevcut!', 'error')
            return redirect(url_for('tag.add_tag'))
        
        try:
            tag = Tag(name=name)
            db.session.add(tag)
            db.session.commit()
            flash('Tag başarıyla eklendi!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Tag eklenirken bir hata oluştu: {str(e)}')
            flash('Tag eklenirken bir hata oluştu.', 'error')
        return redirect(url_for('tag.index'))
    return render_template('tag/form.html')

@tag_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form['name']
        
        existing = Tag.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash('Bu tag zaten mevcut!', 'error')
            return redirect(url_for('tag.edit_tag', id=id))
        
        try:
            tag.name = name
            db.session.commit()
            flash('Tag başarıyla güncellendi!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Tag güncellenirken bir hata oluştu: {str(e)}')
            flash('Tag güncellenirken bir hata oluştu.', 'error')
        return redirect(url_for('tag.index'))
    return render_template('tag/form.html', tag=tag)

@tag_bp.route('/delete/<int:id>', methods=['POST'])
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    if tag.transactions:
        flash('Bu tage ait işlemler var. Önce işlemleri silmelisiniz!', 'error')
        return redirect(url_for('tag.index'))

    try:
        db.session.delete(tag)
        db.session.commit()
        flash('Tag başarıyla silindi!', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Tag silinirken bir hata oluştu: {str(e)}')
        flash('Tag silinirken bir hata oluştu.', 'error')
    return redirect(url_for('tag.index'))