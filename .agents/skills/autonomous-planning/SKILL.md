---
name: autonomous-planning
description: Use when the user requests an executable software plan and a current sufficient Discovery artifact or equivalent framing exists, or when an execution request needs a bounded planning repair. Route missing, stale, or framing-conflicted inputs to Discovery and route a current approved plan requested for execution to Implementation.
---

# Autonomous Planning

## Purpose

Turn current, bounded project framing into an execution-ready, verified, resumable `MASTER-PLAN.md`. Planning owns architecture, interfaces, data models, workflows, migrations, testing, deployment, observability, verification design, sequencing, and exact implementation Task Contracts. It consumes product framing from Discovery and must not redefine that framing or write product code.

This is bounded autonomy. It may span multiple manually restarted sessions, but it never claims that a host can create a new top-level session, select a model, or report context usage unless those capabilities were observed.

## Required references

Load the six binding references progressively. A deferred read becomes required when its pointer fires:

1. During bootstrap, read [Artifact protocol](references/artifact-protocol.md) and [Harness adapters](references/harness-adapters.md) completely before writing run state or dispatching a worker. Capability-check Python and run the bundled `scripts/append_event.py --self-test` contract before initializing `EVENTS.jsonl`; use an independently verified equivalent only when Python is unavailable.
2. Before accepting upstream framing, making a Planning-owned decision, routing a defect, defining readiness, or reviewing the plan, read [Planning method](references/planning-method.md) completely.
3. Before packet decomposition, dependency ordering, dispatch, budget cutover, or retry decisions, read [Work sizing](references/work-sizing.md) completely.
4. Before writing or updating an artifact, read that artifact's complete section in [State templates](references/state-templates.md); read additional sections only when their artifact is needed.
5. Read [Launcher template](references/launcher-template.md) completely only when starting from it or when the user requests a copyable launcher prompt.

Treat every loaded rule as binding. If references conflict, apply the safer ownership or side-effect boundary, record the conflict, and block rather than inventing compatibility.

## Activation and routing boundary

Use this workflow for:

- a request for an executable plan when a current sufficient Discovery artifact or content-equivalent framing exists;
- a request to prepare implementation when framing is current but the plan is missing or mechanically incomplete;
- a bounded Planning repair routed from Implementation because architecture, interfaces, data, sequencing, migration, deployment, or verification detail is missing or contradicted.

Do not bypass Discovery. A filename is not readiness: if framing is absent, stale, internally contradictory, or missing a material product decision, preserve evidence and route only the affected scope to `autonomous-project-discovery`. When a safe default and exact stop boundary let Planning define the remaining architecture, interfaces, verification, and conditional Task Contracts without inventing that decision, the upstream gate blocks only the named affected downstream boundary and must not block completion of the remaining Planning-owned contracts. Accept a nonstandard artifact when its content, lineage, freshness, and decision ownership satisfy the Discovery gate.

Do not bypass Implementation. A direct execution request with a current approved execution-ready plan routes to `autonomous-implementation`; Planning reopens only for a concrete plan defect. Ordinary questions, small bug fixes, narrow refactors, copy changes, and fully specified low-risk changes use ordinary scoped workflows unless the user explicitly invokes this pipeline.

Run the orchestrator in the top-level session. If invoked inside a worker and the host forbids nested delegation, return a hard blocker to the parent instead of pretending orchestration occurred.

## Invariants

