---
title: Docker Setup
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
  - docker-compose.yml
---

# Docker Setup

Docker Compose with three services: app, PostgreSQL 15, pgAdmin.

## Commands

| Command | Use |
|---------|-----|
| `make dev` | Development with hot-reload |
| `make dev-d` | Development in background |
| `make prod` | Production (Gunicorn) |
| `make down` | Stop all services |

## Environment Variables

**Required (production):** `POSTGRES_PASSWORD`, `SECRET_KEY`

**Optional:** `FLASK_ENV`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `BEHIND_PROXY`

## Key Points

- Everything runs in Docker — no local venv, no local `pip install`
- Tests run in Docker via `make test`
- Production uses Gunicorn WSGI server
- Development uses Flask dev server with hot-reload
- Container timezone is UTC (see [[planned-features]] for TZ issue)

## Related

- [[stack]]
- [[testing-strategy]]
