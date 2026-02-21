# CLAUDE.md -- Context for AI Coding Assistants

## Project Overview

**Where's My Money?** is a self-hosted, single-user personal finance tracker built with Flask and PostgreSQL. It provides cashflow tracking (income/expense), investment transaction tracking, bank statement import (Excel/CSV), bank API sync, and a dashboard with analytics charts. All amounts are in Turkish Lira (TRY).

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Framework | Flask 3.0.2 |
| ORM | SQLAlchemy 2.0 via Flask-SQLAlchemy |
| Database | PostgreSQL 15 |
| Migrations | Alembic via Flask-Migrate |
| Auth | Flask-Login (single-user, auto-creates admin on first run) |
| CSRF | Flask-WTF (CSRFProtect) |
| Templates | Jinja2 (server-side rendering) |
| CSS | Tailwind CSS via CDN (with forms, typography plugins) + custom dark theme CSS |
| Charts | Chart.js v4 (CDN, dashboard only) |
| Icons | Font Awesome 6.5.2 (CDN) |
| Font | Google Fonts "Inter" |
| Encryption | Fernet (for bank credentials, derived from SECRET_KEY) |
| Server | Gunicorn (4 workers) in production, Flask dev server in development |
| Container | Docker (python:3.11-slim), Docker Compose |

## Architecture

- **Application factory pattern**: `create_app()` in `app.py`
- **Blueprint-based routing**: Each domain (cashflow, category, tag, investment, etc.) has its own blueprint with url_prefix
- **Server-side rendering**: Jinja2 templates with template inheritance (base_layout -> base -> page templates)
- **No separate frontend build**: Tailwind, Chart.js, Font Awesome all loaded via CDN. All JS is inline in templates (~535 lines total)
- **Adapter pattern for bank sync**: Abstract `BaseBankAdapter` with registry decorator, extensible for new banks
- **Single-user auth**: Flask-Login with Werkzeug password hashing, default admin created on first run

## Directory Structure

```
track-finance/
  app.py                          # Flask app factory, middleware, error handlers
  config.py                       # Dev/Prod config classes
  gunicorn-conf.py                # Production WSGI server config
  requirements.txt                # Python dependencies
  Dockerfile                      # Container build (python:3.11-slim, non-root user)
  docker-compose.yml              # Production stack (app + db + pgadmin)
  docker-compose.dev.yml          # Dev overlay (hot-reload, source mount)
  Makefile                        # Docker convenience commands
  models/
    __init__.py                   # Shared db = SQLAlchemy() instance
    user.py                       # User auth (single-user)
    category.py                   # Hierarchical categories (self-referential)
    tag.py                        # Transaction tags (M2M with cashflow)
    cashflow.py                   # CashflowTransaction + junction table
    investment.py                 # InvestmentType (hierarchical) + InvestmentTransaction
    settings.py                   # Key-value settings store
    bank_connection.py            # Bank API connections (encrypted credentials)
  routes/
    auth.py                       # /auth -- login, logout, account, password/username change
    cashflow.py                   # /cashflow -- dashboard, transactions, import, sync, bulk-edit, API
    category.py                   # /categories -- CRUD
    tag.py                        # /tags -- CRUD
    investment.py                 # /investments -- CRUD with filters
    investment_type.py            # /investment-types -- CRUD
    settings.py                   # /settings -- config, seed data, bank connections, DB reset
  utils/
    data_utils.py                 # Seed data generators (categories, tags, investment types, dummy data)
    excel_processor.py            # Excel/CSV import pipeline (Turkish amount parsing)
    bank_configs.py               # Bank-specific Excel format definitions
    encryption.py                 # Fernet encrypt/decrypt for bank credentials
    bank_sync/
      base.py                     # Abstract BaseBankAdapter, dataclasses, exceptions
      registry.py                 # Adapter registry (decorator pattern)
      service.py                  # Sync orchestration service
      yapikredi_adapter.py        # Yapi Kredi bank API adapter (OAuth2)
  templates/                      # Jinja2 templates (18 files)
    base_layout.html              # Root: head, Tailwind CDN, custom config
    base.html                     # App layout: navbar, flash messages, content
    base_minimal.html             # Minimal layout (login page only)
    cashflow/                     # dashboard.html, index.html, form.html, import.html
    investment/                   # index.html, form.html
    category/                     # index.html, form.html
    tag/                          # index.html, form.html
    investment_type/              # index.html, form.html
    auth/                         # login.html, account.html
    settings/                     # index.html
  static/
    css/style.css                 # 357 lines custom dark theme CSS
    *.png, favicon.ico            # App icons (16, 32, 192, 512)
    site.webmanifest              # PWA manifest
  migrations/                     # Alembic migrations
  logs/                           # App logs (gitignored)
```

