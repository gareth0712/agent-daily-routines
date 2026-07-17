---
name: autonomous-project-discovery
description: Use whenever a greenfield project, product, repository, or application has no current sufficient Discovery artifact or equivalent, even when the request is detailed; also use for materially ambiguous substantial new subsystems or when the user asks whether an idea should exist. Skip routine, well-specified work in an understood existing project.
---

# Autonomous Project Discovery

## Purpose

Turn project fog into a bounded, evidence-backed framing and an explicit Planning-readiness decision. Discovery owns the problem, users, outcomes, scope, non-goals, hard constraints, acceptance intent, and project-wide uncertainty. Planning owns detailed architecture, interfaces, data models, milestones, migration, deployment, and verification design.

Discovery produces canonical `DISCOVERY.md` and `AGENT-STATE.md`. It may create isolated disposable examples or prototypes that unlock a named decision, but it does not create production implementation.

## Required references

Load the six binding references progressively. A deferred read becomes required when its pointer fires:

1. During bootstrap, read [Artifact protocol](references/artifact-protocol.md) and [Harness adapters](references/harness-adapters.md) completely before writing run state or dispatching a worker. Capability-check Python and run the bundled `scripts/append_event.py --self-test` contract before initializing `EVENTS.jsonl`; use an independently verified equivalent only when Python is unavailable.
2. Before territory, depth, framing, unknown, gate, or readiness decisions, read [Discovery method](references/discovery-method.md) completely.
3. Before packet decomposition, dependency ordering, dispatch, budget cutover, or retry decisions, read [Work sizing](references/work-sizing.md) completely.
4. Before writing or updating an artifact, read that artifact's complete section in [State templates](references/state-templates.md); read additional sections only when their artifact is needed.
5. Read [Launcher template](references/launcher-template.md) completely only when starting from it or when the user requests a copyable launcher prompt.

Treat every loaded rule as binding. If the references conflict, apply the safer boundary and record the conflict as `blocked`; do not invent a compatibility behavior.

## Activation boundary

Use this workflow for:

- any greenfield/new project, product, repository, application, platform, service, or system without a current sufficient Discovery artifact or equivalent, even when the prompt appears detailed or well specified;
- a substantial new subsystem whose outcome, users, scope, risks, or constraints remain materially ambiguous;
- a request to explore whether an idea should exist;
- stale or insufficient framing routed backward by Planning or Implementation.

Do not activate the full workflow for ordinary questions, small bug fixes, narrow refactors, copy changes, or well-specified work in an understood existing project. If invoked for one of those existing-project cases and the evidence supports `skip`, record the depth decision and route to the ordinary scoped workflow.

Do not use prompt detail as a substitute for a current upstream artifact. A greenfield request without a sufficient Discovery artifact enters Discovery first and selects `full`; a detailed brief may make that pass short and immediately ready, but it may not bypass the stage. A current equivalent artifact may satisfy the gate when it contains the required framing and freshness evidence even if its filename differs.

Run the orchestrator in the top-level session. If this skill is invoked inside a worker and the host forbids nested delegation, return a hard blocker to the parent instead of pretending orchestration occurred.

## Invariants

- Use protocol `autonomous-artifacts-v2`; durable files, not conversation memory, carry state.
- `AGENT-STATE.md` has one writer: the orchestrator.
- `AGENT-STATE.md` is the sole authoritative control-plane index. The top-level orchestrator alone appends bounded audit evidence to canonical `EVENTS.jsonl` through bundled `scripts/append_event.py` after its self-test passes; never patch, edit, truncate, or rewrite existing event lines. `EVENTS.FROZEN` forbids all later appends; close the predecessor with only state/gate/handoff evidence, hash it, make it immutable, and recover in a distinct run root with the exact lineage schema. Never delete the marker or repair old event bytes in place.
- Use only these Discovery depths: `skip`, `targeted`, `full`.
- Use only these unknown classes: `known_known`, `known_unknown`, `unknown_known`, `candidate_unknown_unknown`.
- Every retained unknown or research/prototype packet names a non-empty `decision_unlocked`, an owner, and an allowed disposition.
- A research action exists only when it unlocks a named decision. Drop open-ended exploration.
- A worker writes its reusable report and evidence before returning. The orchestrator inspects them before changing the packet to `verified`.
- Every dispatch carries lexical absolute and physical/canonical repository, worktree, run-root, working-directory, input, output, report, and evidence anchors. Portable relative paths remain the canonical artifact references.
- The top-level orchestrator, not the worker, owns path-containment acceptance. It rejects or blocks on escaping links, junctions, mount points, Windows reparse points, unresolved nearest existing ancestors, or unavailable physical-path inspection, and repeats the physical check after worker writes. Worker path checks are defense in depth only.
- Worker returns contain at most ten lines. They point to durable artifacts; they do not reproduce the work.
- Never request or persist chain-of-thought, secrets, full transcripts, or unbounded logs. Store conclusions, assumptions, decisions, redacted excerpts, commands, and reproducible evidence.
- Preferred models and context telemetry are optional capabilities. Record requested/effective values and fallbacks; never claim unavailable capabilities ran.
- Manual restart and user preference/UAT gates are real pauses. Describe the run as resumable bounded autonomy, not literal unattended multi-session execution.

