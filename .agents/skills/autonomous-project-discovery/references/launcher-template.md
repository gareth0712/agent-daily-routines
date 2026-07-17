# Discovery Launcher Template

Copy the single prompt below and replace only fields whose defaults do not fit. Safe defaults deny external/irreversible effects, production code, commits, and silent preference gates.

```markdown
Use `autonomous-project-discovery` to run bounded, artifact-driven Discovery from the top-level session.

Goal:
- Desired outcome: {describe the problem or idea to frame}
- Why now / evidence: {known evidence, or "not yet established"}

Scope:
- In scope: {bounded product, repository, or subsystem}
- Out of scope: {adjacent work excluded from this run}
- Stop boundary: produce a current `DISCOVERY.md` and explicit Planning-readiness decision; do not create production implementation or Planning-owned architecture/API/data/stage detail

Authority and external effects:
- Reversible Discovery artifact edits inside the selected run root: allowed
- Disposable prototypes/examples: allowed only in an isolated scratch path when they unlock a named decision
- Network research: read-only and bounded to a named decision; otherwise disabled
- Credentials, secrets, destructive changes, deployment, publishing, purchases, messages, and public actions: not authorized
- Material product, legal, security, expensive, or hard-to-reverse decisions: require explicit approval

Checkpoint policy:
- Commit policy: do not commit unless I explicitly authorize a path-limited checkpoint
- Preserve all pre-existing dirty paths and record the baseline Git/filesystem state

Human preference / UAT policy:
- Inspect available evidence first
- When a tacit preference materially affects framing, show bounded alternatives or a disposable prototype, persist the gate, and ask one focused question
- Treat preference/UAT response and manual session restart as real pauses; do not claim unattended continuation

Model and capability policy:
- Preferred orchestrator: highest-reasoning/Fable-class if the host exposes it
- Preferred Discovery workers: highest-reasoning/Fable-class if the host exposes it
- Exact model required: no
- If selection is unavailable, use `host_default` and record requested model, effective model, and fallback reason
- If context telemetry is unavailable, record `unavailable` and enforce work-unit budgets without estimating hidden context

Artifact policy:
- Existing planning location: auto-detect
- Fallback run root: `docs/agent-runs/<YYYYMMDD>-<goal-slug>[-N]/`
- Protocol: `autonomous-artifacts-v2`
- Canonical outputs: `AGENT-STATE.md`, bounded append-only `EVENTS.jsonl`, `SCOPE.md`, `DISCOVERY.md`, and `gates/G-###.md` when paused
- Worker dispatch: keep portable artifact references, but have the top-level orchestrator resolve lexical and physical/canonical repository/worktree/run/working/input/output/report/evidence paths; reject escaping symlink/junction/mount/Windows-reparse traversal or unprovable nearest-existing-ancestor containment before dispatch, then physically recheck every written target before acceptance
- On resume or compaction, reconstruct from files and repository evidence before dispatch

Retry and session policy:
- Maximum evidence-driven remediation cycles per packet: 2
- Normal `session_budget`: 6 weight units
- High-risk or UI/preference session budget: 4 weight units
- Split every Large unit; do not reduce verification to fit a session
- When cutover is required, write `SESSION-HANDOFF.md`, `continuation_kind`, `continuation_verification`, and the exact `continuation_command` value; use a command only after a harmless capability check, otherwise write a precise manual host action

Requested follow-through:
- After Discovery: {stop | route to Planning when ready}
- After Planning: {stop by default; only a separately authorized execution request may route to Implementation}

Begin by discovering capabilities, reading applicable project instructions, inspecting repository/reference territory, and checking existing artifact freshness. Ask no question until observable evidence has been inspected. Report completion only after opening representative artifacts and verifying the readiness evidence.
```