## Database Models

```
User (standalone, single-user auth)
  - id, username (unique), password_hash

Category (self-referential parent/child via parent_id)
  |-- CashflowTransaction (many, via category_id FK)
        |-- Tag (many-to-many via cashflow_transaction_tags junction table)
        |-- BankConnection (optional FK via bank_connection_id)
        Fields: id, date, type ('income'/'expense'), amount (Float), description,
                category_id, external_transaction_id, source ('manual'/'excel_import'/'bank_sync'),
                bank_connection_id
        Unique constraint: (external_transaction_id, bank_connection_id)

InvestmentType (self-referential parent/child via parent_id)
  |-- InvestmentTransaction (many, via investment_type_id FK)
        Fields: id, investment_type_id, transaction_date, transaction_type ('buy'/'sell'),
                price, quantity, total_amount (price * quantity), description

Settings (key-value store: key, value)
BankConnection (bank_code, bank_name, encrypted client_id/secret, account_id, sync status)
```

## Key Patterns and Conventions

- **CSRF protection**: All POST forms must include `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`
- **Dark theme only**: Background `#1a1d20`, cards `#23272b`, text gray-100 to gray-400. No light theme.
- **Hierarchical categories**: Both Category and InvestmentType use self-referential `parent_id` for parent/child relationships
- **Currency**: Turkish Lira (TRY) throughout. Amount parsing handles Turkish locale (e.g., "1.234,56 TL")
- **Delete protection**: Categories, tags, and investment types cannot be deleted if they have associated transactions or child items
- **Flash messages**: Use `flash('message', 'category')` with categories: success (green), danger (red), info (blue)
- **Form pattern**: All forms use card containers with consistent grid layout and dark-themed inputs
- **Template inheritance**: base_layout.html -> base.html -> page template (or base_minimal.html for login)
- **Inline JavaScript**: All JS is inline in templates. No separate .js files. Dashboard has ~415 lines of Chart.js code.
- **Global login requirement**: `@app.before_request require_login` forces auth for all routes except login, logout, static, health_check
- **Error handlers**: Both 404 and 500 redirect to cashflow index; 500 also rolls back DB session
- **Security headers**: X-Frame-Options: DENY, X-Content-Type-Options: nosniff, HSTS in production

## Running the Application

### Docker Commands (via Makefile)

| Command | Description |
|---|---|
| `make dev` | Development with hot-reload (mounts source, Flask debug mode) |
| `make dev-d` | Development in background |
| `make prod` | Production mode (Gunicorn) |
| `make prod-pull` | Pull latest image + start production |
| `make down` | Stop all services |
| `make logs` | View all logs |
| `make logs-app` | View app logs only |
| `make clean` | Stop + remove everything including volumes (destructive) |

### Docker Compose Files

- `docker-compose.yml` -- Production: app (ghcr.io image) + PostgreSQL 15 + pgAdmin
- `docker-compose.dev.yml` -- Dev overlay: local build, source mount, Flask dev server
- Dev usage: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `FLASK_ENV` | `development` | Config mode (development/production) |
| `SECRET_KEY` | `very-secret-key` | Flask secret (production raises error if default) |
| `ADMIN_USERNAME` | `admin` | Default admin username |
| `ADMIN_PASSWORD` | `changeme123` | Default admin password |
| `POSTGRES_PASSWORD` | (required) | PostgreSQL password |
| `POSTGRES_HOST` | (in connection string) | PostgreSQL host |
| `BEHIND_PROXY` | `false` | Enable ProxyFix middleware for reverse proxy |

## Testing

### Test Stack

| Package | Purpose |
|---|---|
| pytest | Test runner |
| pytest-flask | Flask test client integration |
| pytest-cov | Code coverage reporting |
| factory-boy | Test data factories |
| faker | Fake data generation |
| responses | HTTP request mocking |
| freezegun | Time/date mocking |

### Running Tests

| Command | Description |
|---|---|
| `make test` | Run tests in Docker container |
| `make test-cov` | Run tests with HTML coverage report |
| `make test-local` | Run tests locally (requires deps) |
| `make test-security` | Run security tests only |
| `pytest tests/unit/ -v` | Unit tests only |
| `pytest tests/integration/ -v` | Integration tests only |
| `pytest tests/security/ -v` | Security tests only |
| `pytest tests/api/ -v` | API tests only |

### Test Directory Structure

