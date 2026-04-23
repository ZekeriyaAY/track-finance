---
title: Application Factory Pattern
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - app.py
  - CLAUDE.md
---

# Application Factory Pattern

The app uses Flask's application factory pattern via `create_app()` in `app.py`.

## How It Works

`create_app(config_name=None)` does the following in order:

1. **Config**: Loads from `config.py` based on `FLASK_ENV` env var
2. **Proxy fix**: Optionally wraps WSGI app with `ProxyFix` if `BEHIND_PROXY=true`
3. **Logging**: Sets up `RotatingFileHandler` (10MB, 5 backups) + console handler
4. **Extensions**: Initializes `db`, `Migrate`, `CSRFProtect`, `LoginManager`
5. **Middleware**: `add_security_headers` (after_request), `log_request_info` (before_request), `require_login` (before_request)
6. **Blueprints**: Registers all 8 blueprints
7. **Admin user**: `ensure_admin_user` before_request creates default admin on first run (runs once)
8. **Routes**: Root `/` redirects to dashboard, `/health` endpoint for load balancers

## Security Headers

Applied to every response:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: same-origin`
- `Strict-Transport-Security` (production only)

## App Instance

`app = create_app()` at module level — used by Gunicorn in production, Flask dev server in development.

## Related

- [[blueprint-pattern]]
- [[stack]]
- [[auth]]
