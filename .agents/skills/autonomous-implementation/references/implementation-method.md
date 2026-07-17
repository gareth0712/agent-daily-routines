# Implementation Method

## Ownership boundary

Implementation changes product/test/documentation/migration surfaces only inside a current approved Task Contract. Discovery owns users, outcomes, scope, non-goals, hard constraints, primary journeys, and acceptance intent. Planning owns architecture, interfaces, data contracts, workflows, sequencing, migration/deployment design, verification strategy, rollback design, and Task Contracts.

Do not repeat upstream work. Apply one narrow consistency/freshness gate and route only the affected defect. Implementation may decide a local reversible detail only when the exact contract delegates it and the choice preserves all recorded invariants.

## Readiness and backward routing

Accept `MASTER-PLAN.md` or a differently named equivalent only when its content provides:

- current approved Discovery source/equivalent and reproducible lineage/freshness;
- current repository/reference revision and known dirty-path treatment;
- ordered Small/Medium implementation stages with acyclic dependencies;
- for every stage, the complete exact Task Contract defined below;
- independent Planning review and durable dispositions for findings;
- `planning_approval_state` equal to `delegated_execution_authority` or `explicitly_approved`, plus exact current `planning_approval_evidence` fields `path`, `revision`, and named `authority` that cover this plan revision/scope/stop boundary/side effects;
- separate `pre_implementation_blocking_gates` and `scheduled_downstream_gates`;
- `planning_readiness: ready` and `implementation_readiness: ready`, or equivalent evidence supporting both.

Map equivalent fields explicitly. Approval or filename presence without content/freshness is not sufficient. Compare recorded revisions with current Git/filesystem evidence, applicable instructions, known contradiction paths, and pre-existing dirty changes.

Approval is independent of Planning readiness. `delegated_execution_authority` is valid only when its durable request/scope artifact explicitly requested execution and the current plan stays within the recorded authority. `explicitly_approved` is valid only when its canonical resolved gate names the authority and exact plan revision/boundaries. Independent review PASS, orchestrator acceptance, silence, `not_requested`, `approval_required`, missing fields, or stale evidence never authorizes product edits. Preserve an existing `approval_required` gate and stop; route a missing/stale producer mapping to Planning rather than inventing it.

The read-only readiness review returns exactly:

- `READY`: framing and execution contracts are current; required verification/capabilities are available or have safe declared fallback; no pre-Implementation blocker remains.
- `NEEDS_PLANNING`: framing remains current but a Planning-owned decision or contract is absent, stale, contradictory, Large, unbounded, unverifiable, or under-authorized.
- `NEEDS_DISCOVERY`: a framing-owned decision or acceptance intent is absent, stale, or contradicted.

For a route, record the exact missing/contradicted field, source revisions, impact, owner, and smallest affected scope. Do not perform a Planning repair inside an implementation worker. Scheduled later UAT/external gates do not block start; they block the exact dependent-stage transition named in the plan.

## Exact Task Contract consumption

Copy the approved stage contract verbatim into `packets/I-###.md`. It must contain:

1. `Stage ID and title`
2. `Goal` — one observable primary outcome.
3. `Inputs and freshness` — upstream revisions, instruction paths, files/surfaces.
4. `Dependencies` — verified stages and external prerequisites.
5. `In scope / Out of scope` — explicit boundaries.
6. `Owned changes` — exact expected product/test/docs/migration paths or bounded globs.
7. `Allowed side effects` — exact filesystem, database, network, deployment, messaging, live-data, or external effects. Missing external/irreversible/destructive/public authority means `none/not_authorized`; owned paths never imply those effects.
8. `Decision authority` — local choices permitted and choices requiring Planning/Discovery/human approval.
9. `Implementation constraints` — interface/data/security/compatibility invariants.
10. `Verification` — commands/reads/UI observations, expected signals, representative real flow, and evidence destinations.
11. `Fallback / rollback` — safe checkpoint, trigger, and exact stage-local recovery boundary.
12. `UAT and external gates` — `[UI]`/`[non-UI]`, criteria, timing, owner, evidence, and named boundary.
13. `Completion and stop` — objective acceptance and when not to continue.

Reject and route a contract that changes meaning when made verbatim, has multiple outcomes, has an unknown interface, requires three or more coupled subsystems, lacks observable verification, grants ambiguous side effects, depends on a later unresolved decision, or contradicts current evidence.

