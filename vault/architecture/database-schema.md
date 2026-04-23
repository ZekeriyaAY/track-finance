---
title: Database Schema
created: 2026-04-23
updated: 2026-04-24
status: draft
sources:
  - CLAUDE.md
  - models/
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
---

# Database Schema

PostgreSQL 15, managed via SQLAlchemy 2.0 + Alembic (Flask-Migrate).

## Tables

```
User (id, username, password_hash)

Category (id, name, parent_id FK→self)
  └→ CashflowTransaction
  Indexes: parent_id

Tag (id, name)
  └→ cashflow_transaction_tags (M2M)
  └→ categorization_rule_tags (M2M)

CashflowTransaction (id, date, type, amount, description, category_id, source)
  └→ cashflow_transaction_tags (M2M with Tag)
  Indexes: date, category_id, type, source

CategorizationRule (id, name, priority, is_active, field, operator, value,
                    category_id, type_override)
  └→ categorization_rule_tags (M2M with Tag)
  Indexes: is_active, priority

Settings (id, key, value, created_at, updated_at)
```

## Removed Tables

The following tables were dropped via Alembic migration (commit `190f32e`):
- `InvestmentType` — see [[investment-type]] (archived)
- `InvestmentTransaction` — see [[investment]] (archived)
- `BankConnection` — see [[2026-04-23-remove-bank-sync-investment]]

## Key Constraints

- **Money fields:** Always `Numeric(12, 2)`, never Float
- **Hierarchical data:** Self-referential FK via `parent_id` on Category
- **M2M tables:** Composite primary keys (`cashflow_transaction_tags`, `categorization_rule_tags`)
- **Timestamps:** `lambda: datetime.now(timezone.utc)`, never `datetime.utcnow()`

## Indexes

Added for query performance (commit `d5775b3`):
- `cashflow_transaction`: `date`, `category_id`, `type`, `source`
- `category`: `parent_id`
- `categorization_rule`: `is_active`, `priority`

## Related

- [[model-definition]]
- [[hierarchical-data]]
- [[pre-computed-counts]]
- [[2026-04-23-remove-bank-sync-investment]]
- [[2026-04-23-major-cleanup]]