```
tests/
  conftest.py                    # Shared fixtures (app, db, client, auth_client, sample data)
  unit/
    test_models.py               # All database models
    test_excel_processor.py      # Turkish amount/date parsing, import pipeline
    test_encryption.py           # Fernet encrypt/decrypt
    test_data_utils.py           # Seed data generators
    test_bank_configs.py         # Bank config lookup
    test_bank_sync_registry.py   # Adapter registry pattern
  integration/
    test_auth_routes.py          # Login, logout, password/username change
    test_cashflow_routes.py      # CRUD, filters, search, import, bulk edit
    test_category_routes.py      # CRUD, delete protection
    test_tag_routes.py           # CRUD, delete protection
    test_investment_routes.py    # CRUD, filters
    test_investment_type_routes.py # CRUD, delete protection
    test_settings_routes.py      # Settings, seed data, DB reset
  security/
    test_csrf.py                 # CSRF enforcement on all POST endpoints
    test_auth_security.py        # Auth bypass, open redirect, session security
    test_input_validation.py     # XSS, SQL injection, type validation
    test_file_upload.py          # File type/size validation
    test_headers.py              # Security headers verification
  api/
    test_category_data_api.py    # JSON API endpoint tests
```

### Test Fixtures (conftest.py)

- `app` - Flask test app with SQLite in-memory DB
- `db` - Fresh database per test (create_all/drop_all)
- `client` - Unauthenticated test client
- `admin_user` - Creates admin user
- `auth_client` - Authenticated test client (auto-login)
- `sample_category`, `sample_subcategory` - Category fixtures
- `sample_tag` - Tag fixture
- `sample_transaction` - CashflowTransaction with tag
- `sample_investment_type` - InvestmentType fixture
- `sample_investment` - InvestmentTransaction fixture
- `get_csrf_token(client, url)` - Extract CSRF token from page

## Development Workflow (MANDATORY)

### Test-First Rule
- **Every code change MUST have corresponding tests.** No exceptions.
- New routes: add integration tests in `tests/integration/`
- New utility functions: add unit tests in `tests/unit/`
- Security-sensitive changes: add tests in `tests/security/`
- API changes: add tests in `tests/api/`

### Before Every Commit
1. Write or update tests for the changed code
2. Run `make test` to verify ALL tests pass
3. A git pre-commit hook will block commits if tests fail
4. Claude Code hooks also enforce this automatically

### Test Commands

| Command | Description |
|---|---|
| `make test` | Run all tests in Docker (terminal output) |
| `make test-report` | Run tests + generate `tests/report.html` (open in browser) |
| `make test-cov` | Run tests + generate coverage report in `htmlcov/index.html` |
| `make test-security` | Run only security tests |

### Test File Conventions
- Fixtures in `tests/conftest.py` (shared: `auth_client`, `sample_category`, `sample_tag`, etc.)
- Use `get_csrf_token(client, url)` helper for CSRF tokens in integration tests
- Use `pytest.mark.unit`, `pytest.mark.integration`, `pytest.mark.security`, `pytest.mark.api` markers
- Use `with app.app_context():` when querying DB after HTTP requests in integration tests

### Custom Slash Commands
- `/test` - Run test suite and analyze results
- `/test-fix <test_name>` - Debug and fix a specific failing test

### Code Quality Rules
- Use `datetime.now(timezone.utc)` instead of `datetime.utcnow()` (deprecated)
- Use `db.session.get(Model, id)` instead of `Model.query.get(id)` (legacy)
- All POST forms must include CSRF token
- Validate input types (income/expense, buy/sell) before processing

## Important Notes

- **No REST API**: Server-side rendered app. One JSON endpoint exists: `/cashflow/api/category-data` for chart drill-down via AJAX.
- **No frontend build step**: No npm, no webpack, no compiled CSS/JS. Tailwind is loaded via CDN with inline config.
- **Single-user only**: No multi-tenancy. One admin user auto-created on first run.
- **Turkish bank support**: Excel import supports Yapi Kredi and Kuveyt Turk formats. Bank sync adapter exists for Yapi Kredi API (OAuth2).
- **Seed data available**: Settings page has buttons to create default categories (13 parents with subs), tags (14), and investment types (5 parents with children), plus dummy transaction data.
- **Custom CSS has Bootstrap-like class names**: `.card`, `.btn`, `.badge`, `.alert`, `.table` are custom dark-theme classes in `style.css`, not actual Bootstrap.
- **Database migrations**: Run automatically on container start via `flask db upgrade`. Use `flask db migrate -m "description"` to generate new migrations.
- **PWA manifest**: `site.webmanifest` defines the app for home screen installation.