## Dirty-worktree preservation

Before the first product write, inventory:

- baseline Git SHA when Git exists, otherwise a reproducible filesystem revision;
- every pre-existing staged, unstaged, untracked, ignored-but-relevant, or externally supplied dirty path;
- baseline and current SHA-256 for each dirty file, or bounded directory inventory for a dirty directory;
- a redacted bounded diff/status summary and evidence path;
- paths that overlap a contract-owned surface.

For an overlapping dirty path, distinguish upstream user work from authorized stage work before dispatch. If they cannot be separated safely, open an authority/internal-recovery gate; never overwrite and hope to reconstruct later.

After every worker and checkpoint, compare the baseline inventory with current paths. Preserve unrelated hashes/content exactly. For a legitimate overlap, record the prior/current diff and attribution. A hash mismatch outside assigned paths blocks acceptance even when tests pass.

Never use `git reset --hard`, broad checkout/restore/clean, unscoped stash, force operations, or another destructive command that can erase user work or audit artifacts. A stage-local revert names exact stage-owned paths and preserves reports/evidence/events.

## Worker dispatch contract

The orchestrator freezes these details before invoking a worker:

- verbatim Task Contract and accepted upstream revisions;
- every applicable `AGENTS.md`/`CLAUDE.md` path;
- canonical repository/worktree/run/working roots;
- exact allowed read roots, product write paths, artifact write paths, report/evidence paths, and side effects;
- dirty baseline evidence and forbidden unrelated paths;
- requested/effective worker model and fallback;
- deterministic completion/verification/real-flow commands and expected signals;
- `[UI]` design-skill preferences and required visual evidence when relevant;
- durable progress marker and host-enforceable exhaustion signal;
- report-before-state and at-most-ten-line return contract.

The worker first repeats physical containment and writes `evidence/I-###/worker-progress.md`. It then reads instructions, inspects current inputs, implements only the primary outcome, adds/updates relevant tests unless repository policy records an exception, runs scoped checks and the representative flow, records actual changed paths and side effects, writes the report/evidence, and returns a pointer-only summary.

Workers never update `AGENT-STATE.md`, append `EVENTS.jsonl`, resolve their own UAT, accept their own stage, commit unless the exact contract and orchestrator authorize it, or perform an upstream redesign.

After every readiness, implementation, repair, or integration return, the orchestrator captures the exact host terminal/return boundary in a new immutable `evidence/I-###/worker-return-attempt-###.md`. The receipt contains the packet-local monotonic attempt number, dispatch event and fresh worker identity, full subtree terminal status, prior receipt, `host_return_observed_at`, later `receipt_created_at`, canonical UTF-8 base64 return payload with derived line count/hash, and report/evidence hashes. The receipt disposition is only `return_observed`; final acceptance/rejection and final disposition are a later immutable event. Verify report/evidence stable mtimes and embedded completion times are no later than `host_return_observed_at`, then require `host_return_observed_at <= receipt_created_at <= worker_return_observed event time < final-disposition event time`. Reconcile dispatch count, receipt count, packet retry count, and session remediation count before acceptance or another dispatch.

## Independent automatic acceptance

Treat the report as a claim. After the worker returns, the top-level orchestrator:

1. verifies the immutable `return_observed` receipt, terminal subtree, canonical bounded return bytes, report/evidence hashes, and lifecycle times;
2. re-resolves all written paths and proves physical containment;
3. inventories repository/worktree changes and compares them with owned paths plus dirty baseline;
4. opens the report and representative changed artifacts;
5. checks the exact Task Contract remains current and no unauthorized side effect occurred;
6. reruns required commands and inspects bounded relevant output, not only exit status;
7. drives one representative affected user/system flow and records the observed result;
8. for `[UI]`, inspects actual rendered behavior, functional state, accessibility signal where required, and screenshot/live URL evidence;
9. records receipt/report/evidence/artifact/diff/flow observations in bounded evidence and events;
10. records final attempt disposition in a later immutable acceptance/rejection event and changes status to `verified` only after every required signal passes.

A test suite that does not exercise the changed behavior, a screenshot without the accepted build/revision, or a worker-authored commit is insufficient. When required verification cannot be run, block or route; do not mark pass from code inspection.

## Diagnosis, remediation, and rollback

