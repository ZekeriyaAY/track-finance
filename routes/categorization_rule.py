from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy.orm import joinedload
from models import db
from models.categorization_rule import CategorizationRule
from models.category import Category
from models.tag import Tag
import logging

logger = logging.getLogger(__name__)

categorization_rule_bp = Blueprint('categorization_rule', __name__, url_prefix='/rules')

VALID_OPERATORS = ['contains', 'equals', 'starts_with', 'ends_with']


@categorization_rule_bp.route('/')
def index():
    rules = CategorizationRule.query.order_by(CategorizationRule.priority.asc()).options(
        joinedload(CategorizationRule.tags),
        joinedload(CategorizationRule.category),
    ).all()
    return render_template('categorization_rule/index.html', rules=rules)


@categorization_rule_bp.route('/add', methods=['GET', 'POST'])
def add_rule():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        operator = request.form.get('operator', '')
        value = CategorizationRule.normalize(request.form.get('value', '').strip())
        category_id = request.form.get('category_id')
        type_override = request.form.get('type_override') or None
        is_active = 'is_active' in request.form
        tag_ids = request.form.getlist('tags')

        if not name or not value or not category_id or operator not in VALID_OPERATORS:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('categorization_rule.add_rule'))

        if type_override and type_override not in ('income', 'expense'):
            type_override = None

        try:
            max_priority = db.session.query(db.func.max(CategorizationRule.priority)).scalar()
            new_priority = (max_priority or 0) + 1

            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all() if tag_ids else []

            rule = CategorizationRule(
                name=name,
                priority=new_priority,
                is_active=is_active,
                field='description',
                operator=operator,
                value=value,
                category_id=int(category_id),
                type_override=type_override,
                tags=tags,
            )
            db.session.add(rule)
            db.session.commit()
            flash('Rule added!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error adding rule: {str(e)}')
            flash('Something went wrong. Please try again.', 'error')
        return redirect(url_for('categorization_rule.index'))

    categories = Category.query.all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('categorization_rule/form.html', categories=categories, tags=tags)


@categorization_rule_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_rule(id):
    rule = db.get_or_404(CategorizationRule, id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        operator = request.form.get('operator', '')
        value = CategorizationRule.normalize(request.form.get('value', '').strip())
        category_id = request.form.get('category_id')
        type_override = request.form.get('type_override') or None
        is_active = 'is_active' in request.form
        tag_ids = request.form.getlist('tags')

        if not name or not value or not category_id or operator not in VALID_OPERATORS:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('categorization_rule.edit_rule', id=id))

        if type_override and type_override not in ('income', 'expense'):
            type_override = None

        try:
            rule.name = name
            rule.operator = operator
            rule.value = value
            rule.category_id = int(category_id)
            rule.type_override = type_override
            rule.is_active = is_active
            rule.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all() if tag_ids else []
            db.session.commit()
            flash('Rule updated!', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating rule: {str(e)}')
            flash('Something went wrong. Please try again.', 'error')
        return redirect(url_for('categorization_rule.index'))

    categories = Category.query.all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('categorization_rule/form.html', rule=rule, categories=categories, tags=tags)


@categorization_rule_bp.route('/delete/<int:id>', methods=['POST'])
def delete_rule(id):
    rule = db.get_or_404(CategorizationRule, id)
    try:
        db.session.delete(rule)
        db.session.commit()
        flash('Rule removed.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting rule: {str(e)}')
        flash('Something went wrong. Please try again.', 'error')
    return redirect(url_for('categorization_rule.index'))


@categorization_rule_bp.route('/reorder', methods=['POST'])
def reorder():
    data = request.get_json()
    if not data or 'rule_ids' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    try:
        for index, rule_id in enumerate(data['rule_ids']):
            rule = db.session.get(CategorizationRule, int(rule_id))
            if rule:
                rule.priority = index
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error reordering rules: {str(e)}')
        return jsonify({'error': 'Failed to reorder'}), 500
