# Autonomous Implementation Launcher Template

Copy the single prompt below and replace only fields whose defaults do not fit. Safe defaults deny external/irreversible/public effects, live migrations, deployment, messages, credentials, destructive resets, broad commits, and silent upstream/product decisions.

```markdown
Use `autonomous-implementation` from the top-level session to execute the current approved plan sequentially, verify every stage independently, preserve unrelated work, pause for UI UAT, and finish with independent integration acceptance plus resumable artifacts.

Goal and bounded scope:
- Requested implementation outcome: {bounded outcome}
- In scope stages/features: {plan stage IDs or exact scope}
- Out of scope: {adjacent work}
- Stop boundary: {verified requested stages + required UAT + integration review + IMPLEMENTATION-NOTES.md; do not continue into later roadmap work}

Upstream artifacts:
- Discovery artifact or equivalent: {path}
- Approved execution-ready plan or equivalent: {path}
- Expected revisions/approval: {values if known; otherwise auto-detect and verify}
- Required approval semantic: `planning_approval_state` is `delegated_execution_authority` or `explicitly_approved`, with current `planning_approval_evidence` path, revision, and named authority covering the exact plan/scope/stop boundary/side effects
- Planning readiness, independent review, orchestrator acceptance, silence, `not_requested`, `approval_required`, or missing/stale approval fields are not execution approval; preserve/route the canonical Planning approval mapping or gate instead of inventing it
- If framing is missing/stale/contradicted: return `NEEDS_DISCOVERY` and route only the affected scope
- If architecture, interfaces, data, sequencing, migration/deployment, verification, rollback, or Task Contracts are missing/stale/contradicted: return `NEEDS_PLANNING` and route a bounded repair
- Do not change product files until a read-only consistency review returns evidence-backed `READY`

Authority and side effects:
- Consume every Planning Task Contract verbatim, including `Allowed side effects`
- Reversible local choices: allowed only inside exact delegated decision authority
- External, irreversible, destructive, live-data, public, deploy, publish, message, purchase, credential, and secret effects: `none/not_authorized` unless I grant exact current authority here: {none}
- Material product/framing choices: Discovery or explicit approval; architecture/interface/contract choices: Planning or explicit approval
- Maximum remediation cycles for one failure family: 2 after evidence-backed diagnosis
- Never use destructive reset or erase reports, evidence, events, checkpoints, or unrelated user work

Repository and checkpoint policy:
- Read every applicable `AGENTS.md`/`CLAUDE.md`
- Inventory all pre-existing dirty paths with baseline/current hashes and bounded diffs before product edits; preserve unrelated paths exactly
- Commit policy: {not authorized | path-limited commits for exact stage-owned paths after acceptance}
- Never stage/commit unrelated dirty paths; without commit authority use reversible Git/filesystem hashes/diffs and rollback evidence

Worker and evidence policy:
- Protocol: `autonomous-artifacts-v2`
- Existing run/planning location: auto-detect
- Fallback run root: `docs/agent-runs/<YYYYMMDD>-<goal-slug>[-N]/`
- Canonical outputs: `AGENT-STATE.md`, `EVENTS.jsonl`, `SCOPE.md`, `IMPLEMENTATION-NOTES.md`, `packets/I-###.md`, `reports/I-###-report.md`, `evidence/`, `gates/`, and `SESSION-HANDOFF.md`
- Freeze only Small/1 or Medium/2 stages; Large is invalid and routes to Planning for splitting
- Dispatch exactly one fresh state-changing implementation worker at a time with the Task Contract verbatim, instruction paths, exact product/artifact writes, exact side effects, physical anchors, verification/fallback/UAT, and <=10-line return contract
- Worker writes full report/evidence first; worker `done`, exit code, or commit is not acceptance
- After every worker/reviewer return, the orchestrator records the exact host-return boundary and writes an immutable `evidence/I-###/worker-return-attempt-###.md` with dispatch/worker identity, terminal subtree status, canonical UTF-8 base64 return bytes/line count/hash, report/evidence hashes, and temporal checks; the receipt says only `return_observed`, while a later immutable acceptance/rejection event records final disposition; reconcile dispatch, receipt, retry, and remediation counts before acceptance or redispatch
- Top-level orchestrator independently rechecks containment, dirty paths, scoped diff, exact commands, representative changed artifacts, and one real affected flow before `verified`

Model and host policy:
- Preferred orchestrator: highest-reasoning model if exposed
- Preferred implementation worker: Sonnet-class/high-effort if exposed
- Exact model required: no
- Record requested/effective model and fallback per worker; use `host_default` honestly when selection is unavailable
- Record unavailable context telemetry instead of estimating it
- Never assume browser/screenshot, Git, or automatic top-level restart exists

UI policy:
- `[non-UI]` stages auto-continue after independent automatic acceptance
- `[UI]` stages require automatic functional/visual/accessibility verification plus actual screenshot or live URL tied to the accepted build, then human UAT before any dependent stage
- Request installed relevant `design-taste-frontend`, `high-end-visual-design`, and `minimalist-ui`; request `redesign-existing-projects` for existing-page redesign; record unavailable/not-installed fallback without pretending invocation
- Treat later UAT as `scheduled_downstream`, not a pre-Implementation blocker; never cross its named boundary silently

Sizing, cutover, and completion:
- Every dispatched readiness/stage/repair/integration unit is Small/1 or Medium/2
- Normal session ceiling = 6; security/data/external-integration/UI/high-risk ceiling = 4; these are maxima, not targets
- Before dispatch persist `completed_weight + next_stage_weight`; if it exceeds the ceiling, write `SESSION-HANDOFF.md` and stop before dispatch
- Also hand off after compaction, >=50% host-reported context, two remediation cycles in the session, or when the next action is not recoverable from state + current report
- After requested stages/UAT, dispatch a fresh independent read-only integration reviewer; route critical findings to the owning stage and never accept CRITICAL risk
- Finish only when IMPLEMENTATION-NOTES.md records actual-vs-plan behavior, deviations, assumptions, changed files, checks/real flows/UI evidence, dirty preservation, retries, UAT, integration findings, residual gates, checkpoints, and rollback
- On cutover use a harmlessly verified continuation command or a precise `manual_host_action` naming this skill, absolute run root, first-read files, gate input, and next action

Begin by discovering actual host capabilities, reconciling current artifacts/Git/filesystem/dirty paths, verifying the append adapter, and dispatching one read-only readiness review. Continue autonomously inside recorded authority; ask only at a hard blocker, exact material authority/product decision, required unavailable verification, or UI UAT after automatic acceptance.
```
