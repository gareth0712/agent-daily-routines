# Planning State Templates

Replace every brace-delimited value with observed run data before accepting an artifact. Remove optional rows only when they do not apply and record the evidence-based reason in `Assumptions and omissions`; never leave unresolved placeholders. Canonical artifact references use portable forward slashes. Worker dispatch records lexical absolute and physical/canonical anchors.

## Contents

- [`AGENT-STATE.md`](#agent-statemd)
- [`EVENTS.jsonl`](#eventsjsonl)
- [`SCOPE.md`](#scopemd)
- [`MASTER-PLAN.md`](#master-planmd)
- [`packets/P-###.md`](#packetsp-md)
- [`reports/P-###-report.md`](#reportsp--reportmd)
- [`gates/G-###.md`](#gatesg-md)
- [`SESSION-HANDOFF.md`](#session-handoffmd)

The frozen-predecessor successor artifact and six exact lineage fields use the byte-identical template in `artifact-protocol.md`.

## `AGENT-STATE.md`

Only the top-level orchestrator writes this file.

```markdown
# Agent State

protocol_version: autonomous-artifacts-v2
workflow_type: planning
active_pipeline_stage: PLANNING
run_id: {YYYYMMDD-goal-slug-N}
repository_root: {absolute repository/project root}
worktree_root: {absolute active worktree root or repository_root}
run_root: {portable project-relative run path}
canonical_repository_root: {physical/canonical existing repository root}
canonical_worktree_root: {physical/canonical existing worktree root}
canonical_run_root: {physical/canonical run root, or verified nearest existing ancestor plus uncreated suffix until created}
events_path: EVENTS.jsonl
events_accepted_count: {0 before first append | accepted_event_count returned by last successful append}
events_accepted_tip: {64 lowercase zeroes before first append | accepted_event_tip returned by last successful append}
events_accepted_file_sha256: {e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 before first append | accepted_events_sha256 returned by last successful append}
events_anchor_updated_at: {ISO-8601 timestamp and helper result evidence path}
updated_at: {timezone-aware ISO-8601 timestamp}

## Harness and capabilities

harness: {Claude Code | Codex | generic host name}
restart_mode: {manual | host-confirmed automatic action}
context_telemetry: {host-reported percentage | unavailable}

| capability | status | observed evidence | fallback |
|---|---|---|---|
| fresh_isolated_worker | {available | unavailable | unknown} | {host surface evidence} | {hard blocker when unavailable} |
| model_selection | {available | unavailable | unknown} | {selector evidence} | {host_default when unavailable} |
| context_telemetry | {available | unavailable | unknown} | {signal evidence} | {weight ceiling without estimation} |
| repository_read | {available | unavailable | unknown} | {filesystem/tool evidence} | {block decisions requiring unavailable evidence} |
| new_top_level_session | {available | unavailable | unknown} | {host evidence} | {manual_host_action} |

## Models

orchestrator_requested_model: {highest-reasoning/Fable-class preference or user value}
orchestrator_effective_model: {confirmed model ID | host_default}
orchestrator_fallback_reason: {none when confirmed | observed selector limitation}

## Instructions and repository baseline

applicable_instruction_paths:
- {project-relative path | none_found_after_search}
baseline_git_sha: {Git SHA | not_a_git_repository}
repository_revision: {current Git SHA, content digest, or dated filesystem revision}
pre_existing_dirty_paths:
- {path | none_observed}

## Scope and authority

scope_path: SCOPE.md
stop_boundary: {observable Planning stop boundary}
risk_mode: {normal | high_risk | ui}
allowed_external_effects: {bounded list | none}
commit_policy: {not_authorized | path_limited_authorized}
product_code_changes: forbidden

## Pipeline readiness and routing

discovery_gate_status: {CURRENT | INSUFFICIENT | STALE}
discovery_readiness: {ready | not_ready | stale}
planning_readiness: {not_assessed | ready | not_ready | stale}
implementation_readiness: {not_assessed | ready | not_ready | stale}
planning_approval_state: {not_requested | delegated_execution_authority | approval_required | explicitly_approved}
planning_approval_evidence:
  path: {SCOPE.md | durable request artifact | gates/G-###.md | none}
  revision: {stable revision/digest | none}
  authority: {named user/role | none}
next_stage: {DISCOVERY | PLANNING | IMPLEMENTATION | STOP}

Approval is separate from readiness. Only `delegated_execution_authority` or `explicitly_approved` with current non-`none` path/revision/authority may route to Implementation. `not_requested` routes `STOP`; `approval_required` uses a canonical pre-Implementation gate. Independent review/orchestrator acceptance is not approval.

## Artifact lineage

discovery_artifact_path: {DISCOVERY.md | portable equivalent path}
discovery_source_kind: {canonical | equivalent}
discovery_revision: {stable revision/digest}
repository_revision_at_discovery: {revision recorded upstream}
discovery_field_mapping_evidence: {evidence/discovery-gate.md}
discovery_freshness_evidence: {paths/revisions/commands}
discovery_supersedes: {prior revision | none}

planning_artifact_path: MASTER-PLAN.md
planning_revision: {stable revision/digest | not_assessed}
repository_revision_at_planning: {revision inspected | not_assessed}
planning_derived_from: {accepted Discovery revision | not_assessed}
planning_freshness_evidence: {paths/revisions/commands | not_assessed}
planning_supersedes: {prior planning revision | none}

implementation_artifact_path: {current equivalent path | none_created}
implementation_revision: {revision | not_assessed}

predecessor_run_root: {portable frozen run root | none_for_initial_run}
predecessor_state_sha256: {lowercase 64-hex | none_for_initial_run}
predecessor_events_sha256: {lowercase 64-hex | none_for_initial_run}
predecessor_freeze_sha256: {lowercase 64-hex | none_for_initial_run}
recovery_evidence_path: {evidence/recovery/frozen-predecessor.md | none_for_initial_run}
recovery_reason: {bounded reason | none_for_initial_run}

## Session control

session_budget: {6 | 4}
completed_weight: {sum of verified packet weights}
next_packet_weight: {1 | 2 | none}
remediation_cycles_this_session: {0 | 1 | 2}

## Planning packets

| packet | primary_outcome | size | weight | dependencies | status | report | evidence | requested_model | effective_model | fallback_reason | retry_count | packet_kind |
|---|---|---|---:|---|---|---|---|---|---|---|---:|---|
| P-001 | {one Planning outcome} | {Small | Medium} | {1 | 2} | {verified IDs | none} | {pending | in_progress | verified | blocked | superseded} | {reports/P-001-report.md | none_not_dispatched} | evidence/P-001/ | {preference} | {confirmed ID | host_default | not_executed} | {none or non-empty fallback/block reason} | {0 | 1 | 2} | {readiness_review | planning | final_review | repair} |

`not_executed` is paired with `none_not_dispatched` only when preflight blocked before a worker ran; completed weight does not change.

## Attempt accounting

| packet | dispatch_count | terminal_receipt_count | accepted_attempt | retry_count | session_remediation_delta | reconciliation |
|---|---:|---:|---:|---:|---:|---|
| P-001 | {0..3} | {same as terminal dispatches} | {attempt number | none} | {max(0, dispatch_count - 1)} | {new dispatches after terminal non-accepted attempts} | {PASS | FAIL} |

Every `worker_dispatched` event has exactly one immutable attempt-specific terminal receipt. A new dispatch for the same packet after a terminal non-accepted attempt increments packet `retry_count` and `remediation_cycles_this_session` exactly once. Preflight failures with no dispatch and side-effect-free command corrections inside one attempt increment neither count.

## Gates

pre_implementation_blocking_gates:
- {gates/G-###.md plus unresolved decision required before Implementation may start | none}
scheduled_downstream_gates:
- {stage ID, gates/G-###.md or planned gate ID, owner, evidence required, and exact later boundary it blocks | none}
pending_human_gate: {one active pre-implementation material decision | none}
pending_operational_gate: {capability/environment/internal recovery blocker and owner | none}
gate_evidence_path: {gates/G-###.md | none}

Only a gate in `pre_implementation_blocking_gates` blocks `planning_readiness`/`implementation_readiness`. A correctly owned UI UAT or external gate in `scheduled_downstream_gates` permits Implementation to start but still blocks crossing its named stage boundary.

## Final review

independent_review_packet: {P-### | not_started}
independent_review_report: {reports/P-###-report.md | not_started}
critical_findings_open: {integer}
important_findings_disposition: {bounded summary | not_started}

## Next action

next_action: {one evidence-based action}
continuation_kind: {verified_command | manual_host_action}
continuation_verification: {harmless capability check and signal | command_not_verified_use_manual_host_action}
continuation_command: {exact verified command | precise natural-language action naming autonomous-planning, absolute run root, first-read files, gate input, and next action}
blockers:
- {named blocker, owner, and recovery route | none}

## Assumptions and omissions

- {assumption, owner, validation signal, effect if false | none}
```

## `EVENTS.jsonl`

Only the top-level orchestrator appends through the verified adapter. `AGENT-STATE.md` remains the sole control-plane index. Follow the complete byte/freeze/recovery contract in `artifact-protocol.md`.

Each line is one object with monotonic `event_seq`, a fresh strictly increasing timezone-aware timestamp, `event_type`, stage `PLANNING`, optional valid `P-###` and statuses, actor `top_level_orchestrator`, existing local references with actual lowercase SHA-256, bounded evidence summary, `previous_event_sha256`, and canonical `event_sha256`. Never edit/rewrite/truncate an existing stream. A referenced path/version becomes immutable at those exact bytes; a later update uses a new versioned path and later event.

CLI/reference validation occurs before freezing. The helper then arms `EVENTS.FROZEN` before actual-prefix read, validates the chain and durable accepted count/tip/file digest, appends once, proves byte/chain postconditions, returns the next accepted anchor, and only then removes the marker. Malformed/partial/chain-invalid streams and anchor mismatches remain frozen. This detects history inconsistent with the durable accepted anchor; it does not resist rewriting both stream and every anchor.

Default commands after replacing values:

```text
python {absolute-skill-root}/scripts/append_event.py --self-test --run-root {absolute-run-root}
python {absolute-skill-root}/scripts/append_event.py --run-root {absolute-run-root} --stage PLANNING --event-type {event_type} --packet-id {P-###} --from-status {status} --to-status {status} --reference {portable/existing/path} --evidence-summary {bounded summary} --expected-event-count {events_accepted_count} --expected-event-tip {events_accepted_tip} --expected-events-sha256 {events_accepted_file_sha256}
```

After success, persist returned `accepted_event_count`, `accepted_event_tip`, and `accepted_events_sha256` before another append. Append the protocol-required lifecycle events. A verified transition is invalid without earlier passing post-write containment, worker-return receipt, report/evidence observation, and orchestrator artifact sampling events. The observation event timestamp must be later than the receipt and every observed artifact's stable mtime/embedded completion time. Any append failure or remaining `EVENTS.FROZEN` stops later appends and triggers the protocol's bounded predecessor closure plus distinct successor run.

For terminal finalization, freeze artifacts first, write and verify `evidence/finalization-manifest.md`, and reference only that immutable manifest/frozen versioned evidence from the terminal event. Update live `AGENT-STATE.md` and `SESSION-HANDOFF.md` with the returned terminal anchor afterward; never include either mutable index as a terminal-event reference.

## `SCOPE.md`

```markdown
# Planning Scope

run_id: {run ID}
scope_revision: {stable revision/digest}
updated_at: {ISO-8601 timestamp}

## Goal and accepted framing

- Planning outcome: {observable plan outcome}
- Accepted Discovery source/revision: {path and revision}
- Discovery gate status/evidence: {CURRENT plus evidence path, or backward route}
- Repository/reference revision: {current revision and evidence}

## Requested follow-through and execution authority

- Requested follow-through: {stop_after_planning | execute_after_planning}
- Durable request evidence: {bounded request summary/source path and revision}
- Granting authority: {named user/role | none_for_planning_only}
- Delegated execution scope and stop boundary: {exact stage/scope boundary | none}
- Delegated side-effect ceiling: {exact effects authorized | none_not_authorized}
- Approval rule: delegated authority is valid only while the final plan remains inside these exact boundaries; otherwise use a canonical approval gate

## In scope

- {bounded architecture/interface/data/workflow/migration/testing/deployment/verification surface}

## Out of scope

- {adjacent Planning work}
- Product code, tests, migrations, deployment changes, secrets, and external writes
- Reframing current Discovery-owned users/outcomes/scope without a routed contradiction

## Stop boundary

Planning stops after a current independently reviewed `MASTER-PLAN.md`, exact Task Contracts, explicit readiness values, and durable next route.

## Authority

- Low-impact reversible Planning choices: {delegated boundary}
- Medium-impact choices: {upstream delegation | approval required}
- High-impact/product/security/legal/public/destructive choices: {approval owner}
- Read-only repository/network research: {bounded authority}
- Commits/checkpoints: {not_authorized | exact planning paths}
- Product and external state changes: not_authorized

## Acceptance

- {relevant coverage and exact-contract criteria}
- Independent final review with zero unresolved critical findings
- Representative artifact and repository-evidence sampling by orchestrator
```

## `MASTER-PLAN.md`

```markdown
# Master Plan

run_id: {run ID}
planning_revision: {stable revision/digest}
derived_from: {accepted Discovery revision}
repository_revision: {revision inspected}
freshness_evidence: {paths/revisions/commands}
supersedes: {prior plan revision | none}
planning_approval_state: {not_requested | delegated_execution_authority | approval_required | explicitly_approved}
planning_approval_evidence:
  path: {SCOPE.md | durable request artifact | gates/G-###.md | none}
  revision: {stable revision/digest | none}
  authority: {named user/role | none}
updated_at: {ISO-8601 timestamp}

The approval mapping binds to this exact planning revision, requested execution scope/stop boundary, and every Task Contract side effect. A superseding revision or boundary change invalidates the mapping until current authority is re-established. Plan readiness/review PASS does not grant approval.

## Executive design

- Goal and stop boundary: {accepted bounded outcome}
- Accepted framing source: {path/revision and field-mapping evidence}
- Architecture summary: {bounded system design}
- Key constraints/invariants: {evidence-backed list}
- Rejected alternatives: {alternative and evidence-based reason}

## System design scenario matrix

Omit this entire section when activation evidence is absent. When present, it must cover all three profiles and every applicable domain.

- Activation evidence kind: {explicit_request | discovery_trigger}
- Activation evidence alternative: {explicit_request: current request path/revision, current-scope mapping, requested dimension, material_trigger: none_not_required | discovery_trigger: current Discovery/equivalent path/revision, current-scope mapping, one named material trigger}
- User metric: {registered users | MAU | DAU | concurrent users | other defined metric | unknown with validation action}
- Workload/risk envelope: {known values, explicit assumptions, falsification methods, and thresholds}
- Shared correctness/security/privacy/safety invariants: {requirements that remain identical across all three profiles and evidence that no profile weakens them}
- `recommended_current_profile`: {Small / Baseline | Medium / Growth and HA | Enterprise / High-scale or mission-critical}
- Recommendation evidence: {dominant constraints and rejected alternatives}

| profile | domain | disposition | architecture delta/evidence | owner | `validation_action` | `upgrade_trigger` | `decision_deadline` |
|---|---|---|---|---|---|---|---|
| {profile} | {domain} | {required | not_applicable | deferred} | {bounded evidence} | {owner | none_when_not_applicable} | {action | none_when_not_applicable} | {measurable trigger | none_when_not_applicable} | {deadline | none_when_not_applicable} |

- Transition, compatibility, migration/backfill, rollback/recovery: {bounded path between relevant profiles}
- Current execution request for future-profile work: {path, revision, authority, and explicitly named profiles | none_not_authorized}
- Authorized implementation profile: {current profile only unless the current execution-request field above contains complete explicit authorization}

## Repository evidence and inherited assumptions

| claim/surface | path and revision | observed signal | classification/owner |
|---|---|---|---|
| {claim} | {source} | {bounded observation} | {fact | inference | proposal | assumption | unavailable plus owner} |

## Component architecture

| component/boundary | responsibility | dependencies/direction | invariants | owner |
|---|---|---|---|---|
| {component} | {one responsibility} | {dependency rule} | {constraint} | {stage/team} |

## Interfaces and compatibility

| interface | producer/consumer | request/event/data contract | error/idempotency/versioning | verification |
|---|---|---|---|---|
| {interface} | {owners} | {exact shape or referenced schema} | {semantics} | {contract check} |

## Data model and lifecycle

| entity/state | invariants | ownership/access | lifecycle/retention | consistency/recovery |
|---|---|---|---|---|
| {entity} | {rules} | {boundary} | {create/change/delete} | {failure handling} |

## Workflows and failure paths

| flow | start to finish | authorization/failure/degraded behavior | observability | acceptance evidence |
|---|---|---|---|---|
| {flow} | {steps} | {recovery} | {signals} | {representative check} |

## Migration, deployment, and rollback

- Migration/backfill: {steps, compatibility window, validation, or not_applicable reason}
- Deployment/rollout: {order, environment/flag/canary evidence, or not_applicable reason}
- Rollback/recovery: {checkpoint, trigger, data recovery, owner}
- Operational ownership: {alerts/dashboards/runbook owner or not_applicable reason}

## Testing and verification strategy

| risk/acceptance intent | test level/check | exact command/read/UI observation | expected signal | evidence destination |
|---|---|---|---|---|
| {risk} | {unit/integration/contract/e2e/manual} | {reproducible check} | {observable pass} | {portable path} |

## Planning decisions and residual uncertainty

| decision/unknown | outcome or alternatives | evidence/authority | owner | resolution deadline/route |
|---|---|---|---|---|
| {item} | {result} | {source} | {role/stage} | {before_plan_review | before_implementation | implementation_may_decide | human_gate | defer} |

## Implementation dependency graph

| stage | dependencies | size/weight | `[UI]` or `[non-UI]` | primary outcome | checkpoint |
|---|---|---|---|---|---|
| I-001 | {verified IDs | none} | {Small/1 | Medium/2} | {[UI] | [non-UI]} | {one outcome} | {rollback point} |

## Exact implementation Task Contracts

### I-{sequence}: {title}

- Goal: {one observable outcome}
- Inputs and freshness: {upstream revisions, instructions, required paths}
- Dependencies: {verified prior stages/external prerequisites}
- In scope: {bounded changes}
- Out of scope: {excluded work}
- Owned files/surfaces: {expected product/test/docs/migration paths}
- Allowed side effects: {exact authorized filesystem/database/network/deployment/messaging/external effects; default external/irreversible/destructive/live-data/public effects to none/not_authorized unless exact authority is cited}
- Decision authority: {local choices allowed; choices that route to Planning/Discovery/human approval}
- Implementation constraints: {interface/data/security/compatibility invariants}
- Verification: {exact commands/reads/UI observation, expected signals, representative real flow, evidence paths}
- Fallback/rollback: {safe checkpoint, recovery command/operation, trigger}
- UAT/external gates: {[UI] human criteria after automatic verification | [non-UI] not_required | named external prerequisite; classify each as pre_implementation_blocking or scheduled_downstream and name the boundary it blocks}
- Completion and stop: {objective pass condition and when not to continue}

## Independent final review

- Review packet/report: {P-### and reports/P-###-report.md}
- Discovery alignment: {PASS/FAIL evidence}
- Repository evidence/feasibility: {PASS/FAIL evidence}
- Cross-contract consistency: {PASS/FAIL evidence}
- Critical findings: {none | IDs and dispositions}
- Important findings: {IDs and dispositions}
- Finding closure evidence/authority: {verified repair paths, owning-stage route paths, or named authority for non-critical accepted risk}

## Readiness and route

- `planning_readiness`: {ready | not_ready | stale}
- `implementation_readiness`: {ready | not_ready | stale}
- `planning_approval_state`: {not_requested | delegated_execution_authority | approval_required | explicitly_approved}
- `planning_approval_evidence`: {path, revision, authority; all current and non-none only for delegated/explicit approval}
- Next stage: {DISCOVERY | PLANNING | IMPLEMENTATION | STOP}
- Pre-Implementation blocking gates: {gate paths/owners | none}
- Scheduled downstream gates: {stage/boundary/gate/owner | none}
- Continuation kind/verification/value: {exact state values}
```

Every relevant coverage surface must appear or be explicitly `not_applicable` with evidence. Every implementation stage uses one complete contract and Small/Medium sizing.

## `packets/P-###.md`

```markdown
# Planning Packet P-{sequence}

packet_id: P-{sequence}
packet_kind: {readiness_review | planning | final_review | repair}
primary_outcome: {one observable Planning outcome}
decision_or_surface_unlocked: {one named design/readiness surface}
size: {Small | Medium}
weight: {1 | 2}
requested_model: {preference}
report_path: reports/P-{sequence}-report.md
evidence_root: evidence/P-{sequence}/

## Goal and ownership

- Goal: {one outcome}
- Planning authority: {decisions allowed}
- Route backward if: {specific framing-changing finding}
- Product-code writes: forbidden

## Inputs and freshness

- Accepted Discovery source/revision: {path/revision}
- Repository/reference evidence: {paths/revisions}
- Applicable instructions: {paths}
- Dependencies: {verified P packet IDs | none}

## Pre-dispatch and physical anchors

- Preflight: {passed | blocked}
- Required input/capability/authority/dependency/progress checks: {results}
- Preflight evidence: evidence/P-{sequence}/preflight.md
- Gate: {gates/G-###.md and type | none}
- Lexical/canonical repository root: {both values}
- Lexical/canonical worktree root: {both values}
- Lexical/canonical run root: {both values or nearest existing ancestor plus suffix}
- Working directory: {lexical/canonical}
- Input paths and allowed read roots: {absolute/canonical list}
- Output/report/evidence paths: {absolute/canonical or nearest ancestor plus suffix list}
- Containment preflight/postwrite evidence: {portable paths}
- Worker progress marker: evidence/P-{sequence}/worker-progress.md

If preflight blocks, do not dispatch; use `not_executed`, `none_not_dispatched`, unchanged completed weight, bounded orchestrator evidence, and the canonical gate.

## Scope and stop

- In scope: {one design/evidence surface}
- Out of scope: {other packets, product changes, unrelated dirty paths}
- Stop when: {observable result or bounded negative result}
- Durable progress boundary: {marker milestone and verified enforceable exhaustion signal}

## Completion, verification, and fallback

- Completion criterion: {artifact/result}
- Verification: {command/read/consistency check}
- Expected signal: {observable pass/fail}
- Artifact sampling: {representative output the orchestrator opens}
- Fallback: {preserve evidence, diagnosis, one bounded change, route}
- Maximum remediation cycles: 2

## Worker report and return

Repeat physical containment, write the progress marker before analysis, then write the full reusable report/evidence. Return at most ten lines: verdict, report/evidence/changed paths, one-line verification, and blocker/next action. Never include chain-of-thought, secrets, transcripts, or raw logs.
```

## `evidence/P-###/worker-return-attempt-###.md`

The top-level orchestrator creates this after the host reports the worker terminal. It is acceptance evidence, not a worker-authored report.

```markdown
# Worker Return Receipt

packet_id: P-{sequence}
attempt_number: {packet-local integer starting at 1}
worker_dispatched_event_seq: {matching event sequence}
worker_identity: {fresh host worker ID/name}
host_terminal_status: {completed | failed | blocked | interrupted}
attempt_disposition: {accepted | non_accepted_retryable | non_accepted_terminal}
prior_attempt_receipt: {worker-return-attempt-NNN.md | none_first_attempt}
dispatch_count_after_attempt: {integer}
packet_retry_count_after_attempt: {integer}
session_remediation_cycles_after_attempt: {integer}
observed_at: {strictly increasing ISO-8601 timestamp from the orchestrator}
line_count: {integer 0..10}
return_sha256: {lowercase 64-hex of the exact bounded return text}
report_path: reports/P-{sequence}-report.md
report_sha256: {lowercase 64-hex}
evidence_paths_and_sha256:
- {path}: {lowercase 64-hex}

## Bounded returned text

{exact returned lines, at most ten; no hidden reasoning or transcript}

## Temporal checks

- Report/evidence existed before `observed_at`: {PASS | FAIL with path}
- Stable mtimes and embedded completion times are not later than observation: {PASS | FAIL with path/time}
- Full agent subtree terminal before next dispatch: {PASS | FAIL with observed identities/statuses}
- Dispatch count, immutable receipt count, packet retry count, and session remediation count reconcile: {PASS | FAIL with counts}
```

## `reports/P-###-report.md`

Create only after a worker actually ran. For `final_review`, include the severity table; for other packet kinds remove that section and record why.

```markdown
# Planning Packet P-{sequence} Report

packet_id: P-{sequence}
packet_kind: {readiness_review | planning | final_review | repair}
verdict: {PASS | FAIL | BLOCKED}
primary_outcome: {one result}
report_revision: {stable revision/digest}
completed_at: {ISO-8601 timestamp}

## Outcome, decisions, and route

- Outcome: {result}
- Planning decisions enabled: {decisions and confidence}
- Framing contradiction: {evidence and Discovery route | none}
- Recommended next action: {packet/gate/stage}

## Evidence and assumptions

| item | classification | source path/revision or owner | effect if false |
|---|---|---|---|
| {item} | {fact | inference | proposal | assumption | unavailable | residual unknown} | {source/owner} | {impact} |

## Verification

| command/read/consistency check | expected signal | observed bounded signal | evidence path |
|---|---|---|---|
| {check} | {expected} | {observed} | evidence/P-{sequence}/{artifact} |

## Independent review findings

| finding | severity | evidence | owner/route | disposition | closure evidence or named authority |
|---|---|---|---|---|---|
| {finding or none} | {CRITICAL | IMPORTANT | MINOR} | {path/revision} | {Planning repair | Discovery | human gate} | {open | verified_repair | routed | accepted_risk} | {repair/route path | authority plus readiness impact} |

A CRITICAL finding closes only as `verified_repair` or `routed` with durable evidence; `accepted_risk` is forbidden. Any non-critical `accepted_risk` requires named authority and cannot silently satisfy readiness.

## Created/changed and intentionally untouched

- Created/changed: {assigned planning artifacts/evidence only}
- Intentionally untouched: product code, migrations, tests, deployment config, unrelated dirty paths, secrets, and external state

## Failures, fallback, and model

- Failure/limitation: {condition | none}
- Fallback/retry: {action and count 0/1/2 | none}
- Requested/effective model: {requested} / {confirmed ID | host_default}
- Model fallback reason: {none | observed limitation}

## Redaction

Conclusions and bounded evidence only; no chain-of-thought, secrets, full transcripts, or unbounded logs were requested or persisted.
```

## `gates/G-###.md`

Use one canonical schema for human decisions, external evidence, or operational recovery. Human types are `preference`, `product_decision`, `authority`, `uat`, and `security_legal`; external wait is `external_evidence`; operational types are `capability`, `environment`, and `internal_recovery`.

```markdown
# Gate G-{sequence}

gate_id: G-{sequence}
gate_type: {preference | product_decision | authority | uat | external_evidence | security_legal | capability | environment | internal_recovery}
decision_unlocked: {one named decision}
owner: {role/person/stage/system}
owner_kind: {human | external_system | orchestrator | owning_stage | host_environment | parent_session}
requires_human_response: {yes | no}
opened_at: {ISO-8601 timestamp}
source_evidence_revisions:
- {path/revision/hash}
alternatives_or_required_input:
- {bounded choice or exact missing input}
impact: {what remains blocked}
safe_default: {safe default | no_safe_default}
focused_question_or_recovery_request: {one question or falsifiable recovery request}
recovery_check: {observable signal | not_applicable_for_human_decision}
pause_state: {paused | resumed}
response_state: {pending | accepted | rejected | supplied | unavailable}
gate_timing: {pre_implementation_blocking | scheduled_downstream}
blocked_boundary: {Implementation start | exact stage ID acceptance/dependent-stage transition}
resulting_route: {DISCOVERY | PLANNING | IMPLEMENTATION | STOP | pending}
resolution_evidence: {path/revision | pending}
```

Operational gates do not manufacture a product question; human product/authority/security decisions are not mislabeled operational.

Before opening a human gate, cite the accepted upstream ownership field and the exact boundary exceeded. If upstream framing delegates the decision category and the proposed least-privilege mechanism stays inside its outcomes, constraints, non-goals, and side-effect ceiling, keep the decision in Planning; a security label alone is not a gate justification.

## `evidence/final-plan-lock.md`

```markdown
# Final Plan Lock

reviewed_candidate_path: {immutable candidate path}
reviewed_candidate_sha256: {lowercase 64-hex reviewed by P-###}
final_plan_path: MASTER-PLAN.md
final_plan_sha256: {lowercase 64-hex}
review_report_path: reports/P-{review}-report.md
review_report_sha256: {lowercase 64-hex}
allowed_post_review_change: review disposition metadata only
mechanical_diff_check: {PASS with bounded changed headings/lines | FAIL}
pending_review_marker_count: 0
semantic_change_detected: no
```

Any non-metadata change or pending-review marker invalidates the lock and requires a fresh independent review.

## `evidence/finalization-manifest.md`

Write once after all listed artifacts are frozen and before the terminal event. Do not list mutable `AGENT-STATE.md` or `SESSION-HANDOFF.md`.

```markdown
# Planning Finalization Manifest

manifest_revision: {stable revision}
created_at: {ISO-8601 timestamp}
final_route: {DISCOVERY | PLANNING | IMPLEMENTATION | STOP}
planning_readiness: {ready | not_ready | stale}
implementation_readiness: {ready | not_ready | stale}
planning_approval_state: {not_requested | delegated_execution_authority | approval_required | explicitly_approved}
frozen_artifacts:
- path: MASTER-PLAN.md
  sha256: {lowercase 64-hex}
  stable_mtime: {ISO-8601}
- path: evidence/final-plan-lock.md
  sha256: {lowercase 64-hex}
  stable_mtime: {ISO-8601}
- path: {each final review/verification/response/versioned worker-return attempt artifact; one entry per frozen path}
  sha256: {lowercase 64-hex}
  stable_mtime: {ISO-8601}
hash_recheck: PASS
temporal_order_check: PASS
```

The terminal event references this manifest. After append, only the live state/handoff anchor/index fields may change; a change to any manifest-listed path requires a new versioned manifest and later event.

## `SESSION-HANDOFF.md`

```markdown
# Session Handoff

protocol_version: autonomous-artifacts-v2
run_id: {run ID}
handoff_revision: {stable revision/digest}
created_at: {ISO-8601 timestamp}
restart_mode: {manual | host-confirmed automatic action}

## Verified state

- Accepted Discovery source/revision and gate evidence: {path/revision/evidence}
- Current Planning revision: {revision | not_ready}
- Planning approval state/evidence: {state plus exact path/revision/authority}
- Repository revision/freshness evidence: {revision/paths}
- Verified packets/weights: {IDs and weights}
- `completed_weight` / `session_budget`: {number} / {6 or 4}
- Representative artifacts sampled: {paths and observed signals}
- Independent review: {packet/report/verdict | not_started}
- Accepted event anchor: count {events_accepted_count}, tip {events_accepted_tip}, file SHA-256 {events_accepted_file_sha256}, accepted at {events_anchor_updated_at}
- Pre-Implementation blocking gates: {paths, owners, required evidence | none}
- Scheduled downstream gates: {stage/boundary/gate/owner | none}

## Active or blocked state

- Active packet: {P-### | none}
- Unsupported status downgraded: {finding | none}
- Blocker/gate and owner: {condition/type/recovery/human-response requirement | none}
- Pre-existing dirty paths to preserve: {paths | none_observed}
- Frozen predecessor lineage: {run root and state/events/freeze SHA-256 plus recovery artifact | none}

## Next action

- Owning stage: {DISCOVERY | PLANNING | IMPLEMENTATION | STOP}
- Exact next action: {one evidence-based action}
- First-read files: AGENT-STATE.md, SCOPE.md, {accepted Discovery path}, MASTER-PLAN.md, {active packet/report}
- Continuation kind: {verified_command | manual_host_action}
- Continuation verification: {capability check/signal | command_not_verified_use_manual_host_action}
- Exact continuation command/action: {existing state value naming autonomous-planning, absolute run root, gate input, and next action when manual}

## Recovery discipline

Distrust conversation summaries. Reconcile state, reports, evidence, upstream and Planning lineage, Git/filesystem state, packet weights, and the actual event chain/count/tip/full-file digest against the durable accepted anchor before dispatch. Never update an anchor to bless unexplained bytes. If `EVENTS.FROZEN` exists or the anchor mismatches, perform only bounded predecessor closure and continue in a distinct successor run with verified lineage.
```
