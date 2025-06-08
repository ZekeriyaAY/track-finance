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
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        flash('Etiket başarıyla eklendi!', 'success')
        return redirect(url_for('tag.index'))
    
    return render_template('tags/add.html')

@tag_bp.route('/edit_tag/<int:id>', methods=['GET', 'POST'])
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    if request.method == 'POST':
        tag.name = request.form['name']
        db.session.commit()
        flash('Etiket başarıyla güncellendi!', 'success')
        return redirect(url_for('tag.index'))
    
    return render_template('tags/edit.html', tag=tag)

@tag_bp.route('/delete_tag/<int:id>')
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    flash('Etiket başarıyla silindi!', 'success')
    return redirect(url_for('tag.index')) 