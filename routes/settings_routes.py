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
    # Ana yatırım türleri
    main_types = [
        {
            'name': 'Menkul Kıymetler',
            'code': 'securities',
            'icon': 'fas fa-chart-line',
            'color': '#3B82F6',
            'children': [
                {'name': 'Hisse Senedi', 'code': 'stock', 'icon': 'fas fa-chart-line', 'color': '#3B82F6'},
                {'name': 'Tahvil/Bono', 'code': 'bond', 'icon': 'fas fa-file-invoice-dollar', 'color': '#10B981'},
                {'name': 'Vadeli İşlemler', 'code': 'futures', 'icon': 'fas fa-exchange-alt', 'color': '#8B5CF6'},
                {'name': 'Yatırım Fonu', 'code': 'fund', 'icon': 'fas fa-piggy-bank', 'color': '#EC4899'}
            ]
        },
        {
            'name': 'Kripto Varlıklar',
            'code': 'crypto_assets',
            'icon': 'fab fa-bitcoin',
            'color': '#F59E0B',
            'children': [
                {'name': 'Bitcoin', 'code': 'btc', 'icon': 'fab fa-bitcoin', 'color': '#F59E0B'},
                {'name': 'Ethereum', 'code': 'eth', 'icon': 'fab fa-ethereum', 'color': '#6366F1'},
                {'name': 'Diğer Altcoinler', 'code': 'altcoins', 'icon': 'fas fa-coins', 'color': '#8B5CF6'}
            ]
        },
        {
            'name': 'Değerli Metaller',
            'code': 'precious_metals',
            'icon': 'fas fa-coins',
            'color': '#FCD34D',
            'children': [
                {'name': 'Altın', 'code': 'gold', 'icon': 'fas fa-coins', 'color': '#FCD34D'},
                {'name': 'Gümüş', 'code': 'silver', 'icon': 'fas fa-coins', 'color': '#9CA3AF'},
                {'name': 'Platin', 'code': 'platinum', 'icon': 'fas fa-coins', 'color': '#6B7280'}
            ]
        },
        {
            'name': 'Döviz',
            'code': 'forex',
            'icon': 'fas fa-dollar-sign',
            'color': '#10B981',
            'children': [
                {'name': 'USD', 'code': 'usd', 'icon': 'fas fa-dollar-sign', 'color': '#10B981'},
                {'name': 'EUR', 'code': 'eur', 'icon': 'fas fa-euro-sign', 'color': '#3B82F6'},
                {'name': 'GBP', 'code': 'gbp', 'icon': 'fas fa-pound-sign', 'color': '#8B5CF6'},
                {'name': 'Diğer Dövizler', 'code': 'other_forex', 'icon': 'fas fa-money-bill-wave', 'color': '#6366F1'}
            ]
        },
        {
            'name': 'Gayrimenkul',
            'code': 'real_estate',
            'icon': 'fas fa-home',
            'color': '#EC4899',
            'children': [
                {'name': 'Konut', 'code': 'residential', 'icon': 'fas fa-home', 'color': '#EC4899'},
                {'name': 'Ticari', 'code': 'commercial', 'icon': 'fas fa-store', 'color': '#8B5CF6'},
                {'name': 'Arsa', 'code': 'land', 'icon': 'fas fa-mountain', 'color': '#10B981'}
            ]
        },
        {
            'name': 'Emtia',
            'code': 'commodity',
            'icon': 'fas fa-box',
            'color': '#6366F1',
            'children': [
                {'name': 'Enerji', 'code': 'energy', 'icon': 'fas fa-bolt', 'color': '#F59E0B'},
                {'name': 'Tarım', 'code': 'agriculture', 'icon': 'fas fa-seedling', 'color': '#10B981'},
                {'name': 'Endüstriyel', 'code': 'industrial', 'icon': 'fas fa-industry', 'color': '#6B7280'}
            ]
        },
        {
            'name': 'Diğer',
            'code': 'other',
            'icon': 'fas fa-ellipsis-h',
            'color': '#6B7280',
            'children': [
                {'name': 'NFT', 'code': 'nft', 'icon': 'fas fa-image', 'color': '#8B5CF6'},
                {'name': 'Koleksiyon', 'code': 'collectibles', 'icon': 'fas fa-gem', 'color': '#EC4899'},
                {'name': 'Diğer', 'code': 'misc', 'icon': 'fas fa-ellipsis-h', 'color': '#6B7280'}
            ]
        }
    ]

    # Ana türleri ve alt türleri oluştur
    for main_type in main_types:
        children = main_type.pop('children', [])
        
        # Ana türü oluştur
        if not InvestmentType.query.filter_by(code=main_type['code']).first():
            parent_type = InvestmentType(**main_type)
            db.session.add(parent_type)
            db.session.flush()  # ID'yi almak için flush yapıyoruz
            
            # Alt türleri oluştur
            for child in children:
                if not InvestmentType.query.filter_by(code=child['code']).first():
                    child_type = InvestmentType(**child, parent_id=parent_type.id)
                    db.session.add(child_type)

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