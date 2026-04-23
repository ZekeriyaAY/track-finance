---
title: Settings Component
created: 2026-04-23
updated: 2026-04-24
status: draft
sources:
  - routes/settings.py
  - models/settings.py
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
---

# Settings Component

Application settings, seed data management, and database reset.

## Files

| Layer | File |
|-------|------|
| Route | `routes/settings.py` — Blueprint `settings_bp`, prefix `/settings` |
| Models | `models/settings.py` — `Settings` (key-value store) |
| Utils | `utils/data_utils.py` — seed data functions |
| Templates | `templates/settings/index.html` |

## Model: Settings

Key-value store for app configuration:
- **key:** `String(100)`, unique
- **value:** `Text`, nullable
- Class methods: `get_setting(key, default)`, `set_setting(key, value)`
- Currently stores: `pgadmin_url`, `currency_symbol`

## Routes

### `GET /settings/`
Main settings page. Shows PgAdmin URL, currency selector, seed data buttons.

### `POST /settings/update-currency`
Updates the `currency_symbol` setting. Dropdown with 10 currency options. Value injected globally via [[context-processor]].

### Seed Data Routes
- `POST /settings/create-dummy-data` — test data
- `POST /settings/create-default-categories` — default category tree
- `POST /settings/create-default-tags` — default tags

### `POST /settings/reset-database`
Deletes all data from all tables (ordered by FK dependencies), resets PostgreSQL sequences. Dangerous operation — no undo.

## Key Behaviors

- PgAdmin URL and currency symbol injected globally via `app.context_processor` — see [[context-processor]]
- Reset deletes junction tables first, then child tables, then parent tables

## Related

- [[cashflow]]
- [[route-handler]]
- [[context-processor]]
- [[2026-04-23-remove-bank-sync-investment]]
- [[2026-04-23-major-cleanup]]
