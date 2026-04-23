---
title: Context Processor Pattern
created: 2026-04-24
updated: 2026-04-24
status: draft
sources:
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
  - commit:45dc913
---

# Context Processor Pattern

Use Flask's `app.context_processor` to inject global settings into all Jinja2 templates, avoiding repetitive per-route lookups.

## Implementation

In `app.py` inside `create_app()`:

```python
@app.context_processor
def inject_global_settings():
    from models.settings import Settings
    return {
        'currency_symbol': Settings.get_setting('currency_symbol', '₺'),
        'pgadmin_url': Settings.get_setting('pgadmin_url', '')
    }
```

## Where Used

- **`currency_symbol`** — injected globally, used in dashboard KPIs, cashflow index amounts, counter animations (`data-suffix`), and summary bars
- **`pgadmin_url`** — injected globally for sidebar link

## Key Points

- Settings are fetched per request (simple key-value lookup, negligible cost)
- Templates access `{{ currency_symbol }}` directly without route passing it
- Counter animation JS reads `data-suffix` attribute for appending currency after animated numbers

## Related

- [[settings]]
- [[cashflow]]
- [[design-system]]
- [[2026-04-23-major-cleanup]]
