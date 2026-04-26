---
title: Design Review & UI Improvements Session
created: 2026-04-26
updated: 2026-04-26
status: draft
sources:
  - raw/sessions/2ad8e597-2cdb-434c-a9cb-b6c17165c9d7.jsonl
---

# Design Review & UI Improvements Session

Session on 2026-04-25. Started with a multi-persona design council review (`/council` with Dieter Rams, Linus Torvalds, Alan Watts), then implemented the council's recommendations.

## Goal

Evaluate whether the application's design is professional enough, then implement actionable improvements from the council's feedback.

## What Was Done

### Council Verdict

The council concluded the design system is already professional and internally consistent. The warm amber palette, dark theme, semantic coloring, and CSS token system are intentional and effective. Comparing to commercial SaaS products (Revolut, Mercury) is the wrong benchmark for a self-hosted single-user tool.

### Implemented Improvements (5 tasks)

1. **Removed Font Awesome CDN** — ~400KB dead weight, zero icons actually used (Lucide is the sole icon library). Removed from `base_layout.html`.

2. **Improved secondary text contrast** — Changed `--text-secondary` from `#9ca3af` to `#b0b8c4` across CSS, Tailwind config, and hardcoded template values. Improved contrast ratio from ~4.1:1 to ~5.2:1 (WCAG AA compliant).

3. **Promoted Filter button to `btn-primary`** — On both transaction list and dashboard pages, the Filter button was `btn-secondary` despite being the primary action. Changed to `btn-primary`.

4. **Removed inconsistent date preset icons** — Dashboard had calendar icons on some preset buttons but not others. All calendar icons removed for consistency (removal over addition).

5. **Replaced checkboxes with clickable row selection** — Transaction table rows are now selectable by clicking anywhere on the row. Visual feedback: `primary-muted` background + left orange border. Bulk bar gets "Select All" / "Deselect" links. Clicks on interactive elements (links, buttons, forms) don't trigger selection. — [[row-selection]]

### Skipped

- **Dashboard chart count reduction** (council recommended evaluating 5→3 charts) — user explicitly skipped

## Files Modified

- `templates/base_layout.html` — Font Awesome CDN removed, Tailwind `secondary` color updated
- `templates/base.html` — Hardcoded `#9ca3af` → `#b0b8c4`
- `templates/cashflow/index.html` — Filter button, checkbox column removed, row-click selection JS
- `templates/cashflow/dashboard.html` — Filter button, calendar icons removed
- `static/css/style.css` — `--text-secondary` updated, `.selectable-row` styles added, `.row-select` styles removed
- `CLAUDE.md` — `text-secondary` color updated
- `docs/DESIGN_SYSTEM.md` — `text-secondary` color updated

## Commits

- `85ace3d` — fix: improve UI polish — remove Font Awesome, fix contrast, button hierarchy, icon consistency
- `88624ba` — refactor: replace transaction checkboxes with clickable row selection

## Related

- [[cashflow]]
- [[design-system]]
- [[template-structure]]
- [[row-selection]]
- [[2026-01-15-dark-theme-only]]
