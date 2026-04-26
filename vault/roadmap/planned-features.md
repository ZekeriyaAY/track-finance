---
title: Planned Features & Technical Debt
created: 2026-04-23
updated: 2026-04-26
status: draft
sources:
  - docs/PLAN.md
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
  - raw/sessions/4fef5bde-9c63-451f-9e02-927c83d0e0af.jsonl
---

# Planned Features & Technical Debt

Tracked in `docs/PLAN.md`. Grouped by category.

## Completed (Session 2026-04-23)

The following items were completed in [[2026-04-23-major-cleanup]]:
- ~~Remove bank integrations~~ → [[2026-04-23-remove-bank-sync-investment]]
- ~~Remove investment pages~~ → fully removed (models, routes, templates, migrations)
- ~~Dynamic currency selection~~ → [[context-processor]]
- ~~Full-width page layout~~ → removed `max-w-7xl`
- ~~Friendly empty state messages~~ → rewrote across 4 templates
- ~~Friendly toast/flash messages~~ → updated across 6 route files
- ~~Pagination~~ → [[pagination]]
- ~~N+1 query optimization~~ → [[pre-computed-counts]]
- ~~Database indexes~~ → added on frequently queried columns
- ~~Legacy Query.get() cleanup~~ → replaced 14 occurrences with `db.session.get()`

## Completed (Session 2026-04-25)

The following items were completed in [[2026-04-25-bugfixes-ui-polish]]:
- ~~Toast notification visibility~~ → fixed by removing 12% opacity overrides — [[toast-visibility]]
- ~~pgAdmin external tools section~~ → fully removed (route, context processor, tests)
- ~~Page title and button label standardization~~ → unified across all templates
- ~~Sticky column hover delay~~ → explicit background color on sticky cells — [[sticky-column-hover]]
- ~~Dashboard date preset alignment~~ → month-based presets use day 1 — [[date-preset-alignment]]

## Remaining UX Improvements

- **Recurring transaction templates** — `CashflowTemplate` model for auto-fill
- **Filter panel as drawer on mobile** — Bottom-sheet filter UI

## Dashboard Improvements

- **Category trend analysis** — Monthly spending trend line per category
- **Weekly view** — Weekly trend option alongside monthly/daily
- **Budget/limit alerts** — `CategoryBudget` model with threshold warnings

## Remaining Performance & Technical Debt

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
- [[2026-04-23-major-cleanup]]
- [[2026-04-25-bugfixes-ui-polish]]
- [[toast-visibility]]
- [[sticky-column-hover]]
- [[date-preset-alignment]]
