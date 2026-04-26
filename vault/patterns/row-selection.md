---
title: Clickable Row Selection Pattern
created: 2026-04-26
updated: 2026-04-26
status: draft
sources:
  - raw/sessions/2ad8e597-2cdb-434c-a9cb-b6c17165c9d7.jsonl
  - commit:88624ba
---

# Clickable Row Selection Pattern

Interaction pattern for selecting multiple rows in a data table without visible checkboxes.

## Implementation

Used on the cashflow transaction list (`templates/cashflow/index.html`).

### HTML

Each row has a `data-id` attribute. No checkbox column — the entire row is the selection target.

### CSS

```css
.selectable-row {
    cursor: pointer;
}
.selectable-row.selected {
    background-color: var(--primary-muted);
    border-left: 3px solid var(--primary);
}
```

### JavaScript

- Click on a row toggles its `selected` class and tracks the ID in a Set
- Clicks on interactive elements (`a`, `button`, `form`, `select`, `input`) are excluded via `event.target.closest()`
- Bulk action bar shows/hides based on selection count
- "Select All" / "Deselect" links in the bulk bar for batch operations
- Selected IDs are collected into hidden form fields when submitting bulk actions

### Design Decisions

- **No checkboxes**: Originally implemented with hover-visible checkboxes, but user feedback confirmed that row highlighting alone is sufficient visual feedback
- **Icon removal over addition**: When faced with inconsistent UI, prefer removing excess elements over adding missing ones
- **Event delegation**: Selection logic delegates from the table body, not individual rows

## Related

- [[cashflow]]
- [[design-system]]
- [[2026-04-25-design-review-ui-improvements]]
