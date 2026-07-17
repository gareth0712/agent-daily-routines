# Product Brief: CSV Task Import

artifact_revision: brief-csv-import-v1
repository_revision: fixture-csv-v1
planning_readiness: ready

## Users and outcome

Small teams already using the task board need to import a UTF-8 CSV export from another tool without manually recreating tasks. A team owner uploads one file, reviews validation results, and commits only valid rows after explicit confirmation.

## Scope and journeys

- Accept one UTF-8 CSV with headers `title`, `description`, and `status`.
- Maximum 1,000 rows and 2 MiB.
- Parse and validate server-side; never trust client-reported counts.
- Show row-numbered validation errors and a valid/invalid summary before commit.
- On confirmation, create all valid rows in one transaction; if creation fails, create none.
- Record importer identity and aggregate counts, not raw CSV content, in the existing audit sink.

## Non-goals

- Background jobs, scheduled imports, other file formats, column mapping, duplicate detection, or partial commits.

## Hard constraints and acceptance intent

- Reuse current repository conventions and authorization boundary.
- No product file changes during Planning.
- The plan must specify exact interface/data/transaction/testing/UI verification contracts and a later `[UI]` UAT stage.
- High-impact product decisions are resolved; Planning owns technical design inside this brief.

## Residual ownership and freshness

- Implementation may decide local names only when contracts preserve these behaviors.
- Any request to add formats, partial commit, mapping, or duplicate policy routes to Discovery.
- Freshness evidence is the supplied repository fixture at revision `fixture-csv-v1`; inspect its instruction, package, store, route, and test surfaces.
