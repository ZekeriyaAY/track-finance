# CLAUDE.md — Knowledge Vault

## Purpose

Persistent knowledge archive for the **track-finance** project, following the LLM-Wiki pattern: `RAW (immutable) → WIKI (LLM writes) ← SCHEMA (this file)`.

This vault accumulates project knowledge — architecture decisions, component behavior, code patterns, bug resolutions, and development session insights — so that future sessions start with full context instead of rediscovering it.

## Relationship to Root CLAUDE.md

- **Root `../CLAUDE.md`** governs application code (routes, models, templates, tests).
- **This file** governs wiki operations inside `vault/`.
- On conflict, **root CLAUDE.md wins**. Flag the discrepancy to the user.

## Language

All wiki content in **English**. Conversations with the user may be in Turkish, but every wiki page, frontmatter field, and log entry is written in English.

## Link Format

Use **Obsidian `[[wikilinks]]`** for inter-page links:
- `[[cashflow]]` links to `components/cashflow.md`
- `[[route-handler]]` links to `patterns/route-handler.md`
- `[[2026-01-15-no-spa]]` links to `decisions/2026-01-15-no-spa.md`

## Naming Conventions

- **Page files:** `kebab-case.md` (e.g., `bank-sync.md`, `route-handler.md`)
- **Decision files:** `YYYY-MM-DD-slug.md` (e.g., `2026-01-15-no-spa.md`). Date is when the decision was made (or best estimate).
- **Source summaries:** `YYYY-MM-DD-slug.md` in `sources/sessions/`

## Status Enum

Every page has a `status` field in frontmatter:

| Status | Meaning | When to use |
|--------|---------|-------------|
| `draft` | Incomplete, may have gaps | Newly created during seed or ingest, not yet validated |
| `stable` | Current and reliable | Reviewed, source-backed, matches current code |
| `outdated` | Stale, use with caution | Code has changed but page not yet updated. Flagged by LINT |
| `archived` | No longer valid | Moved to `archive/`, kept for historical reference only |

**Transitions:**
- New page → `draft`
- `draft` → `stable`: **only** via explicit user approval, or when LINT confirms content matches current code + user approves
- LINT detects code drift → `outdated`
- Page no longer applicable → `archived` (see Archive Protocol below)

**Schema evolution note:** When status rules change, existing pages are NOT retroactively reformatted. LINT flags pages that don't conform to current rules; the user decides when to update them.

## Page Template

Every wiki page uses this structure:

```markdown
---
title: Page Title
created: 2026-04-23
updated: 2026-04-23
status: draft
sources:
  - raw/sessions/e411f033-xxx.jsonl
  - commit:5f5b800
---

# Page Title

Description of the topic.

## Key Points

- Point 1
- Point 2

## Sources (optional)

Detailed source explanations with context:
- Extracted from dashboard fix session — [[2026-04-20-dashboard-fix]]
- Related commit: `5f5b800` — fix(dashboard): fix date preset highlight

## Related

- [[cashflow]]
- [[route-handler]]
```

## Source Referencing Rules

| Where | What to write | Example |
|-------|--------------|---------|
| **Frontmatter `sources:`** | Short file path or commit hash | `raw/sessions/xxx.jsonl`, `commit:abc1234` |
| **Inline in text** | Claim + source wikilink | `...this decision was made — [[2026-04-20-dashboard-fix]]` |
| **`## Sources` section** | Detailed explanation + context | `- In session X, topic Y was discussed, Z was decided` |

**Rules:**
- Frontmatter `sources:` is **always** populated (for mechanical tracking).
- `## Sources` section is **optional** — include it only when claims need detailed context beyond what inline references provide. Omit for straightforward pages where frontmatter + inline refs are sufficient.
- Inline references support specific claims within the text body.

**Special cases:**
- **Synthesis pages** (`syntheses/`): Frontmatter `sources:` lists the wiki pages that were synthesized, not raw sources. The synthesized pages themselves trace back to raw sources.
- **Seed pages** (created during initial vault setup): Frontmatter `sources:` references the project file(s) the content was extracted from (e.g., `CLAUDE.md`, `routes/cashflow.py`).

## Folder Structure & Decision Tree

