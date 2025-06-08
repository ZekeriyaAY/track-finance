from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.tag import Tag

tag_bp = Blueprint('tag', __name__)

@tag_bp.route('/tags')
def index():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('tags/index.html', tags=tags)

@tag_bp.route('/add_tag', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        name = request.form['name']
        
        if Tag.query.filter_by(name=name).first():
            flash('Bu tag zaten mevcut!', 'error')
            return redirect(url_for('tag.add_tag'))
        
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        flash('Tag başarıyla eklendi!', 'success')
        return redirect(url_for('tag.index'))
    
    return render_template('tags/form.html')

@tag_bp.route('/edit_tag/<int:id>', methods=['GET', 'POST'])
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    
    if request.method == 'POST':
        name = request.form['name']
        
        existing = Tag.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash('Bu tag zaten mevcut!', 'error')
            return redirect(url_for('tag.edit_tag', id=id))
        
        tag.name = name
        db.session.commit()
        flash('Tag başarıyla güncellendi!', 'success')
        return redirect(url_for('tag.index'))
    
    return render_template('tags/form.html', tag=tag)

@tag_bp.route('/delete_tag/<int:id>')
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    
    # Check if tag has transactions
    if tag.transactions:
        flash('Bu tage ait işlemler var. Önce işlemleri silmelisiniz!', 'error')
        return redirect(url_for('tag.index'))
    
    db.session.delete(tag)
    db.session.commit()
    flash('Tag başarıyla silindi!', 'success')
    return redirect(url_for('tag.index')) 