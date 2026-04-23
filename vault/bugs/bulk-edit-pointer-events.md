---
title: Bulk Edit Bar Blocking Pagination Clicks
created: 2026-04-24
updated: 2026-04-24
status: draft
sources:
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
  - commit:44561ab
---

# Bulk Edit Bar Blocking Pagination Clicks

## Problem

The bulk edit floating bar in cashflow index had `pointer-events-auto` permanently set. When hidden (opacity-0, no checkboxes selected), it still intercepted mouse clicks on the pagination controls below it, making pagination unclickable.

## Root Cause

The bar used CSS opacity transition for show/hide but retained pointer events in both states.

## Fix

Toggle `pointer-events-none` / `pointer-events-auto` via JavaScript based on checkbox selection state:
- No checkboxes selected → `pointer-events-none` (bar is transparent and click-through)
- Checkboxes selected → `pointer-events-auto` (bar is visible and interactive)

## Status

**Resolved** — commit `44561ab`.

## Related

- [[cashflow]]
- [[pagination]]
- [[2026-04-23-major-cleanup]]
