---
title: Investment Type Component
created: 2026-04-23
updated: 2026-04-24
status: archived
archived_date: 2026-04-24
sources:
  - routes/investment_type.py
  - models/investment.py
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
---

> [!info] ARCHIVED: This page was archived on 2026-04-24. The investment type feature was fully removed in commit `190f32e`. See [[2026-04-23-remove-bank-sync-investment]] for the decision context.

# Investment Type Component

Hierarchical classification for investments. Used same self-referential pattern as [[category]].

## Model: InvestmentType (Dropped)

- **name:** `String(100)`
- **code:** `String(50)`, unique
- **icon:** `String(50)` — Font Awesome class (was the only place FA icons were used)
- **color:** `String(7)` — hex color
- **parent_id:** Self-referential FK

## Related

- [[investment]]
- [[2026-04-23-remove-bank-sync-investment]]
