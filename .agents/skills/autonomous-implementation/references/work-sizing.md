# Work Sizing and Session Cutover

## Observable implementation-unit rubric

Every dispatched unit—including readiness review, implementation stage, remediation, and integration review—has one primary outcome, current inputs, exact owned writes or read-only scope, observable completion, verification, fallback, authority, dependencies, and no unresolved dependency on a later unit.

Before dispatch, declare a durable progress marker, the next milestone that changes it, and at least one host-enforceable exhaustion signal: a maximum evidence-surface/check count, a per-operation timeout the host actually enforces, or a reliable host/monotonic elapsed deadline. If none is observable/enforceable, block capability preflight rather than estimating context or time.

| size | weight | boundary |
|---|---:|---|
| `Small` | 1 | One behavior/stage outcome in one subsystem with scoped tests and direct representative-flow verification. |
| `Medium` | 2 | One outcome across at most two coupled subsystems with integration-level or UI acceptance evidence. |
| `Large` | invalid | Multiple outcomes, three or more coupled subsystems, unknown interface, unbounded verification, ambiguous side effects, or a unit that cannot be independently accepted. Route to Planning and split before dispatch. |

Only Small/1 and Medium/2 are dispatchable. Never relabel Large as Medium to fit a session. A remediation stays within the original stage's owned paths and receives its own declared weight; it does not silently expand scope.

## Dependency ordering

Prefer this order:

1. evidence-first rehydration and one read-only readiness review;
2. foundational interfaces/data/migration compatibility before dependent behavior;
3. non-UI behavior and tests before UI consumers when the plan permits;
4. automatic verification immediately after each worker;
5. UI UAT immediately after automatic UI acceptance and before dependents;
6. bounded remediation at the failed stage, never after dependent work accumulates;
7. independent integration review after requested stages/UAT are complete.

A unit is dispatchable only when all dependencies are verified, current inputs exist, pre-start/named downstream gates permit it, exact side effects are authorized, dirty-path overlap is safe, and required verification is available. Dispatch exactly one state-changing worker at a time. Do not parallelize writes, remediation, UI-dependent stages, shared artifact updates, or integration acceptance.

## Session ceiling

Use `session_budget: 6` normally. Use `session_budget: 4` when the session contains security-sensitive behavior, data changes/migration, external integrations, destructive/irreversible risk, or `[UI]` work/human UAT.

Before every dispatch, calculate and persist `completed_weight + next_stage_weight`. If the sum exceeds the ceiling, do not dispatch. Write `SESSION-HANDOFF.md`, persist continuation kind/verification/exact value, mark restart manual unless the host proves automatic top-level continuation, and end cleanly.

The ceiling is a maximum, never a target. Stop earlier after the current unit when:

- host-reported context usage reaches at least 50%;
- compaction occurred;
- two remediation cycles were needed in the session;
- the next action cannot be selected from `AGENT-STATE.md` plus the current report/evidence alone;
- a UAT, human, external, authority, operational, or upstream-routing gate is pending.

When telemetry is absent, record `unavailable`; artifact and numeric weight ceilings still apply. Do not merge outcomes, omit tests/flow sampling, accept worker self-report, skip UAT/review, or lower evidence quality to fit another unit.

## Retry and failure-family circuit breaker

For a failed command, flow, containment check, side-effect audit, UAT, or integration finding:

1. inspect actual artifacts/diffs/output and persist a stable `failure_family`;
2. preserve useful safe work and dirty-path evidence;
3. state one falsifiable repair and the changed variable;
4. dispatch a fresh bounded repair worker only when authority/paths remain exact;
5. independently rerun acceptance.

Allow at most two evidence-driven remediation cycles for the same failure family across sessions. Persist both stage `retry_count` and `remediation_cycles_this_session`; compaction does not reset either. A denial is not retried through alternate syntax. After the second unsuccessful cycle, block and route/open the correct gate.

## Liveness without rushing

Worker `running`, chat reassurance, or recent tool activity is not durable progress. Compare the declared marker, report, evidence, and owned-path changes through host-supported waiting. Repeated no-change observations may trigger one completion-or-blocker request, but wait count alone cannot terminate a worker. End an attempt only at the predeclared exhaustion signal or a host hard failure/limit, preserve evidence, then diagnose.

Ending a session with exact state, hashes/diffs, reports, gate, rollback point, and continuation is correct. Rushing, compressing contracts, or treating the six/four ceiling as a quota is not.
