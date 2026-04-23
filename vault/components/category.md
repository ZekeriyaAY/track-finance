---
title: Category Component
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - routes/category.py
  - models/category.py
---

# Category Component

Hierarchical transaction categories with parent/child relationships. Used to classify cashflow transactions.

## Files

| Layer | File |
|-------|------|
| Route | `routes/category.py` — Blueprint `category_bp`, prefix `/categories` |
| Model | `models/category.py` — `Category` |
| Templates | `templates/category/index.html`, `form.html` |

## Model: Category

- **name:** `String(100)`, not null
- **parent_id:** Self-referential FK to `category.id` (nullable — null means root/parent)
- **subcategories:** `db.relationship` with `backref('parent')` via `remote_side=[id]`
- **transactions:** Relationship to `CashflowTransaction`

Helper methods:
- `get_all_transactions_count()`, `get_income_count()`, `get_expense_count()` — recursive, counts through subcategories (note: N+1 query issue, see [[planned-features]])
- `is_parent()` / `is_subcategory()` — check `parent_id`

## Routes

Standard CRUD following [[route-handler]] pattern.

### Delete Protection

Two checks before deletion:
1. **Has subcategories** → block with "delete them first"
2. **Has transactions** → block with "cannot be deleted"

### Duplicate Prevention

On add/edit: checks `Category.query.filter_by(name=name, parent_id=parent_id)` — same name under same parent is rejected.

## Key Behaviors

- List view shows only root categories (`parent_id=None`), subcategories nested underneath
- Form provides parent category dropdown (only root categories)
- Cashflow filters include subcategories when parent is selected (handled in [[cashflow]])
- Dashboard aggregates child category totals under parent for charts

## Related

- [[cashflow]]
- [[hierarchical-data]]
- [[categorization-rule]]
- [[route-handler]]
