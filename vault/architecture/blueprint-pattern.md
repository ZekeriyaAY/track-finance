---
title: Blueprint Pattern
created: 2026-04-23
updated: 2026-04-24
status: draft
sources:
  - app.py
  - CLAUDE.md
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
---

# Blueprint Pattern

One Flask Blueprint per domain, registered in `create_app()`.

## Registered Blueprints

| Blueprint | Prefix | File |
|-----------|--------|------|
| `auth_bp` | `/auth` | `routes/auth.py` |
| `cashflow_bp` | `/cashflow` | `routes/cashflow.py` |
| `category_bp` | `/categories` | `routes/category.py` |
| `tag_bp` | `/tags` | `routes/tag.py` |
| `settings_bp` | `/settings` | `routes/settings.py` |
| `categorization_rule_bp` | `/rules` | `routes/categorization_rule.py` |

### Removed Blueprints

The following were removed in commit `f63aa75` / `190f32e` — see [[2026-04-23-remove-bank-sync-investment]]:
- `investment_bp` (`/investments`)
- `investment_type_bp` (`/investment-types`)

## Conventions

- Naming: `{feature}_bp`
- URL prefixes: kebab-case (`/categorization-rules`)
- Template subdirectory matches blueprint name: `templates/{feature}/`
- Each blueprint is self-contained — imports its own models and utils

## Related

- [[factory-pattern]]
- [[route-handler]]
- [[2026-04-23-remove-bank-sync-investment]]
- [[2026-04-23-major-cleanup]]
