# Track Finance

Kişisel finans, harcama ve yatırım takibi için geliştirilen, kategoriler, etiketler ve yatırım türleriyle detaylı yönetim sunan bir Flask uygulaması.

## Özellikler

- **Gelir/Gider Takibi:** Kategorilere ve etiketlere göre işlemler ekleyin, düzenleyin, silin.
- **Kategoriler:** Ana ve alt kategorilerle harcamalarınızı gruplayın.
- **Etiketler:** İşlemlerinize birden fazla etiket ekleyin.
- **Yatırımlar:** Hisse, kripto, döviz, değerli metal, bono, gayrimenkul ve diğer yatırım türlerini takip edin.
- **Yatırım Türleri Yönetimi:** Ana ve alt yatırım türlerini oluşturun, düzenleyin, silin.
- **Yatırım Geçmişi:** Yatırımlarınızın fiyat değişim geçmişini otomatik olarak kaydedin.
- **Ayarlar:** Varsayılan kategori, etiket ve yatırım türü yapısını tek tıkla oluşturun.
- **Modern Arayüz:** Responsive ve kullanıcı dostu arayüz.

## Kurulum

### Gereksinimler

- Python 3.8+
- pip

### Kurulum Adımları

1. Depoyu klonlayın:

   ```bash
   git clone https://github.com/kullanici/track-finance.git
   cd track-finance
   ```

2. Sanal ortam oluşturun ve aktif edin:

   ```bash
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

5. (İsteğe bağlı) Varsayılan kategorileri, etiketleri ve yatırım türlerini oluşturmak için uygulamayı başlatıp Ayarlar menüsünden ilgili butonlara tıklayın.

6. Uygulamayı başlatın:

   ```bash
   flask run
   ```

## Kullanım

- Ana sayfada işlemlerinizi görebilir, yeni gelir/gider ekleyebilirsiniz.
- Kategoriler ve etiketler menüsünden gruplama ve filtreleme yapabilirsiniz.
- Yatırımlar menüsünden yatırım ekleyebilir, geçmiş fiyatlarını görebilirsiniz.
- Yönetim menüsünden kategoriler, etiketler ve yatırım türlerini yönetebilirsiniz.
- Ayarlar menüsünden veritabanını sıfırlayabilir veya örnek veriler oluşturabilirsiniz.

## Proje Yapısı

```
models/
  category.py
  tag.py
  transaction.py
  investment.py
  investment_type.py
  investment_history.py
templates/
  base.html
  transactions/
  categories/
  tags/
  investments/
  investment_types/
  settings/
static/
  icons/
app.py
requirements.txt
```

## Geliştirici Notları

- Tüm modeller `models/` klasöründe ayrı dosyalarda tutulur.
- Migration işlemleri için Flask-Migrate ve Alembic kullanılır.
- Varsayılan veriler ve örnekler için Ayarlar menüsünü kullanabilirsiniz.

## TODO

- [ ] Yatırım performans grafikleri ve raporlama özellikleri ekle.
- [ ] Çoklu para birimi desteği ekle.
- [ ] Otomatik yatırım fiyat güncellemeleri için harici API entegrasyonu yap.
- [ ] Dışa/içe aktarma özellikleri (CSV, Excel) ekle.
- [ ] Daha kapsamlı testler yaz.

## Katkı

Pull request ve issue açarak katkıda bulunabilirsiniz.
