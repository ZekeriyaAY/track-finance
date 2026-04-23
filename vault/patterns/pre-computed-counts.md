---
title: Pre-computed Counts Pattern
created: 2026-04-24
updated: 2026-04-24
status: draft
sources:
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
  - commit:8b06969
---

# Pre-computed Counts Pattern

For index pages showing item counts (e.g., transaction counts per category/tag), compute counts via a single aggregate query in the route and pass as a dictionary to the template, instead of using model properties that trigger lazy-loaded N+1 queries.

## Problem

Model helper methods like `category.get_all_transactions_count()` executed individual queries per item, causing N+1 issues. Category index had ~142 queries, tag index ~30.

## Solution

```python
# In route — single GROUP BY query
counts = dict(
    db.session.query(
        CashflowTransaction.category_id,
        func.count(CashflowTransaction.id)
    ).group_by(CashflowTransaction.category_id).all()
)

# Pass to template
return render_template('index.html', categories=categories, counts=counts)
```

```html
<!-- In template — dictionary lookup -->
{{ counts.get(category.id, 0) }}
```

## Where Used

- `routes/category.py` — transaction counts per category (income/expense/total)
- `routes/tag.py` — transaction counts per tag
- `routes/categorization_rule.py` — eager loading for category and tags via `joinedload()`

## Complementary Techniques

- **`joinedload()`** for eager loading relationships (cashflow → category, parent, tags)
- **`EXISTS` subqueries** for delete protection checks (instead of loading full relationship)
- **Separate aggregate queries** for summary totals when using pagination

## Related

- [[cashflow]]
- [[category]]
- [[tag]]
- [[route-handler]]
- [[2026-04-23-major-cleanup]]
