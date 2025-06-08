from datetime import datetime, timedelta
import random
from models.__init__ import db
from models.category import Category
from models.tag import Tag
from models.transaction import Transaction

def create_default_categories():
    default_categories = {
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
        category = Category(name=main_category)
        db.session.add(category)
        db.session.flush()  # ID'yi almak için flush
        
        # Alt kategorileri oluştur
        for subcategory_name in subcategories:
            subcategory = Category(name=subcategory_name, parent_id=category.id)
            db.session.add(subcategory)
    
    db.session.commit()

def create_dummy_data():
    # Create default categories
    create_default_categories()
    
    # Create sample tags
    sample_tags = [
        'Acil', 'Önemli', 'Düzenli', 'Aylık', 'Yıllık',
        'Tatil', 'İş', 'Kişisel', 'Aile', 'Arkadaşlar'
    ]
    
    for tag_name in sample_tags:
        tag = Tag(name=tag_name)
        db.session.add(tag)
    
    db.session.commit()
    
    # Get all categories and tags
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # Sample transaction descriptions
    descriptions = [
        'Market alışverişi', 'Restoran yemeği', 'Sinema bileti',
        'Kira ödemesi', 'Elektrik faturası', 'Su faturası',
        'İnternet faturası', 'Telefon faturası', 'Maaş',
        'Freelance proje', 'Hediye', 'Tatil', 'Spor salonu üyeliği',
        'Kitap alışverişi', 'Kıyafet alışverişi', 'Toplu taşıma',
        'Taksi', 'Yakıt', 'Sağlık sigortası', 'Doktor randevusu'
    ]
    
    # Create transactions for the last 3 months
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    current_date = start_date
    while current_date <= end_date:
        # Create 1-3 transactions per day
        num_transactions = random.randint(1, 3)
        
        for _ in range(num_transactions):
            # Randomly select transaction type
            transaction_type = random.choice(['income', 'expense'])
            
            # Generate random amount based on type
            if transaction_type == 'income':
                amount = round(random.uniform(1000, 10000), 2)
            else:
                amount = round(random.uniform(50, 2000), 2)
            
            # Randomly select category and tags
            category = random.choice(categories)
            selected_tags = random.sample(tags, k=random.randint(0, 3))
            
            # Create transaction
            transaction = Transaction(
                date=current_date,
                type=transaction_type,
                amount=amount,
                description=random.choice(descriptions),
                category_id=category.id,
                tags=selected_tags
            )
            
            db.session.add(transaction)
        
        current_date += timedelta(days=1)
    
    db.session.commit() 