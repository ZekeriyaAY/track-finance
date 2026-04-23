---
title: Design System
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - docs/DESIGN_SYSTEM.md
  - CLAUDE.md
  - static/css/style.css
---

# Design System

Dark theme only, no light mode. Defined in `static/css/style.css` and `docs/DESIGN_SYSTEM.md`.

## Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#e5884a` | Buttons, links, active states (warm amber) |
| `bg-base` | `#0d1117` | Page background |
| `bg-surface` | `#161b22` | Card/container background |
| `bg-elevated` | `#1c2128` | Modal, dropdown, popover |
| `positive` | `#6dba8a` | Income, success |
| `negative` | `#d4616e` | Expense, errors |

## Typography

Geist Sans (UI) + Geist Mono (amounts/numbers), loaded via CDN. Weights: 400, 500, 600, 700.

## Components

CSS component classes (not Tailwind utilities): `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-danger`, `.card`, `.form-control`, `.table`, `.badge-*`, `.empty-state`, `.skeleton`.

## Icons

- **Primary:** Lucide Icons via `<i data-lucide="icon-name"></i>`
- **Legacy:** Font Awesome only for `InvestmentType` custom icons

## Layout

- Sidebar navigation: collapsed 64px, expanded 240px overlay
- Spacing via Tailwind utilities
- Mobile-responsive with `md:`, `lg:` breakpoints

## Related

- [[template-structure]]
- [[2026-01-15-no-spa]]
