---
name: autonomous-implementation
description: Use when the user requests autonomous execution of a current approved execution-ready software plan or equivalent specification, including resumed staged implementation, verification, UI UAT, and integration acceptance. Route missing/stale framing to Discovery and missing/contradicted architecture, interfaces, sequencing, migration, or verification contracts to Planning. Do not trigger for ordinary small fixes unless the user explicitly invokes this pipeline.
---

# Autonomous Implementation

## Purpose

Execute a current approved plan as sequential, independently accepted `I-###` stages while preserving unrelated work and durable context. Produce verified product changes plus `IMPLEMENTATION-NOTES.md`, or a lossless route/handoff when a gate prevents safe continuation.

This is bounded autonomy. Continue through non-UI stages without asking for reversible local choices already delegated by the plan. Pause only for a hard blocker, an exact authority/product decision, required unavailable verification, session cutover, or human UAT after automatic UI verification. Never claim unattended multi-session continuation unless the host proves it.

## Required references

Load the six binding references progressively; a fired pointer makes the whole referenced file required:

1. During bootstrap, read [Artifact protocol](references/artifact-protocol.md) and [Harness adapters](references/harness-adapters.md) completely before writing run state or dispatching. Capability-check Python and run the bundled `scripts/append_event.py --self-test` before initializing `EVENTS.jsonl`; use an independently verified equivalent only if Python is unavailable.
2. Before judging readiness, routing ownership, freezing contracts, accepting/remediating work, handling dirty paths, UAT, checkpointing, integration review, or completion, read [Implementation method](references/implementation-method.md) completely.
3. Before sizing, dispatch, budget cutover, retry, or liveness decisions, read [Work sizing](references/work-sizing.md) completely.
4. Before writing or updating an artifact, read that artifact's complete section in [State templates](references/state-templates.md).
5. Read [Launcher template](references/launcher-template.md) completely when starting from it or when the user requests a copyable one-prompt launcher.

If references conflict, preserve the safer upstream ownership, side-effect, dirty-path, or human-gate boundary and record the conflict rather than inventing compatibility.

## Activation and routing boundary

Use this workflow only when execution is requested and a current approved execution-ready `MASTER-PLAN.md` or content-equivalent specification exists. A differently named plan is valid when it maps all required Task Contract fields, current lineage/freshness, approval, and unresolved gates.

“Approved” has one exact durable meaning: `planning_approval_state` is `delegated_execution_authority` or `explicitly_approved`, and `planning_approval_evidence` supplies a current path, revision, and named authority covering the exact plan revision, execution scope, stop boundary, and side effects. Planning readiness/review, orchestrator acceptance, silence, `not_requested`, `approval_required`, or stale/missing fields do not authorize product edits; route the missing producer mapping/gate to Planning.

Before product edits, validate Discovery, Planning, repository, and pre-existing dirty state together. Classify exactly:

- `READY`: framing and execution contracts are current; all gates required before Implementation starts are resolved.
- `NEEDS_PLANNING`: framing is current, but architecture, interface, data, sequence, migration, deployment, verification, rollback, contract, or pre-start gate detail is absent/stale/contradicted.
- `NEEDS_DISCOVERY`: users, outcomes, scope, acceptance intent, hard constraints, or another framing-owned decision is absent/stale/contradicted.

Route only the affected scope upstream. Implementation does not silently redesign architecture or product framing. A correctly scheduled later UI UAT or external gate belongs in `scheduled_downstream_gates` and does not prevent Implementation start; it blocks only its named later boundary. A gate in `pre_implementation_blocking_gates` does prevent start.

Ordinary small bug fixes, narrow refactors, copy changes, and fully specified low-risk changes use ordinary scoped implementation unless the user explicitly invokes this pipeline. A resumed run with current artifacts rehydrates Implementation rather than restarting upstream stages.

Run the orchestrator in the top-level session. If invoked inside a worker and the host forbids nested delegation, return a hard blocker to the parent.

## Invariants

