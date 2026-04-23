---
title: Major Cleanup & Performance Session
created: 2026-04-24
updated: 2026-04-24
status: draft
sources:
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
---

# Major Cleanup & Performance Session

Large-scale cleanup session: removed unused features, improved UI/UX, and optimized performance. 13 commits produced across ~18-20 meaningful exchanges.

## Goal

Systematically work through planned tasks from `docs/PLAN.md` — feature removal, UI improvements, and performance optimization.

## What Was Done

### Feature Removal
- **Bank sync removed** (`10c7797`): Deleted `BankConnection` model, `utils/bank_sync/` adapter directory, bank connection settings routes/templates, cashflow sync button. Kept Excel import bank configs (`utils/bank_configs.py`).
- **Investment UI removed** (`f63aa75`): Removed investment route files, templates, sidebar links, integration tests.
- **Investment fully removed** (`190f32e`): Complete removal of `InvestmentType` and `InvestmentTransaction` models, seed data, all references. Created Alembic migration to drop tables.

### UI/UX Improvements
- **Full-width layout** (`37b6d71`): Removed `max-w-7xl` constraint from `base.html`.
- **Dynamic currency** (`45dc913`): Added `currency_symbol` setting with dropdown of 10 currencies. Created Jinja2 context processor for global injection. Added `data-suffix` support to counter animations.
- **Friendly messages** (`c2e8e1c`): Rewrote empty states across 4 templates and flash messages across 6 route files. Updated ~49 test assertions.
- **Pagination** (`415b262`): Converted cashflow index to `.paginate(page, per_page=25)`. Summary totals from full filtered query. Added pagination UI.
- **Merged summary bar** (`d175a0b`): Combined pagination + summary into single footer row.

### Bug Fixes
- **Bulk edit blocking pagination** (`44561ab`): Fixed `pointer-events-auto` on hidden bulk edit bar — [[bulk-edit-pointer-events]]
- **CSRF token missing**: Removing sync form left no CSRF token source on empty cashflow page. Tests updated to fetch from add form.
- **Flash message escaping**: Apostrophes rendered as `\u0027` in JS toast, not `&#39;`. Fixed test assertions.
- **Toast visibility identified** (`7394c9c`): Documented in PLAN.md — [[toast-visibility]]

### Performance
- **N+1 query fix** (`8b06969`): Category index ~142→~2 queries, tag index ~30→~2, cashflow ~75→~3. Pre-computed counts via GROUP BY, `joinedload()` for eager loading, `EXISTS` subqueries for delete checks — [[pre-computed-counts]]
- **Database indexes** (`d5775b3`): Added indexes on `cashflow_transaction.date`, `.category_id`, `.type`, `.source`, `category.parent_id`, `categorization_rule.is_active`, `.priority`.
- **Deprecated API cleanup** (`80c094d`): Replaced 14 `Model.query.get()` with `db.session.get()`.

## Decisions

- Bank sync API removed but Excel import bank configs preserved — different purposes — [[2026-04-23-remove-bank-sync-investment]]
- Investment removed in two phases, then fully removed including models/migrations
- Currency stored as Settings key-value, not per-transaction
- N+1 fix via pre-computed counts in routes, not model properties

## Open Threads

- Toast notification visibility still unfixed — [[toast-visibility]]
- Remaining PLAN.md items not addressed in this session

## Related

- [[cashflow]]
- [[category]]
- [[tag]]
- [[settings]]
- [[categorization-rule]]
- [[pre-computed-counts]]
- [[pagination]]
- [[context-processor]]
- [[bulk-edit-pointer-events]]
- [[toast-visibility]]
- [[2026-04-23-remove-bank-sync-investment]]
