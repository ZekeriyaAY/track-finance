---
title: Cashflow Component
created: 2026-04-23
updated: 2026-04-26
status: draft
sources:
  - routes/cashflow.py
  - models/cashflow.py
  - templates/cashflow/
  - commit:37a41c9
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
  - raw/sessions/4fef5bde-9c63-451f-9e02-927c83d0e0af.jsonl
  - raw/sessions/2ad8e597-2cdb-434c-a9cb-b6c17165c9d7.jsonl
---

# Cashflow Component

The core component of track-finance. Handles income/expense transactions — CRUD, dashboard analytics, Excel/CSV import, pagination, and bulk editing.

## Files

| Layer | File |
|-------|------|
| Route | `routes/cashflow.py` — Blueprint `cashflow_bp`, prefix `/cashflow` |
| Model | `models/cashflow.py` — `CashflowTransaction` + `cashflow_transaction_tags` M2M table |
| Templates | `templates/cashflow/dashboard.html`, `index.html`, `form.html`, `import.html` |
| Utils | `utils/excel_processor.py` |

## Model: CashflowTransaction

- **amount:** `Numeric(12, 2)` — never Float
- **type:** `String(10)` — enum `income` or `expense`
- **source:** `String(20)` — `manual` or `excel_import`
- **category_id:** FK to `Category` (required)
- **tags:** M2M via `cashflow_transaction_tags` association table
- **Indexes:** `date`, `category_id`, `type`, `source` (added for query performance)

## Routes

### `GET /cashflow/dashboard`
Dashboard with KPIs and charts. Features:
- Date range filter (defaults to current month, starting from day 1)
- Date presets (This Month, Last Month, 30 Days, 3 Months, 6 Months, 1 Year) — all month-based presets align to day 1 of month — [[date-preset-alignment]]
- 4 KPIs: total income, total expense, net savings, transaction count
- Period-over-period comparison (previous N days)
- Charts: monthly income vs expense, category expense breakdown (doughnut with drill-down), daily trend with 7-day moving average, top 10 expense categories (horizontal bar)
- Category breakdown aggregates child categories under parent

### `GET /cashflow/`
Transaction list with filters: category (includes subcategories), tag, type, date range, text search on description. Ordered by date descending. **Paginated** at 25 per page — see [[pagination]]. Uses `joinedload()` for category, parent, and tags to avoid N+1 queries — see [[pre-computed-counts]].

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
- Row selection via clickable rows (no checkboxes) — [[row-selection]]
- Filter button uses `btn-primary` (primary action on the page)
- Bulk edit floating bar uses `pointer-events-none` when hidden to avoid blocking pagination — [[bulk-edit-pointer-events]]
- Currency symbol injected globally via [[context-processor]]
- Summary bar merges count + pagination + income/expense/net into single footer row
- Sticky `.col-amount` uses explicit `var(--bg-surface)` background (not `inherit`) — [[sticky-column-hover]]
- Page titles standardized: "Dashboard" (not "Cash Flow Dashboard"), "Transactions" (not "Cashflow Transactions"), "Import Transactions" (not "Excel Import") — [[2026-04-25-bugfixes-ui-polish]]

## Related

- [[category]]
- [[tag]]
- [[categorization-rule]]
- [[route-handler]]
- [[pagination]]
- [[pre-computed-counts]]
- [[context-processor]]
- [[bulk-edit-pointer-events]]
- [[2026-04-23-major-cleanup]]
- [[2026-04-25-bugfixes-ui-polish]]
- [[sticky-column-hover]]
- [[date-preset-alignment]]
- [[row-selection]]
- [[2026-04-25-design-review-ui-improvements]]