```
vault/
├── raw/sessions/     — IMMUTABLE JSONL transcripts (agent reads, NEVER writes)
├── sources/sessions/ — One summary page per raw source
├── components/       — One page per application component
├── architecture/     — System-level architectural knowledge
├── decisions/        — ADR-style decision records (one decision = one page)
├── patterns/         — Recurring code patterns and conventions
├── bugs/             — Bug reports, debugging sessions, resolutions
├── roadmap/          — Future plans, feature analysis
├── syntheses/        — High-level cross-cutting analyses
└── archive/          — Retired pages (never deleted, moved here)
```

### Where does a piece of knowledge go?

```
Knowledge arrives
│
├─ Belongs to a specific route/model/template group?
│  └─ YES → components/     (e.g., "cashflow import also works with CSV")
│
├─ Cross-cutting system decision spanning multiple components?
│  └─ YES → architecture/   (e.g., "why PostgreSQL", "Docker compose layout")
│
├─ Recurring code writing pattern?
│  └─ YES → patterns/       (e.g., "POST handler try/except/rollback pattern")
│
├─ A choice was made with rationale?
│  └─ YES → decisions/      (e.g., "why no SPA", "why dark-only theme")
│
├─ A bug was found and fixed?
│  └─ YES → bugs/           (e.g., "Turkish uppercase I issue")
│
├─ Future work item?
│  └─ YES → roadmap/
│
└─ High-level analysis synthesizing multiple sources?
   └─ YES → syntheses/
```

## Hard Rules

1. **`raw/` is IMMUTABLE.** Agent reads only, never writes or modifies. Only the user or SessionEnd hook adds files.
2. **Every claim must cite its source.** No unsourced assertions. Use frontmatter `sources:` and inline references.
3. **Contradictions are flagged, never silently resolved.** Use Obsidian callout: `> [!warning] CONTRADICTION: Source A says X, but Source B says Y.` INGEST must not silently pick one side — it flags. LINT surfaces unresolved contradictions. The user decides which is correct.
4. **Bidirectional linking is enforced during INGEST and QUERY.** When adding `[[wikilink]]` to page A pointing to B, automatically check B's `## Related` section and add `[[A]]` back-link if missing.
5. **Pages are never deleted.** Use the Archive Protocol (below) to retire pages.
6. **Every operation is logged.** INGEST, QUERY (when filed back), and LINT passes go to `log.md`.
7. **Schema co-evolves.** If a rule doesn't work, update this file. Changes apply from the next session onward. Existing pages are NOT retroactively reformatted — LINT flags non-conforming pages for the user to update incrementally.

## Archive Protocol

When a page is no longer valid or relevant:

1. **Update frontmatter:** Set `status: archived` and add `archived_date: YYYY-MM-DD`.
2. **Add redirect note** at the top of the page body: `> [!info] ARCHIVED: This page was archived on YYYY-MM-DD. See [[replacement-page]] for current information.` (omit replacement link if none exists).
3. **Move** the file from its current folder to `archive/` (preserving the filename).
4. **Update `index.md`:** Remove the page from its category section. Optionally add to an "Archived" section if the page had significant historical value.
5. **Do NOT update back-links** in other pages — they will naturally point to `archive/page-name` and LINT will flag them as needing review.

**Note on wikilinks and archive:** Obsidian wikilinks resolve by filename regardless of folder. Moving a page to `archive/` does NOT break links — it just makes them point to an archived target. LINT distinguishes these two cases: `broken-wikilink` (target does not exist at all, high priority) vs `archived-target` (target exists in `archive/`, info-level priority).

## Operations

> These workflows are invoked via `/vault-ingest`, `/vault-query`, and `/vault-lint` slash commands.

### INGEST — Process a new raw source

When a new JSONL transcript or other raw source arrives:

1. **Read** the raw source. Extract: main topic, key findings, entities mentioned (files, models, routes), concepts, decisions, bugs fixed.

2. **Value check** (step 1.5): If the session has fewer than 10 meaningful exchanges (user↔assistant turns with substantive content — not confirmations, single-word answers, or trivial formatting fixes), ask the user: *"This session appears low-value (N exchanges, topic: X). Skip?"* If user skips, mark as `"skipped"` in queue/manifest and move on.

3. **Show** a 5-point summary to the user and wait for approval before writing. Each session gets its own individual approval — no batch approval.

4. **Create** a source summary page in `sources/sessions/YYYY-MM-DD-slug.md` with frontmatter + sections (Goal, What was done, Key points, Decisions, Open threads, Sources, Related).

