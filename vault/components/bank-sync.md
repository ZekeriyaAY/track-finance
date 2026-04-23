---
title: Bank Sync Component
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - utils/bank_sync/
  - routes/cashflow.py
  - routes/settings.py
---

# Bank Sync Component

Bank API integration using adapter pattern. Currently has one adapter (Yapi Kredi). Planned for removal (see [[planned-features]]).

## Files

| File | Purpose |
|------|---------|
| `utils/bank_sync/__init__.py` | Public API: `sync_bank_connection()`, `get_available_banks()`, `get_adapter()` |
| `utils/bank_sync/base.py` | Abstract base class `BankAdapter` |
| `utils/bank_sync/registry.py` | Adapter registry decorator `@register_adapter` |
| `utils/bank_sync/service.py` | Sync orchestration: fetches transactions, deduplicates, applies rules, saves |
| `utils/bank_sync/yapikredi_adapter.py` | Yapi Kredi OAuth2 adapter implementation |

## Architecture

Uses **adapter pattern** with decorator-based registry:
1. `@register_adapter('bank_code')` decorator registers adapter classes
2. `get_adapter(bank_code)` looks up the registry
3. `sync_bank_connection(conn_id)` orchestrates: get adapter → authenticate → fetch → deduplicate → categorize → save
4. Deduplication via `external_transaction_id + bank_connection_id` unique constraint

## Key Behaviors

- Sync triggered from [[cashflow]] `POST /cashflow/sync` route
- Connection management in [[settings]]
- Transactions saved with `source='bank_sync'`
- Active categorization rules applied during sync (same as Excel import)
- `BankSyncError` custom exception for adapter-level errors

## Related

- [[cashflow]]
- [[settings]]
- [[categorization-rule]]
- [[adapter-registry]]
- [[planned-features]]
