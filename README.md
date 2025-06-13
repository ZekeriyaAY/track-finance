# Track Finance

Kişisel finans, harcama ve yatırım takibi için geliştirilen, kategoriler, etiketler ve yatırım türleriyle detaylı yönetim sunan bir Flask uygulaması.

## Özellikler

- **İşlem Takibi:** Gelir ve giderlerinizi kategorilere ve etiketlere göre yönetin
- **Kategori Yönetimi:** Ana ve alt kategorilerle harcamalarınızı organize edin
- **Etiket Sistemi:** İşlemlerinize özel etiketler ekleyerek detaylı sınıflandırma yapın
- **Yatırım Portföyü:** 
  - Çeşitli yatırım türlerini (hisse, kripto, döviz, değerli metal, bono, gayrimenkul) takip edin
  - Yatırım türlerini özelleştirin ve yönetin
  - Otomatik fiyat geçmişi takibi
- **Kolay Kurulum:** Varsayılan kategori, etiket ve yatırım türü yapısını tek tıkla oluşturun
- **Modern Arayüz:** Responsive tasarım ve kullanıcı dostu navigasyon

## Kurulum

### Gereksinimler

- Python 3.8+
- pip
- SQLite (varsayılan veritabanı)

### Kurulum Adımları

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/kullanici/track-finance.git
   cd track-finance
   ```

2. Sanal ortam oluşturun ve aktif edin:
   ```bash
   # Windows için
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac için
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. Veritabanını başlatın:
   ```bash
   flask db upgrade
   ```

5. Uygulamayı başlatın:
   ```bash
   flask run
   ```

6. Tarayıcınızda `http://localhost:5000` adresine gidin

## Kullanım

### İşlemler
- Ana sayfada tüm işlemlerinizi görüntüleyin
- Yeni gelir/gider ekleyin
- Mevcut işlemleri düzenleyin veya silin

### Kategoriler ve Etiketler
- Kategoriler menüsünden ana ve alt kategorileri yönetin
- Etiketler menüsünden özel etiketler oluşturun
- İşlemlerinizi kategorilere ve etiketlere göre filtreleyin

### Yatırımlar
- Yatırım türlerini özelleştirin
- Yeni yatırımlar ekleyin
- Fiyat geçmişini takip edin
- Portföy performansını izleyin

### Ayarlar
- Varsayılan kategori yapısını oluşturun
- Varsayılan etiketleri ekleyin
- Varsayılan yatırım türlerini tanımlayın
- Veritabanını sıfırlayın veya örnek veriler oluşturun

## Proje Yapısı

```
track-finance/
├── models/                 # Veritabanı modelleri
│   ├── category.py        # Kategori modeli
│   ├── tag.py            # Etiket modeli
│   ├── transaction.py    # İşlem modeli
│   ├── investment.py     # Yatırım modeli
│   ├── investment_type.py # Yatırım türü modeli
│   └── investment_history.py # Yatırım geçmişi modeli
├── routes/               # Route tanımlamaları
├── templates/            # HTML şablonları
│   ├── base.html        # Ana şablon
│   ├── transactions/    # İşlem sayfaları
│   ├── categories/      # Kategori sayfaları
│   ├── tags/           # Etiket sayfaları
│   ├── investments/    # Yatırım sayfaları
│   ├── investment_types/ # Yatırım türü sayfaları
│   └── settings/       # Ayarlar sayfaları
├── static/              # Statik dosyalar
│   └── css/            # CSS dosyaları
├── migrations/          # Veritabanı migrasyon dosyaları
├── instance/           # Instance-specific dosyalar
├── utils.py            # Yardımcı fonksiyonlar
├── app.py              # Ana uygulama dosyası
└── requirements.txt    # Bağımlılıklar
```

## Geliştirici Notları

- Flask-Migrate ve Alembic ile veritabanı migrasyonları yönetilir
- SQLAlchemy ORM kullanılarak veritabanı işlemleri yapılır
- Tailwind CSS ile modern ve responsive arayüz sağlanır
- Font Awesome ikonları kullanılır

## Gelecek Özellikler

- [ ] Yatırım performans grafikleri
- [ ] Çoklu para birimi desteği
- [ ] Otomatik fiyat güncellemeleri için API entegrasyonu
- [ ] Dışa/içe aktarma özellikleri (CSV, Excel)
- [ ] Detaylı raporlama ve analiz araçları
- [ ] Kullanıcı yönetimi ve çoklu hesap desteği

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: Açıklama'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.
