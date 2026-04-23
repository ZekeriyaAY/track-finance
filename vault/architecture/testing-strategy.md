---
title: Testing Strategy
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
  - tests/conftest.py
---

# Testing Strategy

All tests run in Docker via `make test`. Never `pip install` locally.

## Commands

| Command | Use |
|---------|-----|
| `make test` | Run all tests |
| `make test-report` | Run + generate `tests/report.html` |
| `make test-cov` | Run + coverage in `htmlcov/` |
| `make test-security` | Security tests only |

## Structure

```
tests/
├── conftest.py     — Fixtures: app, db, client, auth_client, sample_*
├── unit/           — Models, utils, processors
├── integration/    — Route tests (CRUD, filters, import)
├── security/       — CSRF, XSS, auth bypass, headers
└── api/            — JSON endpoint tests
```

## Conventions

- Markers: `@pytest.mark.unit`, `.integration`, `.security`, `.api`
- SQLite in-memory for test isolation (not PostgreSQL)
- CSRF tokens: `get_csrf_token(client, url)` helper
- DB queries after requests: wrap in `with app.app_context():`
- Fixtures: `auth_client` (logged-in), `client` (anonymous), `sample_*` (test data)

## Enforcement

- Pre-commit hook blocks commits if tests fail
- PostToolUse hook runs tests after Python file edits (fast feedback)
- Every code change must have tests — no exceptions

## Related

- [[test-conventions]]
- [[docker-setup]]
