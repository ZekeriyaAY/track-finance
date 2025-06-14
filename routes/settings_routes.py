from flask import Blueprint, render_template, redirect, url_for, flash
from models.__init__ import db
from utils import create_dummy_data
import logging

# Loglama ayarları
logger = logging.getLogger(__name__)

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

@settings_bp.route('/')
def index():
    return render_template('settings/index.html')

@settings_bp.route('/create-dummy-data', methods=['POST'])
def create_dummy_data_route():
    """Örnek verileri oluşturur."""
    try:
        create_dummy_data()
        flash('Örnek veriler başarıyla oluşturuldu.', 'success')
        logger.info("Örnek veriler başarıyla oluşturuldu.")
    except Exception as e:
        logger.error(f"Örnek veriler oluşturulurken bir hata oluştu: {str(e)}")
        flash('Örnek veriler oluşturulurken bir hata oluştu.', 'error')
    return redirect(url_for('settings.index'))

@settings_bp.route('/reset-database', methods=['POST'])
def reset_database():
    """Veritabanını sıfırlar."""
    try:
        # Tüm tabloları temizle
        db.drop_all()
        # Tabloları yeniden oluştur
        db.create_all()
        flash('Veritabanı başarıyla sıfırlandı.', 'success')
        logger.info("Veritabanı başarıyla sıfırlandı.")
    except Exception as e:
        logger.error(f"Veritabanı sıfırlanırken bir hata oluştu: {str(e)}")
        flash('Veritabanı sıfırlanırken bir hata oluştu.', 'error')
    return redirect(url_for('settings.index')) 