- Use `protocol_version: autonomous-artifacts-v2`; artifacts and repository evidence, not conversation memory, carry state.
- `AGENT-STATE.md` and `EVENTS.jsonl` have one writer: the top-level orchestrator. Workers never update control state or append events.
- On compaction, interruption, resume, or handoff, treat summaries, checkboxes, commits, and worker claims as unverified until reconciled with artifacts, Git/filesystem evidence, current upstream revisions, and the event anchor.
- Product edits require a current verbatim Planning Task Contract. Consume `Allowed side effects` exactly. Missing authority means `none/not_authorized`, especially for external, irreversible, destructive, live-data, public, deployment, messaging, and credential effects.
- Consume Planning approval exactly as emitted. Never translate plan readiness or independent review into approval, and never widen delegated/explicit authority beyond its evidence revision.
- Freeze only `Small`/1 or `Medium`/2 stages. `Large` is invalid and routes to Planning for splitting before dispatch.
- Dispatch exactly one fresh state-changing implementation worker at a time and wait before accepting or dispatching another. Do not parallelize product writes, repairs, UAT-dependent work, or integration acceptance.
- A worker receives the verbatim Task Contract, instruction paths, requested/effective model policy, exact allowed product and artifact writes, exact side effects, physical anchors, report/evidence targets, and at-most-ten-line return contract.
- After every readiness, implementation, repair, or integration worker return, the orchestrator writes a new immutable `evidence/I-###/worker-return-attempt-###.md`. It records the attempt number, dispatch event and fresh worker identity, full subtree terminal status, exact `host_return_observed_at` boundary, canonical returned bytes/line count/hash, report/evidence hashes, and lifecycle-time checks. The pre-acceptance receipt records only `return_observed`; a later immutable acceptance/rejection event records final disposition. Packet prose or event summaries are not evidence that a worker was fresh, terminal, independent, artifact-first, or within ten lines.
- Worker `done`, exit code alone, or a commit is not evidence. The orchestrator independently checks containment, scoped changes, representative outputs, required commands, and one real affected flow before `verified`.
- Record pre-existing dirty paths with baseline/current hashes and bounded diffs. Never stage, overwrite, revert, or checkpoint unrelated user work.
- Diagnose from actual evidence before remediation. Permit at most two evidence-driven remediation cycles for the same failure family and persist the family/counter across sessions.
- Preserve useful safe work. Revert only exact stage-owned unsafe/invalid changes; never use destructive reset or erase run artifacts/audit history.
- `[UI]` requires automatic verification plus actual screenshot or live-URL evidence, then a durable human UAT gate. No dependent stage crosses that gate before recorded approval.
- Model classes, design skills, context telemetry, Git, browser evidence, commits, and automatic restart are requested capabilities, never assumptions.
- Session ceilings are maxima, not targets: 6 weight units normally and 4 for security/data/external-integration/UI/high-risk sessions. Never rush to fit a session.

## Workflow

### 1. Bootstrap or rehydrate

Discover actual host capabilities, applicable `AGENTS.md`/`CLAUDE.md`, repository/worktree root, plan/run locations, Git/filesystem baseline, dirty paths, upstream artifacts, current state, and continuation truth. Resolve lexical and physical/canonical anchors and check `EVENTS.FROZEN` before any append.

On resume, reconcile `AGENT-STATE.md`, `SCOPE.md`, accepted Discovery and Planning sources, `MASTER-PLAN.md`, `IMPLEMENTATION-NOTES.md`, active stage/report/evidence, gates, `SESSION-HANDOFF.md`, event chain/anchor, Git history, current files, dirty hashes, retry counters, and UAT state. Downgrade unsupported `verified` claims.

Record requested highest-reasoning orchestrator and Sonnet-class/high-effort implementation worker only as preferences. Persist observed effective model or `host_default`, fallback reason, context telemetry or `unavailable`, and manual/automatic restart evidence.

Completion criterion: current lineage, baseline/dirty inventory, capabilities/fallbacks, physical anchors, accepted event adapter, and one evidence-based next action are durable.

