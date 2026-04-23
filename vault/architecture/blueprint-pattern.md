---
title: Blueprint Pattern
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - app.py
  - CLAUDE.md
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
| `investment_bp` | `/investments` | `routes/investment.py` |
| `investment_type_bp` | `/investment-types` | `routes/investment_type.py` |
| `settings_bp` | `/settings` | `routes/settings.py` |
| `categorization_rule_bp` | `/rules` | `routes/categorization_rule.py` |

## Conventions

- Naming: `{feature}_bp`
- URL prefixes: kebab-case (`/investment-types`, `/categorization-rules`)
- Template subdirectory matches blueprint name: `templates/{feature}/`
- Each blueprint is self-contained — imports its own models and utils

## Related

- [[factory-pattern]]
- [[route-handler]]
