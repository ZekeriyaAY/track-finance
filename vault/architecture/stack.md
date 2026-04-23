---
title: Tech Stack
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
  - requirements.txt
---

# Tech Stack

## Backend
- **Python 3.11** with **Flask 3.0.2**
- **SQLAlchemy 2.0** ORM with **PostgreSQL 15**
- **Flask-Migrate** (Alembic) for database migrations
- **Flask-Login** for session-based authentication
- **Flask-WTF** for CSRF protection
- **Gunicorn** for production WSGI server

## Frontend
- **Jinja2** server-side rendering (no SPA — see [[2026-01-15-no-spa]])
- **Tailwind CSS** via CDN — utility-first styling
- **Chart.js v4** via CDN — dashboard visualizations
- **Lucide Icons** via CDN — primary icon set
- **Geist Sans/Mono** via CDN — typography

## Infrastructure
- **Docker Compose** — app + PostgreSQL + pgAdmin containers
- **pytest** in Docker for testing (SQLite in-memory for test isolation)

## Key Constraints
- No npm, no frontend build step, no `node_modules`
- All JS inline in templates
- Single-user only, no multi-tenancy
- Everything runs in Docker (`make dev`, `make test`)

## Related

- [[2026-01-15-no-spa]]
- [[factory-pattern]]
- [[docker-setup]]
- [[testing-strategy]]