## Workflow

### 1. Bootstrap or rehydrate

Discover host capabilities, applicable `AGENTS.md`/`CLAUDE.md`, repository root, established planning location, Git/filesystem state, relevant references, existing artifacts, and prior run state. On resume or after compaction, distrust the conversation summary and reconstruct from the protocol artifacts and repository evidence. Check for `EVENTS.FROZEN` before any append. If present, never append to that stream; apply the bounded predecessor-closure and successor-lineage procedure in `artifact-protocol.md` and `state-templates.md`.

Completion criterion: capabilities and fallbacks are recorded, the run root is known, the bundled append self-test (or independently verified equivalent) has passed with bounded evidence, canonical `EVENTS.jsonl` has a `run_initialized` event, no freeze marker exists, pre-existing dirty paths are inventoried when Git exists, and existing artifact freshness has been checked.

### 2. Inspect territory before interviewing

Read the cheapest high-signal repository, product, domain, and reference evidence. Separate explicit facts from assumptions and proposals. Do not ask the user for information the available tools can observe.

Completion criterion: every framing claim has evidence, is labeled as an assumption/proposal, or is listed as an owned unknown.

### 3. Select Discovery depth

Apply the factor gate in `discovery-method.md` to greenfield status, ambiguity, blast radius, irreversibility, and artifact freshness. Record exactly one of `skip`, `targeted`, or `full`, with evidence for every factor.

Completion criterion: `AGENT-STATE.md` and `DISCOVERY.md` agree on the selected depth and its evidence.

### 4. Establish the framing

Record stakeholders, users, underlying problem, desired outcomes, scope, non-goals, constraints, existing assets, primary journeys, acceptance intent, facts, assumptions, proposals, and rejected framings. Challenge the requested solution against simpler validation paths and direct contradictions.

Keep architecture candidates at the level needed to expose constraints or decisions. Do not select detailed components, API/data contracts, implementation stages, or detailed test/deployment plans; route those to Planning.

Completion criterion: the problem and outcome are testable, scope has a stop boundary, and proposals are not presented as facts.

### 5. Map and prioritize uncertainty

Classify retained items with the four exact unknown classes. Search for project-specific blind spots rather than claiming exhaustive unknown-unknown coverage. Give every item a `decision_unlocked`, owner, and allowed disposition.

Use one focused user question only when a material decision cannot be resolved safely from evidence, research, or a cheap disposable example. For preference-heavy `unknown_known` items, show meaningfully different examples or prototypes and wait for reaction.

Completion criterion: every remaining uncertainty is connected to a decision, owner, and stopping disposition.

### 6. Decompose bounded packets

Create sequential `D-###` packets for only the inspections, framing challenges, research, or prototypes still needed. Each packet has one primary outcome, explicit inputs, `decision_unlocked`, Small/1 or Medium/2 sizing, dependencies, observable completion, verification, and fallback. Split every Large unit before dispatch.

Independent read-only scouts may run in parallel only when their outputs are isolated and one primary packet remains the acceptance unit. State-changing work stays sequential.

Completion criterion: every pending packet is dispatchable without depending on a later packet, and the next packet fits the session budget.

### 7. Resolve and accept one packet

Before dispatch, preflight every required input, capability, authority, dependency, and path anchor. The top-level orchestrator resolves and records lexical and physical/canonical roots, walks existing target components with no-follow metadata, and validates every read/write target against an allowed physical root. For an uncreated target it resolves the nearest existing ancestor, proves that ancestor is contained, rejects a symlink, junction, mount, or Windows reparse traversal, then creates/re-resolves only required directory components and leaves the assigned file leaf for its authorized writer. A string-prefix or lexical-only comparison is never proof. If the host cannot establish these facts, do not dispatch.

When any preflight requirement is missing, set the packet to `blocked` without changing `completed_weight`, set `effective_model: not_executed` with a non-empty block/fallback reason, set report to `none_not_dispatched`, write bounded orchestrator-owned preflight evidence plus `gates/G-###.md`, and append the status/preflight/gate events. Choose the canonical gate type that matches the blocker: human decision gates remain human pauses; `capability`, `environment`, and `internal_recovery` gates carry explicit non-human owners and recovery routes when no human answer is required. `not_executed` is valid only when no worker ran.

