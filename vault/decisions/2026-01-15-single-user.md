---
title: "Decision: Single User Only"
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - CLAUDE.md
---

# Single User Only

## Decision

The application is designed for **one person** tracking their own finances. No multi-user, no multi-tenancy.

## Rationale

- Personal finance tracker — one user, one database, one deployment
- Simplifies auth (no registration, no user management, no role-based access)
- No need for data isolation between users
- Admin user auto-created on first run

## Consequences

- `User` model has no relationships to transactions (no `user_id` FK on data tables)
- `require_login` middleware is a simple boolean check, not role-based
- No user registration endpoint
- No "shared budgets" or collaborative features
- Default credentials configurable via env vars (`ADMIN_USERNAME`, `ADMIN_PASSWORD`)

## Related

- [[auth]]
- [[factory-pattern]]
