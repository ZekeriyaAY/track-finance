---
title: Cashflow Component
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - routes/cashflow.py
  - models/cashflow.py
  - templates/cashflow/
  - commit:37a41c9
---

# Cashflow Component

The core component of track-finance. Handles income/expense transactions — CRUD, dashboard analytics, Excel/CSV import, bank sync, and bulk editing.

## Files

| Layer | File |
|-------|------|
| Route | `routes/cashflow.py` — Blueprint `cashflow_bp`, prefix `/cashflow` |
| Model | `models/cashflow.py` — `CashflowTransaction` + `cashflow_transaction_tags` M2M table |
| Templates | `templates/cashflow/dashboard.html`, `index.html`, `form.html`, `import.html` |
| Utils | `utils/excel_processor.py`, `utils/bank_sync/` |

## Model: CashflowTransaction

- **amount:** `Numeric(12, 2)` — never Float
- **type:** `String(10)` — enum `income` or `expense`
- **source:** `String(20)` — `manual`, `excel_import`, or `bank_sync`
- **category_id:** FK to `Category` (required)
- **tags:** M2M via `cashflow_transaction_tags` association table
- **external_transaction_id:** Indexed, used for deduplication with `bank_connection_id` (unique constraint `uq_external_txn_bank`)
- **bank_connection_id:** FK to `BankConnection` (nullable, only for synced transactions)

## Routes

### `GET /cashflow/dashboard`
Dashboard with KPIs and charts. Features:
- Date range filter (defaults to current month)
- 4 KPIs: total income, total expense, net savings, transaction count
- Period-over-period comparison (previous N days)
- Charts: monthly income vs expense, category expense breakdown (doughnut with drill-down), daily trend with 7-day moving average, top 10 expense categories (horizontal bar)
- Category breakdown aggregates child categories under parent

### `GET /cashflow/`
Transaction list with filters: category (includes subcategories), tag, type, date range, text search on description. Ordered by date descending.

### `GET/POST /cashflow/add`
Add new transaction. Form fields: date, amount, type (income/expense), category, tags (multi-select), description.

### `GET/POST /cashflow/edit/<id>`
Edit existing transaction. Uses `db.get_or_404()`.

### `POST /cashflow/delete/<id>`
Delete transaction. Uses `db.get_or_404()`.

### `GET/POST /cashflow/import`
Excel/CSV import. Supports `.xlsx`, `.xls`, `.csv` via `werkzeug.utils.secure_filename`. Flow:
1. User selects bank and uploads file
2. `process_excel_data()` parses bank-specific format
3. Auto-creates "Import" category and bank tag if missing
4. Applies active `CategorizationRule`s (first match wins by priority)
5. Saves transactions with `source='excel_import'`

### `POST /cashflow/sync`
Syncs all active `BankConnection`s. Calls `sync_bank_connection()` per connection. Reports new/skipped/error counts.

### `POST /cashflow/bulk-edit`
Bulk update category and/or tags for multiple transactions. Tag mode: `replace` or `add`. Preserves filter params on redirect.

### `GET /cashflow/api/category-data`
JSON API for category chart drill-down. Modes: `parent` (aggregated), `children_of` (subcategories of a parent), flat child view.

## Key Behaviors

- Category filter includes subcategories automatically (queries parent + all children)
- Dashboard monthly chart enforces minimum 4-month window regardless of selected date range
- Daily trend fills gaps (no missing days in x-axis)
- Import uses `db.session.flush()` to get IDs for auto-created category/tag before committing
- Bulk edit preserves current filter state via hidden form fields

## Related

- [[category]]
- [[tag]]
- [[bank-sync]]
- [[categorization-rule]]
- [[route-handler]]
