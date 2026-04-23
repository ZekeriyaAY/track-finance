---
title: Remove Bank Sync & Investment Features
created: 2026-04-24
updated: 2026-04-24
status: draft
sources:
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
  - commit:10c7797
  - commit:f63aa75
  - commit:190f32e
---

# Remove Bank Sync & Investment Features

## Decision

Remove both bank sync API integration and the investment module entirely from the application.

## Context

Both features were early additions that were not actively used. The project's scope was narrowed to focus on cashflow tracking (income/expense) only.

## Details

### Bank Sync Removal
- Removed: `BankConnection` model, `utils/bank_sync/` adapter directory, bank connection management routes in settings, cashflow sync button
- **Preserved:** `utils/bank_configs.py` (Excel import bank-specific parsing configs) — these serve a different purpose (parsing uploaded Excel files, not API integration)
- Scope distinction: API-based sync was removed; file-based import was kept

### Investment Removal (Two Phases)
1. First removed only UI pages (routes, templates, sidebar links) with the idea of keeping models for potential future use
2. User decided to remove everything completely — models (`InvestmentType`, `InvestmentTransaction`), seed data, all references, Alembic migration to drop tables

### Impact
- Removed blueprints: `investment_bp`, `investment_type_bp`
- Removed from sidebar navigation
- Removed from settings page (seed data buttons, bank connections card)
- Removed Font Awesome dependency (was only used for investment type icons)
- Updated all test files to remove investment/bank fixtures and assertions

## Related

- [[cashflow]]
- [[settings]]
- [[2026-04-23-major-cleanup]]
