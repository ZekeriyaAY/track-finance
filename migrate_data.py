from app import create_app, db
from app.models import User, Category, Brand, Transaction
import sqlite3
from datetime import datetime, timezone

def transfer_data():
    # Backup veritabanına bağlan
    backup_conn = sqlite3.connect('app.db.backup')
    backup_cur = backup_conn.cursor()

    app = create_app()
    with app.app_context():
        # Kullanıcıları aktar
        backup_cur.execute('SELECT * FROM "user"')
        users = backup_cur.fetchall()
        for user_data in users:
            user = User(
                id=user_data[0],
                username=user_data[1],
                email=user_data[2],
                password_hash=user_data[3],
                created_at=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                preferences={}
            )
            db.session.add(user)
        
        # Kategorileri aktar
        backup_cur.execute('SELECT * FROM "category"')
        categories = backup_cur.fetchall()
        for cat_data in categories:
            category = Category(
                id=cat_data[0],
                user_id=cat_data[1],
                name=cat_data[2],
                type=cat_data[3],
                is_deleted=cat_data[4],
                deleted_at=datetime.fromisoformat(cat_data[5]) if cat_data[5] else None,
                original_name=cat_data[6],
                timestamp=datetime.fromisoformat(cat_data[7]) if cat_data[7] else datetime.now(timezone.utc)
            )
            db.session.add(category)
        
        # Brandleri aktar
        backup_cur.execute('SELECT * FROM "brand"')
        brands = backup_cur.fetchall()
        for brand_data in brands:
            brand = Brand(
                id=brand_data[0],
                user_id=brand_data[1],
                name=brand_data[2],
                is_deleted=brand_data[3],
                deleted_at=datetime.fromisoformat(brand_data[4]) if brand_data[4] else None,
                original_name=brand_data[5],
                timestamp=datetime.fromisoformat(brand_data[6]) if brand_data[6] else datetime.now(timezone.utc)
            )
            db.session.add(brand)
        
        # Transactionları aktar
        backup_cur.execute('SELECT * FROM "transaction"')
        transactions = backup_cur.fetchall()
        for trans_data in transactions:
            transaction = Transaction(
                id=trans_data[0],
                user_id=trans_data[1],
                category_id=trans_data[2],
                brand_id=trans_data[3],
                name=trans_data[4],
                amount=trans_data[5],
                timestamp=datetime.fromisoformat(trans_data[6]) if trans_data[6] else datetime.now(timezone.utc)
            )
            db.session.add(transaction)
        
        try:
            db.session.commit()
            print("Veri aktarımı başarılı!")
        except Exception as e:
            db.session.rollback()
            print(f"Hata oluştu: {str(e)}")
        finally:
            backup_conn.close()

if __name__ == '__main__':
    transfer_data() 