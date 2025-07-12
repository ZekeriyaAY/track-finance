# 💰 Finance Tracker

A modern Flask-based web application for tracking personal income, expenses, and investments with professional Grafana analytics.

## 🚀 Quick Start

```bash
git clone <your-repo-url>
cd track-finance
make init
```

**Access Points:**
- **Web App**: http://localhost:5001
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

### Ready Database Views:
1. **grafana_monthly_summary**: Monthly income/expense summary
2. **grafana_category_trends**: Category-based trend analysis  
3. **grafana_investment_performance**: Investment performance analysis
4. **grafana_cashflow_analysis**: Detailed cash flow analysis

### Setup Grafana:
```bash
make up                     # Start all services
make setup_grafana_views    # Create database views
make show_grafana          # Check Grafana status
```

**Grafana Login**: admin / `GRAFANA_ADMIN_PASSWORD` (in .env.docker)

## 🚀 Development Setup

### Docker (Recommended)
```bash
git clone https://github.com/ZekeriyaAY/track-finance.git
cd track-finance
make init
```

### Local Development
```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS

# Install and run
pip install -r requirements.txt
flask db upgrade
flask run
```

## ⚙️ Configuration

Key environment variables (`.env.docker`):
```bash
WEB_PORT=5001
GRAFANA_PORT=3000
PGADMIN_PORT=8080
SECRET_KEY=your-secret-key
POSTGRES_PASSWORD=secure-password
GRAFANA_ADMIN_PASSWORD=secure-password
```

## 📈 Usage

1. Navigate to **Settings** → **Management**
2. Create default categories, tags, and investment types
3. Start adding transactions and investments
4. View analytics in Grafana

## 🤝 Contributing

1. Fork the project
2. Create feature branch
3. Commit changes
4. Push and open Pull Request

For deployment and operations, see [DEPLOYMENT.md](DEPLOYMENT.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
