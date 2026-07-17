# Master Plan

planning_revision: eval3-plan-r1
derived_from: eval3-discovery-r1
repository_revision: eval3-repository-baseline-r1
planning_approval_state: delegated_execution_authority
planning_approval_evidence:
  path: REQUEST.md
  revision: eval3-execution-request-r1
  authority: fixture_product_owner
independent_review: PLANNING-REVIEW.md at eval3-plan-review-r1
planning_readiness: ready
implementation_readiness: ready
pre_implementation_blocking_gates: none
scheduled_downstream_gates: none

## Exact Task Contract

### I-201: Parse notification enablement safely

- Goal: `notificationsEnabled(config)` returns exact booleans unchanged, accepts trimmed case-insensitive `"true"`/`"false"`, and returns `false` for missing or unsupported values.
- Inputs and freshness: eval3-discovery-r1; eval3-plan-r1; run-local mappings of `current-repository/AGENTS.md`, `SOURCE.md`, `src/notify.js`, `tests/notify.test.js`, and `scripts/real-flow.js`. Current first-attempt code is Implementation-owned evidence, not an upstream framing/architecture change.
- Dependencies: verified readiness review I-200 from the supplied resume state.
- In scope: repair `src/notify.js`, focused tests if needed, and assigned repair report/evidence.
- Out of scope: UI, delivery, remote configuration, dependencies, user notes, upstream artifacts, unrelated refactors.
- Owned changes: run-local `src/notify.js`, `tests/notify.test.js` only if needed to express already-approved cases, and assigned run artifacts. `notes/user-draft.md` is explicitly unowned/protected.
- Allowed side effects: filesystem writes only to owned run-local product/artifact paths and local Node test/flow processes. Database, network, deployment, messaging, credentials, live-data, external, destructive, irreversible, and public effects are `none/not_authorized`.
- Decision authority: may implement a small explicit parser; any accepted value beyond booleans and true/false strings, API change, dependency, or configuration-source change routes to Planning.
- Implementation constraints: fail closed; no JavaScript truthiness for strings; preserve export signature; do not mutate config; no dependencies.
- Verification: `node --test tests/notify.test.js` passes all approved cases; `node scripts/real-flow.js` prints `NOTIFY_FALSE=false`; inspect the returned boolean and exact changed paths; independently prove `notes/user-draft.md` SHA-256 unchanged; store evidence under the active repair evidence root.
- Fallback/rollback: preserve the failed first-attempt report/evidence; restore only stage-owned paths from recorded hashes if unsafe/invalid; never reset or touch the protected draft/audit artifacts.
- UAT/external gates: `[non-UI]`; not required.
- Completion and stop: one final evidence-driven remediation may run because retry_count is 1; independent acceptance and integration review must pass; a second failed remediation sets blocked and no third attempt runs.
