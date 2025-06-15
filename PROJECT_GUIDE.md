# Track Finance - Proje Tanıtımı ve Kullanım Kılavuzu

## Proje Hakkında
Track Finance, kişisel finans takibi yapmanızı sağlayan bir web uygulamasıdır. Temel özellikleri:

- Yatırım portföyü yönetimi
- Günlük gelir/gider takibi
- Bütçe planlama ve takibi
- Otomatik fiyat güncellemeleri (cron job)

## Teknik Detaylar

### Kullanılan Teknolojiler
- Backend: Python Flask
- Frontend: HTML, Tailwind CSS, JavaScript
- Veritabanı: SQLite
- ORM: SQLAlchemy
- Fiyat Güncellemeleri: Python Requests

### Proje Yapısı
```
track-finance/
├── app.py                 # Ana uygulama dosyası
├── config.py             # Konfigürasyon ayarları
├── models/               # Veritabanı modelleri
├── routes/               # Route tanımlamaları
├── services/             # İş mantığı servisleri
├── templates/            # HTML şablonları
├── static/              # Statik dosyalar (CSS, JS)
└── utils.py             # Yardımcı fonksiyonlar
```

### Veritabanı Modelleri ve İlişkileri

#### 1. Kategori Sistemi
- `Category` modeli: Gelir/gider kategorilerini temsil eder
- Hiyerarşik yapı: Ana kategoriler ve alt kategoriler
- Her kategori bir tipe sahiptir (gelir/gider)
- İlişkiler:
  - `Transaction` ile one-to-many
  - `Budget` ile one-to-many

#### 2. Etiket Sistemi
- `Tag` modeli: İşlemleri etiketlemek için kullanılır
- Many-to-many ilişki:
  - `Transaction` ile many-to-many
  - `Investment` ile many-to-many

#### 3. Yatırım Sistemi
- `Investment` modeli: Yatırım varlıklarını temsil eder
- `InvestmentType` modeli: Yatırım türlerini tanımlar (altın, döviz, kripto vb.)
- `InvestmentHistory` modeli: Yatırım fiyat geçmişini tutar
- İlişkiler:
  - `Investment` -> `InvestmentType` (many-to-one)
  - `Investment` -> `InvestmentHistory` (one-to-many)
  - `Investment` -> `Tag` (many-to-many)

#### 4. İşlem Sistemi
- `Transaction` modeli: Gelir/gider işlemlerini temsil eder
- `TransactionType` modeli: İşlem türlerini tanımlar (gelir/gider)
- İlişkiler:
  - `Transaction` -> `Category` (many-to-one)
  - `Transaction` -> `Tag` (many-to-many)

### Servis Katmanı

#### 1. Yatırım Servisi (`InvestmentService`)
- Yatırım fiyatlarını güncelleme
- Portföy performans hesaplama
- Yatırım geçmişi yönetimi

### Route Yapısı

#### 1. Yatırım Route'ları (`investment_routes.py`)
- CRUD işlemleri
- Portföy görüntüleme
- Performans analizi

#### 2. İşlem Route'ları (`transaction_routes.py`)
- CRUD işlemleri
- Kategori bazlı filtreleme
- Tarih aralığı filtreleme

#### 3. Kategori Route'ları (`category_routes.py`)
- Kategori yönetimi
- Hiyerarşik yapı yönetimi

#### 4. Etiket Route'ları (`tag_routes.py`)
- Etiket yönetimi
- İşlem etiketleme

### Sık Kullanılan Komutlar
```bash
# Projeyi başlatma
python app.py

# Veritabanını sıfırlama
python -c "from app import db; db.drop_all(); db.create_all()"
```

## Güvenlik Önlemleri
1. API anahtarlarını güvenli şekilde saklayın
2. Kullanıcı girişlerini doğrulayın
3. SQL injection'a karşı koruma sağlayın
4. XSS saldırılarına karşı önlem alın

## Performans İyileştirmeleri
1. Veritabanı indeksleri kullanın
2. Önbellek mekanizması ekleyin
3. API isteklerini optimize edin
4. Statik dosyaları CDN üzerinden sunun 