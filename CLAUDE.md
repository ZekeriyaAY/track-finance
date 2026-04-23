# CLAUDE.md

## Project Identity

**Where's My Money?** — Self-hosted, single-user personal finance tracker.
Target: One person tracking their own income/expenses and investments. No multi-tenancy, no public API.

## Tech Stack

- **Backend:** Python 3.11, Flask 3.0.2, SQLAlchemy 2.0, PostgreSQL 15
- **Frontend:** Jinja2 SSR, Tailwind CSS (CDN), Chart.js v4 (CDN), Lucide Icons (CDN), Geist Sans/Mono (CDN)
- **Auth:** Flask-Login, single admin user (auto-created on first run)
- **Container:** Docker Compose (app + db + pgadmin), Gunicorn in production
- **Tests:** pytest in Docker, SQLite in-memory for test isolation

## Architecture Fundamentals

```
app.py (factory: create_app)
├── models/          → SQLAlchemy models, db instance in __init__.py
├── routes/          → Flask Blueprints (one per domain)
├── utils/           → Pure functions, Excel processors, data utilities
├── templates/       → Jinja2 (base_layout → base → page)
├── static/css/      → Custom dark-theme CSS (design system component classes)
└── tests/           → unit/ integration/ security/ api/
```

**Key architectural decisions:**
- Application factory pattern (`create_app()` in `app.py`)
- Blueprint-per-domain with `url_prefix` (cashflow, category, tag, settings, auth, categorization_rule)
- Investment routes/templates removed (models kept for future use)
- Server-side rendering only — no SPA, no frontend build step, no npm
- All JS is inline in templates (no separate .js files)
- Hierarchical models via self-referential `parent_id` (Category, InvestmentType)
- Excel import uses bank-specific configs for parsing (`utils/bank_configs.py`)

## Code Conventions

### Language & Naming
- **Code language:** English (variables, functions, classes, comments)
- **Functions/variables:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_SNAKE_CASE`
- **URLs:** kebab-case (`/investment-types`, `/categorization-rules`)
- **Template files:** `snake_case.html` in feature subdirectories
- **Blueprint names:** `{feature}_bp` (e.g., `cashflow_bp`, `category_bp`)

### Import Pattern
```python
# Standard library
from datetime import datetime, timezone

# Third-party
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func

