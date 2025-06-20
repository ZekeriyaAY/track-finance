from flask import Blueprint, render_template, redirect, url_for, flash
from flask_babel import _
from models.__init__ import db
from utils import create_dummy_data, create_default_categories, create_default_tags, create_default_investment_types
import logging

logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
def index():
    return render_template('settings/index.html')

@settings_bp.route('/create-dummy-data', methods=['POST'])
def create_dummy_data_route():
    try:
        create_dummy_data()
        flash(_('Dummy data created successfully.'), 'success')
        logger.info("Dummy data created successfully.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating dummy data: {str(e)}")
        flash(_('An error occurred while creating dummy data.'), 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-categories', methods=['POST'])
def create_default_categories_route():
    try:
        create_default_categories()
        flash(_('Default categories created successfully.'), 'success')
        logger.info("Default categories created successfully.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default categories: {str(e)}")
        flash(_('An error occurred while creating default categories.'), 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-tags', methods=['POST'])
def create_default_tags_route():
    try:
        create_default_tags()
        flash(_('Default tags created successfully.'), 'success')
        logger.info("Default tags created successfully.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default tags: {str(e)}")
        flash(_('An error occurred while creating default tags.'), 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-investment-types', methods=['POST'])
def create_default_investment_types_route():
    try:
        create_default_investment_types()
        flash(_('Default investment types created successfully.'), 'success')
        logger.info("Default investment types created successfully.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while creating default investment types: {str(e)}")
        flash(_('An error occurred while creating default investment types.'), 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/reset-database', methods=['POST'])
def reset_database():
    try:
        db.drop_all()
        db.create_all()
        flash(_('Database reset successfully.'), 'success')
        logger.info("Database reset successfully.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"An error occurred while resetting the database: {str(e)}")
        flash(_('An error occurred while resetting the database.'), 'error')
    return redirect(url_for('settings.index')) 