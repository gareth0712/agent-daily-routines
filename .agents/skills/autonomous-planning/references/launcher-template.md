# Autonomous Planning Launcher Template

Copy the single prompt below and replace only fields whose defaults do not fit. Safe defaults deny product changes, irreversible/external effects, commits, and silent high-impact decisions.

```markdown
Use `autonomous-planning` from the top-level session to create a current, execution-ready, independently reviewed plan with resumable artifacts.

Goal and scope:
- Desired planned outcome: {bounded outcome}
- In scope: {features/subsystems}
- Out of scope: {adjacent work}
- Stop boundary: produce a current `MASTER-PLAN.md`, exact implementation Task Contracts, independent review, and explicit readiness/route; do not modify product code

Upstream framing:
- Discovery artifact or equivalent path: {path}
- Expected framing revision: {revision if known, otherwise auto-detect and verify}
- If content is insufficient or current repository evidence contradicts framing: route only the affected scope to `autonomous-project-discovery`; do not invent the missing product decision

Planning authority:
- Reversible Planning-owned design choices supported by evidence: allowed
- Medium-impact choices: allowed only when upstream framing delegates them
- Material product, legal, security, expensive, public, destructive, user-facing, or hard-to-reverse choices: require explicit approval unless exact authority is already recorded
- Resolve ownership before applying the impact label: when current Discovery delegates the exact architecture/interface/data/workflow/authorization design and the proposal stays inside its constraints and side-effect ceiling, Planning must choose and record a least-privilege mechanism rather than manufacture a human gate
- A product/security/privacy decision that remains upstream-owned blocks only its named affected downstream boundary when a safe default and exact conditional stop allow the remaining Planning-owned contracts and final review to complete
- Product code, migrations, tests, deployment, publishing, credentials, secrets, purchases, messages, and external writes: not authorized
- Every implementation Task Contract must declare `Allowed side effects`; external, irreversible, live-data, and public effects default to `none/not_authorized` unless I grant exact authority

Execution approval and follow-through:
- After Planning: {stop | route to Implementation because this same request also authorizes execution}
- Named granting authority: {me/current user | named role | none for planning-only}
- Delegated execution scope and stop boundary: {exact requested implementation scope | none for planning-only}
- Delegated side-effect ceiling: {exact effects already authorized | none/not_authorized}
- Persist this bounded request and authority in `SCOPE.md` with a stable revision
- Use `planning_approval_state: not_requested` for planning-only work
- Use `delegated_execution_authority` only when this request explicitly includes execution and every final stage/side effect stays inside the recorded boundary
- If execution authority is absent, ambiguous, stale, or narrower than the final plan, use `approval_required` plus one canonical pre-Implementation gate; after the named authority accepts the exact plan revision/scope/side effects, use `explicitly_approved`
- Persist `planning_approval_evidence` with exact `path`, stable `revision`, and named `authority` in AGENT-STATE.md, MASTER-PLAN.md, and SESSION-HANDOFF.md; use `none` values only with `not_requested`
- Independent review, orchestrator acceptance, silence, or plan readiness never grants execution approval

Evidence and checkpoint policy:
- Read applicable `AGENTS.md`/`CLAUDE.md` and relevant repository evidence before freezing architecture
- Baseline and preserve all pre-existing dirty paths
- Commit policy: do not commit unless I explicitly authorize a path-limited planning checkpoint
- Treat worker reports and compacted summaries as claims until artifacts plus Git/filesystem evidence are reconciled

Architecture scenario policy:
- When I explicitly request architecture/scale/resilience/tier comparison, or current Discovery/equivalent evidence for this scope contains one named material system-design trigger, include the conditional three-profile matrix
- Define workload/risk inputs and do not invent precise traffic, SLO, capacity, recovery, or cost numbers
- User count is an input, never a universal tier boundary or automatic topology choice
- Keep correctness, security, privacy, and safety requirements identical across all three profiles
- Scope Task Contracts to the current profile unless this current execution request explicitly authorizes named future-profile work; record its path, revision, authority, and profiles
- Without activation evidence, keep the plan lean

Model/capability policy:
- Preferred orchestrator and Planning workers: highest-reasoning/Fable-class if exposed
- Exact model required: no
- If selection is unavailable, use `host_default` and record requested/effective model plus fallback reason
- If context telemetry is unavailable, record `unavailable` and use work-unit ceilings without estimating hidden context
- Never assume the host can create a new top-level session

Artifact and worker policy:
- Protocol: `autonomous-artifacts-v2`
- Existing planning location: auto-detect
- Fallback run root: `docs/agent-runs/<YYYYMMDD>-<goal-slug>[-N]/`
- Canonical outputs: `AGENT-STATE.md`, `EVENTS.jsonl`, `SCOPE.md`, `MASTER-PLAN.md`, `packets/P-###.md`, `reports/P-###-report.md`, `evidence/`, gates when needed, and `SESSION-HANDOFF.md`
- Dispatch exactly one fresh Planning worker per packet and wait before the next
- Worker writes full reusable output to report/evidence first and returns at most ten lines
- After each return, the orchestrator writes a new immutable `evidence/P-###/worker-return-attempt-###.md` with monotonic attempt number, dispatch event/worker identity, terminal disposition, observed time, exact line count/text hash, report/evidence hashes, and subtree-terminal/temporal checks; reconcile dispatch, receipt, retry, and remediation counts before acceptance or redispatch
- Top-level orchestrator resolves lexical and physical/canonical anchors before dispatch, rejects escaping link/reparse traversal, and rechecks all writes before acceptance

Sizing, review, and continuation:
- Small = 1, Medium = 2, Large = invalid and must split
- Normal ceiling = 6; security/data/external-integration/UI/high-risk ceiling = 4; ceiling is not a target
- Maximum evidence-driven remediation cycles per packet: 2
- Require a fresh independent final plan-review packet before readiness
- Human UAT default: every `[UI]` Task Contract pauses for human UAT after automatic UI verification and before the next dependent stage; record this as a scheduled downstream gate, not a pre-Implementation blocker
- On cutover, write `SESSION-HANDOFF.md`; use a verified command only after a harmless capability check, otherwise persist a precise `manual_host_action`
- Before the terminal event, lock the exact final plan/review disposition, remove pending-review markers, freeze terminal evidence, and write immutable `evidence/finalization-manifest.md`; the terminal event references that manifest, never mutable state/handoff, then the returned anchor is persisted in those live indexes

Begin by discovering capabilities, validating the upstream artifact by content/lineage/freshness, reconciling current state and repository evidence, and recording safe fallbacks. Persist the requested follow-through and execution authority before Planning. Ask only for a material decision that evidence cannot resolve within delegated authority. Report completion only after sampling representative artifacts, independent-review evidence, and the exact approval mapping.
```