# Local - CRITICAL: always `from models import db`, NEVER `from models.__init__ import db`
from models import db
from models.cashflow import CashflowTransaction
```

### Route Pattern
```python
@blueprint.route('/resource/add', methods=['GET', 'POST'])
def add_resource():
    if request.method == 'POST':
        try:
            # validate, create, commit
            db.session.add(obj)
            db.session.commit()
            flash('Added successfully.', 'success')
            return redirect(url_for('blueprint.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error: {e}")
            flash('An error occurred.', 'danger')
    return render_template('feature/form.html')
```

### Model Pattern
```python
class MyModel(db.Model):
    __tablename__ = 'my_model'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # Money fields: always Numeric(12, 2), never Float
    amount = db.Column(db.Numeric(12, 2), nullable=False)
```

## Database Rules

- **Money:** `db.Numeric(12, 2)` — never Float for currency
- **Timestamps:** `datetime.now(timezone.utc)` — never `datetime.utcnow()` (deprecated)
- **Query by ID:** `db.session.get(Model, id)` — never `Model.query.get(id)` (legacy)
- **Hierarchical data:** Self-referential FK (`parent_id → same table`)
- **Many-to-many:** Association tables with composite primary keys
- **Unique constraints:** Used for deduplication where needed
- **Delete protection:** Check for child records/transactions before allowing deletion
- **Migrations:** Alembic via Flask-Migrate. Generate with `flask db migrate -m "description"`

### Schema Overview
```
User (id, username, password_hash)
Category (id, name, parent_id FK→self) → has many CashflowTransaction
Tag (id, name) ←→ CashflowTransaction (M2M via cashflow_transaction_tags)
CashflowTransaction (id, date, type[income/expense], amount, description, category_id, source)
InvestmentType (id, name, code, icon, color, parent_id FK→self) → has many InvestmentTransaction
InvestmentTransaction (id, investment_type_id, transaction_date, transaction_type[buy/sell], price, quantity, total_amount, description)
CategorizationRule (id, name, priority, is_active, field, operator, value, category_id, type_override) ←→ Tag (M2M)
Settings (id, key, value)
```

## Design System

### Colors (dark theme only, no light mode)
| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#e5884a` | Buttons, links, active states (warm amber) |
| `bg-base` | `#0d1117` | Page background |
| `bg-surface` | `#161b22` | Card/container background |
| `bg-elevated` | `#1c2128` | Modal, dropdown, popover |
| `bg-overlay` | `#21262d` | Hover state, active row |
| `positive` | `#6dba8a` | Income amounts, success |
| `negative` | `#d4616e` | Expense amounts, errors |
| `text-primary` | `#e6edf3` | Headings, important text |
| `text-secondary` | `#9ca3af` | Body text |
| `text-muted` | `#6b7280` | Labels, placeholders |
| `border-default` | `rgba(255,255,255,0.08)` | Dividers, card borders |

### UI Components
- **Font:** Geist Sans (CDN) for UI, Geist Mono for amounts/numbers — weights 400, 500, 600, 700
- **Cards:** `.card` class, `bg-surface` background, `rounded-lg`, subtle border, shadow
- **Buttons:** `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-danger` (CSS component classes)
- **Forms:** `.form-control` dark inputs with `bg-elevated` background
- **Tables:** `.table` class with hover states, `.amount` for money formatting
- **Flash messages:** Toast notifications — success (green), danger (red), warning (yellow), info (blue)
- **Icons:** Lucide icons (primary), Font Awesome (legacy for investment type custom icons only)
- **Typography:** `.text-display`, `.text-h1`, `.text-h2`, `.text-h3`, `.text-body`, `.text-caption`
- **Badges:** `.badge-positive`, `.badge-negative`, `.badge-warning`, `.badge-info`
- **Empty states:** `.empty-state` component with icon + message + CTA
- **Skeletons:** `.skeleton` loading placeholders with pulse animation
- **Counter animation:** `.counter-animate` with `data-target` and `data-decimals` for KPI cards
- **Spacing:** Tailwind utilities (px-4, py-2, gap-2, etc.)
- **Navigation:** Sidebar layout (collapsed 64px, expanded 240px overlay)

### Template Rules
- Extend `base.html` (or `base_minimal.html` for login only)
- CSRF token required in ALL POST forms: `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`
- Mobile-responsive: use Tailwind responsive prefixes (`md:`, `lg:`)
- No external JS files — all JavaScript inline in `<script>` tags within templates
- Icons: use Lucide icons via `<i data-lucide="icon-name"></i>` (Font Awesome only for legacy investment type icons)

## Testing (MANDATORY)

### Rules
- **Every code change MUST have tests.** No exceptions.
- Tests run in Docker: `make test` (never `pip install` locally, no local venv)
- Pre-commit hook blocks commits if tests fail
- Claude Code hooks auto-run tests after Python file edits

### Commands
| Command | Use |
|---------|-----|
| `make test` | Run all tests (terminal output) |
| `make test-report` | Run + generate `tests/report.html` |
| `make test-cov` | Run + generate coverage in `htmlcov/` |
| `make test-security` | Security tests only |

### Test Structure
```
tests/
├── conftest.py          → Fixtures: app, db, client, auth_client, sample_*
├── unit/                → Models, utils, processors
├── integration/         → Route tests (CRUD, filters, import)
├── security/            → CSRF, XSS, auth bypass, headers
└── api/                 → JSON endpoint tests
```

### Test Conventions
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.security`, `@pytest.mark.api`
- CSRF tokens: use `get_csrf_token(client, url)` helper from conftest
- DB queries after requests: wrap in `with app.app_context():`
- Fixtures: `auth_client` (logged-in), `client` (anonymous), `sample_*` (test data)

## Do / Don't

### DO
- Use `from models import db` for database access
- Use `db.Numeric(12, 2)` for all money fields
- Use `datetime.now(timezone.utc)` for timestamps
- Use `db.session.get(Model, id)` for primary key lookups
- Use `flash()` with English user-facing messages
- Use try/except with `db.session.rollback()` in all route POST handlers
- Use `logger.error()` before flash on exceptions
- Wrap hierarchical queries to handle parent/child relationships
- Write tests before committing — run `make test`
- Keep JS inline in templates
- Use Tailwind classes for layout, custom CSS classes for components

### DON'T
- Don't use `from models.__init__ import db` (creates separate SQLAlchemy instance)
- Don't use `datetime.utcnow()` (deprecated)
- Don't use `Model.query.get(id)` (legacy pattern)
- Don't use Float for money (precision loss)
- Don't create separate .js files
- Don't add npm/webpack/frontend build tools
- Don't add light theme or theme switching
- Don't allow deletion of categories/tags/types with existing transactions
- Don't skip CSRF tokens in POST forms
- Don't run `pip install` locally — everything runs in Docker
- Don't commit without passing tests
- Don't add multi-user or tenant features

## Acceptance Criteria

### Backend (Routes/Models)
- [ ] All POST routes wrapped in try/except with rollback
- [ ] Input validation for enum fields (income/expense, buy/sell)
- [ ] Delete protection for parent records with children
- [ ] Flash messages in English for user feedback
- [ ] Logger.error() on all caught exceptions
- [ ] CSRF protection on all forms
- [ ] Integration tests covering happy path + edge cases

### Frontend (Templates)
- [ ] Extends `base.html` with proper block structure
- [ ] Mobile-responsive (works on md: breakpoint)
- [ ] Dark theme only — uses design system colors
- [ ] CSRF hidden input in all forms
- [ ] Flash message display via base template
- [ ] Consistent card/form layout matching existing pages
- [ ] Lucide icons where appropriate (Font Awesome only for legacy investment type icons)

### Database Changes
- [ ] Alembic migration generated and tested
- [ ] Numeric(12,2) for money, never Float
- [ ] Proper FK constraints and indexes
- [ ] Default values use `lambda: datetime.now(timezone.utc)`

## Environment & Running

```bash
make dev          # Development with hot-reload
make dev-d        # Development in background
make prod         # Production (Gunicorn)
make down         # Stop all services
make test         # Run tests in Docker
make test-report  # Tests + HTML report
```

Required env vars: `POSTGRES_PASSWORD`, `SECRET_KEY` (production).
Optional: `FLASK_ENV`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `BEHIND_PROXY`.

## Wiki Usage

This project maintains a structured knowledge vault at `vault/`. You must
consult it in the following situations:

1. **Before touching a component file**: If you're about to edit
   `routes/X.py`, `models/X.py`, or `templates/X/`, first read
   `vault/components/<component>.md` if it exists. It may contain domain
   rules, gotchas, or decisions you need to respect.

2. **Before proposing an architectural change**: If you're suggesting a
   new library, pattern, or system-level change, first scan
   `vault/decisions/` for relevant past decisions. Don't re-litigate
   settled choices without flagging the conflict.

3. **Before debugging a non-trivial issue**: Check `vault/bugs/` for
   similar past patterns. If you recognize a match, reference the
   relevant page.

4. **When uncertain about project conventions**: Read `vault/patterns/`
   before writing new route handlers, models, or tests.

5. **Starting any new session with unclear scope**: Read `vault/index.md`
   first to orient yourself.

### Hard rules

- You do NOT write to `vault/` during normal development sessions.
  Vault writes happen only via `/vault-ingest`, `/vault-query`,
  `/vault-lint` slash commands.
- If vault content contradicts actual code, flag it to the user —
  do not silently follow either. The user decides which is correct.
- If you read a vault page, mention it briefly in your response
  ("Checked `vault/components/cashflow.md` — noted that imports
  are deduplicated by hash.") so the user knows the context you
  brought in.

## Self-Maintenance

**This file must stay in sync with the codebase.** When you make changes that affect any documented pattern — colors, schema, architecture, conventions, stack — update the relevant section in this file within the same session. Do not wait for the user to ask.

Trigger files (a PostToolUse hook will remind you):
- `base_layout.html`, `style.css` → Design System section
- `app.py`, `config.py`, `requirements.txt` → Tech Stack / Architecture sections
- New `models/*.py` → Schema Overview
- New `routes/*.py` → Architecture Fundamentals (blueprint list)

When updating this file: keep it concise, actionable, and focused on what an AI assistant needs to write correct code. No prose, no redundancy.
