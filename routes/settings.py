from flask import Blueprint, render_template, redirect, url_for, flash
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
        flash('Örnek veriler başarıyla oluşturuldu.', 'success')
        logger.info("Örnek veriler başarıyla oluşturuldu.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Örnek veriler oluşturulurken bir hata oluştu: {str(e)}")
        flash('Örnek veriler oluşturulurken bir hata oluştu.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-categories', methods=['POST'])
def create_default_categories_route():
    try:
        create_default_categories()
        flash('Varsayılan kategoriler başarıyla oluşturuldu.', 'success')
        logger.info("Varsayılan kategoriler başarıyla oluşturuldu.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Varsayılan kategoriler oluşturulurken bir hata oluştu: {str(e)}")
        flash('Varsayılan kategoriler oluşturulurken bir hata oluştu.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-tags', methods=['POST'])
def create_default_tags_route():
    try:
        create_default_tags()
        flash('Varsayılan etiketler başarıyla oluşturuldu.', 'success')
        logger.info("Varsayılan etiketler başarıyla oluşturuldu.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Varsayılan etiketler oluşturulurken bir hata oluştu: {str(e)}")
        flash('Varsayılan etiketler oluşturulurken bir hata oluştu.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/create-default-investment-types', methods=['POST'])
def create_default_investment_types_route():
    try:
        create_default_investment_types()
        flash('Varsayılan yatırım türleri başarıyla oluşturuldu.', 'success')
        logger.info("Varsayılan yatırım türleri başarıyla oluşturuldu.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Varsayılan yatırım türleri oluşturulurken bir hata oluştu: {str(e)}")
        flash('Varsayılan yatırım türleri oluşturulurken bir hata oluştu.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/reset-database', methods=['POST'])
def reset_database():
    try:
        db.drop_all()
        db.create_all()
        flash('Veritabanı başarıyla sıfırlandı.', 'success')
        logger.info("Veritabanı başarıyla sıfırlandı.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Veritabanı sıfırlanırken bir hata oluştu: {str(e)}")
        flash('Veritabanı sıfırlanırken bir hata oluştu.', 'error')
    return redirect(url_for('settings.index')) 