---
title: Planned Features & Technical Debt
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - docs/PLAN.md
---

# Planned Features & Technical Debt

Tracked in `docs/PLAN.md`. Grouped by category.

## Existing Feature Changes

- **Remove bank integrations** — Clean up Settings bank connections section, Cashflow sync button, `utils/bank_sync/` code
- **Remove investment pages** — Disable UI access (keep models/migrations)
- **Dynamic currency selection** — Replace static `₺` with user-selected currency on Settings page
- **Full-width page layout** — Remove `max-w-7xl` constraint, use full width with sidebar

## UX Improvements

- **Friendly empty state messages** — Casual, personable empty table messages
- **Friendly toast/flash messages** — More human flash messages
- **Recurring transaction templates** — `CashflowTemplate` model for auto-fill
- **Filter panel as drawer on mobile** — Bottom-sheet filter UI

## Dashboard Improvements

- **Category trend analysis** — Monthly spending trend line per category
- **Weekly view** — Weekly trend option alongside monthly/daily
- **Budget/limit alerts** — `CategoryBudget` model with threshold warnings

## Performance & Technical Debt

- **Pagination** — Replace `.all()` with `.paginate()` for transaction lists
- **N+1 query optimization** — Replace Python loops with `func.count() + group_by()`
- **Database indexes** — Add indexes on `date`, `category_id`, `type`, `settings.key`
- **Legacy Query.get() cleanup** — 22 test warnings, update to `db.session.get()`
- **Docker container timezone** — Set `TZ=Europe/Istanbul` or make date comparisons timezone-aware

## Data Management

- **Transaction export** (CSV/Excel) — Download filtered transaction list
- **Database backup/restore** — One-click DB dump, periodic backup option
- **Import history and rollback** — `ImportBatch` model, batch-level undo
- **Import rule test interface** — Preview which rules would match a sample description

## Security

- **Login rate limiting** — Flask-Limiter on login endpoint (5 attempts/minute)
- **Import rule matching optimization** — Pre-compile rules for large imports

## Related

- [[cashflow]]
- [[settings]]
- [[investment]]
- [[bank-sync]]
