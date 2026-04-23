---
title: Investment Component
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - routes/investment.py
  - models/investment.py
---

# Investment Component

Tracks buy/sell investment transactions. Planned for removal from UI (see [[planned-features]]).

## Files

| Layer | File |
|-------|------|
| Route | `routes/investment.py` — Blueprint `investment_bp`, prefix `/investments` |
| Model | `models/investment.py` — `InvestmentTransaction` |
| Templates | `templates/investment/index.html`, `form.html` |

## Model: InvestmentTransaction

- **investment_type_id:** FK to `InvestmentType`
- **transaction_date:** DateTime
- **transaction_type:** `String(10)` — enum `buy` or `sell` (validated in route)
- **price:** `Numeric(12, 2)`
- **quantity:** `Numeric(15, 6)` — higher precision for fractional units (crypto, etc.)
- **total_amount:** `Numeric(12, 2)` — auto-calculated as `price * quantity` in `__init__`
- **description:** `String(255)`
- Timestamps: `created_at`, `updated_at` with `timezone.utc`

## Routes

Standard CRUD following [[route-handler]] pattern. Filters: investment_type (includes subtypes), transaction_type, date range. Type filter includes subtypes (same pattern as [[category]]).

## Key Behaviors

- `total_amount` is computed in model `__init__`, also manually set on edit route
- Investment type filter includes subtypes (same hierarchical pattern as category)
- Planned for UI removal per `docs/PLAN.md` — models and migrations will be kept

## Related

- [[investment-type]]
- [[hierarchical-data]]
- [[route-handler]]
- [[planned-features]]
