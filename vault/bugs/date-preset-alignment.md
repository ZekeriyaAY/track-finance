---
title: Dashboard Date Preset Alignment
created: 2026-04-26
updated: 2026-04-26
status: draft
sources:
  - raw/sessions/4fef5bde-9c63-451f-9e02-927c83d0e0af.jsonl
  - commit:38ff7e2
---

# Dashboard Date Preset Alignment

## Problem

Month-based dashboard filter presets (3 Months, 6 Months, 1 Year) produced incorrect chart data — the first month in the range was always partial.

## Root Cause

JavaScript `setDatePreset()` function used `today.getDate()` (e.g., day 25) when calculating the start date for month-based ranges. This meant a "3 Months" preset starting on April 25 would query from January 25, missing 24 days of January data.

The same issue existed in the backend: `default_monthly_from` in `routes/cashflow.py` also used the current day-of-month.

The `highlightActivePreset()` function had the same logic, so preset buttons wouldn't highlight correctly even if the URL was manually corrected.

## Fix

- Frontend JS: All month-based presets now use day 1 when computing start dates
- Frontend JS: `highlightActivePreset()` comparison uses day 1 to match
- Backend Python: `default_monthly_from` uses `.replace(day=1)` to align to month boundaries

Both frontend and backend must stay in sync on this rule.

## Rule

All time-based filter presets that compute month offsets must use day 1 to align with calendar month boundaries.

## Status

**Resolved** — commit `38ff7e2`.

## Related

- [[cashflow]]
- [[2026-04-25-bugfixes-ui-polish]]
