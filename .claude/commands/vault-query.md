# Query the Knowledge Vault

Answer a question using the vault knowledge base, following `vault/CLAUDE.md` QUERY workflow.

## Input

$ARGUMENTS — The question to answer.

## Workflow

1. **Read** `vault/index.md` to identify relevant categories and pages.
2. **Read** up to **10 most relevant pages** across the wiki layer (`components/`, `architecture/`, `decisions/`, `patterns/`, `bugs/`, `syntheses/`, `roadmap/`, `sources/`). If more than 10 pages seem relevant, inform the user and ask whether to continue reading more.
3. **Synthesize** an answer with **source citations** — every claim references which wiki page it comes from.
4. **File-back criteria**: Offer to file the answer as a new wiki page **only** when all three conditions are met:
   - The answer synthesizes content from **2 or more** existing wiki pages
   - The filed-back page content (not the chat answer) would be **>200 words**
   - The content is **reusable** (not a one-off clarification)
5. If filing back:
   - Create the page with proper frontmatter and `status: draft`
   - Frontmatter `sources:` lists the wiki pages synthesized (not raw sources)
   - Update `vault/index.md`
   - Append to `vault/log.md`
6. **If the wiki cannot answer the question:**
   - List which pages were searched (with paths)
   - Explicitly state what knowledge is missing
   - Suggest specific raw sources to ingest or actions to take (e.g., "Ingest session X which likely covers this topic")

## Read Scope

**Wiki layer only.** QUERY reads pages in `vault/` (components, architecture, decisions, patterns, bugs, syntheses, roadmap, sources). It does **NOT** read `raw/sessions/` JSONL files — that is INGEST's job. If relevant knowledge hasn't been ingested yet, report the gap instead of reading raw sources.

## Language

- **Respond** to the user in **Turkish** (their preferred language)
- **Wiki page names and direct quotes** from wiki pages stay in **English** — do not translate them
- Any **new wiki pages** created via file-back are written entirely in **English**

## Rules

- Follow `vault/CLAUDE.md` for page format, naming, and status conventions.
- Use `[[wikilinks]]` for inter-page links.
- `raw/` is IMMUTABLE and out of QUERY's read scope.
- Enforce bidirectional links when filing back: if the new page links to existing pages, add back-links to their `## Related` sections.
