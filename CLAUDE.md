# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Where's My Money?** — A personal finance management app (single-user) built with Flask, SQLAlchemy, PostgreSQL, and Jinja2 templates styled with Tailwind CSS (CDN). Tracks cashflow transactions, hierarchical categories/tags, and investments with an analytics dashboard.

## Development Commands

### Docker-based development (primary workflow)
```bash
make dev          # Start dev environment with hot-reload (docker-compose + dev overrides)
make prod         # Start production environment
make down         # Stop all services
make logs         # View all service logs
make logs-app     # View app logs only
make clean        # Delete everything (volumes, images)
```

### Flask commands (inside container or local venv)
```bash
flask db upgrade              # Apply database migrations
flask db migrate -m "msg"     # Generate new migration
flask db downgrade            # Rollback last migration
```

### Running the app
- Dev: `make dev` → app at http://localhost:5001, PgAdmin at http://localhost:5050
- The app auto-creates a default admin user on first request (credentials in config.py)
- Database initializes via `flask db upgrade` which runs automatically in Docker entrypoint

### No test suite exists
There are no automated tests. No pytest, no test directory.

## Architecture

### Backend (Flask MVC with Blueprints)

```
app.py          → App factory, middleware, error handlers, auth enforcement
config.py       → Environment configs (Dev/Prod), DB URI, session settings
models/         → SQLAlchemy ORM models (one file per entity)
routes/         → Flask blueprints (one file per feature domain)
utils/          → Excel import processor, bank configs, bulk data generators
templates/      → Jinja2 templates (base_layout.html → base.html → feature templates)
```

### Blueprint → URL prefix mapping
| Blueprint | Prefix | Key functionality |
|---|---|---|
| `auth_bp` | `/auth` | Login/logout, password/username change |
| `cashflow_bp` | `/cashflow` | Transaction CRUD, dashboard analytics, Excel import |
| `category_bp` | `/categories` | Hierarchical category CRUD |
| `tag_bp` | `/tags` | Tag CRUD |
| `investment_bp` | `/investments` | Investment transaction CRUD with filtering |
| `investment_type_bp` | `/investment-types` | Investment type CRUD |
| `settings_bp` | `/settings` | App config, dummy data generation, DB reset |

Root `/` redirects to `/cashflow/dashboard`. Health check at `/health`.

### Database Models & Relationships
- **User** — Single admin user, werkzeug password hashing
- **CashflowTransaction** — Core entity with date, type (income/expense), amount, description. FK to Category, M2M to Tags via `cashflow_transaction_tags` junction table
- **Category** — Self-referential parent/child hierarchy. Dashboard aggregates child transactions into parents
- **Tag** — M2M with transactions
- **InvestmentType** — Self-referential hierarchy (e.g., "Securities" > "Stocks"), has icon/color
- **InvestmentTransaction** — buy/sell with price, quantity, total_amount. FK to InvestmentType
- **Settings** — Key-value store for app configuration

### Frontend
- **Jinja2** server-side rendering, no SPA/JS framework
- **Tailwind CSS via CDN** — dark theme (custom colors in base_layout.html)
- **Font Awesome 6.5.2 via CDN** for icons
- **Chart.js** for dashboard charts
- No build step, no bundler, no package.json

### Key Patterns
- **Auth enforcement**: `@app.before_request` in app.py checks login on all routes except `/auth/login`, `/auth/logout`, `/static/*`, `/health`
- **POST-Redirect-GET** with flash messages for all form submissions
- **Single JSON API endpoint**: `/cashflow/api/category-data` for dynamic chart updates
- **Turkish locale support**: `parse_turkish_amount()` in excel_processor.py handles `1.234,56` number format
- **Excel import**: Supports Yapı Kredi and Kuveyt Türk bank statement formats via bank_configs.py

### Database
- PostgreSQL 15 (Docker: `postgres:15-alpine`)
- Alembic migrations in `migrations/versions/`
- Connection pool with `pool_pre_ping=True` and 300s recycle

## CI/CD

GitHub Actions workflow (`.github/workflows/docker-publish.yml`) builds multi-arch Docker images (amd64/arm64) and pushes to GHCR on master push.
