---
title: Categorization Rule Component
created: 2026-04-23
updated: 2026-04-24
status: draft
sources:
  - routes/categorization_rule.py
  - models/categorization_rule.py
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
---

# Categorization Rule Component

Automatic categorization rules for imported transactions. Rules match transaction descriptions and assign a category, tags, and optional type override.

## Files

| Layer | File |
|-------|------|
| Route | `routes/categorization_rule.py` — Blueprint `categorization_rule_bp`, prefix `/rules` |
| Model | `models/categorization_rule.py` — `CategorizationRule` + `categorization_rule_tags` M2M table |
| Templates | `templates/categorization_rule/index.html`, `form.html` |

## Model: CategorizationRule

- **name:** `String(100)`, display name
- **priority:** `Integer` — lower = higher priority. First match wins during import
- **is_active:** `Boolean`
- **field:** `String(20)`, always `description` currently
- **operator:** `String(20)` — one of: `contains`, `equals`, `starts_with`, `ends_with`
- **value:** `String(255)` — normalized at save time via `normalize()` method
- **category_id:** FK to `Category` — target category for matched transactions
- **type_override:** `String(10)`, nullable — override transaction type to `income` or `expense`
- **tags:** M2M with `Tag` via `categorization_rule_tags`

### Turkish Text Normalization

`normalize()` static method handles Turkish I variants: maps `İ`, `ı`, `I` all to `i` before lowercasing. This ensures `MIGROS`, `Migros`, `MİGROS` all match consistently.

### Match Logic

`matches(description)` normalizes input, then applies the operator against the stored (pre-normalized) value.

## Routes

Standard CRUD + priority reorder endpoint.

### `POST /rules/reorder`
JSON endpoint for drag-and-drop reordering. Receives `rule_ids[]` array, sets `priority = index` for each.

## Key Behaviors

- Rules are applied during Excel import in [[cashflow]] — first match by priority wins
- New rules get `priority = max + 1` (appended to end)
- Operator validation against `VALID_OPERATORS` constant
- No delete protection — rules can be freely deleted

## Performance

Index page uses `joinedload()` for category and tags to avoid N+1 queries — see [[pre-computed-counts]].

## Related

- [[cashflow]]
- [[category]]
- [[tag]]
- [[route-handler]]
- [[pre-computed-counts]]
- [[2026-04-23-major-cleanup]]
