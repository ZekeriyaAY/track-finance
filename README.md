# Where's My Money? (track-finance)

A self-hosted personal finance management web application built with Flask and PostgreSQL. Track your income and expenses, categorize transactions, manage investments, import bank statements from Excel/CSV files, and visualize your financial data through interactive dashboards -- all within a dark-themed, responsive UI.

Designed as a single-user, Docker-deployed application with integrated database administration via pgAdmin.

## Key Features

- **Dashboard & Analytics** -- Interactive dashboard with KPI cards (income, expenses, net savings, transaction count), percentage change vs. previous period, and five Chart.js visualizations: monthly income vs. expense bars, expense-by-category doughnut with drill-down into subcategories, daily trend lines with 7-day moving averages, monthly net savings, and top 10 expense categories with drill-down.
- **Cash Flow Management** -- Full CRUD for income and expense transactions with filtering by category, tag, type, date range, and description search. Bulk edit support for category and tag reassignment across multiple transactions.
- **Hierarchical Categories & Tags** -- Self-referential parent/child category tree and flat tags with many-to-many transaction association. Transaction counts tracked per category and tag.
- **Investment Tracking** -- Record buy/sell transactions for configurable investment types (stocks, ETFs, crypto, metals, currencies) organized in a parent/child hierarchy with custom icons and colors.
- **Excel/CSV Import** -- Import bank statements from Yapi Kredi and Kuveyt Turk with automatic header detection, Turkish locale amount parsing, and column mapping. Supports `.xlsx`, `.xls`, and `.csv` formats.
- **Bank Sync** -- Adapter-pattern bank API integration with encrypted credential storage (Fernet). Includes deduplication via external transaction ID constraints. Ships with a Yapi Kredi OAuth2 adapter.
- **Dark Theme** -- Fully dark UI built with Tailwind CSS, custom color palette, and responsive design across desktop and mobile.
- **PWA Support** -- Web app manifest with multiple icon sizes for home screen installation.
- **Authentication** -- Single-user login with Flask-Login, Werkzeug password hashing, remember-me sessions (7 days), and automatic admin user creation on first run.
- **Seed Data** -- One-click setup for default categories, tags, and investment types from the settings page, plus a dummy data generator for testing.
- **Security** -- CSRF protection on all forms, security headers (X-Frame-Options, HSTS in production, etc.), encrypted bank credentials, and production enforcement of a secure SECRET_KEY.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask 3.0, Python 3.11 |
| ORM | SQLAlchemy 2.0 via Flask-SQLAlchemy |
| Database | PostgreSQL 15 (Alpine) |
| Migrations | Alembic via Flask-Migrate |
| Auth | Flask-Login, Werkzeug password hashing |
| Frontend | Tailwind CSS (CDN), Font Awesome 6.5, Chart.js v4, Google Fonts (Inter) |
| Templating | Jinja2 (server-side rendering) |
| Data Import | pandas, openpyxl, xlrd |
| Encryption | cryptography (Fernet) |
| Production Server | Gunicorn (4 workers) |
| Containerization | Docker, Docker Compose |
| DB Admin | pgAdmin 4 |

## Project Structure

```
track-finance/
  app.py                        # Flask app factory, middleware, error handlers
  config.py                     # Development/Production config classes
  gunicorn-conf.py              # Production WSGI server config
  requirements.txt              # Python dependencies
  Dockerfile                    # Container build (python:3.11-slim)
  docker-compose.yml            # Production stack (app + db + pgadmin)
  docker-compose.dev.yml        # Development overlay (hot-reload, source mount)
  Makefile                      # Docker convenience commands
  models/
    __init__.py                 # Shared SQLAlchemy instance
    user.py                     # User authentication model
    category.py                 # Hierarchical categories (self-referential)
    tag.py                      # Transaction tags (many-to-many)
    cashflow.py                 # Cash flow transactions + junction table
    investment.py               # Investment types + transactions
    settings.py                 # Key-value settings store
    bank_connection.py          # Bank API connections (encrypted credentials)
  routes/
    auth.py                     # Login, logout, account settings
    cashflow.py                 # Dashboard, transactions, import, sync, bulk edit
    category.py                 # Category CRUD
    tag.py                      # Tag CRUD
    investment.py               # Investment transaction CRUD
    investment_type.py          # Investment type CRUD
    settings.py                 # App settings, seed data, bank connections, DB reset
  utils/
    data_utils.py               # Seed data and dummy data generators
    excel_processor.py          # Excel/CSV import pipeline
    bank_configs.py             # Bank-specific Excel format definitions
    encryption.py               # Fernet encryption helpers
    bank_sync/
      base.py                   # Abstract adapter, dataclasses, exceptions
      registry.py               # Adapter registry (decorator pattern)
      service.py                # Sync orchestration service
      yapikredi_adapter.py      # Yapi Kredi bank API adapter
  templates/                    # Jinja2 templates (18 files, 3-level inheritance)
  static/
    css/style.css               # Custom dark theme styles
    site.webmanifest            # PWA manifest
    *.png, favicon.ico          # App icons and favicons
  migrations/                   # Alembic migration versions
  logs/                         # Application logs (gitignored)
```

