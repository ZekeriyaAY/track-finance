from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from datetime import datetime, date

from models.__init__ import db
from models.category import Category
from models.tag import Tag
from models.transaction import Transaction, transaction_tags

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

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
    
    # Create sample transactions
    from datetime import datetime, timedelta
    import random
    
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

@app.route('/')
def index():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('transactions/index.html', transactions=transactions)

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        transaction_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        type = request.form['type']
        category_id = request.form['category_id']
        amount = float(request.form['amount'])
        description = request.form['description']
        
        transaction = Transaction(
            date=transaction_date,
            type=type,
            category_id=category_id,
            amount=amount,
            description=description
        )
        
        # Tag'leri ekle
        tag_ids = request.form.getlist('tags')
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            transaction.tags = tags
        
        db.session.add(transaction)
        db.session.commit()
        flash('İşlem başarıyla eklendi!', 'success')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    tags = Tag.query.all()
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('transactions/add.html', categories=categories, tags=tags, today=today)

@app.route('/edit_transaction/<int:id>', methods=['GET', 'POST'])
def edit_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    if request.method == 'POST':
        transaction.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        transaction.type = request.form['type']
        transaction.amount = float(request.form['amount'])
        transaction.description = request.form['description']
        transaction.category_id = request.form['category_id']

        # Tag'leri güncelle
        tag_ids = request.form.getlist('tags')
        if tag_ids:
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            transaction.tags = tags
        else:
            transaction.tags = []

        db.session.commit()
        flash('İşlem başarıyla güncellendi!', 'success')
        return redirect(url_for('index'))

    # Ana kategorileri ve alt kategorilerini getir
    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('transactions/edit.html', transaction=transaction, categories=categories, tags=tags)

@app.route('/delete_transaction/<int:id>')
def delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    flash('İşlem başarıyla silindi!', 'success')
    return redirect(url_for('index'))

@app.route('/categories')
def categories():
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/index.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        parent_id = request.form.get('parent_id')
        
        if parent_id == '':
            parent_id = None
        else:
            parent_id = int(parent_id)
            
        category = Category(name=name, parent_id=parent_id)
        db.session.add(category)
        db.session.commit()
        flash('Kategori başarıyla eklendi!', 'success')
        return redirect(url_for('categories'))
    
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/add.html', categories=categories)

@app.route('/edit_category/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form['name']
        parent_id = request.form.get('parent_id')
        
        if parent_id == '':
            parent_id = None
        else:
            parent_id = int(parent_id)
            
        # Eğer kategori kendisini üst kategori olarak seçmeye çalışıyorsa engelle
        if parent_id == category.id:
            flash('Bir kategori kendisini üst kategori olarak seçemez!', 'error')
            return redirect(url_for('edit_category', id=id))
            
        # Eğer seçilen üst kategori bir alt kategori ise engelle
        if parent_id:
            parent = Category.query.get(parent_id)
            if parent and parent.is_subcategory():
                flash('Alt kategoriler üst kategori olamaz!', 'error')
                return redirect(url_for('edit_category', id=id))
            
        category.parent_id = parent_id
        db.session.commit()
        flash('Kategori başarıyla güncellendi!', 'success')
        return redirect(url_for('categories'))
    
    # Ana kategorileri getir (alt kategoriler hariç)
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('categories/edit.html', category=category, categories=categories)

@app.route('/delete_category/<int:id>')
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    if category.transactions:
        flash('Bu kategoriye ait işlemler olduğu için silinemez!', 'error')
        return redirect(url_for('categories'))

    if category.subcategories:
        flash('Bu kategoriye ait alt kategoriler olduğu için silinemez!', 'error')
        return redirect(url_for('categories'))

    db.session.delete(category)
    db.session.commit()
    flash('Kategori başarıyla silindi!', 'success')
    return redirect(url_for('categories'))

@app.route('/tags')
def tags():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('tags/index.html', tags=tags)

@app.route('/add_tag', methods=['GET', 'POST'])
def add_tag():
    if request.method == 'POST':
        name = request.form['name']
        
        if Tag.query.filter_by(name=name).first():
            flash('Bu tag zaten mevcut!', 'error')
            return redirect(url_for('add_tag'))
            
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        flash('Tag başarıyla eklendi!', 'success')
        return redirect(url_for('tags'))
    
    return render_template('tags/add.html')

@app.route('/edit_tag/<int:id>', methods=['GET', 'POST'])
def edit_tag(id):
    tag = Tag.query.get_or_404(id)
    if request.method == 'POST':
        name = request.form['name']
        
        existing = Tag.query.filter_by(name=name).first()
        if existing and existing.id != id:
            flash('Bu tag zaten mevcut!', 'error')
            return redirect(url_for('edit_tag', id=id))
            
        tag.name = name
        db.session.commit()
        flash('Tag başarıyla güncellendi!', 'success')
        return redirect(url_for('tags'))
    
    return render_template('tags/edit.html', tag=tag)

@app.route('/delete_tag/<int:id>')
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    
    if tag.transactions:
        flash('Bu taga ait işlemler olduğu için silinemez!', 'error')
        return redirect(url_for('tags'))

    db.session.delete(tag)
    db.session.commit()
    flash('Tag başarıyla silindi!', 'success')
    return redirect(url_for('tags'))

@app.route('/settings')
def settings():
    return render_template('settings/index.html')

@app.route('/settings/create_default_categories', methods=['POST'])
def create_default_categories_route():
    if not Category.query.first():
        create_default_categories()
        flash('Varsayılan kategoriler başarıyla oluşturuldu!', 'success')
    else:
        flash('Kategoriler zaten mevcut! Tüm kategorilerin silinmesi gerekiyor.', 'error')
    return redirect(url_for('settings'))

@app.route('/settings/create_dummy_data', methods=['POST'])
def create_dummy_data_route():
    if not Category.query.first():
        create_dummy_data()
        flash('Örnek veriler başarıyla oluşturuldu!', 'success')
    else:
        flash('Veritabanı boş değil! Örnek veriler oluşturulamadı.', 'error')
    return redirect(url_for('settings'))

@app.route('/settings/reset_database', methods=['POST'])
def reset_database():
    # Tüm tabloları sil
    db.drop_all()
    # Tabloları yeniden oluştur
    db.create_all()
    flash('Veritabanı başarıyla sıfırlandı!', 'success')
    return redirect(url_for('settings'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 