- Use `protocol_version: autonomous-artifacts-v2`; durable artifacts and repository evidence, not conversation memory, carry state.
- `AGENT-STATE.md` has one writer: the top-level orchestrator. Only that orchestrator appends bounded events through the verified helper.
- On compaction, interruption, or handoff, treat summaries and checkboxes as claims. Reconcile state, reports, evidence, upstream revisions, and Git/filesystem evidence before dispatch.
- Evaluate equivalent Discovery artifacts by required content and freshness, never filename alone.
- Planning may inspect repository instructions, code, schemas, configs, and tests as read-only evidence. It writes only planning-run artifacts; it does not modify product code, migrations, tests, deployment config, or production state.
- Dispatch exactly one fresh Planning worker for the current `P-###` packet and wait for it before accepting or dispatching the next. Independent final review is also a bounded sequential packet. Do not parallelize Planning packets or writes to shared artifacts.
- Every packet has one primary outcome and is `Small`/1 or `Medium`/2. `Large` is invalid and must be split.
- Session budgets are ceilings: 6 weight units normally, 4 for high-risk, security/data/external-integration, or UI-related planning. Never rush, merge, or weaken verification to spend or fit the budget.
- A worker writes its report and evidence before returning at most ten lines. The orchestrator independently inspects representative artifacts and cited evidence before changing status to `verified`.
- After every worker return, the orchestrator writes an immutable attempt receipt such as `evidence/P-###/worker-return-attempt-001.md` with the attempt number, dispatch event/worker identity, host terminal status, disposition, observation time, exact returned line count, and bounded returned text/hash. Packet instructions or chat summaries are not evidence that the return was fresh, terminal, or at most ten lines.
- Record `requested_model`, `effective_model`, and fallback reason. When context telemetry is unavailable, record `unavailable`; never estimate hidden context.
- Every final implementation stage has an exact Task Contract. Never leave architecture-changing decisions for Implementation under vague labels such as “follow best practices.”
- Every Task Contract declares `Allowed side effects`. External, irreversible, destructive, or public effects default to `none/not_authorized` unless exact current authority is cited; owned files never imply authority to deploy, message, migrate live data, or mutate another system.
- Plan readiness is not execution approval. Persist `planning_approval_state` and the exact `planning_approval_evidence` mapping (`path`, `revision`, `authority`). Only a current execution request whose bounded scope and side effects stay within recorded authority may become `delegated_execution_authority`; otherwise use a canonical approval gate. Independent review and orchestrator acceptance never manufacture approval.
- Decision authority precedes impact labels. Before opening a human/product/security gate, map the exact choice to accepted Discovery/SCOPE ownership. Planning must decide an architecture, interface, data, workflow, or security mechanism that remains inside explicitly delegated outcomes, constraints, non-goals, and side-effect ceilings; a security label alone cannot revoke that delegation.
- Preferred tools, model classes, and automatic session restart are requests, not assumptions.

## Workflow

### 1. Bootstrap or rehydrate

Discover the host's actual capabilities, all applicable `AGENTS.md`/`CLAUDE.md`, repository/worktree root, established planning location, Git/filesystem baseline, current run artifacts, and upstream artifact candidates. Check `EVENTS.FROZEN` before any append and follow the protocol's successor-run recovery contract if present.

On resume, read and reconcile `AGENT-STATE.md`, `SCOPE.md`, the accepted Discovery source, `MASTER-PLAN.md`, active packet/report/evidence, `SESSION-HANDOFF.md`, events, and current repository evidence. Downgrade unsupported `verified` state.

Completion criterion: capabilities/fallbacks, physical path anchors, baseline revision/dirty paths, run root, event-adapter evidence, requested follow-through and its authority evidence, and reconciled next action are durable.

### 2. Apply the Discovery sufficiency and freshness gate

Inspect the candidate artifact by content. Require bounded users/outcomes, scope/non-goals, primary journeys and acceptance intent, hard constraints, dangerous assumptions, delegated architecture questions, owned residual unknowns, source revision, and freshness evidence. Compare its recorded sources to current repository/reference revisions and known contradiction paths.

Classify the gate exactly:

- `CURRENT`: content is sufficient and current; Planning may proceed.
- `INSUFFICIENT`: a framing-owned decision is absent; route the affected scope to Discovery.
- `STALE`: current evidence contradicts a framing-owned decision; mark the Discovery input stale, preserve supersession evidence, and route the affected scope to Discovery.

An architecture-only gap in otherwise current framing remains Planning-owned. Do not repeat broad Discovery merely to rename or restate valid framing.

