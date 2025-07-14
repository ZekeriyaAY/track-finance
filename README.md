# 💰 Finance Tracker

A modern Flask-based web application for tracking personal income, expenses, and investments with professional Grafana analytics.

## 🚀 Quick Start

```bash
git clone <your-repo-url>
cd track-finance

# First time setup
make setup

# Or manually:
cp .env.example .env
# Edit .env with your settings
make up
```

### 🔧 Development/Debug Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
flask run
```

**Access Points:**
- **Web App**: http://localhost:5000

## ✨ Features

- **Cash Flow Tracking**: Income and expenses with categories and tags
- **Investment Portfolio**: Track stocks, crypto, currencies with transaction history
- **Grafana Integration**: Professional dashboards and analytics
- **Multi-language**: English and Turkish support
- **Modern UI**: Mobile-friendly interface with Tailwind CSS
- **Excel Import**: Bank statement import support

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, Jinja2, Tailwind CSS, Font Awesome
- **Database**: SQLite
- **Analytics**: Grafana (Optional)

##  Configuration & Commands

### Environment Variables (.env)
- **Database**: `DATABASE_URL`
- **Flask**: `FLASK_ENV`, `FLASK_DEBUG`, `SECRET_KEY`

### Available Commands
For complete setup and deployment guide, see [DEPLOYMENT.md](DEPLOYMENT.md).

```bash
# Development setup
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
flask db upgrade
flask run
```

### Local Development (Without Docker)
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
flask db upgrade
flask run
```

## 📈 Usage

1. **Add Categories**: Create income/expense categories
2. **Track Cash Flow**: Record income and expenses with tags  
3. **Manage Investments**: Add portfolio positions and transactions

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Setup and deployment guide

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔧 Troubleshooting

For detailed troubleshooting, operations guide, and system-specific issues, see **[DEPLOYMENT.md](DEPLOYMENT.md)**.
