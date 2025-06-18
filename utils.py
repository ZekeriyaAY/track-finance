from datetime import datetime, timedelta
import random
from models.__init__ import db
from models.category import Category
from models.tag import Tag
from models.cashflow import CashflowTransaction
from models.investment import InvestmentType, InvestmentTransaction

def create_default_categories():
    """Varsayılan gelir ve gider kategorilerini oluşturur."""
    default_categories = {
        'Gelir': ['Maaş', 'Freelance', 'Yatırım', 'Kira', 'Diğer'],
        'Ulaşım': ['Uçak', 'Toplu Taşıma', 'Taksi', 'Yakıt'],
        'Yemek': ['Restoran', 'Market', 'Kahve'],
        'Alışveriş': ['Giyim', 'Elektronik', 'Ev Eşyaları', 'Kozmetik'],
        'Sağlık': ['Doktor', 'İlaç', 'Spor', 'Sağlık Sigortası'],
        'Eğlence': ['Sinema', 'Tiyatro', 'Konser', 'Hobi'],
        'Konut': ['Kira', 'Faturalar', 'Bakım', 'Mobilya'],
        'İletişim': ['Telefon', 'İnternet', 'TV', 'Abonelikler'],
        'Eğitim': ['Kurs', 'Kitap', 'Sınav'],
        'Seyahat': ['Otel', 'Aktivite'],
        'Diğer': ['Hediye', 'Bağış', 'Vergi', 'Diğer']
    }
    
    for main_category, subcategories in default_categories.items():
        # Ana kategoriyi oluştur
        if not Category.query.filter_by(name=main_category).first():
            category = Category(name=main_category)
            db.session.add(category)
            db.session.flush()  # ID'yi almak için flush
            
            # Alt kategorileri oluştur
            for subcategory_name in subcategories:
                if not Category.query.filter_by(name=subcategory_name).first():
                    subcategory = Category(name=subcategory_name, parent_id=category.id)
                    db.session.add(subcategory)
    
    db.session.commit()

def create_default_investment_types():
    """Varsayılan yatırım türlerini oluşturur."""
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

def create_default_tags():
    """Varsayılan etiketleri oluşturur."""
    default_tags = [
        'Acil Durum',
        'Tasarruf',
        'Yatırım',
        'Borç',
        'Gelir',
        'Gider',
        'Fatura',
        'Kira',
        'Market',
        'Ulaşım',
        'Sağlık',
        'Eğitim',
        'Eğlence',
        'Hediye',
        'Bağış'
    ]

    # Etiketleri oluştur
    for tag_name in default_tags:
        if not Tag.query.filter_by(name=tag_name).first():
            tag = Tag(name=tag_name)
            db.session.add(tag)

    db.session.commit()

def create_dummy_transactions(start_date, end_date):
    """Belirtilen tarih aralığında örnek işlemler oluşturur."""
    # Kategorileri ve etiketleri al
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # Örnek işlem açıklamaları
    descriptions = [
        'Market alışverişi', 'Restoran yemeği', 'Sinema bileti',
        'Kira ödemesi', 'Elektrik faturası', 'Su faturası',
        'İnternet faturası', 'Telefon faturası', 'Maaş',
        'Freelance proje', 'Hediye', 'Tatil', 'Spor salonu üyeliği',
        'Kitap alışverişi', 'Kıyafet alışverişi', 'Toplu taşıma',
        'Taksi', 'Yakıt', 'Sağlık sigortası', 'Doktor randevusu'
    ]
    
    current_date = start_date
    while current_date <= end_date:
        # Her gün 1-3 işlem oluştur
        num_transactions = random.randint(1, 3)
        
        for _ in range(num_transactions):
            # Rastgele işlem tipi seç
            transaction_type = random.choice(['income', 'expense'])
            
            # İşlem tipine göre rastgele tutar oluştur
            if transaction_type == 'income':
                amount = round(random.uniform(1000, 10000), 2)
            else:
                amount = round(random.uniform(50, 2000), 2)
            
            # Rastgele kategori ve etiket seç
            category = random.choice(categories)
            selected_tags = random.sample(tags, k=random.randint(0, 3))
            
            # İşlemi oluştur
            transaction = CashflowTransaction(
                date=current_date,
                type=transaction_type,
                amount=amount,
                description=random.choice(descriptions),
                category_id=category.id,
                tags=selected_tags
            )
            
            db.session.add(transaction)
        
        current_date += timedelta(days=1)

def create_dummy_investments(start_date, end_date):
    """Belirtilen tarih aralığında örnek yatırım işlemleri oluşturur."""
    # Yatırım türlerini al
    investment_types = InvestmentType.query.all()
    
    current_date = start_date
    while current_date <= end_date:
        # Her ayın 1'inde 1-2 yatırım işlemi oluştur
        if current_date.day == 1:
            num_investments = random.randint(1, 2)
            for _ in range(num_investments):
                # Rastgele yatırım türü seç
                investment_type = random.choice(investment_types)
                
                # Yatırım miktarı ve fiyatları oluştur
                quantity = round(random.uniform(1, 10), 2)
                price = round(random.uniform(100, 1000), 2)
                
                # Yatırım işlemini oluştur
                transaction = InvestmentTransaction(
                    investment_type_id=investment_type.id,
                    transaction_date=current_date,
                    transaction_type='buy',
                    price=price,
                    quantity=quantity,
                    description=f'{investment_type.name} alım işlemi'
                )
                
                db.session.add(transaction)
        
        current_date += timedelta(days=1)
    
    db.session.commit()

def create_dummy_data():
    """Örnek veriler oluşturur."""
    # Varsayılan verileri oluştur
    create_default_categories()
    create_default_tags()
    create_default_investment_types()
    
    # Son 3 ay için tarih aralığını belirle
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    # Örnek işlemleri oluştur
    create_dummy_transactions(start_date, end_date)
    create_dummy_investments(start_date, end_date)
    
    db.session.commit() 