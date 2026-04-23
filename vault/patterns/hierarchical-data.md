---
title: Hierarchical Data Pattern
created: 2026-04-23
updated: 2026-04-24
status: draft
sources:
  - models/category.py
  - CLAUDE.md
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
---

# Hierarchical Data Pattern

Self-referential FK pattern used for parent/child relationships within the same model.

## Implementation

```python
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    subcategories = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))
```

## Used By

- **Category** — `parent_id → category.id`, relationship: `subcategories` / `parent`

> Previously also used by **InvestmentType**, which was fully removed — see [[2026-04-23-remove-bank-sync-investment]].

## Query Patterns

### List root items only
```python
Category.query.filter_by(parent_id=None).all()
```

### Include children in filter
```python
category_ids = [parent.id] + [c.id for c in parent.subcategories]
query.filter(Model.category_id.in_(category_ids))
```

### Delete protection
Check for children AND transactions before allowing deletion.

## Key Behaviors

- `parent_id=None` means root/parent category
- Filters throughout the app include subcategories when parent is selected
- Dashboard charts aggregate child totals under parent
- Forms provide parent dropdown for hierarchy assignment

## Related

- [[category]]
- [[model-definition]]
- [[database-schema]]
- [[2026-04-23-remove-bank-sync-investment]]
