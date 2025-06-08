from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.__init__ import db
from models.investment_type import InvestmentType
from utils import create_default_categories, create_dummy_data

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def index():
    return render_template('settings/index.html')

@settings_bp.route('/settings/create_default_categories', methods=['POST'])
def create_default_categories_route():
    create_default_categories()
    flash('Varsayılan kategoriler başarıyla oluşturuldu!', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/settings/create_default_investment_types', methods=['POST'])
def create_default_investment_types_route():
    # Varsayılan yatırım türlerini oluştur
    default_types = [
        {'name': 'Hisse Senedi', 'code': 'stock', 'icon': 'fas fa-chart-line', 'color': '#3B82F6'},
        {'name': 'Kripto Para', 'code': 'crypto', 'icon': 'fab fa-bitcoin', 'color': '#F59E0B'},
        {'name': 'Altın', 'code': 'gold', 'icon': 'fas fa-coins', 'color': '#FCD34D'},
        {'name': 'Döviz', 'code': 'forex', 'icon': 'fas fa-dollar-sign', 'color': '#10B981'},
        {'name': 'Emtia', 'code': 'commodity', 'icon': 'fas fa-box', 'color': '#6366F1'},
        {'name': 'Gayrimenkul', 'code': 'real_estate', 'icon': 'fas fa-home', 'color': '#EC4899'},
        {'name': 'Vadeli İşlemler', 'code': 'futures', 'icon': 'fas fa-exchange-alt', 'color': '#8B5CF6'},
        {'name': 'Diğer', 'code': 'other', 'icon': 'fas fa-ellipsis-h', 'color': '#6B7280'}
    ]

    for type_data in default_types:
        if not InvestmentType.query.filter_by(code=type_data['code']).first():
            type = InvestmentType(**type_data)
            db.session.add(type)

    db.session.commit()
    flash('Varsayılan yatırım türleri başarıyla oluşturuldu!', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/settings/create_dummy_data', methods=['POST'])
def create_dummy_data_route():
    create_dummy_data()
    flash('Örnek veriler başarıyla oluşturuldu!', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/settings/reset_database', methods=['POST'])
def reset_database():
    # Tüm tabloları sil
    db.drop_all()
    # Tabloları yeniden oluştur
    db.create_all()
    flash('Veritabanı başarıyla sıfırlandı!', 'success')
    return redirect(url_for('settings.index')) 