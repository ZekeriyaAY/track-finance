---
title: Model Definition Pattern
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
  - models/
---

# Model Definition Pattern

Standard conventions for SQLAlchemy model definitions.

## Template

```python
from models import db  # CRITICAL: always from models, never from models.__init__
from datetime import datetime, timezone

class MyModel(db.Model):
    __tablename__ = 'my_model'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    amount = db.Column(db.Numeric(12, 2), nullable=False)  # Money: always Numeric
```

## Rules

1. **Import:** `from models import db` — never `from models.__init__ import db` (creates separate SQLAlchemy instance)
2. **Money:** `db.Numeric(12, 2)` — never `Float` for currency
3. **Timestamps:** `lambda: datetime.now(timezone.utc)` — never `datetime.utcnow()` (deprecated)
4. **PK lookup:** `db.session.get(Model, id)` — never `Model.query.get(id)` (legacy)
5. **Hierarchical data:** Self-referential FK `parent_id` — see [[hierarchical-data]]

## Related

- [[route-handler]]
- [[hierarchical-data]]
- [[database-schema]]
