# Knowledge Vault Index

> Content catalog for the track-finance knowledge base.
> Updated after every INGEST and SEED operation.

## Components

- [[cashflow]] — Core component: transactions CRUD, dashboard analytics, Excel import, pagination, bulk edit
- [[category]] — Hierarchical transaction categories with parent/child relationships
- [[tag]] — Flat labels for cross-cutting transaction classification (M2M)
- [[categorization-rule]] — Automatic categorization rules for imported transactions
- [[auth]] — Single-user authentication via Flask-Login
- [[settings]] — App settings (currency, pgadmin URL), seed data, database reset

## Architecture

- [[stack]] — Tech stack: Python/Flask/SQLAlchemy/PostgreSQL, Jinja2/Tailwind/Chart.js
- [[factory-pattern]] — Application factory pattern in app.py
- [[blueprint-pattern]] — One Flask Blueprint per domain
- [[database-schema]] — PostgreSQL schema, constraints, indexes
- [[design-system]] — Dark theme colors, typography, CSS components
- [[testing-strategy]] — pytest in Docker, test structure, enforcement
- [[docker-setup]] — Docker Compose services, make commands, env vars

## Decisions

- [[2026-01-15-no-spa]] — No SPA, server-side rendering only with Jinja2
- [[2026-01-15-dark-theme-only]] — Single dark theme, no light mode
- [[2026-01-15-numeric-for-money]] — Numeric(12,2) for all money fields, never Float
- [[2026-01-15-single-user]] — Single user only, no multi-tenancy
- [[2026-04-23-remove-bank-sync-investment]] — Removed bank sync API and investment module entirely

## Patterns

- [[route-handler]] — Standard Flask route handler pattern (GET/POST, try/except/rollback, PRG)
- [[model-definition]] — SQLAlchemy model conventions (imports, types, timestamps)
- [[hierarchical-data]] — Self-referential FK pattern for parent/child models
- [[template-structure]] — Jinja2 template hierarchy and conventions
- [[test-conventions]] — Test file organization, markers, fixtures, patterns
- [[pre-computed-counts]] — GROUP BY counts in routes instead of N+1 model properties
- [[context-processor]] — Flask context processor for global template variables
- [[pagination]] — Server-side pagination with merged summary footer
- [[row-selection]] — Clickable row selection without checkboxes

## Bugs

- [[bulk-edit-pointer-events]] — Bulk edit bar blocking pagination clicks (resolved)
- [[toast-visibility]] — Toast notifications nearly transparent (resolved)
- [[sticky-column-hover]] — Sticky column hover delay on amount cells (resolved)
- [[date-preset-alignment]] — Dashboard date presets misaligned to month boundaries (resolved)

## Roadmap

- [[planned-features]] — Planned features and technical debt from docs/PLAN.md

## Syntheses

## Sources

- [[2026-04-23-major-cleanup]] — Large cleanup: removed bank sync/investment, added pagination, fixed N+1, UI improvements
- [[2026-04-25-bugfixes-ui-polish]] — Bug fixes (sticky column, date presets, toasts), pgAdmin removal, title standardization
- [[2026-04-25-design-review-ui-improvements]] — Design council review, Font Awesome removal, contrast fix, row selection

## Archived

- [[investment]] — Investment transaction tracking (removed 2026-04-24)
- [[investment-type]] — Hierarchical investment classification (removed 2026-04-24)
- [[adapter-registry]] — Bank sync adapter registry pattern (removed 2026-04-24)