### 2. Run a bounded Implementation readiness review

Dispatch one fresh read-only `I-###` readiness worker before product edits. Give it current Discovery/Planning artifacts or equivalents, repository instructions/surfaces, dirty inventory, exact gate lists, and the three-value verdict contract.

Independently inspect its report and cited evidence. Confirm the exact Planning approval state/path/revision/authority covers the current plan and every requested side effect, Task Contract completeness, upstream/repository freshness, dirty consistency, pre-start authority, and verification availability. The worker identifies defects; it does not repair framing or planning.

Completion criterion: `READY`, `NEEDS_PLANNING`, or `NEEDS_DISCOVERY` is independently supported by paths/revisions and a bounded route.

### 3. Route upstream when readiness fails

For `NEEDS_DISCOVERY`, persist the framing contradiction/missing decision and route the smallest affected scope to `autonomous-project-discovery`. For `NEEDS_PLANNING`, persist the exact architecture/contract defect and route a bounded repair to `autonomous-planning`. Do not edit product code while routed.

Only return after a refreshed upstream artifact is current and approved. Re-run the consistency gate; do not bless an upstream worker's claim without evidence.

### 4. Freeze execution stages and exact contracts

When `READY`, freeze the ordered `I-###` dependency graph and copy every Task Contract verbatim into the run packet. Do not reinterpret or broaden:

- Goal; inputs/freshness; dependencies; in/out scope; owned files/surfaces;
- `Allowed side effects`;
- decision authority and constraints;
- exact verification, expected signals, representative real flow, and evidence paths;
- fallback/rollback; `[UI]`/`[non-UI]`; gate timing/boundary; completion/stop.

Split or route any Large, multi-outcome, unbounded, untestable, or under-authorized contract before dispatch. When commits are authorized, checkpoint the frozen spec separately and only on exact owned artifact paths; otherwise record reversible hashes/diffs.

### 5. Preflight and dispatch one stage

Before dispatch, verify dependencies, current inputs, side-effect authority, isolated-worker capability, model fallback, instruction paths, progress/exhaustion signals, remaining budget, dirty-path baseline, and every physical read/write/report/evidence anchor. If preflight fails, do not spawn; use `blocked`, `effective_model: not_executed`, `none_not_dispatched`, bounded evidence, and the canonical gate.

When it passes, dispatch one fresh implementation worker. The worker may edit only exact contract-owned product paths and assigned packet/report/evidence paths. It reads all named instructions, adds/updates appropriate tests for changed behavior unless the repository records an exception, runs contract checks, drives the representative affected flow, inventories changed paths, preserves dirty paths, writes its full report/evidence first, and returns at most ten lines.

For `[UI]`, request installed relevant design preferences: `design-taste-frontend`, `high-end-visual-design`, `minimalist-ui`, and `redesign-existing-projects` when redesigning an existing page. Record observed invocation or unavailable/not-installed fallback; never claim a skill ran without evidence and never install it silently.

### 6. Independently accept or reject the stage

After return, capture the exact host terminal/return observation time, canonicalize the returned bytes by the state-template rule, and persist the immutable `return_observed` receipt. Every report/evidence stable mtime and embedded completion time must be no later than that host-return boundary; the receipt creation and `worker_return_observed` event follow it. Reconcile dispatch count, receipt count, packet retry count, and session remediation count. A contradictory lifecycle blocks acceptance rather than being backdated. The orchestrator then re-resolves every written target and checks:

1. physical containment and exact changed-file scope;
2. pre-existing dirty baseline/current hashes and bounded diffs;
3. report and bounded evidence existence before state transition;
4. contract verification commands with expected signals;
5. representative real output/flow, not only exit codes;
6. side effects against exact authority;
7. for UI, functional/visual/accessibility behavior plus actual screenshot or live URL evidence.

