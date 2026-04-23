---
title: Database Schema
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
  - models/
---

# Database Schema

PostgreSQL 15, managed via SQLAlchemy 2.0 + Alembic (Flask-Migrate).

## Tables

```
User (id, username, password_hash)

Category (id, name, parent_id FK→self)
  └→ CashflowTransaction

Tag (id, name)
  └→ cashflow_transaction_tags (M2M)
  └→ categorization_rule_tags (M2M)

CashflowTransaction (id, date, type, amount, description, category_id,
                      source, external_transaction_id, bank_connection_id)
  └→ cashflow_transaction_tags (M2M with Tag)

InvestmentType (id, name, code, icon, color, parent_id FK→self)
  └→ InvestmentTransaction

InvestmentTransaction (id, investment_type_id, transaction_date,
                        transaction_type, price, quantity, total_amount,
                        description, created_at, updated_at)

CategorizationRule (id, name, priority, is_active, field, operator, value,
                    category_id, type_override)
  └→ categorization_rule_tags (M2M with Tag)

BankConnection (id, bank_code, bank_name, client_id_encrypted,
                client_secret_encrypted, account_id, is_active,
                last_sync_*, created_at, updated_at)

Settings (id, key, value, created_at, updated_at)
```

## Key Constraints

- **Money fields:** Always `Numeric(12, 2)`, never Float
- **Quantity:** `Numeric(15, 6)` for investment quantities (fractional units)
- **Deduplication:** Unique constraint `(external_transaction_id, bank_connection_id)` on CashflowTransaction
- **Hierarchical data:** Self-referential FK via `parent_id` on Category and InvestmentType
- **M2M tables:** Composite primary keys (`cashflow_transaction_tags`, `categorization_rule_tags`)
- **Timestamps:** `lambda: datetime.now(timezone.utc)`, never `datetime.utcnow()`

## Related

- [[model-definition]]
- [[hierarchical-data]]
