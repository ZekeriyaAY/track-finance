# Operation Log

> Append-only temporal log. Every INGEST, QUERY, and LINT operation is recorded here.
> Format: `## [YYYY-MM-DD] operation | slug`

## [2026-04-23] seed | phase-1
- Created: components/cashflow.md
- Created: decisions/2026-01-15-no-spa.md
- Created: patterns/route-handler.md
- Updated: index.md

## [2026-04-23] seed | phase-2
- Created 8 component pages: category, tag, investment, investment-type, categorization-rule, auth, settings, bank-sync
- Created 7 architecture pages: stack, factory-pattern, blueprint-pattern, database-schema, design-system, testing-strategy, docker-setup
- Created 5 pattern pages: model-definition, hierarchical-data, adapter-registry, template-structure, test-conventions
- Created 3 decision pages: dark-theme-only, numeric-for-money, single-user
- Created 1 roadmap page: planned-features
- Updated: index.md (full catalog)

## [2026-04-24] ingest | major-cleanup
- Source: raw/sessions/878f22f8-2eaa-41b6-9f26-0afefba04885.jsonl
- Created: sources/sessions/2026-04-23-major-cleanup.md
- Created: decisions/2026-04-23-remove-bank-sync-investment.md
- Created: patterns/pre-computed-counts.md, patterns/context-processor.md, patterns/pagination.md
- Created: bugs/bulk-edit-pointer-events.md, bugs/toast-visibility.md
- Updated: [[cashflow]], [[category]], [[tag]], [[settings]], [[categorization-rule]]
- Updated: [[database-schema]], [[design-system]], [[blueprint-pattern]]
- Updated: [[route-handler]], [[planned-features]]
- Archived: [[investment]] → archive/, [[investment-type]] → archive/, [[adapter-registry]] → archive/
- Removed stale reference: bank-sync (page never existed as file)
- Updated: index.md (full catalog refresh)

## [2026-04-24] lint | 24 findings (H:0 M:4 L:20)
- 3 stale-claim: auth.md, factory-pattern.md, hierarchical-data.md
- 1 drift: root CLAUDE.md Font Awesome references (investment types removed)
- 2 archived-target: hierarchical-data → investment-type, database-schema → investment/investment-type
- 18 one-way-xref: route-handler hub (7), decision pages (5), component/architecture (6)