Append receipt observation and sampling events, then record the attempt's final `accepted`, `non_accepted_retryable`, or `non_accepted_terminal` disposition in a later immutable acceptance/rejection event. Mark `verified` only after all required evidence passes. A worker-authored commit or self-review cannot accept its own stage.

### 7. Diagnose and remediate bounded failures

On failure, preserve evidence and write the failure family, root-cause hypothesis, falsifiable next change, retry count, useful work retained, and rollback trigger. Dispatch one fresh repair worker only for the same exact contract-owned paths. Change an evidence-backed variable; do not blindly repeat.

Allow at most two remediation cycles for that failure family across compaction/session boundaries. If work is safe and directionally valid, repair it in place. Use a stage-local revert only for unsafe/invalid stage-owned changes and preserve reports/events. After two unsuccessful cycles, block and route/ask rather than rushing.

### 8. Apply the UI UAT gate

After automatic acceptance of `[UI]`, persist the accepted build/revision, screenshot or live URL, automatic checks, human acceptance criteria, and gate artifact. Present the actual evidence and wait. Record `approved` or `rejected` plus authority and feedback.

Approval permits dependent dispatch. Rejection creates a bounded repair stage/packet without erasing prior evidence. Browser/screenshot capability absence blocks required UI verification; code inspection is not a substitute.

### 9. Checkpoint safely and continue

After a verified stage and required UAT, create a path-limited commit only when exact commit authority exists. Confirm the staged set contains only owned paths and excludes pre-existing dirty work. Otherwise record current hashes, scoped diff, rollback point, and artifact/event anchor as the reversible checkpoint.

Recalculate `completed_weight + next_stage_weight` before every dispatch. Continue automatically when dependencies/gates/authority/evidence allow. At a ceiling or cutover trigger, write `SESSION-HANDOFF.md` and end; do not compress work or weaken checks.

### 10. Run independent integration acceptance

After requested stages and UAT gates are complete, dispatch one fresh read-only reviewer that did not author the stages. It checks Discovery intent, Planning contracts, changed-file containment, cross-stage interfaces/data, tests/build/type checks, representative flows, UI evidence/UAT, side effects, deviations, dirty preservation, rollback, residual gates, and scope leakage.

Route findings to their owner. Local Implementation defects become bounded repair stages; architecture/contract defects route to Planning; framing defects route to Discovery. A CRITICAL finding closes only through verified repair or evidence-backed owning-stage routing, never accepted risk.

### 11. Finish or hand off

Maintain `IMPLEMENTATION-NOTES.md` as the actual-vs-plan ledger: verified stages, changed files, observed behavior, commands/evidence, deviations and disposition, assumptions, dirty-path proof, retries, UAT, integration findings, residual gates, checkpoints, rollback points, and current upstream revisions.

Persist `continuation_kind`, verification, exact value, restart truth, first-read files, and one next action. Use a command only after harmlessly verifying it; otherwise write a precise `manual_host_action` naming `autonomous-implementation`, absolute run root, required gate input, and next action.

## Completion checklist

Implementation is complete only when:

- current Discovery/Planning inputs and repository/dirty evidence support `READY`;
- every requested stage is Small/Medium, verified from report-before-state evidence, and within its exact side-effect authority;
- every required command and representative affected flow was independently sampled;
- every `[UI]` stage has automatic visual evidence and durable human UAT approval before dependent work;
- pre-existing dirty paths remain preserved and every checkpoint contains only authorized owned paths;
- retry counters/failure families, model/capability fallbacks, session ceilings, and handoffs are honest;
- every dispatched worker/reviewer has one immutable terminal `return_observed` attempt receipt plus a later immutable final-disposition event, dispatch/receipt/retry/remediation counts reconcile, and artifact/host-return/receipt/event times are monotonically observable;
- a fresh integration reviewer has no unresolved critical finding;
- `IMPLEMENTATION-NOTES.md`, state, gates, event anchor, repository state, and continuation agree;
- no unapproved deploy, public/external effect, secret change, live migration, destructive reset, audit erasure, or unrelated edit occurred.
