---
title: Toast Notification Visibility Issue
created: 2026-04-24
updated: 2026-04-26
status: draft
sources:
  - raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
  - raw/sessions/4fef5bde-9c63-451f-9e02-927c83d0e0af.jsonl
  - commit:7394c9c
  - commit:76b69fc
---

# Toast Notification Visibility Issue

## Problem

Toast/flash notifications were nearly transparent and hard to read, especially when overlapping page buttons or other interactive elements. The low opacity made them easy to miss.

## Root Cause

Type-specific toast variants (success, danger, warning, info) had `background-color` overrides using colors at ~12% opacity. These overrides sat on top of the base `var(--bg-elevated)` background, making the combined result very faint.

## Fix

Removed the muted `background-color` overrides from type-specific variants, allowing the solid `var(--bg-elevated)` base background to show through. Also improved mobile positioning.

## Status

**Resolved** — commit `76b69fc`.

## Related

- [[cashflow]]
- [[design-system]]
- [[2026-04-23-major-cleanup]]
- [[2026-04-25-bugfixes-ui-polish]]
