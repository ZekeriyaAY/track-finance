---
title: Investment Type Component
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - routes/investment_type.py
  - models/investment.py
---

# Investment Type Component

Hierarchical classification for investments (e.g., Stock > BIST, Crypto > Bitcoin). Uses same self-referential pattern as [[category]].

## Files

| Layer | File |
|-------|------|
| Route | `routes/investment_type.py` — Blueprint `investment_type_bp`, prefix `/investment-types` |
| Model | `models/investment.py` — `InvestmentType` (shares file with `InvestmentTransaction`) |
| Templates | `templates/investment_type/index.html`, `form.html` |

## Model: InvestmentType

- **name:** `String(100)`, not null
- **code:** `String(50)`, unique — internal identifier (e.g., `stock`, `crypto`)
- **icon:** `String(50)`, default `fas fa-chart-pie` — Font Awesome class (legacy, only place FA icons are used)
- **color:** `String(7)`, default `#3B82F6` — hex color for UI
- **parent_id:** Self-referential FK (same pattern as [[category]])
- Timestamps: `created_at`, `updated_at`

## Delete Protection

Two checks: has children → block; has investments → block.

## Related

- [[investment]]
- [[hierarchical-data]]
- [[route-handler]]
- [[planned-features]]