Completion criterion: accepted source path/revision, field mapping, freshness checks, contradictions, and route are recorded in state and evidence.

### 3. Inspect repository evidence before freezing design

Read applicable instructions and the cheapest high-signal code, schemas, migrations, APIs, tests, build/deployment configuration, and established conventions needed to constrain the plan. Record unavailable surfaces explicitly. Do not freeze architecture from the prompt alone or defer all evidence gathering to Implementation.

Completion criterion: Planning claims cite current repository/reference evidence, are labeled proposals/assumptions, or have an owner and resolution boundary.

### 4. Run the Planning readiness review

Dispatch one read-only `P-###` worker to identify architecture-shaping decisions, repository contradictions, inherited assumptions, and Planning-specific unknowns. It must not repeat broad project Discovery. Route framing defects backward; retain architecture/interface/data/workflow/migration/testing/deployment/verification questions in Planning.

Completion criterion: every retained Planning decision has an owner, evidence, impact/reversibility classification, and required resolution point.

### 5. Decompose the plan

Create an ordered dependency graph of `P-###` packets. Each packet names one Planning outcome, inputs and revisions, Small/1 or Medium/2 weight, dependencies, verification, fallback, allowed decisions, stop boundary, report/evidence paths, and physical dispatch anchors. Split every Large packet before dispatch.

Typical outcomes are bounded architecture selection, one interface/data contract, one migration/recovery design, one workflow slice, one verification strategy, or final independent review. They are examples, not a mandatory packet count.

Completion criterion: every pending packet is independently dispatchable after its listed verified dependencies and the next packet fits the session ceiling.

### 6. Resolve and accept one packet sequentially

Preflight inputs, authority, capabilities, model fallback, dependencies, durable progress boundary, and physical containment. If any required item is missing, do not spawn; record `blocked`, `effective_model: not_executed`, `none_not_dispatched`, bounded preflight evidence, and the canonical gate.

When preflight passes, dispatch exactly one fresh worker with the packet verbatim, required instruction paths, accepted Discovery revision, repository evidence paths, allowed writes, report/evidence targets, requested/effective model contract, physical anchors, and at-most-ten-line return contract. Wait only through host-supported mechanisms.

After return, record the orchestrator-owned worker-return receipt, re-resolve every written target, inspect the report and representative output, verify cited evidence against repository files/commands, and append observation/sampling events. The receipt and stable artifact mtimes/embedded timestamps must not be later than the observation event; repair or block contradictory lifecycle time rather than backdating an event. Only then mark the packet verified and fold accepted decisions into `MASTER-PLAN.md`. Diagnose before a bounded retry; allow at most two evidence-driven remediation cycles.

Completion criterion: the packet is `verified`, `blocked`, or `superseded` with durable evidence and one next action.

### 7. Synthesize the execution-ready master plan

Maintain `MASTER-PLAN.md` from accepted packet outputs. Cover, when relevant: architecture and component boundaries; interfaces and versioning; data model and invariants; user/system workflows and failure recovery; security/privacy/accessibility/observability; migration/backfill/rollback; deployment/rollout; tests and real-flow verification; dependency ordering; checkpoints; human gates; and exact implementation Task Contracts.

When the user explicitly requests architecture, scale, resilience, or tier comparison—or current Discovery/equivalent evidence for this scope contains one named material workload, criticality, reliability, recovery, data, geographic, compliance, operational, integration, or cost trigger—include one bounded `System design scenario matrix`. Compare `Small / Baseline`, `Medium / Growth and HA`, and `Enterprise / High-scale or mission-critical` against the same product invariants; correctness, security, privacy, and safety requirements remain identical across all three profiles. A user count alone never selects a profile or topology; record the complete workload/risk envelope, explicit assumptions, recommendation, deltas, and measurable upgrade triggers. Without activation evidence, keep the lean plan and do not manufacture three architectures. Task Contracts cover only the authorized current profile unless the current execution request explicitly authorizes named future-profile work and records that request's path, revision, authority, and profiles.

