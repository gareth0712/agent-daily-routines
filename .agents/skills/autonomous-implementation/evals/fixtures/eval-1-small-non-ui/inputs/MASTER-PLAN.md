# Master Plan

planning_revision: eval1-plan-r1
derived_from: eval1-discovery-r1
repository_revision: eval1-repository-r1
planning_approval_state: delegated_execution_authority
planning_approval_evidence:
  path: REQUEST.md
  revision: eval1-execution-request-r1
  authority: fixture_product_owner
independent_review: PLANNING-REVIEW.md at eval1-plan-review-r1
planning_readiness: ready
implementation_readiness: ready
pre_implementation_blocking_gates: none
scheduled_downstream_gates: none

## Dependency graph

| stage | dependencies | size/weight | classification | outcome |
|---|---|---|---|---|
| I-001 | none | Small/1 | [non-UI] | Normalize task-title search behavior. |

## Exact Task Contract

### I-001: Normalize task-title search

- Goal: `searchTasks` trims the query, compares titles case-insensitively, preserves input order, and returns `[]` for a blank normalized query.
- Inputs and freshness: `DISCOVERY.md` eval1-discovery-r1; this plan eval1-plan-r1; `repository/AGENTS.md`, `repository/SOURCE.md`, `repository/src/search.js`, `repository/tests/search.test.js`, and `repository/scripts/real-flow.js` at eval1-repository-r1. Map these paths to the run-local working copy before editing.
- Dependencies: none.
- In scope: `src/search.js`, behavior tests in `tests/search.test.js`, and bounded run artifacts.
- Out of scope: fuzzy matching, ranking, persistence, UI, package dependencies, unrelated refactors, and fixture-source changes.
- Owned changes: `src/search.js`, `tests/search.test.js`, and the assigned `I-001` report/evidence paths in the run-local copies only.
- Allowed side effects: filesystem writes only to the owned run-local product and run-artifact paths; test/real-flow processes may read the run-local repository. Database, network, deployment, messaging, live-data, external, destructive, irreversible, and public effects are `none/not_authorized`.
- Decision authority: may choose a small local normalization expression consistent with current ESM style; any API shape, fuzzy semantics, dependency, or scope change routes to Planning.
- Implementation constraints: do not mutate the input array/tasks; preserve order; use no new dependency; retain the exported function signature.
- Verification: run `node --test tests/search.test.js` and expect all tests pass; run `node scripts/real-flow.js` and expect exactly `MATCH_IDS=2`; inspect the changed-file list and a real returned task object. Store bounded output under `evidence/I-001/`.
- Fallback/rollback: preserve evidence; restore only stage-owned changes from the recorded pre-stage hashes if the approach violates the contract; never reset unrelated paths.
- UAT/external gates: `[non-UI]`; human UAT and external gates are `not_required`.
- Completion and stop: independent automatic acceptance observes both commands, the representative flow, and exact containment; stop before unrelated improvements.
