---
title: Tag Component
created: 2026-04-23
updated: 2026-04-24
status: draft
sources:
  - routes/tag.py
  - models/tag.py
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
---

# Tag Component

Flat (non-hierarchical) labels for cross-cutting transaction classification. M2M relationship with cashflow transactions.

## Files

| Layer | File |
|-------|------|
| Route | `routes/tag.py` — Blueprint `tag_bp`, prefix `/tags` |
| Model | `models/tag.py` — `Tag` |
| Templates | `templates/tag/index.html`, `form.html` |

## Model: Tag

- **name:** `String(50)`, unique, not null
- **transactions:** M2M with `CashflowTransaction` via `cashflow_transaction_tags` (defined in `models/cashflow.py`)
- Also back-referenced from `CategorizationRule` via `categorization_rule_tags`

## Routes

Standard CRUD following [[route-handler]] pattern.

### Delete Protection

Blocks deletion using `EXISTS` subquery (not full relationship loading) if tag has associated transactions.

### Duplicate Prevention

On add/edit: checks `Tag.query.filter_by(name=name)` — unique name enforced.

## Key Behaviors

- Tags are flat — no hierarchy, unlike [[category]]
- Used in multi-select on cashflow transaction forms
- Auto-created during Excel import (bank name becomes a tag)
- Applied via categorization rules during import
- Transaction counts pre-computed via GROUP BY in route — see [[pre-computed-counts]]

## Related

- [[cashflow]]
- [[categorization-rule]]
- [[route-handler]]
- [[pre-computed-counts]]
- [[2026-04-23-major-cleanup]]