On failure, persist:

- `failure_family` stable across sessions;
- failing command/flow and bounded observed signal;
- evidence-backed root-cause hypothesis and alternatives rejected by evidence;
- useful stage work to preserve;
- one falsifiable repair and changed variable;
- `retry_count` and `remediation_cycles_this_session`;
- rollback trigger and exact stage-owned checkpoint.

Retry only after diagnosis, a terminal `return_observed` receipt, and a later `non_accepted_retryable` event, with one fresh repair worker constrained to the same contract/paths. At most two remediation cycles may target the same failure family. Compaction or restart does not reset the counter. A denied operation is not retried through alternate syntax.

Preserve useful safe work when the approach remains valid. Revert exact stage-owned changes only when the workspace is unsafe, the implementation violates the contract, or the approach is invalid and repair would compound harm. Never erase the failed report, evidence, event history, dirty baseline, or upstream route.

After two unsuccessful cycles, set the stage `blocked`, open the correct operational/human/owning-stage gate, write a handoff, and stop. A time limit is not permission to relabel failure as success or rush a third attempt.

## UI automatic acceptance and human UAT

`[UI]` stages default to this order:

1. worker functional tests and representative UI flow;
2. orchestrator automatic functional/visual/accessibility sampling;
3. actual screenshot(s) or live URL tied to exact build/revision;
4. durable `uat` gate with acceptance criteria and blocked dependency;
5. human `approved` or `rejected` evidence;
6. only then checkpoint and dispatch a dependent stage.

Request relevant installed design preferences (`design-taste-frontend`, `high-end-visual-design`, `minimalist-ui`, and `redesign-existing-projects` for existing-page redesign). Record actual invocation evidence or unavailable/not-installed fallback. These preferences cannot override project instructions, upstream design authority, exact scope, or UAT.

`pending`, `approved`, and `rejected` UAT state names the accepted revision/evidence. New UI-changing work after approval invalidates that approval for the changed surface. Rejection creates a bounded repair with preserved prior evidence. A missing browser/screenshot capability is a verification blocker, not implied approval.

## Safe checkpointing

Checkpoint only after independent automatic acceptance and required UAT. If commit authority exists:

- stage only exact owned paths plus authorized run artifacts;
- inspect the staged diff and path list;
- exclude pre-existing unrelated dirty paths;
- record commit SHA and scoped diff evidence;
- never amend/rewrite user history unless explicitly authorized.

Without commit authority or Git, record exact changed-path hashes, bounded diff/inventory, upstream revision, accepted event anchor, rollback point, and recovery action. A reversible filesystem checkpoint is valid; inventing a commit is not.

## Independent integration review

A fresh read-only reviewer that did not author the stages checks:

- Discovery intent and Planning Task Contract compliance;
- changed-file and side-effect containment;
- cross-stage architecture, interface, data, migration, and compatibility consistency;
- tests/build/type checks and representative affected flows;
- UI evidence and UAT lineage;
- dirty-path preservation, checkpoints, rollback, and residual gates;
- actual-vs-plan deviations, assumptions, scope leakage, and unfinished work.

Classify findings `CRITICAL`, `IMPORTANT`, or `MINOR`, with dispositions `open`, `verified_repair`, `routed`, or `accepted_risk`. CRITICAL closes only through verified repair or evidence-backed route to Discovery/Planning/Implementation ownership; it can never be accepted risk. Noncritical accepted risk requires named authority and explicit completion impact.

## Implementation notes and completion

`IMPLEMENTATION-NOTES.md` is the actual-vs-plan ledger, not a victory summary. It records:

- accepted upstream revisions and readiness evidence;
- every stage contract/revision/status/weight and changed files;
- commands, expected/observed signals, real-flow evidence, UI evidence, and UAT;
- actual design/behavior versus plan, deviations, disposition/owner, assumptions, and unexpected constraints;
- failures, diagnoses, retries, useful work preserved, and stage-local rollback;
- dirty-path baseline/current proof and checkpoint/commit evidence;
- integration findings/dispositions, residual gates, unfinished work, and continuation.

Completion requires all requested stages verified, all required UAT approved, zero unresolved critical integration findings, no unauthorized/unrelated changes or effects, current rollback evidence, and mutually consistent state/events/notes/repository evidence. Otherwise route, block, or hand off honestly.
