---
title: "Decision: Dark Theme Only"
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
---

# Dark Theme Only

## Decision

The application uses a **single dark theme**. No light mode, no theme switching.

## Rationale

- Single-user app — no need to accommodate different user preferences
- Reduces CSS complexity (no theme tokens to duplicate)
- Design system colors are optimized for dark backgrounds
- Consistent visual identity

## Consequences

- All CSS uses dark-themed color tokens (`bg-base: #0d1117`, `bg-surface: #161b22`, etc.)
- No CSS media query for `prefers-color-scheme`
- No theme toggle in UI
- `docs/DESIGN_SYSTEM.md` documents only dark theme values

## Related

- [[design-system]]
- [[2026-01-15-no-spa]]