## Setup & Installation

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ZekeriyaAY/track-finance.git
   cd track-finance
   ```

2. **Configure environment variables (optional):**

   Create a `.env` file in the project root to override defaults:
   ```env
   POSTGRES_PASSWORD=change_me
   SECRET_KEY=very-secret-key
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=changeme123
   PGADMIN_DEFAULT_EMAIL=admin@admin.com
   PGADMIN_DEFAULT_PASSWORD=admin
   ```

3. **Start the application:**
   ```bash
   # Production mode
   make prod

   # Development mode with hot-reload
   make dev
   ```

4. **Access the application:**
   - Application: http://localhost:5001
   - pgAdmin: http://localhost:5050

   Log in with the admin credentials from your `.env` file (defaults: `admin` / `changeme123`).

### Development Setup

The development overlay mounts the source directory into the container and runs the Flask development server with debug mode and auto-reload:

```bash
make dev
# or explicitly:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### Reverse Proxy Configuration

If running behind a reverse proxy (nginx, Traefik, etc.) with SSL termination, add these to your `.env`:

```env
BEHIND_PROXY=True
PREFERRED_URL_SCHEME=https
SESSION_COOKIE_SECURE=True
WTF_CSRF_SSL_STRICT=True
```

If not using HTTPS and encountering "CSRF session token is missing" errors, set:

```env
SESSION_COOKIE_SECURE=False
WTF_CSRF_SSL_STRICT=False
```

## Configuration

All configuration is managed through environment variables loaded in `config.py`:

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `very-secret-key` | Flask secret key. **Must be changed in production.** |
| `ADMIN_USERNAME` | `admin` | Default admin username (created on first run) |
| `ADMIN_PASSWORD` | `changeme123` | Default admin password (created on first run) |
| `POSTGRES_PASSWORD` | `change_me` | PostgreSQL database password |
| `POSTGRES_HOST` | `db` | PostgreSQL hostname (`db` in Docker, `localhost` for local dev) |
| `FLASK_ENV` | `development` | Environment mode (`development` or `production`) |
| `SESSION_COOKIE_SECURE` | `False` (dev) / `True` (prod) | Require HTTPS for session cookies |
| `WTF_CSRF_SSL_STRICT` | `False` (dev) / `True` (prod) | Strict CSRF SSL referer checking |
| `BEHIND_PROXY` | `False` | Enable proxy fix middleware for X-Forwarded headers |
| `PREFERRED_URL_SCHEME` | `http` | URL scheme for generated URLs (`http` or `https`) |
| `PGADMIN_DEFAULT_EMAIL` | `admin@admin.com` | pgAdmin login email |
| `PGADMIN_DEFAULT_PASSWORD` | `admin` | pgAdmin login password |

## Makefile Commands

| Command | Description |
|---|---|
| `make dev` | Start development mode with hot-reload |
| `make dev-d` | Start development mode in background |
| `make prod` | Start production mode |
| `make prod-pull` | Pull latest image and start production |
| `make up` | Start services (production) |
| `make down` | Stop all services |
| `make logs` | View all container logs |
| `make logs-app` | View application logs only |
| `make ps` | Show running containers |
| `make clean` | Stop and remove everything including volumes (destructive) |
| `make help` | Show available commands |

## License

This project is open source. See the repository for license details.
