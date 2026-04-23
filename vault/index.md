# Knowledge Vault Index

> Content catalog for the track-finance knowledge base.
> Updated after every INGEST and SEED operation.

## Components

- [[cashflow]] — Core component: transactions CRUD, dashboard analytics, Excel import, bank sync, bulk edit
- [[category]] — Hierarchical transaction categories with parent/child relationships
- [[tag]] — Flat labels for cross-cutting transaction classification (M2M)
- [[investment]] — Buy/sell investment transactions (planned for UI removal)
- [[investment-type]] — Hierarchical investment type classification
- [[categorization-rule]] — Automatic categorization rules for imported transactions
- [[auth]] — Single-user authentication via Flask-Login
- [[settings]] — App settings, seed data, bank connections, database reset
- [[bank-sync]] — Bank API integration with adapter pattern (planned for removal)

## Architecture

- [[stack]] — Tech stack: Python/Flask/SQLAlchemy/PostgreSQL, Jinja2/Tailwind/Chart.js
- [[factory-pattern]] — Application factory pattern in app.py
- [[blueprint-pattern]] — One Flask Blueprint per domain
- [[database-schema]] — PostgreSQL schema, constraints, conventions
- [[design-system]] — Dark theme colors, typography, CSS components
- [[testing-strategy]] — pytest in Docker, test structure, enforcement
- [[docker-setup]] — Docker Compose services, make commands, env vars

## Decisions

- [[2026-01-15-no-spa]] — No SPA, server-side rendering only with Jinja2
- [[2026-01-15-dark-theme-only]] — Single dark theme, no light mode
- [[2026-01-15-numeric-for-money]] — Numeric(12,2) for all money fields, never Float
- [[2026-01-15-single-user]] — Single user only, no multi-tenancy

## Patterns

- [[route-handler]] — Standard Flask route handler pattern (GET/POST, try/except/rollback, PRG)
- [[model-definition]] — SQLAlchemy model conventions (imports, types, timestamps)
- [[hierarchical-data]] — Self-referential FK pattern for parent/child models
- [[adapter-registry]] — Decorator-based adapter registry for bank sync
- [[template-structure]] — Jinja2 template hierarchy and conventions
- [[test-conventions]] — Test file organization, markers, fixtures, patterns

## Bugs

## Roadmap

- [[planned-features]] — Planned features and technical debt from docs/PLAN.md

## Syntheses

## Sources
