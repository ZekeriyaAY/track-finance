---
title: "Decision: Numeric(12,2) for Money Fields"
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
---

# Numeric(12,2) for Money Fields

## Decision

All monetary values use `db.Numeric(12, 2)`. Float is never used for currency.

## Rationale

- Floating point arithmetic causes precision loss (e.g., `0.1 + 0.2 != 0.3`)
- Financial data requires exact decimal representation
- `Numeric(12, 2)` supports values up to 9,999,999,999.99 — sufficient for personal finance

## Consequences

- Model fields: `amount = db.Column(db.Numeric(12, 2), nullable=False)`
- Python code receives `Decimal` objects from SQLAlchemy, must convert to `float` for JSON/Chart.js
- Investment quantity uses `Numeric(15, 6)` for fractional units (different precision)

## Related

- [[model-definition]]
- [[database-schema]]
