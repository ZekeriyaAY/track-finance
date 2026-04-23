---
title: Investment Component
created: 2026-04-23
updated: 2026-04-24
status: archived
archived_date: 2026-04-24
sources:
  - routes/investment.py
  - models/investment.py
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
---

> [!info] ARCHIVED: This page was archived on 2026-04-24. The investment feature was fully removed (models, routes, templates, migrations) in commit `190f32e`. See [[2026-04-23-remove-bank-sync-investment]] for the decision context.

# Investment Component

Tracked buy/sell investment transactions.

## Files (Removed)

| Layer | File |
|-------|------|
| Route | `routes/investment.py` — Blueprint `investment_bp`, prefix `/investments` |
| Model | `models/investment.py` — `InvestmentTransaction` |
| Templates | `templates/investment/index.html`, `form.html` |

## Model: InvestmentTransaction (Dropped)

- **investment_type_id:** FK to `InvestmentType`
- **transaction_date:** DateTime
- **transaction_type:** `String(10)` — enum `buy` or `sell`
- **price:** `Numeric(12, 2)`
- **quantity:** `Numeric(15, 6)` — higher precision for fractional units
- **total_amount:** `Numeric(12, 2)` — auto-calculated as `price * quantity`
- **description:** `String(255)`

## Related

- [[investment-type]]
- [[2026-04-23-remove-bank-sync-investment]]