Every Task Contract includes Goal, Inputs and freshness, dependencies, in/out scope, files or surfaces, decision authority, allowed side effects, concrete verification with expected signal, fallback/rollback point, UAT classification, and stop condition. An Implementation worker must not need conversation history to execute it. Before synthesis acceptance, reapply the observable implementation sizing rubric to each contract, prove every mandatory architecture/interface prerequisite from current repository evidence or explicitly authorize and stage its creation, and close every parsed/serialized data shape with exact malformed-input classification and deterministic ordering. When a public error tuple exposes both class/category and code, every stable code maps to exactly one class; combined class cells are invalid without an explicit deterministic predicate.

Also emit approval separately from technical readiness. Bind approval to the exact planning revision, requested execution scope, stop boundary, and side-effect authority. `delegated_execution_authority` cites a durable request/scope artifact; `explicitly_approved` cites the resolved canonical gate. `not_requested` and `approval_required` never route to Implementation as if approved.

Completion criterion: no stage is Large, dependencies are acyclic, verification is observable, ownership and approval state are explicit, and no product file was changed.

### 8. Run independent final plan review

After synthesis, dispatch a fresh reviewer as its own sequential `P-###` packet. The reviewer checks Discovery alignment, repository evidence, completeness, internal consistency, feasibility, dependency order, interface/data coherence, migration and recovery safety, verification coverage, exact Task Contracts, scope leakage, and unresolved decision ownership. It must independently repeat the per-contract sizing, evidence-backed mandatory-prerequisite, closed deterministic data-shape, and total per-code public-error class mapping checks; structural field completeness alone is not readiness evidence.

For an activated system-design matrix, the reviewer also verifies all three profiles, an evidence-driven recommendation, `required` / evidenced `not_applicable` / owned-and-triggered `deferred` dispositions, resilience/recovery/operations/security/cost coverage, identical correctness/security/privacy/safety requirements, and that Task Contracts implement only the authorized current profile unless the current execution request contains the exact future-profile authorization evidence.

Critical Planning defects become bounded repair packets. A framing defect routes to Discovery. A CRITICAL finding closes only through verified repair or an evidence-backed route to its owning stage; it can never be accepted as risk. Any non-critical risk acceptance names the authority and does not silently satisfy readiness. The author of a packet must not be treated as the independent acceptor of the overall plan.

Completion criterion: all critical findings are repaired or routed with evidence; review report and disposition are linked from `MASTER-PLAN.md` and state.

Fold only the review disposition into the final candidate, remove every pending-review marker, and write `evidence/final-plan-lock.md`. That lock records the reviewed candidate hash, final plan hash, and a mechanically checked candidate-to-final diff limited to review metadata. Any semantic change requires another fresh review.

### 9. Apply the Implementation readiness gate

Set `planning_readiness` exactly:

- `ready`: the plan is current, independently reviewed, executable in Small/Medium stages, and contains relevant architecture, interfaces, data/workflows, sequencing, verification, migration/deployment, rollback, gates, and delegated decision boundaries.
- `not_ready`: a named Planning packet, unresolved gate required before Implementation may start, or critical review finding remains.
- `stale`: newer evidence contradicts a Planning-owned decision.

Use `implementation_readiness: ready` only when `planning_readiness: ready`, the requested execution scope has current Task Contracts, and `pre_implementation_blocking_gates` is empty. Correctly owned downstream UI UAT or external gates scheduled inside a Task Contract remain in `scheduled_downstream_gates` and do not block Implementation from starting; they still block crossing their named stage boundary. Never use worker “done” as readiness evidence.

Set `planning_approval_state` independently:

