# Lint the Knowledge Vault

Run a periodic health check on the vault, following `vault/CLAUDE.md` LINT workflow.

## Workflow

Scan all markdown files in `vault/` (excluding `raw/`) for:

1. **Contradictions** — Two pages making opposing claims about the same topic.
   - *Fix template:* `Update [page] to reflect current state per [source]. Mark old claim with > [!warning] CONTRADICTION if ambiguous.`

2. **Stale claims** — Component pages whose `updated` frontmatter date is older than recent changes to corresponding source files. Check with: `git log --since="YYYY-MM-DD" -- <source-file>` where `YYYY-MM-DD` is the page's `updated` date. If commits exist after that date, the page is stale.
   - *Fix template:* `Re-read [source-file] (changed in commit [hash]), update [wiki-page] Key Points and set updated: [today], status: stable.`

3. **Orphan pages** — Pages not linked from `vault/index.md` or any other page.
   - *Fix template:* `Add [[page-name]] to index.md under [category] section, and add to ## Related of [related-page].`

4. **Missing concept pages** — Terms or entities mentioned in 3+ pages but lacking their own page.
   - *Fix template:* `Create [folder]/[term].md with frontmatter, extract relevant content from [page1], [page2], [page3].`

5. **One-way cross-references** — Page A links to B but B does not link back to A in its `## Related` section.
   - *Fix template:* `Add [[page-a]] to ## Related section of [page-b].`

6. **Weak sources** — Important pages relying on only a single raw source.
   - *Fix template:* `[page] relies solely on [source]. Cross-reference with [suggested-source] or mark as low-confidence.`

7. **Drift from root CLAUDE.md** — Vault claims that conflict with current conventions in the root `CLAUDE.md`.
   - *Fix template:* `[wiki-page] says "[claim]" but root CLAUDE.md says "[truth]". Update wiki page to match.`

8. **Broken wikilinks** — `[[wikilinks]]` that point to pages that do not exist anywhere in the vault (not even in `archive/`).
   - *Priority:* **high** — broken links degrade navigation and trust.
   - *Fix template:* `Either create the missing page [target].md, or update [[broken-link]] in [source-page] to point to the correct page.`

9. **Archived-target links** — `[[wikilinks]]` that resolve to a page in `archive/`. Not broken (Obsidian resolves by filename regardless of folder), but signals the linking page may need updating.
   - *Priority:* **info**
   - *Fix template:* `[[target]] in [source-page] points to archived page archive/[target].md. Review whether to update the link to a replacement page or remove it.`

10. **Stale status** — Pages stuck in transitional states too long:
   - `draft` for more than **60 days** without promotion to `stable`
   - `outdated` for more than **30 days** without being updated or archived
   - *Fix template:* `[page] has been [status] since [date] ([N] days). Review and either promote to stable, update content, or archive.`

## Output

**Overwrite** `vault/lint-report.md` on each run (not append — each lint is a fresh snapshot).

Each finding includes:
- **Category** (contradiction / stale-claim / orphan / missing-concept / one-way-xref / weak-source / drift / broken-wikilink / archived-target / stale-status)
- **Affected file(s)** with specific details
- **Suggested fix** using the category-specific template above
- **Priority** (high / medium / low)

**Do NOT auto-fix.** Report only. The user decides which fixes to apply.

## Logging

Append to `vault/log.md`:
```
## [YYYY-MM-DD] lint | N findings (H:x M:y L:z)
- Summary of findings by category
```

## Final Report

Show the user:
- Total files scanned
- Findings per category
- Top 3 most critical findings
- Overall vault health assessment
