# Work Sizing and Session Cutover

## Observable planning-unit rubric

Every Planning packet has one primary outcome, explicit current inputs, one decision or plan surface unlocked, an observable completion criterion, verification, fallback, authority, dependencies, and no unresolved dependency on a later packet.

Before dispatch, declare a durable progress marker, the next bounded milestone that changes it, and at least one host-enforceable exhaustion signal: a maximum evidence-surface/check count, a per-operation timeout the host actually enforces, or a reliable host/monotonic elapsed deadline. If none can be observed and enforced, block capability preflight; do not invent context or time estimates.

| size | weight | boundary |
|---|---:|---|
| `Small` | 1 | One design decision, contract, or verification surface in one subsystem with direct evidence. |
| `Medium` | 2 | One outcome across at most two coupled subsystems with integration-level consistency verification. |
| `Large` | invalid | Multiple outcomes, three or more coupled subsystems, an unknown interface, unbounded verification, or a plan that cannot be accepted independently. Split before dispatch. |

Only Small/1 and Medium/2 are dispatchable. Do not relabel Large as Medium to fit a session. Apply the same rubric to every final implementation Task Contract from its actual outcomes, coupled subsystems, and independent verification boundaries; a `Small` or `Medium` label never overrides Large contents.

## Dependency ordering

Build an explicit acyclic graph and prefer:

1. instruction, upstream freshness, and repository evidence needed by later packets;
2. architecture boundaries that eliminate downstream alternatives;
3. interface and data invariants before dependent workflows;
4. high-impact migration/security/external-integration decisions before rollout polish;
5. testability and verification design while contracts can still change;
6. implementation Task Contract synthesis after its decisions are verified;
7. independent final review after the candidate master plan is complete.

A packet is dispatchable only when every dependency is verified and required inputs exist. Dispatch exactly one Planning worker at a time. Do not parallelize Planning packets, independent review, or writes to shared artifacts.

## Session ceiling

Use `session_budget: 6` normally. Use `session_budget: 4` when the session includes security-sensitive design, data changes/migration, external integrations, destructive/irreversible risk, or UI/human-UAT architecture.

Before dispatch, calculate `completed_weight + next_packet_weight`. If it exceeds the ceiling, do not dispatch. Write `SESSION-HANDOFF.md`, persist continuation kind/verification/exact value, mark restart manual unless the host proves automatic top-level continuation, and end cleanly.

The ceiling is a maximum, never a target. Stop earlier after the current unit when:

- host-reported context usage reaches at least 50%;
- compaction occurred;
- two orchestrator-authorized packet remediation cycles were needed in the session;
- the next action cannot be selected from `AGENT-STATE.md` plus the current report alone;
- a human, external, authority, or stage-routing gate is pending.

When telemetry is absent, record `unavailable`; artifact and weight ceilings still apply.

## Retry and liveness circuit breaker

For failure or contradiction, inspect the actual report/evidence, write a bounded diagnosis, preserve useful artifacts, and change one falsifiable variable or repair the contract. Retry at most twice for the same packet. A repeated denial is not retried with alternate syntax. After the second unsuccessful remediation, set `blocked`, open the correct gate/route, and hand off when needed.

A remediation cycle is any actual new worker dispatch for the same packet after a prior worker reached a terminal non-accepted disposition, whether or not the orchestrator used the word “rejected.” Increment exactly once at that dispatch boundary and reconcile it with the versioned attempt receipts and packet retry count. A preflight failure with no dispatch and a side-effect-free local inspection-command correction inside the same attempt do not increment the counter; record the command error and final bounded signal instead. If the error requires a new worker dispatch, that new attempt is one remediation cycle.

Worker `running` and chat assurance are not durable progress. Compare the declared marker/report/evidence leaves through host-supported waiting. Repeated no-change observations may trigger one completion-or-blocker request, but wait count alone cannot terminate work. End an attempt only at the predeclared exhaustion signal or a host hard failure/limit; preserve evidence and diagnose before retry.

## No-rushing rule

Never combine outcomes, lower evidence quality, skip repository inspection, omit artifact sampling, self-review the final plan as “independent,” leave exact contracts for later, or cross a gate to fit the session. Ending early with a lossless handoff is correct; rushing is not.
