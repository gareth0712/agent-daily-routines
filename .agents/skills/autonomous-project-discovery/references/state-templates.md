# Discovery State Templates

Replace every brace-delimited value with observed run data before accepting an artifact. Remove optional rows that truly do not apply and record the reason in `Assumptions and omissions`; never leave unresolved placeholders. Use forward-slash portable paths for canonical artifact references and record both lexical absolute and physical/canonical paths for worker dispatch anchors.

## Contents

- [`AGENT-STATE.md`](#agent-statemd)
- [`EVENTS.jsonl`](#eventsjsonl)
- [`evidence/recovery/frozen-predecessor.md`](#evidencerecoveryfrozen-predecessormd)
- [`SCOPE.md`](#scopemd)
- [`DISCOVERY.md`](#discoverymd)
- [`packets/D-###.md`](#packetsd-md)
- [`gates/G-###.md`](#gatesg-md)
- [`reports/D-###-report.md`](#reportsd--reportmd)
- [`SESSION-HANDOFF.md`](#session-handoffmd)

## `AGENT-STATE.md`

Only the top-level orchestrator writes this file.

`discovery_readiness` is this Discovery artifact's handoff/entry readiness for Planning. It alone derives the `DISCOVERY.md` line: `ready` => `Planning readiness: READY`; `not_ready` or `stale` => `Planning readiness: NOT_READY`. `planning_readiness` instead describes an actual Planning artifact's downstream readiness and remains `not_assessed` until Planning exists.

```markdown
# Agent State

protocol_version: autonomous-artifacts-v2
workflow_type: discovery
active_pipeline_stage: DISCOVERY
run_id: {YYYYMMDD-goal-slug-N}
repository_root: {absolute repository or project root}
worktree_root: {absolute active worktree root, or same value as repository_root}
run_root: {portable project-relative planning/run path}
canonical_repository_root: {physical/canonical existing repository root}
canonical_worktree_root: {physical/canonical existing worktree root}
canonical_run_root: {physical/canonical run root, or canonical nearest existing ancestor plus declared uncreated suffix until created}
events_path: EVENTS.jsonl
events_accepted_count: {0 before first append | accepted_event_count returned by last successful append}
events_accepted_tip: {64 lowercase zeroes before first append | accepted_event_tip returned by last successful append}
events_accepted_file_sha256: {e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 before first append | accepted_events_sha256 returned by last successful append}
events_anchor_updated_at: {ISO-8601 timestamp and helper result evidence path}
updated_at: {ISO-8601 timestamp}

## Harness and capabilities

harness: {Claude Code | Codex | generic host name}
restart_mode: {automatic only when explicitly supported | manual}
context_telemetry: {reported percentage | unavailable}

| capability | status | observed evidence | fallback |
|---|---|---|---|
| fresh_isolated_worker | {available | unavailable | unknown} | {host surface inspected} | {hard blocker when unavailable} |
| model_selection | {available | unavailable | unknown} | {host surface inspected} | {host_default when unavailable} |
| context_telemetry | {available | unavailable | unknown} | {host signal inspected} | {weight budget without estimation} |
| ui_observation | {available | unavailable | unknown} | {host surface inspected} | {human gate when required} |
| new_top_level_session | {available | unavailable | unknown} | {host surface inspected} | {manual continuation command} |

## Models

orchestrator_requested_model: {user preference or highest-reasoning preference}
orchestrator_effective_model: {confirmed model ID | host_default}
orchestrator_fallback_reason: {none when confirmed | observed selector limitation}

## Instructions and repository baseline

applicable_instruction_paths:
- {project-relative instruction path, or none_found after an explicit search}

baseline_git_sha: {Git SHA | not_a_git_repository}
repository_revision: {current Git SHA, content digest, or dated filesystem revision}
pre_existing_dirty_paths:
- {path present before this run, or none_observed}

## Scope and authority

scope_path: SCOPE.md
stop_boundary: {observable Discovery stop boundary}
risk_mode: {normal | high_risk | ui}
allowed_external_effects: {bounded list | none}
commit_policy: {not_authorized | path_limited_authorized}

## Pipeline readiness

discovery_depth: {skip | targeted | full}
discovery_readiness: {ready | not_ready | stale}
planning_readiness: not_assessed
implementation_readiness: not_assessed
next_stage: {DISCOVERY | PLANNING | STOP}

## Artifact lineage

discovery_artifact_path: DISCOVERY.md
discovery_revision: {stable revision or digest}
repository_revision_at_discovery: {revision inspected by DISCOVERY.md}
derived_from: {source artifact revision | none_for_initial_discovery}
freshness_evidence: {paths/revisions/commands proving currency}
supersedes: {prior discovery revision | none_for_initial_revision}

planning_artifact_path: {current equivalent path | none_created}
planning_revision: {current revision | not_assessed}
implementation_artifact_path: {current equivalent path | none_created}
implementation_revision: {current revision | not_assessed}

predecessor_run_root: {portable project-relative frozen run root | none_for_initial_run}
predecessor_state_sha256: {final lowercase 64-hex SHA-256 of predecessor AGENT-STATE.md | none_for_initial_run}
predecessor_events_sha256: {final lowercase 64-hex SHA-256 of predecessor EVENTS.jsonl | none_for_initial_run}
predecessor_freeze_sha256: {final lowercase 64-hex SHA-256 of predecessor EVENTS.FROZEN | none_for_initial_run}
recovery_evidence_path: {evidence/recovery/frozen-predecessor.md | none_for_initial_run}
recovery_reason: {bounded frozen-stream recovery reason | none_for_initial_run}

## Session control

session_budget: {6 | 4}
completed_weight: {sum of verified packet weights}
next_packet_weight: {1 | 2 | none}
remediation_cycles_this_session: {0 | 1 | 2}

## Packets

| packet | decision_unlocked | size | weight | dependencies | status | report | evidence | requested_model | effective_model | fallback_reason | retry_count |
|---|---|---|---:|---|---|---|---|---|---|---|---:|
| D-001 | {named decision} | {Small | Medium} | {1 | 2} | {verified packet IDs | none} | {pending | in_progress | verified | blocked | superseded} | {reports/D-001-report.md | none_not_dispatched} | evidence/{bounded evidence or preflight path} | {requested preference} | {confirmed model ID | host_default | not_executed} | {none when confirmed | non-empty observed fallback/block reason} | {0 | 1 | 2} |

`effective_model: not_executed` and report `none_not_dispatched` are paired and permitted only when preflight blocked dispatch before any worker ran. Such a block leaves `completed_weight` unchanged.

## Gates and UAT

uat_state: {not_required | pending_preference_reaction | approved | rejected}
pending_human_gate: {one material question and decision | none}
pending_operational_gate: {capability/environment/internal recovery blocker and owner | none}
gate_evidence_path: {one active gates/G-###.md | none}

## Next action

next_action: {one evidence-based action}
continuation_kind: {verified_command | manual_host_action}
continuation_verification: {harmless capability check plus observed signal | command_not_verified_use_manual_host_action}
continuation_command: {exact verified command | precise natural-language host action naming autonomous-project-discovery, absolute run root, first-read files, gate input, and next action}
blockers:
- {named blocker with owner and recovery route, or none}

## Assumptions and omissions

- {explicit assumption, owner, validation path, and effect if false, or none}
```

## `EVENTS.jsonl`

Only the top-level orchestrator appends this bounded audit artifact. `AGENT-STATE.md` remains the sole authoritative control-plane index. Never edit or reorder existing lines. Append a contradiction event only while the current stream is healthy; a frozen predecessor receives no later event.

Each line is one JSON object using this schema:

```json
{"event_seq": 1, "timestamp": "{fresh timezone-aware ISO-8601 timestamp strictly later than the prior event}", "event_type": "{event type}", "stage": "DISCOVERY", "packet_id": "{D-### | none}", "from_status": "{prior status | none}", "to_status": "{new status | none}", "actor": "top_level_orchestrator", "references": [{"path": "{existing portable artifact path}", "revision": "{reproducible artifact revision}", "sha256": "{actual lowercase 64-hex SHA-256 of current file bytes}"}], "evidence_summary": "{bounded observation without secrets, chain-of-thought, transcripts, or raw logs}", "previous_event_sha256": "{64 zeroes for first event | prior validated event_sha256}", "event_sha256": "{canonical event SHA-256 defined by artifact-protocol.md}"}
```

Use monotonically increasing `event_seq` and append events for `run_initialized`, `frozen_predecessor_reconciled` when applicable, `packet_created`, every `packet_status_transition`, `path_containment_preflight`, `preflight_blocked`, `worker_dispatched`, `report_observed`, `evidence_observed`, `path_containment_postwrite`, `artifact_sampled`, `packet_verified`, `gate_opened`, `gate_resolved`, `handoff_written`, `stage_routed`, and `reconciliation_contradiction` only while the current stream is healthy.

Compute the SHA-256 at append time for every existing local reference and place it in the key named exactly `sha256`. Never write `hash`, `sha256: none`, a placeholder digest, or an informal revision in the digest field. Omit a not-yet-existing file from `references` and name its expected path only in `evidence_summary`. Read a fresh clock value for every line and require strict timestamp increase; do not reuse one timestamp for a batch.

Use the verified `append_event` adapter for each complete line. CLI/reference validation occurs before freezing; then the helper arms `EVENTS.FROZEN` before reading the actual prefix. It validates the complete JSONL chain plus the durable accepted count/tip/file digest, appends once, proves the byte/chain postconditions, returns the next accepted anchor, and only then removes the marker. A malformed/partial/chain-invalid stream or anchor mismatch remains frozen. Never edit, patch, truncate, replace, or repair an existing stream.

Default commands (replace every brace value; omit packet/status flags that do not apply):

```text
python {absolute-skill-root}/scripts/append_event.py --self-test --run-root {absolute-run-root}
python {absolute-skill-root}/scripts/append_event.py --run-root {absolute-run-root} --stage DISCOVERY --event-type {event_type} --packet-id {D-###} --from-status {pending|in_progress|blocked|verified|superseded} --to-status {pending|in_progress|blocked|verified|superseded} --reference {portable/existing/path} --evidence-summary {bounded summary} --expected-event-count {events_accepted_count} --expected-event-tip {events_accepted_tip} --expected-events-sha256 {events_accepted_file_sha256}
```

The script writes exact reference hashes and chained events, then returns bounded metadata including `accepted_event_count`, `accepted_event_tip`, and `accepted_events_sha256`. Persist all three in state before another append. Their comparison detects history inconsistent with that durable anchor, not an attacker who can rewrite both stream and anchors. After every event postcondition passes, the helper may retry only deletion of its own marker for Windows sharing/lock errors `32` or `33`: four total attempts, 25ms between failures, and fresh validation of the original identity, containment, regular single-link type, and exact marker bytes before each attempt. It never repeats the event write; exhaustion, any other error, disappearance, or validation change leaves/restores the stream frozen. Any marker remaining after the helper returns, or any nonzero append result, stops all later event appends. Perform the predecessor's one-time closure by updating only `AGENT-STATE.md`, one `internal_recovery` gate, and `SESSION-HANDOFF.md`; reopen/hash them, then keep the whole predecessor immutable. Recover only into a distinct run root using the exact lineage fields and binding shared template. Callers never remove the marker or repair/retry the stream.

A `verified` transition is invalid unless earlier events for the same packet record passing post-write physical containment, the existing report, existing evidence, and orchestrator sampling. On recovery, reconcile state, files, and events and downgrade unsupported `verified` state. Append `reconciliation_contradiction` only to a healthy current stream. For a frozen predecessor, record the contradiction in closure/successor evidence and append only `frozen_predecessor_reconciled` to the successor stream. `EVENTS.jsonl` improves production handoff but does not replace runner-owned lifecycle audit in evaluations.

## `evidence/recovery/frozen-predecessor.md`

Use the exact binding template in `artifact-protocol.md` under `Binding evidence/recovery/frozen-predecessor.md template`. Do not fork, omit, or locally reinterpret its successor linkage, closure digests, observation times, physical-containment evidence, or six required state-lineage values.

## `SCOPE.md`

```markdown
# Discovery Scope

run_id: {run ID}
scope_revision: {stable revision or digest}
updated_at: {ISO-8601 timestamp}

## Goal and evidence

- Desired outcome: {observable project outcome}
- Why now: {evidence or explicitly unverified motivation}
- Underlying problem hypothesis: {problem statement without assuming the requested solution}

## In scope

- {bounded product, repository, subsystem, user, or decision surface}

## Out of scope

- {explicitly excluded adjacent work}

## Stop boundary

Discovery stops after a current `DISCOVERY.md`, an explicit Planning-readiness decision, and a durable next route. It does not produce production code or Planning-owned detailed architecture, interfaces, data contracts, milestones, migration, deployment, or verification plans.

## Authority

- Reversible artifact choices: {delegated boundary}
- Disposable prototypes: {allowed isolated path and limits | not_authorized}
- Read-only external research: {allowed sources/decision boundary | not_authorized}
- Commits/checkpoints: {not_authorized | exact authorized paths}
- Irreversible/public/destructive effects: {exact authority | not_authorized}
- Credentials/secrets: never persist; {availability boundary}

## Human gates

- Product/preference approval: {one-question policy and owner}
- Security/legal/expensive decisions: {approval owner}
- UI/prototype reaction: {required evidence and pause behavior | not_required}
- Manual restart: {required | host-confirmed automatic action}

## Acceptance

- {observable framing/readiness criteria}
- {representative artifact/evidence sampling required}
```

## `DISCOVERY.md`

```markdown
# Discovery

run_id: {run ID}
discovery_revision: {stable revision or digest}
repository_revision: {revision inspected}
derived_from: {source revision | none_for_initial_discovery}
supersedes: {prior discovery revision | none_for_initial_revision}
freshness_evidence: {paths/revisions/commands proving currency}
updated_at: {ISO-8601 timestamp}

## Executive framing

- Underlying problem: {evidence-backed problem}
- Desired outcome: {observable outcome}
- Why this initiative may or may not exist: {direct evidence-backed challenge}
- Selected depth: {skip | targeted | full}

## Depth evidence

| factor | finding | source path/excerpt or not_applicable reason |
|---|---|---|
| greenfield_status | {finding} | {evidence} |
| ambiguity | {finding} | {evidence} |
| blast_radius | {finding} | {evidence} |
| irreversibility | {finding} | {evidence} |
| artifact_freshness | {finding} | {evidence} |

## Stakeholders, users, and outcomes

| stakeholder/user | need or impact | desired outcome | evidence/confidence |
|---|---|---|---|
| {specific group} | {need/impact} | {observable outcome} | {source and confidence} |

## Primary journeys and acceptance intent

| journey | start and desired finish | acceptance intent | unresolved framing |
|---|---|---|---|
| {user journey} | {bounded start/finish} | {observable intent, not detailed test design} | {owned item | none} |

## Scope, non-goals, and constraints

### In scope
- {bounded item}

### Non-goals
- {excluded item}

### Hard constraints
- {constraint with source}

### Existing assets and dependencies
- {asset/dependency with source and freshness}

## Framing ledger

### Explicit facts
- {fact and evidence}

### Evidence-backed inferences
- {inference, evidence, and confidence}

### Assumptions to test
- {assumption, owner, and effect if false}

### Proposals
- {proposal and decision owner}

### Rejected framings
- {rejected framing and evidence-based reason}

## Unknowns and decision ownership

| unknown | class | decision_unlocked | owner | disposition | confidence/evidence | falsification or next signal |
|---|---|---|---|---|---|---|
| {retained item} | {known_known | known_unknown | unknown_known | candidate_unknown_unknown} | {named decision} | {role/person/stage} | {must_resolve_before_planning | resolve_before_implementation | planner_may_propose | implementation_may_decide | defer | experiment | explicit_approval} | {bounded evidence} | {observable signal} |

## Project-specific blind spots

| candidate blind spot | project evidence making it plausible | decision_unlocked | confidence | cheapest falsification |
|---|---|---|---|---|
| {candidate, without completeness claim} | {specific source/intersection} | {named decision} | {low | medium | high} | {bounded signal} |

## Framing challenge

- Requested solution versus underlying problem: {finding}
- Simpler validation path or existing alternative: {finding}
- Contradictions/excess scope: {finding}
- Boundary handed to Planning: {constraints/decision questions only; no selected detailed architecture/API/data/stages}

## Research and prototype packets

| packet | action | decision_unlocked | owner | disposition | stop condition | artifact/report |
|---|---|---|---|---|---|---|
| D-001 | {bounded inspection/research/disposable example} | {named decision} | {owner} | {must_resolve_before_planning | resolve_before_implementation | planner_may_propose | implementation_may_decide | defer | experiment | explicit_approval} | {observable stopping signal} | {packet and report paths} |

## Decisions and delegated uncertainty

| decision | outcome or bounded alternatives | authority/evidence | downstream owner |
|---|---|---|---|
| {named decision} | {outcome or choices} | {source/approval} | {Discovery | Planning | Implementation | user role} |

## Planning readiness evidence

- Problem/outcome clarity: {pass/fail evidence}
- Bounded scope and stop boundary: {pass/fail evidence}
- Primary journeys and hard constraints: {pass/fail evidence}
- Framing-changing ambiguity: {resolved/blocker}
- Architecture-changing ambiguity: {resolved or explicitly delegated/blocker}
- Dangerous assumptions: {visible with owners/blocker}
- Remaining unknown ownership: {all owned/blocker}

Planning readiness: {READY | NOT_READY}

## Route and residual uncertainty

- Current `discovery_readiness`: {ready | not_ready | stale}
- Next stage: {DISCOVERY | PLANNING | STOP}
- Residual owned uncertainty: {items, owners, dispositions}
- Canonical gates: {human, external, or operational gate with owner/recovery | none}
- Continuation kind: {verified_command | manual_host_action}
- Continuation verification: {harmless capability check and signal | command_not_verified_use_manual_host_action}
- Exact continuation value: {existing `continuation_command` value}
```

## `packets/D-###.md`

```markdown
# Discovery Packet D-{sequence}

packet_id: D-{sequence}
primary_outcome: {one observable outcome}
decision_unlocked: {one named decision}
owner: {orchestrator-assigned owner}
disposition: {must_resolve_before_planning | resolve_before_implementation | planner_may_propose | implementation_may_decide | defer | experiment | explicit_approval}
size: {Small | Medium}
weight: {1 | 2}
requested_model: {preference}
report_path: reports/D-{sequence}-report.md
evidence_root: evidence/D-{sequence}/

## Goal

{One bounded outcome and why it unlocks the named decision.}

## Inputs and freshness

- {source path/revision}
- {applicable instruction path}
- Dependencies: {verified D packet IDs | none}

## Pre-dispatch record

- Preflight status: {passed | blocked}
- Required input/capability/authority/path checks: {bounded results}
- Preflight evidence: evidence/D-{sequence}/preflight.md
- Canonical gate: {gates/G-###.md | none}
- Canonical gate type: {preference | product_decision | authority | uat | external_evidence | security_legal | capability | environment | internal_recovery | none}
- Block/fallback reason: {non-empty reason when blocked | none}

If preflight is `blocked`, do not dispatch: keep completed weight unchanged, use `effective_model: not_executed`, use report `none_not_dispatched`, write the bounded preflight evidence and canonical gate, and append transition events. `not_executed` is valid only when no worker ran.

## Physical/canonical dispatch path anchors

lexical_repository_root: {normalized absolute repository root}
canonical_repository_root: {physical/canonical existing repository root}
lexical_worktree_root: {normalized absolute active worktree root}
canonical_worktree_root: {physical/canonical existing worktree root}
lexical_run_root: {normalized absolute run root}
canonical_run_root: {physical/canonical run root after creation}
working_directory: {lexical absolute and physical/canonical worker working directory}
input_paths:
- {lexical absolute path; physical/canonical path; allowed read root}
output_paths:
- {lexical absolute path; physical/canonical path or nearest existing ancestor plus uncreated suffix}
report_path: {lexical absolute path; physical/canonical path or nearest existing ancestor plus uncreated suffix}
evidence_paths:
- {lexical absolute path; physical/canonical path or nearest existing ancestor plus uncreated suffix}
containment_preflight_evidence: evidence/D-{sequence}/path-containment-preflight.md
containment_postwrite_evidence: evidence/D-{sequence}/path-containment-postwrite.md
worker_progress_evidence: evidence/{packet_id}/worker-progress.md

Before dispatch, the top-level orchestrator resolves physical/canonical roots, walks every existing component using no-follow metadata, rejects symlink/junction/mount/Windows-reparse traversal, and proves each target is contained by path components rather than string prefix. For an uncreated target, record and resolve the nearest existing ancestor plus the uncreated suffix, then create/re-resolve required directory suffix components one at a time; leave the assigned file leaf for its authorized writer. If inspection is unavailable or containment fails, block with `capability` or `environment` and do not dispatch.

Before its first write, the worker repeats the same checks as defense in depth and blocks on mismatch. After work, inventory the assigned root and check scoped repository/worktree surfaces for out-of-root changes. Before acceptance, the top-level orchestrator physically re-resolves every written target/component, writes the post-write containment evidence, and blocks with `internal_recovery` or `environment` on any escape, mutation, or unprovable result.

## Scope and stop boundary

- In scope: {bounded evidence/prototype surface}
- Out of scope: production implementation and Planning-owned detailed design
- Stop when: {observable signal or bounded negative result}
- Durable progress boundary: {worker-progress marker, next milestone, and verified enforceable exhaustion signal; block capability preflight if none exists}

## Authority and side effects

- Allowed writes: {assigned report/evidence and isolated scratch paths}
- External effects: {read-only bounded research | none}
- Commit/public/destructive/secret changes: not authorized unless this packet cites exact scope authority

## Completion and verification

- Completion criterion: {artifact/result that decides or narrows `decision_unlocked`}
- Verification command/read/UI observation: {reproducible check}
- Expected signal: {observable pass/fail evidence}
- Post-write physical containment: {evidence/D-{sequence}/path-containment-postwrite.md and observed pass/fail signal}
- Artifact sampling: {representative output the orchestrator must open}

## Fallback and retry

- On unavailable capability: {recorded fallback or blocker}
- On failure: preserve evidence, diagnose, and change one bounded variable
- Maximum remediation cycles: 2

## Worker report and return

When a worker was dispatched, perform the containment self-check and write `evidence/{packet_id}/worker-progress.md` before substantive analysis. Keep it bounded to start time, assigned leaves, anchor digest/summary, current milestone, and next action; it is never acceptance evidence by itself. Write the complete reusable report before returning. Return at most ten lines containing verdict, report path, evidence paths, changed paths, verification summary, and blocker/next action. Do not return chain-of-thought, secrets, full transcripts, or unbounded logs. A pre-dispatch block has no worker return or worker report.
```

## `gates/G-###.md`

Use this one schema for human decisions, external evidence waits, and operational blockers. `AGENT-STATE.md` points to one canonical `gates/G-###.md`; supporting prototype/evidence paths stay fields inside it.

- Human-decision types: `preference`, `product_decision`, `authority`, `uat`, `security_legal`.
- External wait type: `external_evidence`.
- Operational types: `capability`, `environment`, `internal_recovery`.

`capability` covers unavailable/unconfirmed host, worker, or tool capability. `environment` covers filesystem, dependency, execution-environment, or physical-path-inspection failures. `internal_recovery` covers an orchestrator/stage-owned contradiction, exhausted remediation, or post-write containment failure. Operational gates do not set `pending_human_gate` unless their recorded recovery truly requires a human host operator. Never use them to hide a product, authority, UAT, security, or legal decision.

```markdown
# Gate G-{sequence}

gate_id: G-{sequence}
gate_type: {preference | product_decision | authority | uat | external_evidence | security_legal | capability | environment | internal_recovery}
decision_unlocked: {one named decision}
owner: {role/person/stage responsible for response}
owner_kind: {human | external_system | orchestrator | owning_stage | host_environment | parent_session}
requires_human_response: {yes | no}
opened_at: {ISO-8601 timestamp}
source_evidence_revisions:
- {path plus revision/hash}
alternatives_or_required_input:
- {bounded alternative or exact missing input}
impact: {what proceeds, changes, or remains blocked}
safe_default: {bounded safe default | no_safe_default}
focused_question_or_recovery_request: {one focused question or exact recovery request}
recovery_check: {observable capability/environment/internal signal, or not_applicable_for_human_decision}
pause_state: {paused | resumed}
response_state: {pending | accepted | rejected | supplied | unavailable}
prototype_paths:
- {portable isolated prototype path | none}
evidence_paths:
- {portable supporting evidence path}

## Allowed responses and routes

| allowed response | evidence required | resulting packet/state transition | route |
|---|---|---|---|
| {exact allowed response or recovery outcome} | {response/prototype/evidence revision} | {from status => to status} | {retry/continue Discovery packet | PLANNING | STOP} |

## Resolution

- Resolved at: {ISO-8601 timestamp | pending}
- Recorded response: {bounded response | pending}
- Resolution evidence/revision: {path/revision | pending}
- Resulting route: {DISCOVERY | PLANNING | STOP | pending}
```

## `reports/D-###-report.md`

Create this artifact only after a worker actually ran. A pre-dispatch block uses `none_not_dispatched` and orchestrator-owned preflight evidence instead.

```markdown
# Discovery Packet D-{sequence} Report

packet_id: D-{sequence}
verdict: {PASS | FAIL | BLOCKED}
decision_unlocked: {named decision}
report_revision: {stable revision or digest}
completed_at: {ISO-8601 timestamp}

## Outcome and conclusions

- Primary outcome: {result}
- Decision enabled or narrowed: {result and confidence}
- Recommended route: {Discovery packet | canonical gate | Planning | stop}

## Decisions and assumptions

| item | type | outcome | owner | effect if false |
|---|---|---|---|---|
| {item} | {decision | assumption | residual unknown} | {result} | {owner} | {impact} |

## Sources and evidence

| source path/revision | relevant bounded excerpt or observation | freshness |
|---|---|---|
| {path/revision} | {redacted relevant signal} | {current/stale finding} |

## Commands and verification

| command/read/observation | expected signal | observed signal | evidence path |
|---|---|---|---|
| {reproducible check} | {expected} | {bounded result} | evidence/D-{sequence}/{artifact} |

## Created or changed files

- {assigned artifact path and purpose, or none}

## Intentionally untouched

- Production code, unrelated dirty paths, secrets, and unapproved external state.

## Failures, fallbacks, and retries

- Failure/limitation: {observed condition | none}
- Fallback used: {recorded fallback | none}
- Retry count: {0 | 1 | 2}
- Requested/effective model: {requested} / {confirmed ID | host_default}
- Model fallback reason: {none when confirmed | observed limitation}

## Residual uncertainty and next action

- {item, owner, allowed disposition, and next signal, or none}

## Redaction statement

This report contains conclusions and bounded evidence only. Secrets, chain-of-thought, full transcripts, and unbounded logs were neither requested nor persisted.
```

## `SESSION-HANDOFF.md`

```markdown
# Session Handoff

protocol_version: autonomous-artifacts-v2
run_id: {run ID}
handoff_revision: {stable revision or digest}
created_at: {ISO-8601 timestamp}
restart_mode: {manual | host-confirmed automatic action}

## Verified state

- Current Discovery revision: {revision}
- Repository revision/freshness evidence: {revision and evidence paths}
- Verified packets and weights: {IDs and weights}
- `completed_weight` / `session_budget`: {number} / {6 or 4}
- Representative artifacts inspected: {paths and observed signals}
- Accepted event anchor: count {events_accepted_count}, tip {events_accepted_tip}, file SHA-256 {events_accepted_file_sha256}, accepted at {events_anchor_updated_at}

## Active or blocked state

- Active packet: {packet ID | none}
- Unsupported status downgraded during reconciliation: {finding | none}
- Blocker/canonical gate: {condition, gate type, owner, human-response requirement, recovery | none}
- Pre-existing dirty paths to preserve: {paths | none_observed}
- Frozen predecessor lineage: {predecessor run root plus state/events/freeze SHA-256 and successor recovery evidence path | none_for_initial_run}

## Next action

- Owning stage: {DISCOVERY | PLANNING | STOP}
- Exact next action: {one evidence-based action}
- Required files to read first: AGENT-STATE.md, SCOPE.md, DISCOVERY.md, {active packet/report paths}
- Continuation kind: {verified_command | manual_host_action}
- Continuation verification: {harmless capability check plus observed signal | command_not_verified_use_manual_host_action}
- Exact continuation command/action: {existing `continuation_command` value; a verified command, or precise natural language naming autonomous-project-discovery, absolute run root, first-read files, gate input, and next action}

## Recovery note

On resume, distrust conversation summaries. Reconcile packet status, reports, evidence, Git/filesystem state, lineage, budget, and the actual event chain/count/tip/full-file digest against the durable accepted anchor before dispatching a worker. Never update an anchor to bless unexplained bytes. If `EVENTS.FROZEN` exists or the anchor mismatches, never append to that stream: complete only the bounded recovery closure, then continue in a distinct successor run root with verified lineage.
```