5. **Update** affected pages — target folders include:
   - `components/` — component-specific knowledge
   - `architecture/` — system-level insights
   - `decisions/` — architectural decisions found
   - `bugs/` — bugs investigated or fixed
   - `patterns/` — new or modified code patterns
   - `roadmap/` — future work items identified

6. **Enforce bidirectional links**: When adding a `[[wikilink]]` to any page, check the target page's `## Related` section and add a back-link if missing.

7. **Update** `index.md` with any new pages.

8. **Append** to `log.md`: `## [YYYY-MM-DD] ingest | slug` with list of pages touched.

9. **Idempotency**: Before processing any session, check `vault/.ingested-manifest.json`. If the session_id already exists, skip (do not re-process or create duplicate entries). After successful processing, add/update the manifest entry. Queue entry status is set to `"done"`. Re-running INGEST on the same session is always safe — it either skips or updates existing entries, never duplicates.

### QUERY — Answer a question from the wiki

**Read scope:** QUERY reads only the wiki layer (`components/`, `architecture/`, `decisions/`, `patterns/`, `bugs/`, `syntheses/`, `roadmap/`, `sources/`). It does **NOT** read `raw/sessions/` JSONL files — that is INGEST's job. If relevant knowledge hasn't been ingested yet, report the gap.

1. **Read** `index.md` to identify relevant categories.
2. **Find and read** up to 10 most relevant pages. If more seem relevant, inform the user before reading further.
3. **Synthesize** an answer with source citations — every claim references which wiki page it comes from.
4. **File back** only when all three criteria are met: synthesizes 2+ existing pages, the filed-back page content (not the chat answer) would be >200 words, and is reusable (not a one-off clarification). When filing back, frontmatter `sources:` lists the synthesized wiki pages.
5. **Enforce bidirectional links** when filing back.
6. **If the wiki cannot answer:** List searched pages (with paths), state explicitly what knowledge is missing, suggest specific raw sources to ingest.
7. **Log** to `log.md`: `## [YYYY-MM-DD] query | "short question"` with filed-back page if any.

### LINT — Periodic health check

Scan all markdown files (excluding `raw/`) for:

1. **Contradictions** — Two pages making opposing claims about the same topic.
2. **Stale claims** — Component pages whose `updated` date is older than recent code changes. Check: `git log --since="<page.updated>" -- <source-file>`. If commits exist, the page is stale.
3. **Orphan pages** — Pages not linked from `index.md` or any other page.
4. **Missing concept pages** — Terms mentioned in 3+ pages but lacking their own page.
5. **One-way cross-references** — Page A links to B, but B doesn't link back to A.
6. **Weak sources** — Important pages relying on a single raw source.
7. **Drift from root CLAUDE.md** — Vault claims that conflict with current root CLAUDE.md conventions.
8. **Broken wikilinks** — `[[wikilinks]]` pointing to pages that do not exist anywhere in the vault (not even in `archive/`). **Priority: high.**
9. **Archived-target links** — `[[wikilinks]]` that resolve to a page in `archive/`. These are not broken (Obsidian resolves by filename regardless of folder) but signal that the linking page may need updating. **Priority: info.**
10. **Stale status** — Pages stuck in transitional states: `draft` for >60 days, `outdated` for >30 days without update or archive.

Output to `vault/lint-report.md` (**overwritten** each run, not appended — each lint is a fresh snapshot). Each finding: category, affected file(s), suggested fix, priority (high/medium/low). **Do NOT auto-fix.** Report only.

Log to `log.md`: `## [YYYY-MM-DD] lint | N findings (H:x M:y L:z)`

## log.md Format

```markdown
## [2026-04-23] seed | Initial vault setup
- Created 9 component pages
- Created 6 pattern pages
- Created 4 decision pages
- Updated index.md

## [2026-04-24] ingest | session-e411f033
- Source: raw/sessions/e411f033-xxx.jsonl
- Created: sources/sessions/2026-04-23-vault-setup.md
- Updated: [[cashflow]], [[route-handler]]
- New decision: [[2026-04-23-obsidian-wikilinks]]

## [2026-04-25] query | "How does bank sync work?"
- Filed back: syntheses/bank-sync-flow.md
- Referenced: [[bank-sync]], [[adapter-registry]]

## [2026-04-27] lint | 5 findings (H:1 M:2 L:2)
- 1 outdated: components/cashflow.md (route changed since last update)
- 2 orphan: bugs/date-format.md, decisions/2026-04-20-csv-encoding.md
- 2 missing cross-ref: investment <-> investment-type
```
