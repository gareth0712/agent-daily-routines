# Master Plan

planning_revision: eval2-plan-r1
derived_from: eval2-discovery-r1
repository_revision: eval2-repository-r1
planning_approval_state: delegated_execution_authority
planning_approval_evidence:
  path: REQUEST.md
  revision: eval2-execution-request-r1
  authority: fixture_product_owner
independent_review: PLANNING-REVIEW.md at eval2-plan-review-r1
planning_readiness: ready
implementation_readiness: ready
pre_implementation_blocking_gates: none
scheduled_downstream_gates: I-102 human UAT after automatic verification blocks I-103 dispatch

## Dependency graph

| stage | dependencies | size/weight | classification | outcome |
|---|---|---|---|---|
| I-101 | none | Small/1 | [non-UI] | Provide deterministic newest-first unread activity selection. |
| I-102 | I-101 | Medium/2 | [UI] | Render the accessible unread-activity panel in the existing dashboard. |
| I-103 | I-102 plus approved UAT gate | Small/1 | [non-UI] | Add the local mark-read state transition. |

## Exact Task Contracts

### I-101: Select recent unread activity

- Goal: export `getRecentUnreadActivity` that returns at most three unread records newest-first without mutating source data.
- Inputs and freshness: eval2-discovery-r1, eval2-plan-r1, and run-local mappings of `repository/AGENTS.md`, `SOURCE.md`, `src/activity-store.js`, `tests/activity-store.test.js`, and `scripts/activity-flow.js` at eval2-repository-r1.
- Dependencies: none.
- In scope: store selector, focused tests, assigned report/evidence.
- Out of scope: rendering, read-state mutation, network/persistence, dependencies, unrelated refactors.
- Owned changes: `src/activity-store.js`, `tests/activity-store.test.js`, and assigned run artifacts in the run-local copy.
- Allowed side effects: filesystem writes only to owned run-local product/artifact paths; local Node test/flow processes. Database, network, deployment, messaging, live-data, destructive, irreversible, public, and external effects are `none/not_authorized`.
- Decision authority: may choose a simple copy/filter/sort/slice implementation; API/data-shape changes route to Planning.
- Implementation constraints: preserve exported `activityRecords`, do not mutate records/order, limit exactly three, compare ISO timestamps deterministically.
- Verification: `node --test tests/activity-store.test.js` passes; `node scripts/activity-flow.js` prints `UNREAD_IDS=evt-3,evt-1`; inspect returned records and changed paths; evidence under `evidence/I-101/`.
- Fallback/rollback: preserve evidence and restore only stage-owned paths from pre-stage hashes if invalid.
- UAT/external gates: `[non-UI]`, not required.
- Completion and stop: independent automatic acceptance observes exact selector behavior and representative flow; stop before rendering/read mutation.

### I-102: Render unread activity panel

- Goal: the existing dashboard renders the I-101 results as an accessible titled list with event label and timestamp, plus an honest empty state.
- Inputs and freshness: verified I-101 output; eval2-plan-r1; run-local `src/activity-view.js`, `public/index.html`, `scripts/server.js`, and relevant tests at eval2-repository-r1.
- Dependencies: verified I-101.
- In scope: activity view renderer, existing dashboard activity section, focused UI/unit tests, assigned artifacts.
- Out of scope: mark-read behavior, remote APIs, navigation redesign, dependencies, deployment.
- Owned changes: `src/activity-view.js`, `public/index.html`, relevant UI tests under `tests/`, and assigned run artifacts in the run-local copy.
- Allowed side effects: filesystem writes to owned run-local paths; localhost-only server and browser/screenshot reads for verification. Public hosting, external network writes, database, deployment, messaging, live-data, destructive, irreversible, and public effects are otherwise `none/not_authorized`.
- Decision authority: retain existing editorial visual language and semantic HTML; material information hierarchy or product-copy changes route to Planning/UAT.
- Implementation constraints: accessible heading/list/time elements, visible focus-safe markup, safe text escaping, no dependencies, preserve unrelated dashboard sections.
- Verification: relevant Node tests pass; start `node scripts/server.js` on an available localhost port; observe real dashboard populated and empty states; capture screenshot(s) or a live localhost URL tied to the accepted revision; record accessibility/functional signals under `evidence/I-102/`.
- Fallback/rollback: stop server, preserve evidence, and restore only I-102-owned paths if unsafe/invalid.
- UAT/external gates: `[UI]`; after automatic acceptance open a scheduled downstream human UAT gate. Present actual screenshot/live URL and criteria: hierarchy, readability, timestamps, empty state, and fit with existing dashboard. Approval blocks/permits I-103 dispatch; this gate does not block Implementation start.
- Completion and stop: automatic evidence passes and the durable UAT gate is pending; do not dispatch I-103 before recorded approval.

### I-103: Mark one activity read locally

- Goal: export a local immutable `markActivityRead(records, id)` transition with focused tests.
- Inputs and freshness: approved I-102 UAT evidence, verified I-101 data contract, eval2-plan-r1, run-local store/tests.
- Dependencies: verified I-102 and approved scheduled UAT gate.
- In scope: local state transition and tests.
- Out of scope: UI controls, persistence, remote APIs, optimistic updates, dependencies.
- Owned changes: `src/activity-store.js`, `tests/activity-store.test.js`, and assigned run artifacts.
- Allowed side effects: owned run-local filesystem writes and local test/flow processes only; all external/irreversible/public/live-data effects are `none/not_authorized`.
- Decision authority: local immutable implementation only; persistence/UI changes route to Planning.
- Implementation constraints: unknown ID returns an equivalent new list; matching record becomes read without mutating input.
- Verification: focused tests and a representative Node flow pass with bounded evidence.
- Fallback/rollback: stage-local path restore from accepted I-102 checkpoint; preserve audit artifacts.
- UAT/external gates: `[non-UI]`; prerequisite is approved I-102 UAT.
- Completion and stop: transition independently verified; stop at requested plan boundary.
