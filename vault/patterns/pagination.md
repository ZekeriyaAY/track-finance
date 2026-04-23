---
title: Pagination Pattern
created: 2026-04-24
updated: 2026-04-24
status: draft
sources:
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
  - commit:415b262
  - commit:d175a0b
---

# Pagination Pattern

Server-side pagination for list views using SQLAlchemy's `.paginate()`.

## Implementation

```python
page = request.args.get('page', 1, type=int)
pagination = query.paginate(page=page, per_page=25, error_out=False)
transactions = pagination.items

# Summary totals from full filtered query (not just current page)
total_income = filtered_query.filter_by(type='income').with_entities(func.sum(...)).scalar()
```

## UI Pattern

Single merged footer row with three sections:
- **Left:** Total count ("N transactions")
- **Center:** Page navigation buttons (prev / page numbers / next)
- **Right:** Summary totals (income / expense / net)

## Key Points

- `error_out=False` prevents 404 on out-of-range pages
- Summary totals are computed from the full filtered query, not just the current page
- Filter parameters are preserved in pagination links
- Per-page count: 25 (hardcoded, not user-configurable)
- Bulk edit floating bar uses `pointer-events-none` when hidden to avoid blocking pagination clicks — [[bulk-edit-pointer-events]]

## Related

- [[cashflow]]
- [[route-handler]]
- [[bulk-edit-pointer-events]]
- [[2026-04-23-major-cleanup]]
