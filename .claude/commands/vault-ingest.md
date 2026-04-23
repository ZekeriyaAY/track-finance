# Ingest Raw Source into Knowledge Vault

Process a raw source into the vault knowledge base following `vault/CLAUDE.md` INGEST workflow.

## Input

$ARGUMENTS — One of:
- *(empty or `queue`)* — **default**: process pending items from `vault/.ingest-queue.jsonl`, oldest-first, max 3 per run. If more remain, tell the user to run `/vault-ingest` again.
- `latest` — process the most recently modified file in `vault/raw/sessions/`
- A specific path to a raw source file (e.g., `vault/raw/sessions/abc123/abc123.jsonl`)

## Workflow

1. **Identify** the raw source(s) to process. For `queue` mode: read `vault/.ingest-queue.jsonl`, filter to `status: "pending"`, take the **oldest 3** (batch limit). If zero pending, inform user and stop.

2. **For each session (one at a time, individual approval):**

   a. **Idempotency check**: Before processing, check `vault/.ingested-manifest.json`. If the session_id already exists, skip it and mark the queue entry as `"done"` (no duplicate writes).

   b. **Read** the raw source. For JSONL session transcripts, parse message types (user prompts, assistant responses, tool calls, errors) to extract:
      - Main topic / goal of the session
      - What was built, fixed, or changed
      - Files modified (routes, models, templates, utils)
      - Architectural decisions made
      - Bugs found and resolved
      - New patterns established or existing ones modified

   c. **Value check**: If the session has fewer than 10 meaningful exchanges (user↔assistant turns with substantive content — not just confirmations, single-word answers, or trivial formatting fixes), ask the user: *"This session appears low-value (N exchanges, topic: X). Skip?"* If user says yes, mark as `"skipped"` in queue and move to next session.

   d. **Show** a 5-point summary to the user and **wait for approval** before writing any wiki pages. Each session gets its own approval — no batch approval.

   e. After approval, execute the INGEST steps from `vault/CLAUDE.md`:
      - Create source summary in `vault/sources/sessions/`
      - Update affected pages in `vault/components/`
      - Create/update pages in `vault/architecture/`
      - Create/update pages in `vault/decisions/`
      - Create/update pages in `vault/bugs/`
      - Create/update pages in `vault/patterns/`
      - Create/update pages in `vault/roadmap/`
      - Update `vault/index.md`
      - Append to `vault/log.md`
      - **Enforce bidirectional links**: when adding a `[[wikilink]]` to any page, check the target page's `## Related` section and add a back-link if missing.

   f. **Update tracking** (idempotent): Set queue entry status to `"done"` and add/update entry in `vault/.ingested-manifest.json`. If entry already exists in manifest, update it rather than adding a duplicate.

3. **Report** per session: pages created, pages updated, cross-references established.

4. If queue has remaining pending items after the batch of 3, tell the user: *"N sessions remaining in queue. Run `/vault-ingest` again to continue."*

## Rules

- Follow `vault/CLAUDE.md` for page format, naming, and status conventions.
- All content in English.
- Use `[[wikilinks]]` for inter-page links.
- `raw/` is IMMUTABLE — read only, never write.
- Every claim must cite its source.
- New pages start with `status: draft`.
- Manifest and queue updates are idempotent — re-running on the same session must not create duplicate entries.