- `not_requested`: this run was asked to plan only. The plan may be technically ready, but route `STOP` rather than inventing execution authority.
- `delegated_execution_authority`: a current durable request explicitly asked to execute this exact bounded scope, and every planned side effect remains within that recorded authority. `planning_approval_evidence` points to the request/scope artifact revision and names the granting authority.
- `approval_required`: execution is requested, but the exact scope, plan revision, or side effects exceed or lack current recorded authority. Open one canonical pre-Implementation approval gate; do not route to Implementation.
- `explicitly_approved`: the named authority accepted the exact planning revision, execution scope, stop boundary, and side effects through the resolved canonical gate. Evidence points to that gate revision.

Any superseding plan revision or authority/scope/side-effect change invalidates the prior mapping until it is re-established from current evidence. Planning readiness, independent review, and orchestrator acceptance are not approval substitutes.

### 10. Finish, route, or hand off

Route by ownership:

| Evidence state | Route |
|---|---|
| Current plan, planning only requested; approval state `not_requested` | `STOP` after durable handoff. |
| Current plan and approval state `delegated_execution_authority` or `explicitly_approved` | `IMPLEMENTATION`. |
| Current plan but approval state `approval_required` | Persist the canonical pre-Implementation approval gate and stop. |
| Framing missing/stale/contradicted | `DISCOVERY` for affected scope. |
| Planning-owned defect remains | Continue bounded `PLANNING` repair. |
| Human/external authority is required before Implementation may start | Persist one canonical pre-implementation gate and stop. |
| Human UI UAT/external gate is correctly scheduled after a later stage | Record it in that Task Contract and permit Implementation to start; never cross the later gate silently. |
| Session ceiling/cutover fires | Write `SESSION-HANDOFF.md` and end cleanly. |

Persist `continuation_kind`, verification, exact continuation value, and manual restart truth. A verified command requires an observed harmless capability check; otherwise write a precise natural-language `manual_host_action` naming `autonomous-planning`, the absolute run root, first-read files, gate input, and next action.

Finalize without circular hashes: freeze the final plan, review, receipts, final verification, response, and other terminal evidence; write an immutable `evidence/finalization-manifest.md` with their exact hashes; append the terminal event referencing only that immutable manifest/frozen artifacts. Then update the live `AGENT-STATE.md` and `SESSION-HANDOFF.md` with the returned terminal anchor. The terminal event must not reference either mutable index. Never modify a manifest-listed artifact afterward; a required change creates a new versioned artifact and later event.

## Bounded authority

Planning may decide low-impact reversible design choices and medium-impact choices only within authority delegated by current framing. High-impact, security/legal-sensitive, public, expensive, destructive, user-facing, or hard-to-reverse choices require explicit authority unless the upstream artifact grants the exact choice.

Planning may write only run artifacts and bounded scratch evidence. It may not implement product code, run destructive migrations, deploy, publish, modify secrets, commit unless explicitly authorized, or silently absorb Discovery/Implementation ownership.

## Completion checklist

Planning is complete only when:

- `AGENT-STATE.md`, `SCOPE.md`, accepted Discovery source, and `MASTER-PLAN.md` are current and mutually consistent;
- the Discovery field-level sufficiency/freshness gate and repository evidence are recorded;
- every verified packet has report-before-state evidence and representative orchestrator sampling;
- every dispatched worker has one immutable terminal `worker-return-attempt-###.md` receipt, dispatch/receipt/retry/remediation counts reconcile, and artifact/receipt/event times are monotonically observable;
- every Large unit was split and session ceilings were treated as maximums, not targets;
- requested/effective models and unavailable telemetry are honest;
- a fresh independent reviewer accepted the plan or every critical finding has a durable route;
- the exact final plan is review-hash-bound or has a mechanically verified metadata-only `final-plan-lock.md`, with no pending-review marker;
- exact Task Contracts make the requested scope executable without conversation history;
- `planning_readiness`, `implementation_readiness`, `planning_approval_state`, exact approval evidence, next stage, gates, and continuation value agree;
- no product code, unrelated dirty path, secret, deployment, or unapproved external state was changed.
- the terminal event references an immutable finalization manifest, all listed hashes still match, and the live state/handoff carry the returned terminal anchor without being terminal-event references.