When preflight passes, dispatch one fresh worker with the packet verbatim, applicable instruction paths, capability/model record, ten-line return contract, portable artifact paths, the declared progress boundary, and the orchestrator-recorded lexical plus physical/canonical anchors. The worker repeats normalization, no-follow component inspection, and physical containment, then writes the assigned worker-progress marker before substantive analysis; the marker is progress evidence only and never satisfies acceptance. After work, it inventories the assigned root and checks scoped out-of-root changes. Never rely on a relative path when worktrees, nested agents, or differing patch/shell bases are possible. Wait using only the host-supported mechanism and apply the durable-progress circuit breaker in `work-sizing.md`; `running` status alone is not progress.

The worker writes reusable artifacts first. Before accepting them, the top-level orchestrator physically re-resolves every written target and its existing components, confirms the canonical target still lies under the recorded canonical run root, and records the post-write containment evidence. A changed/escaping component or inability to recheck blocks acceptance and opens `internal_recovery` or `environment` as appropriate. Independently inspect representative output and cited evidence; rerun a relevant check when available. Append bounded report-observation, evidence-observation, and artifact-sampling events before the verified transition. Only then update `AGENT-STATE.md` to `verified`. Diagnose failures before a bounded retry; apply the circuit breaker in `work-sizing.md`.

Completion criterion: the packet is `verified`, `blocked`, or `superseded` with inspectable evidence and an explicit next action.

### 8. Assess Planning readiness

Write exactly one summary line in `DISCOVERY.md`: `Planning readiness: READY` or `Planning readiness: NOT_READY`.

`discovery_readiness` is the current Discovery artifact's handoff/entry readiness for Planning. Set it in `AGENT-STATE.md` to exactly one of:

- `ready`: framing is current and satisfies the readiness rubric;
- `not_ready`: a named blocking decision, packet, or canonical human/external/operational gate remains;
- `stale`: current repository/reference evidence contradicts the artifact revision.

Derive the exact `DISCOVERY.md` line from that field: `ready` => `Planning readiness: READY`; `not_ready` or `stale` => `Planning readiness: NOT_READY`. The separate `planning_readiness` field means an actual Planning artifact's readiness for its downstream stage, so it remains `not_assessed` until Planning exists.

Discovery readiness means the problem/outcome are clear, scope is bounded, primary journeys and hard constraints are known, architecture-changing ambiguity is resolved or explicitly delegated, dangerous assumptions are visible, and every remaining unknown has an owner. It does not mean zero uncertainty.

Completion criterion: the readiness value, evidence, blocker list, and route agree across `DISCOVERY.md` and `AGENT-STATE.md`.

### 9. Finish, route, or hand off

Use these testable routes:

| State | Route |
|---|---|
| `skip` | Record why ordinary scoped work is sufficient; do not create Planning packets. |
| `ready` and only exploration was requested | Stop after Discovery and preserve the exact continuation command. |
| `ready` and planning/building was requested | Route to Planning; never jump directly to Implementation. |
| `not_ready` with a resolvable packet | Continue bounded Discovery. |
| `not_ready` with a material preference/product decision | Request one focused human gate, persist the pause, and stop. |
| `stale` or framing-changing contradiction | Set `next_stage: DISCOVERY`, preserve supersession evidence, and rediscover only the affected scope. |
| Architecture/interface/sequencing detail only | Preserve Discovery framing and route the question to Planning. |

Before a required session cutover, write `SESSION-HANDOFF.md` and persist `continuation_kind`, `continuation_verification`, and the exact `continuation_command` value. Use `verified_command` only after a harmless capability check proves the executable and invocation form. Otherwise use `manual_host_action` with precise natural language naming this skill, the absolute run root, first-read files, gate input, and next action. Never invent CLI syntax. End cleanly without compressing work, reducing verification, or silently crossing a user gate.

## Bounded authority

Proceed autonomously only inside recorded scope and permissions. Low-impact reversible framing choices may be decided and recorded. Medium-impact reversible choices require delegated authority. High-impact, security/legal-sensitive, user-facing, expensive, difficult-to-reverse, destructive, public, or credential-dependent choices require explicit authority unless the current artifact grants that exact choice.

Discovery may write run artifacts and isolated disposable prototypes. It may not modify product code, perform deployment/publishing, change secrets, commit unless authorized, or decide detailed system design owned by Planning.

## Completion checklist

Discovery is complete only when:

- canonical `AGENT-STATE.md`, `SCOPE.md`, and `DISCOVERY.md` are current and mutually consistent;
- the depth gate and territory evidence are recorded;
- facts, assumptions, proposals, and rejected framings are distinguishable;
- retained unknowns use the exact class/owner/disposition contract;
- every retained packet/report/evidence artifact has been sampled by the orchestrator;
- readiness and the backward/forward route are explicit and testable;
- no production implementation or Planning-owned detail was silently created;
- the continuation kind, verification evidence, exact value, and whether restart is manual are honest;
- representative artifacts, not exit codes or worker self-reports alone, support the verdict.
