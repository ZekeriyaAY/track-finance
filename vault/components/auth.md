---
title: Auth Component
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - routes/auth.py
  - models/user.py
  - app.py
---

# Auth Component

Single-user authentication via Flask-Login. No registration — admin user auto-created on first run.

## Files

| Layer | File |
|-------|------|
| Route | `routes/auth.py` — Blueprint `auth_bp`, prefix `/auth` |
| Model | `models/user.py` — `User` |
| Templates | `templates/auth/login.html`, `account.html` |
| App setup | `app.py` — login_manager config, `require_login` middleware, `ensure_admin_user` |

## Model: User

- **username:** `String(80)`, unique
- **password_hash:** `String(256)` — via `werkzeug.security` generate/check
- `UserMixin` from Flask-Login for session integration
- `create_default_user()` static method — creates admin if `User.query.count() == 0`
- `get_admin_user()` — returns `User.query.first()` (single-user design)

## Routes

### `GET/POST /auth/login`
- Redirects if already authenticated
- Validates credentials via `user.check_password()`
- Supports `remember` checkbox
- Safe `next` redirect (validates starts with `/` and not `//`)
- Logs success/failure with IP address

### `GET /auth/logout`
Requires login. Logs out and redirects to login page.

### `GET /auth/account`
Account settings page (password/username change forms).

### `POST /auth/change-password`
Validates current password, minimum 6 chars, confirmation match.

### `POST /auth/change-username`
Requires password re-entry. Validates minimum 3 chars, not same as current.

## App-Level Auth Setup (app.py)

- `login_manager.login_view = 'auth.login'`
- `require_login` before_request: blocks all endpoints except `auth.login`, `auth.logout`, `static`, `health_check`
- `ensure_admin_user` before_request: creates default admin on first request (runs once via `_admin_user_checked` flag)
- Default credentials from config: `ADMIN_USERNAME` / `ADMIN_PASSWORD` (default: `admin` / `admin`)

## Related

- [[route-handler]]
