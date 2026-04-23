# Planned To-Dos

## Existing Feature Changes

- [x] **Remove bank integrations** — Removed: BankConnection model, utils/bank_sync/, Settings bank connections section, Cashflow sync button, related tests. Migration: `77a5c92582fe`.

- [x] **Remove investment feature** — Fully removed: models, routes, templates, sidebar links, seed data, settings UI, and all related tests. Migration: `b3e4f5a6c7d8`.

- [x] **Dynamic currency selection** — Currency symbol stored in Settings DB, configurable via Settings page dropdown. Injected to all templates via context processor. Dashboard KPI cards and transaction list use dynamic symbol.

- [x] **Full-width page layout** — Removed `max-w-7xl` constraint from `base.html`. Content now fills available width alongside the sidebar.

## UX & Message Improvements

- [x] **Friendly empty state messages** — Updated empty states in cashflow, category, tag, and categorization rule pages to be warmer and more inviting.

- [x] **Friendly toast/flash messages** — Rewrote all flash messages across 6 route files to be concise and friendly (e.g. "Transaction added!", "Category removed.", "Something went wrong. Please try again.").

- [ ] **Recurring transaction templates** — A template system for frequently recurring transactions (rent, salary, subscriptions). When a template is selected, the form should auto-fill. `CashflowTemplate` model + management UI on the Settings or Cashflow page.

- [ ] **Filter panel as a drawer on mobile** — Cashflow and Investment filter areas stack poorly on mobile. Showing filters in a drawer/bottom-sheet on mobile, opened and closed with a "Filter" button, would provide a better UX.

## Dashboard Improvements

- [ ] **Category trend analysis** — A line chart showing the monthly spending trend for a specific category. On the Dashboard or a separate "Analytics" page. The user selects a category and sees a trend line for the last 6-12 months.

- [ ] **Weekly view** — The Dashboard currently only has monthly and daily trends. A weekly view option should be added — especially useful for short-term spending analysis.

- [ ] **Budget/limit alerts** — Setting monthly spending limits per category. When a limit is exceeded, a warning badge and toast notification appear on the dashboard. `CategoryBudget` model (category_id, monthly_limit, alert_threshold_percent).

## Performance & Technical Debt

- [x] **Pagination for transaction lists** — Cashflow index uses `.paginate()` with 25 per page. Summary totals reflect all filtered results. Pagination nav preserves filter params. Investment routes were removed.

- [x] **N+1 query optimization** — Category and tag index pages now use a single aggregation query (`GROUP BY category_id/tag_id, type`) instead of per-row model methods. Parent category counts include subcategory totals. Model methods kept for backward compatibility.

- [x] **Add database indexes** — Added indexes on `cashflow_transaction(date, category_id, type)`, `category(parent_id)`, `categorization_rule(is_active, priority)`, `cashflow_transaction_tags(tag_id)`. Migration: `c4d5e6f7a8b9`. `settings.key` already has unique index.

- [x] **Legacy Query.get() cleanup** — Replaced all `Model.query.get(id)` with `db.session.get(Model, id)` in app.py and test files. Zero LegacyAPIWarning remaining.

- [ ] **Docker container timezone** — The container runs in UTC, so `date.today()` doesn't match the browser's local time. The dashboard preset highlight issue was fixed, but the root solution is: set the `TZ=Europe/Istanbul` environment variable in the container, or make all date comparisons timezone-aware.

## Data Management & Export

- [ ] **Transaction export (CSV/Excel)** — Download the filtered transaction list as CSV or Excel. An "Export" button on the Cashflow index page that applies the current filters, generates the file, and triggers a download. `utils/excel_exporter.py` + route endpoint.

- [ ] **Database backup/restore** — Personal finance data is critical. One-click DB dump (JSON or SQL) download and upload on the Settings page. Automatic periodic backup option (daily/weekly) + writing to Docker volume.

- [ ] **Import history and rollback** — Each Excel import should be recorded as a batch (`ImportBatch` model: date, file name, record count). Batch-level bulk rollback (deletion) feature. Currently there is no way to undo after an import.

- [ ] **Import rule test interface** — Ability to test a categorization rule before saving it. The user enters a sample description, and the system previews which rules would match and which category/tag would be assigned. A "Test Rule" section in `categorization_rule/form.html` + AJAX endpoint.

## Security & Infrastructure

- [ ] **Login rate limiting** — There is no limit on login attempts, leaving it open to brute-force attacks. Rate limiting should be added to the login endpoint with Flask-Limiter (e.g., 5 attempts/minute). Increasing wait time after failed attempts.

- [ ] **Import rule matching optimization** — `routes/cashflow.py:441-446` checks all active rules in a Python loop for each imported transaction (O(n×m) complexity). This can slow down with large import files. Rules could be pre-compiled and matched in a single pass, or DB-level matching could be used.
