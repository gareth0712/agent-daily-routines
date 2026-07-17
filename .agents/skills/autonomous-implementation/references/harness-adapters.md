# Harness Adapters

## Rule

Map semantic actions only to capabilities the active host actually exposes. Claude Code and Codex are adapters to one artifact workflow, not separate workflows. Persist `available`, `unavailable`, or `unknown` with observed evidence and fallback; never infer a model selector, telemetry signal, browser, Git repository, design skill, commit authority, external permission, or new top-level session from another host.

## Semantic action map

| action | Claude Code possibility | Codex possibility | portable fallback |
|---|---|---|---|
| `discover_capabilities` | Inspect Agent/tool surface plus `CLAUDE.md`/`AGENTS.md`. | Inspect collaboration/tool surface plus `AGENTS.md`/`CLAUDE.md`. | Inventory exposed tools and instructions; unknown takes the conservative unavailable fallback. |
| `spawn_worker` | Use one fresh Agent/subagent with a self-contained stage. | Use one fresh collaboration/subagent with a self-contained stage. | Isolated worker is required; otherwise open a `capability` gate and return to the parent/top-level session. |
| `wait_for_worker` | Use foreground result or supported task wait. | Use agent wait/status. | Use only host-supported wait/status; never simulate completion or busy-loop with arbitrary sleep. |
| `inspect_artifact` | Open report/evidence/product output with read tools. | Open report/evidence/product output with read tools. | Read the real artifact/product store; chat return is insufficient. |
| `verify_evidence` | Run project checks, inspect diffs, and use browser/screenshot tools when exposed. | Run project checks, inspect diffs, and use browser/screenshot tools when exposed. | Mark required evidence blocked; do not invent a pass or weaken the contract. |
| `checkpoint_state` | Top-level orchestrator updates state after inspection. | Top-level orchestrator updates state after inspection. | Preserve single-writer and report-before-state ordering. |
| `append_event` | Run bundled Python helper after capability check/self-test. | Run bundled Python helper after capability check/self-test. | Use an independently verified equivalent only if Python is unavailable; otherwise block. |
| `request_design_preferences` | Invoke installed relevant skills when the host exposes them. | Invoke installed relevant skills when the host exposes them. | Record unavailable/not-installed and continue only if the Task Contract remains verifiable without them. |
| `request_human_gate` | Persist one canonical gate, then present actual UI/decision evidence. | Persist one canonical gate, then present actual UI/decision evidence. | Include evidence, criteria, impact, owner, and exact blocked boundary. |
| `route_stage` | Invoke/recommend the owning pipeline skill after durable routing. | Invoke/recommend the owning pipeline skill after durable routing. | Never absorb Discovery framing or Planning architecture/contract ownership. |
| `finish_or_handoff` | Use a new session only when explicitly exposed. | Use a new task only when explicitly exposed. | Persist a verified command or precise manual host action and end cleanly. |

## Model and preference policy

Request a highest-reasoning orchestrator and Sonnet-class/high-effort implementation workers as preferences. Use exact model IDs only after the host confirms support. Record `requested_model`, `effective_model`, and a non-empty fallback reason per worker. If no selector exists, use `host_default`; block only when the user made the exact model mandatory.

For `[UI]`, request installed relevant `design-taste-frontend`, `high-end-visual-design`, and `minimalist-ui`; also request `redesign-existing-projects` for an existing-page redesign. Record each as `invoked`, `unavailable`, `not_installed`, or `not_relevant` with evidence. A named preference is not proof of invocation, and this skill never installs another skill silently.

If context usage is exposed, record the host value. Otherwise use `context_telemetry: unavailable` and enforce work-unit ceilings. If Git is unavailable, use reproducible filesystem hashes/diffs and never invent a SHA or commit. If browser/screenshot capability is unavailable for required UI verification, block the stage instead of substituting source inspection. If the host cannot create a top-level session, restart is manual.

## Dispatch minimum

Before dispatch, preflight current upstream revisions, exact Task Contract, dependencies, side-effect authority, isolated worker, model fallback, applicable instruction paths, durable progress/exhaustion signal, remaining session budget, dirty-path inventory, and lexical plus physical/canonical repository/worktree/run/working/input/output/report/evidence anchors.

If required evidence cannot be established, do not dispatch: use `blocked`, `effective_model: not_executed`, report `none_not_dispatched`, bounded orchestrator preflight evidence, and a canonical `capability`, `environment`, `authority`, or owning-stage route.

A dispatched worker receives the Task Contract verbatim, accepted Discovery/Planning revisions, applicable instructions, exact product/artifact writes, exact side effects, requested/effective model contract, verification/fallback/UAT, progress boundary, physical anchors, and at-most-ten-line return contract. The worker repeats containment checks, writes its progress marker, then changes only owned paths. When the host reports the worker terminal, the orchestrator captures that exact boundary, writes an immutable `return_observed` attempt receipt with fresh identity, full subtree status, canonical UTF-8 base64 return payload/line count/hash, report/evidence hashes, and lifecycle times, then appends the receipt-observation event. It reconciles dispatch/receipt/retry/remediation counts and independently rechecks containment, dirty paths, diffs, commands, and representative behavior before a later acceptance/rejection event records final disposition.

## Continuation adapter

Persist `continuation_kind: verified_command | manual_host_action`, `continuation_verification`, and exact `continuation_command`. A verified command requires an observed harmless check of executable and invocation form. Otherwise write natural language naming `autonomous-implementation`, the absolute run root, first-read files, required gate input, and next action. Never synthesize unsupported CLI syntax or claim automatic restart.
