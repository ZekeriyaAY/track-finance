---
title: Design System
created: 2026-04-23
updated: 2026-04-26
status: draft
sources:
  - docs/DESIGN_SYSTEM.md
  - CLAUDE.md
  - static/css/style.css
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
  - raw/sessions/4fef5bde-9c63-451f-9e02-927c83d0e0af.jsonl
  - raw/sessions/2ad8e597-2cdb-434c-a9cb-b6c17165c9d7.jsonl
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
| `text-secondary` | `#b0b8c4` | Body text (~5.2:1 contrast, WCAG AA) |
| `positive` | `#6dba8a` | Income, success |
| `negative` | `#d4616e` | Expense, errors |

## Typography

Geist Sans (UI) + Geist Mono (amounts/numbers), loaded via CDN. Weights: 400, 500, 600, 700.

## Components

CSS component classes (not Tailwind utilities): `.btn-primary`, `.btn-secondary`, `.btn-ghost`, `.btn-danger`, `.card`, `.form-control`, `.table`, `.badge-*`, `.empty-state`, `.skeleton`.

## Icons

- **Lucide only** via `<i data-lucide="icon-name"></i>`
- Font Awesome CDN fully removed (~400KB dead weight, zero icons used) — commit `85ace3d`

## Layout

- Full-width content (no `max-w-7xl` constraint) — changed in commit `37b6d71`
- Sidebar navigation: collapsed 64px, expanded 240px overlay
- Spacing via Tailwind utilities
- Mobile-responsive with `md:`, `lg:` breakpoints
- Counter animations support `data-suffix` attribute for currency symbols

## Sticky Column Rule

Sticky-positioned table cells (e.g., `.col-amount`) must use explicit background colors, not `inherit`. See [[sticky-column-hover]].

## Related

- [[template-structure]]
- [[2026-01-15-no-spa]]
- [[context-processor]]
- [[toast-visibility]]
- [[sticky-column-hover]]
- [[2026-04-23-major-cleanup]]
- [[2026-04-25-bugfixes-ui-polish]]
- [[2026-04-25-design-review-ui-improvements]]
- [[row-selection]]
- [[2026-01-15-dark-theme-only]]
