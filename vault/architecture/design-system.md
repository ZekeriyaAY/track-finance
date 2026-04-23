---
title: Design System
created: 2026-04-23
updated: 2026-04-24
status: draft
sources:
  - docs/DESIGN_SYSTEM.md
  - CLAUDE.md
  - static/css/style.css
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
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
- Font Awesome dependency removed (was only used for investment type icons, now archived)

## Layout

- Full-width content (no `max-w-7xl` constraint) — changed in commit `37b6d71`
- Sidebar navigation: collapsed 64px, expanded 240px overlay
- Spacing via Tailwind utilities
- Mobile-responsive with `md:`, `lg:` breakpoints
- Counter animations support `data-suffix` attribute for currency symbols

## Known Issues

- Toast notifications are nearly transparent and hard to read — [[toast-visibility]]

## Related

- [[template-structure]]
- [[2026-01-15-no-spa]]
- [[context-processor]]
- [[toast-visibility]]
- [[2026-04-23-major-cleanup]]
