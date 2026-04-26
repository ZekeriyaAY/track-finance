---
title: Sticky Column Hover Delay
created: 2026-04-26
updated: 2026-04-26
status: draft
sources:
  - raw/sessions/4fef5bde-9c63-451f-9e02-927c83d0e0af.jsonl
  - commit:bd53322
---

# Sticky Column Hover Delay

## Problem

The `.col-amount` cell in the cashflow transactions table had a visible hover delay — a double-layer transition artifact. When hovering over a row, the amount column would visually lag behind other cells.

## Root Cause

The sticky-positioned `.col-amount` cell had `background-color: inherit`, which resolved to `transparent`. Because the cell was overlaid on the row (due to `position: sticky`), hover transitions showed through both layers — the row background transitioning underneath, and the cell's own transparent background on top.

## Fix

In `static/css/style.css`:
- Changed `.col-amount` background from `inherit` to explicit `var(--bg-surface)`
- Added `transition` property matching the parent row's transition timing

## Rule

Always use explicit background colors (not `inherit` or `transparent`) on sticky-positioned table cells. The sticky element sits in its own stacking context and `inherit` resolves to transparent, creating double-layer rendering.

## Status

**Resolved** — commit `bd53322`.

## Related

- [[cashflow]]
- [[design-system]]
- [[2026-04-25-bugfixes-ui-polish]]
