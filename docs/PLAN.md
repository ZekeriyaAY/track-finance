# Planned To-Dos

## Existing Feature Changes

- [x] **Remove bank integrations** — Removed: BankConnection model, utils/bank_sync/, Settings bank connections section, Cashflow sync button, related tests. Migration: `77a5c92582fe`.

- [x] **Remove investment feature** — Fully removed: models, routes, templates, sidebar links, seed data, settings UI, and all related tests. Migration: `b3e4f5a6c7d8`.

- [ ] **Dynamic currency selection** — Instead of the currency being statically set to ₺, users should be able to choose their own currency. A currency option on the Settings page, and amount formatting and symbol display should be dynamic across all pages.

- [x] **Full-width page layout** — Removed `max-w-7xl` constraint from `base.html`. Content now fills available width alongside the sidebar.

## UX & Message Improvements

- [ ] **Friendly empty state messages** — Messages shown when tables have no data, like "No transactions found yet", should be made friendlier, more personable (casual but not slangy), and more user-friendly. Example: "It's quiet here so far — get started by adding your first transaction!"

- [ ] **Friendly toast/flash messages** — Backend flash messages (in Turkish) should be made friendlier. Examples defined in the Design System: "Başarıyla eklendi" → "Eklendi, güzel!", "Bir hata oluştu" → "Bir şeyler ters gitti, tekrar dener misin?", "Silindi" → "Kaldırıldı."

- [ ] **Recurring transaction templates** — A template system for frequently recurring transactions (rent, salary, subscriptions). When a template is selected, the form should auto-fill. `CashflowTemplate` model + management UI on the Settings or Cashflow page.

- [ ] **Filter panel as a drawer on mobile** — Cashflow and Investment filter areas stack poorly on mobile. Showing filters in a drawer/bottom-sheet on mobile, opened and closed with a "Filter" button, would provide a better UX.

## Dashboard Improvements

- [ ] **Category trend analysis** — A line chart showing the monthly spending trend for a specific category. On the Dashboard or a separate "Analytics" page. The user selects a category and sees a trend line for the last 6-12 months.

- [ ] **Weekly view** — The Dashboard currently only has monthly and daily trends. A weekly view option should be added — especially useful for short-term spending analysis.

- [ ] **Budget/limit alerts** — Setting monthly spending limits per category. When a limit is exceeded, a warning badge and toast notification appear on the dashboard. `CategoryBudget` model (category_id, monthly_limit, alert_threshold_percent).

## Performance & Technical Debt

- [ ] **Pagination for transaction lists** — `routes/cashflow.py:273` fetches all records with `.all()`. This will cause memory and speed issues at 10K+ records. Page-based loading with SQLAlchemy `.paginate()` + page navigation in the UI should be added. The same applies to `routes/investment.py`.

- [ ] **N+1 query optimization** — `models/category.py` `get_income_count()` and `get_expense_count()` methods execute a separate DB query for each category row. The same issue exists in `models/tag.py`. Solution: instead of Python-level loops, use a single aggregation query (SQLAlchemy `func.count()` + `group_by()`) to fetch all counts in one query.

- [ ] **Add database indexes** — Indexes are missing on frequently filtered columns. Needed: `cashflow_transaction.date`, `cashflow_transaction.category_id`, `cashflow_transaction.type`, `settings.key`, `categorization_rule.is_active` + `categorization_rule.priority`. To be added via Alembic migration.

- [ ] **Legacy Query.get() cleanup** — Test files use `Model.query.get(id)` (deprecated SQLAlchemy 1.x pattern), generating 22 warnings. All should be updated to `db.session.get(Model, id)`.

- [ ] **Docker container timezone** — The container runs in UTC, so `date.today()` doesn't match the browser's local time. The dashboard preset highlight issue was fixed, but the root solution is: set the `TZ=Europe/Istanbul` environment variable in the container, or make all date comparisons timezone-aware.

## Data Management & Export

- [ ] **Transaction export (CSV/Excel)** — Download the filtered transaction list as CSV or Excel. An "Export" button on the Cashflow index page that applies the current filters, generates the file, and triggers a download. `utils/excel_exporter.py` + route endpoint.

- [ ] **Database backup/restore** — Personal finance data is critical. One-click DB dump (JSON or SQL) download and upload on the Settings page. Automatic periodic backup option (daily/weekly) + writing to Docker volume.

- [ ] **Import history and rollback** — Each Excel import should be recorded as a batch (`ImportBatch` model: date, file name, record count). Batch-level bulk rollback (deletion) feature. Currently there is no way to undo after an import.

- [ ] **Import rule test interface** — Ability to test a categorization rule before saving it. The user enters a sample description, and the system previews which rules would match and which category/tag would be assigned. A "Test Rule" section in `categorization_rule/form.html` + AJAX endpoint.

## Security & Infrastructure

- [ ] **Login rate limiting** — There is no limit on login attempts, leaving it open to brute-force attacks. Rate limiting should be added to the login endpoint with Flask-Limiter (e.g., 5 attempts/minute). Increasing wait time after failed attempts.

- [ ] **Import rule matching optimization** — `routes/cashflow.py:441-446` checks all active rules in a Python loop for each imported transaction (O(n×m) complexity). This can slow down with large import files. Rules could be pre-compiled and matched in a single pass, or DB-level matching could be used.
