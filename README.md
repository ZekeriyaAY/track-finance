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
make dev    # Start with debug mode enabled
# Or manually: edit .env and set FLASK_ENV=development, FLASK_DEBUG=1
```

**Access Points:**
- **Web App**: http://localhost:5000
- **Grafana Analytics**: http://localhost:3000  
- **pgAdmin**: http://localhost:8080

## ✨ Features

- **Cash Flow Tracking**: Income and expenses with categories and tags
- **Investment Portfolio**: Track stocks, crypto, currencies with transaction history
- **Grafana Integration**: Professional dashboards and analytics
- **Multi-language**: English and Turkish support
- **Modern UI**: Mobile-friendly interface with Tailwind CSS
- **Docker Ready**: Production-ready Docker configuration

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, Jinja2, Tailwind CSS, Font Awesome
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Analytics**: Grafana with PostgreSQL data source
- **Deployment**: Docker, Docker Compose

## 📊 Grafana Analytics

Integrated Grafana provides professional analytics with pre-built dashboard:

🎯 **Finance Tracker Dashboard** includes:
- **Pie Chart**: Monthly expenses by category
- **Time Series**: Daily income vs expense trends  
- **Portfolio Stats**: Investment performance overview

```bash
make up               # Starts Grafana with other services
make setup_grafana    # Dashboard auto-provisioned on startup
```

**Grafana Access**: http://localhost:3000 (admin / `GRAFANA_ADMIN_PASSWORD`)

## 📋 Configuration & Commands

### Environment Variables (.env)
- **Database**: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- **Flask**: `FLASK_ENV`, `FLASK_DEBUG`, `SECRET_KEY`
- **Ports**: `WEB_PORT`, `PGADMIN_PORT`, `GRAFANA_PORT`
- **Admin**: `PGADMIN_DEFAULT_EMAIL`, `GRAFANA_ADMIN_PASSWORD`

### Available Commands
For complete command reference and troubleshooting, see [DEPLOYMENT.md](DEPLOYMENT.md).

```bash
make help           # Show all available commands
make setup          # First time setup
make up             # Start services
make down           # Stop services
make logs           # Show logs
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

1. Navigate to **Settings** → **Management**
2. Create default categories, tags, and investment types
3. Start adding transactions and investments

## 📈 Quick Usage

1. **Add Categories**: Create income/expense categories
2. **Track Cash Flow**: Record income and expenses with tags  
3. **Manage Investments**: Add portfolio positions and transactions
4. **Analyze Data**: View insights in Grafana dashboards

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Operations and troubleshooting guide
- **Makefile**: Run `make help` for all available commands

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔧 Troubleshooting

For detailed troubleshooting, operations guide, and system-specific issues, see **[DEPLOYMENT.md](DEPLOYMENT.md)**.
