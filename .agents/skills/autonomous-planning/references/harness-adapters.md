# Harness Adapters

## Rule

Use semantic actions and map them only to capabilities the active host actually exposes. Claude Code and Codex are adapters to the same artifact workflow, not separate workflows. Discover capabilities before dispatch, persist `available`, `unavailable`, or `unknown` with evidence and fallback, and never claim a model, telemetry signal, browser, Git repository, or new top-level session exists because another host has one.

## Semantic action map

| action | Claude Code possibility | Codex possibility | portable fallback |
|---|---|---|---|
| `discover_capabilities` | Inspect Agent/tool surface and applicable `CLAUDE.md`/`AGENTS.md`. | Inspect collaboration/tool surface and applicable `AGENTS.md`/`CLAUDE.md`. | Inventory exposed tools and every instruction file; unknown applies the conservative unavailable fallback. |
| `spawn_worker` | Use a fresh Agent/subagent with a self-contained packet. | Use a fresh collaboration/subagent with a self-contained packet. | Isolated worker capability is required; otherwise open a `capability` gate and return to the top-level parent. |
| `wait_for_worker` | Use foreground result or task wait. | Use agent wait/status. | Use only supported wait/status; never simulate completion or busy-loop with arbitrary sleep. |
| `inspect_artifact` | Open report/evidence/output with read tools. | Open report/evidence/output with read tools. | Read the real artifact store; chat return is insufficient. |
| `verify_evidence` | Run read-only project checks and inspect relevant files. | Run read-only project checks and inspect relevant files. | Mark required evidence unavailable; do not invent it or modify product code to obtain it. |
| `checkpoint_state` | Top-level orchestrator updates state after inspection. | Top-level orchestrator updates state after inspection. | Preserve single-writer and report-before-state ordering. |
| `append_event` | Run bundled Python helper after capability check/self-test. | Run bundled Python helper after capability check/self-test. | Use an independently verified equivalent only if Python is unavailable; otherwise block rather than weaken the append/freeze contract. |
| `request_human_gate` | Persist one canonical gate, then ask one focused question. | Persist one canonical gate, then ask one focused question. | Include evidence, alternatives, impact, owner, and safe default if one exists. |
| `route_stage` | Invoke/recommend the owning skill after durable routing. | Invoke/recommend the owning skill after durable routing. | Never absorb Discovery framing or Implementation execution ownership. |
| `finish_or_handoff` | Use a new session only when explicitly exposed. | Use a new task only when explicitly exposed. | Persist a verified command or precise manual host action and end cleanly. |

## Capability and model policy

Request a highest-reasoning/Fable-class orchestrator and Planning workers only as preferences. Use exact model IDs only after the host confirms support. Record `requested_model`, `effective_model`, and non-empty fallback reason per worker. If no selector exists, use `host_default`; block only when the user made an exact model mandatory.

If context usage is exposed, record the host value. Otherwise write `context_telemetry: unavailable` and enforce artifact/weight ceilings without guessing a percentage. If Git is unavailable, record a reproducible filesystem/reference revision and never invent a SHA. If the host cannot create a top-level session, restart is manual.

## Dispatch minimum

Before dispatch, preflight current inputs/revisions, dependencies, authority, isolated worker capability, model fallback, durable progress boundary, and lexical plus physical/canonical repository/worktree/run/working/input/output/report/evidence anchors. The top-level orchestrator resolves physical components, rejects escaping symlink/junction/mount/Windows-reparse traversal, and proves containment using the protocol. If this cannot be established, do not dispatch: use `blocked`, `effective_model: not_executed`, report `none_not_dispatched`, bounded preflight evidence, and a canonical `capability` or `environment` gate.

A dispatched worker receives the packet verbatim, accepted Discovery revision, applicable instruction paths, allowed read/write surfaces, requested model, verification/fallback, progress boundary, physical anchors, and at-most-ten-line return contract. It repeats containment checks as defense in depth and writes its progress marker before analysis. Afterward, the orchestrator rechecks containment and inspects artifacts before acceptance.

## Continuation adapter

Persist `continuation_kind: verified_command | manual_host_action`, `continuation_verification`, and the exact `continuation_command` value. A verified command requires a harmless observed check of executable and invocation form. Otherwise write natural language naming `autonomous-planning`, the absolute run root, first-read files, required gate input, and next action. Never synthesize unsupported CLI syntax or claim automatic restart.
