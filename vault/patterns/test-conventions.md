---
title: Test Conventions
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
  - tests/conftest.py
---

# Test Conventions

Standards for writing tests in track-finance.

## File Organization

- `tests/unit/` — Models, utils, processors
- `tests/integration/` — Route tests (CRUD, filters, import)
- `tests/security/` — CSRF, XSS, auth bypass, headers
- `tests/api/` — JSON endpoint tests

## Markers

```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.security
@pytest.mark.api
```

## Fixtures (from conftest.py)

- `app` — Flask app instance (test config, SQLite in-memory)
- `client` — Anonymous test client
- `auth_client` — Logged-in test client
- `sample_*` — Pre-created test data (categories, tags, transactions)

## Patterns

### CSRF tokens
```python
csrf_token = get_csrf_token(client, '/some-url')
client.post('/some-url', data={'csrf_token': csrf_token, ...})
```

### DB queries after requests
```python
with app.app_context():
    result = db.session.get(Model, id)
```

## Enforcement

- Every code change MUST have tests
- Pre-commit hook blocks commits if tests fail
- `make test` runs everything in Docker

## Related

- [[testing-strategy]]
- [[route-handler]]
