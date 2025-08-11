# 💰 Finance Tracker

A modern Flask-based web application for tracking personal income, expenses, and investments with Excel import support and multi-language interface.

## 🚀 Quick Start

```bash
git clone <your-repo-url>
cd track-finance

# Setup virtual environment and dependencies
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Setup environment (optional)
cp .env.example .env
# Edit .env if needed

# Initialize database
flask db upgrade

# Run the application
flask run --host=0.0.0.0
```


**Access Point:**
- **Web App**: http://localhost:5000

## 🚦 Production (Gunicorn ile Çalıştırma)

Production ortamında uygulamayı Gunicorn ile başlatmak için:

```bash
.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

- `-w 4`: 4 worker ile çalıştırır (isteğe göre artırılabilir)
- `-b 0.0.0.0:8000`: 8000 portundan tüm arayüzlere dinler
- `app:app`: Birinci `app` dosya adı (`app.py`), ikinci `app` Flask uygulama nesnesi

### Systemd Servisi ile Otomatik Başlatma

Gunicorn'u systemd servisi olarak başlatmak için örnek servis dosyası:

```ini
[Unit]
Description=Track Finance Gunicorn Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/track-finance
ExecStart=/home/ubuntu/track-finance/.venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Kendi kullanıcı adınızı ve yolu düzenlemeyi unutmayın.

---

## ✨ Features

- **Cash Flow Tracking**: Income and expenses with categories and tags
- **Investment Portfolio**: Track stocks, crypto, currencies with transaction history
- **Excel Import**: Bank statement import support (Yapı Kredi format)
- **Multi-language**: English and Turkish support with Flask-Babel
- **Modern UI**: Mobile-friendly interface with Tailwind CSS
- **SQLite Database**: No external database setup required

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, Jinja2, Tailwind CSS, Font Awesome
- **Database**: SQLite
- **Internationalization**: Flask-Babel
- **Excel Processing**: pandas, openpyxl

## 🚀 Running the Application

### Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

### Production Mode
```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
flask run --host=0.0.0.0 --port=5000
```

### Using Production Server (Optional)
```bash
# For production, you can use Gunicorn
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:5000 wsgi:app
```

## 🗄️ Database Operations

The application uses SQLite database which requires no additional setup.

```bash
# Run migrations
flask db upgrade

# Create new migration
flask db migrate -m "description"

# Database shell
flask shell
```

The database file (`track_finance.db`) will be created in your project directory.

## 🌐 Translation Management

```bash
# Extract translatable strings
pybabel extract -F babel.cfg -k _l -o messages.pot .

# Update existing translations
pybabel update -i messages.pot -d translations

# Compile translations
pybabel compile -d translations
```

## 📈 Usage

1. **Add Categories**: Create income/expense categories for organization
2. **Track Cash Flow**: Record income and expenses with tags and descriptions
3. **Excel Import**: Import bank transactions from Yapı Kredi Excel files
4. **Manage Investments**: Add portfolio positions and track transactions
5. **Multi-language**: Switch between English and Turkish interfaces


## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
