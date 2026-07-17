# Implementation State Templates

Replace every brace-delimited value with observed run data before accepting an artifact. Remove optional rows only when inapplicable and record the evidence-based reason in `Assumptions and omissions`; never leave unresolved placeholders. Canonical references use portable forward slashes. Worker dispatch records lexical absolute and physical/canonical anchors.

## Contents

- [`AGENT-STATE.md`](#agent-statemd)
- [`EVENTS.jsonl`](#eventsjsonl)
- [`SCOPE.md`](#scopemd)
- [`IMPLEMENTATION-NOTES.md`](#implementation-notesmd)
- [`packets/I-###.md`](#packetsi-md)
- [`evidence/I-###/worker-return-attempt-###.md`](#evidencei-worker-return-attempt-md)
- [`reports/I-###-report.md`](#reportsi--reportmd)
- [`gates/G-###.md`](#gatesg-md)
- [`SESSION-HANDOFF.md`](#session-handoffmd)

Use the byte-identical frozen-predecessor successor template and six exact lineage fields from `artifact-protocol.md`.

## `AGENT-STATE.md`

Only the top-level orchestrator writes this file.

```markdown
# Agent State

protocol_version: autonomous-artifacts-v2
workflow_type: implementation
active_pipeline_stage: IMPLEMENTATION
run_id: {YYYYMMDD-goal-slug-N}
repository_root: {absolute repository/project root}
worktree_root: {absolute active worktree root or repository_root}
run_root: {portable project-relative run path}
canonical_repository_root: {physical/canonical existing repository root}
canonical_worktree_root: {physical/canonical existing worktree root}
canonical_run_root: {physical/canonical run root, or verified nearest existing ancestor plus uncreated suffix}
events_path: EVENTS.jsonl
events_accepted_count: {0 before first append | accepted_event_count from last successful append}
events_accepted_tip: {64 lowercase zeroes before first append | accepted_event_tip}
events_accepted_file_sha256: {empty-file SHA-256 before first append | accepted_events_sha256}
events_anchor_updated_at: {ISO-8601 timestamp and helper evidence path}
updated_at: {timezone-aware ISO-8601 timestamp}

## Harness and capabilities

harness: {Claude Code | Codex | generic host name}
restart_mode: {manual | host-confirmed automatic action}
context_telemetry: {host-reported percentage | unavailable}

| capability | status | observed evidence | fallback |
|---|---|---|---|
| fresh_isolated_worker | {available | unavailable | unknown} | {host evidence} | {hard blocker when unavailable} |
| model_selection | {available | unavailable | unknown} | {selector evidence} | {host_default when unavailable} |
| repository_read_write | {available | unavailable | unknown} | {filesystem/tool evidence} | {block product edits when unavailable} |
| git | {available | unavailable | unknown} | {command evidence} | {filesystem hashes/diffs} |
| browser_or_screenshot | {available | unavailable | unknown} | {tool evidence} | {block required UI verification} |
| context_telemetry | {available | unavailable | unknown} | {signal evidence} | {weight ceiling without estimation} |
| new_top_level_session | {available | unavailable | unknown} | {host evidence} | {manual_host_action} |

## Models and preferences

orchestrator_requested_model: {highest-reasoning preference or user value}
orchestrator_effective_model: {confirmed model ID | host_default}
orchestrator_fallback_reason: {none when confirmed | observed limitation}
implementation_worker_preference: {Sonnet-class/high-effort or user value}

| preference | status | observed evidence | fallback |
|---|---|---|---|
| design-taste-frontend | {invoked | unavailable | not_installed | not_relevant} | {evidence} | {project/current-design conventions} |
| high-end-visual-design | {invoked | unavailable | not_installed | not_relevant} | {evidence} | {project/current-design conventions} |
| minimalist-ui | {invoked | unavailable | not_installed | not_relevant} | {evidence} | {project/current-design conventions} |
| redesign-existing-projects | {invoked | unavailable | not_installed | not_relevant} | {evidence} | {not required unless existing-page redesign} |

## Instructions and repository baseline

applicable_instruction_paths:
- {project-relative path | none_found_after_search}
baseline_git_sha: {Git SHA | not_a_git_repository}
repository_revision: {current Git SHA, content digest, or dated filesystem revision}
dirty_inventory_evidence: evidence/repository/dirty-baseline.md

| pre_existing_dirty_path | baseline_sha256 | current_sha256 | bounded_diff_evidence | overlaps_owned_stage | disposition |
|---|---|---|---|---|---|
| {path | none_observed} | {64-hex | absent_at_baseline | not_applicable} | {64-hex | absent_now | not_applicable} | {evidence path} | {yes | no} | {preserve | attributed overlap | blocked} |

## Scope and authority

scope_path: SCOPE.md
stop_boundary: {observable Implementation stop boundary}
risk_mode: {normal | high_risk | ui}
commit_policy: {not_authorized | exact path_limited_authorized}
allowed_external_effects: {exact list | none_not_authorized}
allowed_irreversible_or_public_effects: {exact list with authority | none_not_authorized}

## Upstream lineage and readiness

discovery_artifact_path: {DISCOVERY.md | portable equivalent path}
discovery_source_kind: {canonical | equivalent}
discovery_revision: {stable revision/digest}
discovery_freshness_evidence: {paths/revisions/commands}
planning_artifact_path: {MASTER-PLAN.md | portable equivalent path}
planning_source_kind: {canonical | equivalent}
planning_revision: {stable revision/digest}
planning_derived_from: {accepted Discovery revision}
planning_approval_state: {delegated_execution_authority | explicitly_approved | approval_required | not_requested}
planning_approval_evidence:
  path: {SCOPE.md | durable request artifact | gates/G-###.md | none}
  revision: {stable revision/digest | none}
  authority: {named user/role | none}
planning_freshness_evidence: {paths/revisions/commands}
discovery_readiness: {ready | not_ready | stale}
planning_readiness: {ready | not_ready | stale}
implementation_readiness: {not_assessed | ready | not_ready | stale}
readiness_review_result: {READY | NEEDS_PLANNING | NEEDS_DISCOVERY | not_started}
readiness_review_report: {reports/I-###-report.md | not_started}
next_stage: {DISCOVERY | PLANNING | IMPLEMENTATION | STOP}

Only `delegated_execution_authority` or `explicitly_approved` with current non-`none` path/revision/authority may proceed to product edits. Planning readiness/review is not approval. `approval_required` preserves its canonical gate; `not_requested`, absent, contradictory, or stale approval evidence routes to Planning for a bounded producer update.

pre_implementation_blocking_gates:
- {gates/G-###.md and unresolved input required before Implementation starts | none}
scheduled_downstream_gates:
- {stage ID, gate path/planned ID, owner, evidence, and exact dependent boundary | none}

Only an unresolved `pre_implementation_blocking_gates` entry blocks start. A scheduled UI UAT/external gate permits earlier implementation and blocks only its named boundary.

## Session control

session_budget: {6 | 4}
completed_weight: {sum of verified dispatched-unit weights}
next_stage_weight: {1 | 2 | none}
remediation_cycles_this_session: {0 | 1 | 2}

## Implementation stages and dispatched units

| stage | packet_kind | primary_outcome | size | weight | dependencies | status | report | evidence | requested_model | effective_model | fallback_reason | failure_family | retry_count | uat_state |
|---|---|---|---|---:|---|---|---|---|---|---|---|---|---:|---|
| I-001 | {readiness_review | implementation | repair | integration_review} | {one outcome} | {Small | Medium} | {1 | 2} | {verified IDs | none} | {pending | in_progress | verified | blocked | superseded} | {reports/I-001-report.md | none_not_dispatched} | evidence/I-001/ | {preference} | {confirmed ID | host_default | not_executed} | {none or reason} | {stable family | none} | {0 | 1 | 2} | {not_required | pending | approved | rejected} |

`not_executed` pairs with `none_not_dispatched` only when preflight blocked before a worker ran. Completed weight changes only after independent verification.

## Current checkpoint and integration

last_verified_stage: {I-### | none}
last_checkpoint_kind: {path_limited_commit | filesystem_git_evidence | none}
last_checkpoint_revision: {commit SHA | evidence path | none}
rollback_point: {exact stage-local recovery evidence | none}
integration_review_stage: {I-### | not_started}
integration_review_report: {reports/I-###-report.md | not_started}
critical_findings_open: {integer}

## Gates

pending_human_gate: {one UAT/product/authority/security gate | none}
pending_operational_gate: {capability/environment/internal recovery gate | none}
gate_evidence_path: {gates/G-###.md | none}

## Frozen predecessor lineage

predecessor_run_root: {portable frozen run root | none_for_initial_run}
predecessor_state_sha256: {lowercase 64-hex | none_for_initial_run}
predecessor_events_sha256: {lowercase 64-hex | none_for_initial_run}
predecessor_freeze_sha256: {lowercase 64-hex | none_for_initial_run}
recovery_evidence_path: {evidence/recovery/frozen-predecessor.md | none_for_initial_run}
recovery_reason: {bounded reason | none_for_initial_run}

## Next action

next_action: {one evidence-based action}
continuation_kind: {verified_command | manual_host_action}
continuation_verification: {harmless capability check/signal | command_not_verified_use_manual_host_action}
continuation_command: {exact verified command | precise action naming autonomous-implementation, absolute run root, first-read files, gate input, and next action}
blockers:
- {named blocker, owner, and recovery route | none}

## Assumptions and omissions

- {assumption, owner, validation signal, effect if false | none}
```

## `EVENTS.jsonl`

Only the top-level orchestrator appends through the verified adapter. Follow the complete byte/freeze/recovery contract in `artifact-protocol.md`; `AGENT-STATE.md` remains the sole control-plane index.

Each line has monotonic `event_seq`, fresh strictly increasing timezone-aware timestamp, event type, stage `IMPLEMENTATION`, optional valid `I-###` and statuses, actor `top_level_orchestrator`, existing local references with actual lowercase SHA-256, bounded evidence summary, previous link, and canonical event digest. Never edit/rewrite/truncate an existing stream.

Default commands after replacing values:

```text
python {absolute-skill-root}/scripts/append_event.py --self-test --run-root {absolute-run-root}
python {absolute-skill-root}/scripts/append_event.py --run-root {absolute-run-root} --stage IMPLEMENTATION --event-type {event_type} --packet-id {I-###} --from-status {status} --to-status {status} --reference {portable/existing/path} --evidence-summary {bounded summary} --expected-event-count {events_accepted_count} --expected-event-tip {events_accepted_tip} --expected-events-sha256 {events_accepted_file_sha256}
```

After success, persist returned accepted count/tip/file SHA-256 before another append. In addition to protocol lifecycle events, record readiness classification/routing, dirty inventory acceptance, contract freezing, worker-return receipt observation, diff/flow/UI sampling, final attempt disposition, remediation diagnosis, UAT open/resolution, checkpoint, integration review, and completion/handoff as bounded events. A verified transition is invalid unless report/evidence times are no later than the host-return boundary, the immutable `return_observed` receipt and its observation event follow that boundary, and a later acceptance event records final disposition. A failed append or remaining `EVENTS.FROZEN` triggers only the protocol's bounded predecessor closure and distinct successor run.

## `SCOPE.md`

```markdown
# Implementation Scope

run_id: {run ID}
scope_revision: {stable revision/digest}
updated_at: {ISO-8601 timestamp}

## Goal and accepted upstream authority

- Requested implementation outcome: {bounded outcome}
- Accepted Discovery source/revision: {path/revision}
- Accepted Planning source/revision/approval: {plan path/revision plus planning_approval_state and exact evidence path/revision/authority}
- Readiness result/evidence: {READY and report/evidence, or upstream route}
- Repository/worktree revision: {revision and evidence}

## In scope

- {exact Task Contract stage IDs and product/test/docs/migration surfaces}
- {exact authorized run artifacts}

## Out of scope

- {adjacent feature/refactor}
- Unrelated pre-existing dirty paths: {paths}
- Discovery framing and Planning architecture/contract changes
- Deploy, publish, message, credentials, live migration, destructive/public/external effects unless exact authority is listed

## Side-effect and checkpoint authority

- Allowed side effects by stage: {stage -> exact list}
- Commits/checkpoints: {not_authorized | exact owned paths}
- External/irreversible/public effects: {none_not_authorized | exact authority}

## Stop boundary

Stop after {verified requested stages, required UAT, independent integration acceptance, IMPLEMENTATION-NOTES.md, and completion/handoff}, or earlier at a recorded gate/cutover.

## Acceptance

- Exact Task Contracts, independent automatic checks, representative real flows, dirty preservation, required UI evidence/UAT, integration review, and rollback evidence
```

## `IMPLEMENTATION-NOTES.md`

```markdown
# Implementation Notes

run_id: {run ID}
implementation_revision: {stable revision/digest}
derived_from_planning_revision: {accepted plan revision}
derived_from_discovery_revision: {accepted framing revision}
repository_revision_before: {baseline Git SHA/filesystem revision}
repository_revision_current: {current Git SHA/filesystem revision}
updated_at: {ISO-8601 timestamp}

## Outcome and readiness

- Requested outcome: {bounded outcome}
- Readiness review: {READY | NEEDS_PLANNING | NEEDS_DISCOVERY} — {report/evidence}
- Completion state: {complete | blocked | routed | handoff_required}
- Stop boundary reached: {yes/no and evidence}

## Actual versus plan

| stage | planned outcome/contract revision | actual behavior | changed files | status | evidence/checkpoint |
|---|---|---|---|---|---|
| I-### | {plan path/revision} | {observed outcome} | {paths} | {verified | blocked | superseded} | {report/evidence/commit or hashes} |

## Verification and representative flows

| stage | command/read/UI/flow | expected signal | observed bounded signal | evidence |
|---|---|---|---|---|
| I-### | {check} | {expected} | {observed} | {evidence path} |

## Deviations, assumptions, and unexpected constraints

| item | classification | evidence | owner/authority | disposition and readiness impact |
|---|---|---|---|---|
| {item} | {approved deviation | rejected deviation | assumption | unexpected constraint} | {path/revision} | {owner} | {implemented | repaired | routed | blocked | accepted_risk} |

## Failures and remediation

| stage | failure_family | observed failure | diagnosis evidence | retry count | useful work preserved | rollback/route |
|---|---|---|---|---:|---|---|
| {I-### | none} | {family} | {signal} | {path} | {0 | 1 | 2} | {paths} | {checkpoint/action} |

## Dirty-worktree preservation

| pre-existing path | baseline/current SHA-256 | bounded diff evidence | overlap attribution | final disposition |
|---|---|---|---|---|
| {path | none} | {hashes} | {evidence} | {none | user/stage split} | {preserved | blocked} |

## UI UAT and external gates

| stage/gate | accepted build/revision | automatic evidence | human/external owner | result | blocked boundary |
|---|---|---|---|---|---|
| {I-###/G-### | none} | {revision} | {screenshots/live URL/checks} | {owner} | {pending | approved | rejected | supplied} | {boundary} |

## Integration review

- Review stage/report: {I-### and report | not_started}
- Discovery/Planning alignment: {PASS/FAIL evidence}
- Cross-stage consistency and flows: {PASS/FAIL evidence}
- Dirty/scope/side-effect containment: {PASS/FAIL evidence}
- Critical findings: {none | IDs and verified repair/route}
- Important/minor dispositions: {IDs, evidence, or named authority}

## Changed files, rollback, and residual work

- Final changed files: {paths with attribution}
- Checkpoints/commits: {exact evidence}
- Rollback points/actions: {stage-local list}
- Residual gates/unfinished work: {owner, evidence, route | none}
- Continuation kind/verification/value: {exact state values}
```

## `packets/I-###.md`

For `implementation` or `repair`, include the exact verbatim upstream Task Contract block. For read-only `readiness_review` or `integration_review`, use the same packet controls and state why product writes are forbidden.

```markdown
# Implementation Packet I-{sequence}

packet_id: I-{sequence}
packet_kind: {readiness_review | implementation | repair | integration_review}
primary_outcome: {one observable outcome}
size: {Small | Medium}
weight: {1 | 2}
requested_model: {preference}
report_path: reports/I-{sequence}-report.md
evidence_root: evidence/I-{sequence}/

## Verbatim Planning Task Contract

{copy the complete approved Task Contract without paraphrase; for read-only control packets write not_applicable_control_packet and define the review contract below}

## Control-packet contract when applicable

- Goal/verdict: {READY/NEEDS_PLANNING/NEEDS_DISCOVERY | independent integration verdict}
- Product writes: forbidden
- Read surfaces: {exact upstream/repository/dirty/evidence paths}
- Verification and route: {exact checks, expected signals, owner}

## Inputs and authority

- Accepted Discovery/Planning paths and revisions: {paths/revisions}
- Applicable instructions: {paths}
- Dependencies: {verified I IDs | none}
- Exact allowed product writes: {paths | none_read_only}
- Exact allowed artifact writes: {packet progress/report/evidence paths}
- Allowed side effects: {verbatim contract value | read_only_none}
- Forbidden paths/effects: {unrelated dirty paths and unauthorized effects}

## Pre-dispatch and physical anchors

- Preflight: {passed | blocked}
- Input/capability/authority/dependency/budget/progress checks: {results}
- Preflight evidence/gate: {evidence/I-###/preflight.md; G-### or none}
- Lexical/canonical repository, worktree, run, and working roots: {pairs}
- Input/read roots: {absolute/canonical list}
- Product output paths: {absolute/canonical or nearest ancestor plus suffix list}
- Report/evidence paths: {absolute/canonical list}
- Containment preflight/postwrite evidence: {paths}
- Dirty baseline evidence: {path and protected-path hashes}
- Worker progress marker: evidence/I-{sequence}/worker-progress.md

If preflight blocks, do not dispatch; use `not_executed`, `none_not_dispatched`, unchanged completed weight, bounded evidence, and the canonical gate.

## Completion, verification, and fallback

- Completion/stop: {observable result}
- Verification and expected signal: {contract checks}
- Representative flow/artifact sampling: {exact target}
- UI automatic evidence/UAT: {requirements | not_required}
- Fallback/rollback: {stage-local checkpoint/route}
- Failure family/retry count: {family/0..2 | none/0}
- Durable progress boundary/exhaustion signal: {observable and host-enforceable}

## Worker report and return

Repeat containment, write the progress marker before work, change only exact owned paths, then write full report/evidence before returning at most ten lines: verdict, report/evidence/changed paths, one-line verification, and blocker/next action. Do not include chain-of-thought, secrets, transcripts, or raw logs.
```

## `evidence/I-###/worker-return-attempt-###.md`

The top-level orchestrator creates this only after the host reports the readiness, implementation, repair, or integration worker terminal. It is immutable return-observation evidence, not a worker-authored report and not final acceptance.

Canonical return encoding is `canonical-utf8-base64-v1`: take the exact host return string, replace CRLF and lone CR with LF, remove all trailing LF characters, encode the resulting Unicode scalar sequence as UTF-8 without BOM, and store RFC 4648 standard base64. The SHA-256 is over those exact decoded bytes. `line_count` is 0 for an empty decoded string; otherwise it is one plus the number of LF bytes. The decoded canonical string must contain no terminal LF and at most ten lines. `return_text_display` is derived, non-authoritative convenience text.

```markdown
# I-{sequence} Worker Return Attempt {NNN}

packet_id: I-{sequence}
attempt_number: {positive packet-local integer}
dispatch_event_seq: {worker_dispatched event sequence}
worker_identity: {fresh host worker ID/name}
host_terminal_status: {completed | failed | blocked | interrupted}
full_subtree_terminal_status: {PASS with observed descendant identities/statuses | FAIL}
attempt_state: return_observed
prior_attempt_receipt: {worker-return-attempt-NNN.md | none_first_attempt}
dispatch_count_after_attempt: {integer}
packet_retry_count_after_attempt: {integer}
session_remediation_cycles_after_attempt: {integer}
host_return_observed_at: {timezone-aware ISO-8601 from the host terminal/return observation boundary}
receipt_created_at: {timezone-aware ISO-8601 at or after host_return_observed_at}
return_encoding: canonical-utf8-base64-v1
return_base64: {RFC 4648 base64 of canonical UTF-8 bytes}
line_count: {integer 0..10}
return_sha256: {lowercase 64-hex of decoded canonical bytes}
return_text_display: |
  {decoded canonical pointer-only return; derived, non-authoritative}
report_path: reports/I-{sequence}-report.md
report_sha256: {lowercase 64-hex}
evidence_hashes:
- {portable evidence path}: {lowercase 64-hex}
final_disposition_event: pending_at_receipt_creation

## Temporal and reconciliation checks

- Report/evidence existed before `host_return_observed_at`: {PASS | FAIL with path}
- Stable mtimes and embedded completion times are not later than `host_return_observed_at`: {PASS | FAIL with path/time}
- Canonical base64 decodes, SHA-256 and line_count recompute, no terminal LF remains, and line_count <= 10: {PASS | FAIL}
- `host_return_observed_at <= receipt_created_at <= worker_return_observed event time`: {PASS | FAIL with times}
- Full agent subtree terminal before another dispatch: {PASS | FAIL with identities/statuses}
- Dispatch count, receipt count, packet retry count, and session remediation count reconcile before final disposition or another dispatch: {PASS | FAIL with counts}
- Later immutable final disposition event: {accepted | non_accepted_retryable | non_accepted_terminal | pending_not_yet_accepted}
```

## `reports/I-###-report.md`

Create only after a worker actually ran. Add readiness or integration finding sections only for the matching packet kind.

```markdown
# Implementation Packet I-{sequence} Report

packet_id: I-{sequence}
packet_kind: {readiness_review | implementation | repair | integration_review}
verdict: {PASS | FAIL | BLOCKED | READY | NEEDS_PLANNING | NEEDS_DISCOVERY}
primary_outcome: {one result}
report_revision: {stable revision/digest}
completed_at: {ISO-8601 timestamp}

## Outcome and route

- Outcome: {actual result}
- Task Contract revision and compliance: {path/revision/result}
- Upstream contradiction/route: {Discovery/Planning evidence | none}
- Recommended next action: {stage/gate/route}

## Changes and side effects

- Created/changed product paths: {exact paths | none_read_only}
- Created/changed artifact paths: {progress/report/evidence}
- Intentionally untouched: {unrelated dirty paths, out-of-scope paths, secrets, unapproved external state}
- Observed side effects versus authority: {exact comparison}

## Verification and representative flow

| command/read/UI/flow | expected signal | observed bounded signal | evidence path |
|---|---|---|---|
| {check} | {expected} | {observed} | evidence/I-{sequence}/{artifact} |

## Dirty-path comparison

| protected path | baseline/current SHA-256 | diff/attribution evidence | result |
|---|---|---|---|
| {path | none} | {hashes} | {path} | {preserved | contradiction} |

## Failure, remediation, and model

- Failure family/diagnosis: {family and evidence | none}
- Retry count: {0 | 1 | 2}
- Useful work preserved: {paths | none}
- Fallback/rollback used: {action/checkpoint | none}
- Requested/effective model: {requested} / {confirmed ID | host_default}
- Model fallback reason: {none | observed limitation}

## UI evidence and UAT

- UI classification: {[UI] | [non-UI] | not_applicable_read_only}
- Design preferences observed: {skill -> invoked/fallback evidence | not_applicable}
- Screenshot/live URL and accepted build: {paths/URL/revision | not_required | unavailable_blocker}
- Automatic acceptance: {PASS/FAIL evidence | not_required}
- UAT gate/result: {G-### pending/approved/rejected | not_required}

## Readiness or integration findings

| finding | severity | evidence | owner/route | disposition | closure evidence/authority |
|---|---|---|---|---|---|
| {finding or none} | {CRITICAL | IMPORTANT | MINOR} | {path/revision} | {Discovery | Planning | Implementation | human gate} | {open | verified_repair | routed | accepted_risk} | {repair/route evidence | named authority for noncritical risk} |

CRITICAL closes only as `verified_repair` or `routed` with durable evidence; `accepted_risk` is forbidden.

## Redaction

Reusable outcomes and bounded evidence only; no chain-of-thought, secrets, credentials, full transcript, or unbounded log was requested or persisted.
```

## `gates/G-###.md`

```markdown
# Gate G-{sequence}

gate_id: G-{sequence}
gate_type: {preference | product_decision | authority | uat | external_evidence | security_legal | capability | environment | internal_recovery}
decision_unlocked: {one named decision/recovery}
owner: {role/person/stage/system}
owner_kind: {human | external_system | orchestrator | owning_stage | host_environment | parent_session}
requires_human_response: {yes | no}
opened_at: {ISO-8601 timestamp}
source_evidence_revisions:
- {path/revision/hash}
accepted_build_or_checkpoint: {revision/evidence | not_applicable}
automatic_verification_evidence: {commands/screenshots/live URL | not_applicable}
alternatives_or_required_input:
- {bounded choice/input}
acceptance_or_recovery_criteria: {observable criteria}
impact: {what remains blocked}
safe_default: {safe default | no_safe_default}
focused_question_or_recovery_request: {one question/falsifiable request}
pause_state: {paused | resumed}
response_state: {pending | approved | rejected | accepted | supplied | unavailable}
gate_timing: {pre_implementation_blocking | scheduled_downstream}
blocked_boundary: {Implementation start | exact stage acceptance/dependent-stage transition}
resulting_route: {DISCOVERY | PLANNING | IMPLEMENTATION | STOP | pending}
resolution_evidence: {path/revision/authority | pending}
```

For UAT, a response applies only to the recorded accepted build/screenshot/live URL. Operational gates do not manufacture product questions, and human product/authority/security decisions are not mislabeled operational.

## `SESSION-HANDOFF.md`

```markdown
# Session Handoff

protocol_version: autonomous-artifacts-v2
run_id: {run ID}
handoff_revision: {stable revision/digest}
created_at: {ISO-8601 timestamp}
restart_mode: {manual | host-confirmed automatic action}

## Verified state

- Accepted Discovery/Planning paths/revisions/approval: {paths/revisions plus planning_approval_state and exact evidence path/revision/authority}
- Readiness result/report: {value/evidence}
- Repository baseline/current revisions: {values/evidence}
- Verified dispatched units/weights: {IDs and weights}
- `completed_weight` / `session_budget`: {number} / {6 or 4}
- Last verified stage/checkpoint/rollback: {values}
- Representative commands/flows/UI artifacts sampled: {paths/signals}
- UAT approvals: {stage/gate/build/evidence | none}
- Integration review: {stage/report/verdict | not_started}
- Accepted event anchor: count {count}, tip {tip}, file SHA-256 {digest}, accepted at {time}

## Protected and gated state

- Pre-existing dirty paths and baseline/current evidence: {paths/hashes/diffs | none}
- Active/failed stage, failure family, retry count: {values | none}
- Pre-Implementation blocking gates: {paths/owners/input | none}
- Scheduled downstream gates: {stage/boundary/gate/owner/status | none}
- Pending UAT/operational/upstream route: {condition/evidence | none}
- Frozen predecessor lineage: {run root and state/events/freeze hashes plus recovery artifact | none}

## Next action

- Owning stage: {DISCOVERY | PLANNING | IMPLEMENTATION | STOP}
- Exact next action: {one evidence-based action}
- First-read files: AGENT-STATE.md, SCOPE.md, {Discovery path}, {Planning path}, IMPLEMENTATION-NOTES.md, {active packet/report/gate}
- Continuation kind: {verified_command | manual_host_action}
- Continuation verification: {capability check/signal | command_not_verified_use_manual_host_action}
- Exact continuation command/action: {existing state value naming autonomous-implementation, absolute run root, gate input, and next action}

## Recovery discipline

Distrust conversation summaries. Reconcile state, upstream lineage, packets/reports/evidence, dirty hashes/diffs, product files, Git/filesystem checkpoints, retry/UAT state, and actual event chain/count/tip/full-file digest before dispatch. Never update an anchor to bless unexplained bytes. If `EVENTS.FROZEN` exists or the anchor mismatches, perform only bounded predecessor closure and continue in a distinct successor run with verified lineage.
```
