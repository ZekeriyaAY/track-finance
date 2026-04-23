---
title: Settings Component
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - routes/settings.py
  - models/settings.py
  - models/bank_connection.py
---

# Settings Component

Application settings, seed data management, bank connections, and database reset. Combines multiple models.

## Files

| Layer | File |
|-------|------|
| Route | `routes/settings.py` — Blueprint `settings_bp`, prefix `/settings` |
| Models | `models/settings.py` — `Settings` (key-value store) |
|        | `models/bank_connection.py` — `BankConnection` (encrypted credentials) |
| Utils | `utils/data_utils.py` — seed data functions |
| Templates | `templates/settings/index.html` |

## Model: Settings

Key-value store for app configuration:
- **key:** `String(100)`, unique
- **value:** `Text`, nullable
- Class methods: `get_setting(key, default)`, `set_setting(key, value)`
- Currently stores: `pgadmin_url`

## Model: BankConnection

Encrypted bank API credentials:
- **bank_code/bank_name:** Bank identifier
- **client_id_encrypted / client_secret_encrypted:** Encrypted via `utils/encryption.py`
- **account_id:** Optional
- **is_active:** Boolean toggle
- **last_sync_at/status/message:** Sync tracking
- Getter/setter methods use `encrypt_value()` / `decrypt_value()`
- Has relationship to `CashflowTransaction` (synced transactions)

## Routes

### `GET /settings/`
Main settings page. Shows PgAdmin URL, bank connections, seed data buttons.

### Seed Data Routes
- `POST /settings/create-dummy-data` — test data
- `POST /settings/create-default-categories` — default category tree
- `POST /settings/create-default-tags` — default tags
- `POST /settings/create-default-investment-types` — default investment types

### Bank Connection Management
- `POST /settings/bank-connections/add` — creates connection with encrypted credentials
- `POST /settings/bank-connections/delete/<id>`
- `POST /settings/bank-connections/toggle/<id>` — activate/deactivate
- `POST /settings/bank-connections/test/<id>` — tests API connectivity via adapter

### `POST /settings/reset-database`
Deletes all data from all tables (ordered by FK dependencies), resets PostgreSQL sequences. Dangerous operation — no undo.

## Key Behaviors

- PgAdmin URL injected globally via `app.context_processor` in `app.py`
- Bank connection uses legacy `Model.query.get_or_404(id)` pattern (see [[planned-features]])
- Reset deletes junction tables first, then child tables, then parent tables

## Related

- [[bank-sync]]
- [[cashflow]]
- [[route-handler]]
- [[planned-features]]
