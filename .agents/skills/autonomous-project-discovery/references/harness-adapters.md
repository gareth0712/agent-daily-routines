# Harness Adapters

## Rule

The workflow names semantic actions. Map each action only to a capability the active host actually exposes. Discover capabilities before dispatch, record unavailable capabilities and fallbacks in `AGENT-STATE.md`, and never claim a tool, model, telemetry signal, browser, or new session exists because another harness has one.

Claude Code and Codex are adapters to the same artifact workflow, not separate workflows.

## Semantic action map

| semantic action | Claude Code adapter | Codex adapter | generic fallback |
|---|---|---|---|
| `discover_capabilities` | Inspect the current tool/agent surface and read applicable `CLAUDE.md` and `AGENTS.md`. | Inspect the current collaboration/tool surface and read applicable `AGENTS.md` and `CLAUDE.md`. | Inventory exposed tools and every applicable instruction file; when evidence cannot establish a capability, persist its status as `unknown`, record why, and apply the conservative unavailable fallback until evidence establishes availability. |
| `spawn_worker` | Use the exposed Agent/subagent mechanism with a fresh, self-contained contract. | Use the exposed collaboration/subagent mechanism with a fresh, self-contained contract. | A genuinely isolated worker mechanism is required; if absent, mark orchestration blocked and return to the top-level user/parent. |
| `wait_for_worker` | Use the host's foreground result or task-wait mechanism. | Use the host's agent wait/status mechanism. | Use only a supported wait/status operation; do not simulate completion or busy-loop with arbitrary sleep. |
| `inspect_artifact` | Open the assigned report, evidence, and representative outputs with available read tools. | Open the assigned report, evidence, and representative outputs with available read tools. | Read the actual filesystem or connected artifact store; a worker return alone is insufficient. |
| `verify_evidence` | Run project checks and use exposed browser/screenshot/computer observation when relevant. | Run project checks and use exposed browser/screenshot/computer observation when relevant. | Use observable commands/files; if required UI observation is unavailable, persist a human gate instead of substituting source inspection. |
| `checkpoint_state` | The top-level orchestrator updates `AGENT-STATE.md` after inspection. | The top-level orchestrator updates `AGENT-STATE.md` after inspection. | Preserve the same single-writer and report-before-state ordering with the host's safe file-edit mechanism. |
| `append_event` | Prefer the bundled `scripts/append_event.py` after a Python capability check and passing `--self-test`; do not invent a new helper. | Prefer the bundled `scripts/append_event.py` after a Python capability check and passing `--self-test`; do not invent a new helper. | Use an independently verified equivalent only when Python is unavailable. It must enforce the same prefix, single-write, `sha256`, pre-armed `EVENTS.FROZEN`, durability, exact-delta, and no-rewrite contract. A frozen/failed stream blocks; never delete its marker or retry it. A denied adapter is not retried through different syntax. |
| `request_human_gate` | Ask one focused question and persist the paused state before yielding. | Ask one focused question and persist the paused state before yielding. | Surface one decision with evidence, alternatives, impact, and safe default if one exists; never claim an answer. |
| `route_stage` | Invoke or recommend the owning skill only after state/artifact readiness is current. | Invoke or recommend the owning skill only after state/artifact readiness is current. | Write the owning stage and reason into state; do not absorb another stage's responsibility. |
| `finish_or_handoff` | Continue in a new top-level session only if the host explicitly supports it; otherwise write a manual host action. | Continue in a new top-level task only if explicitly supported; otherwise write a manual host action. | Persist the verified-command or manual-host-action contract, set `restart_mode: manual` when needed, and end cleanly. |

## Capability record

Record each capability as `available`, `unavailable`, or `unknown`, plus the observed host evidence and selected fallback.

| capability | Claude Code possibility | Codex possibility | recorded fallback |
|---|---|---|---|
| Fresh isolated worker | Agent/subagent mechanism may be exposed. | Collaboration/subagent mechanism may be exposed. | Hard blocker for this orchestration workflow if no isolated worker exists. |
| Model selection | Alias or exact model ID may be selectable. | A selector may or may not be exposed. | Set `effective_model: host_default` and record a non-empty `fallback_reason`; block only when the user required the exact model. |
| Context telemetry | Host-reported usage may be exposed. | Host-reported usage may be exposed. | Set `context_telemetry: unavailable`; enforce artifact and weight budgets without estimating hidden context. |
| Project instructions | `CLAUDE.md` and `AGENTS.md` may both apply. | `AGENTS.md` and `CLAUDE.md` may both apply. | Search the project hierarchy and read every applicable instruction file found. |
| UI observation | Browser, screenshot, or computer-use may be exposed. | Browser, screenshot, or computer-use may be exposed. | Mark required visual verification or preference/UAT as a human gate. |
| Git | Repository commands may be available. | Repository commands may be available. | Record filesystem revision evidence and pre-existing paths; never invent a Git SHA. |
| Python event adapter | `python` may execute the bundled `scripts/append_event.py`. | `python` may execute the bundled `scripts/append_event.py`. | Run a harmless `--self-test`. If Python is unavailable, require an independently verified equivalent; otherwise block event-audit capability rather than generating ad hoc code. |
| New top-level session | May exist only through an explicitly exposed host action. | May exist only through an explicitly exposed host action. | Use `verified_command` only after a harmless capability check; otherwise persist a precise `manual_host_action`. |

## Model policy

Model names are preferences, not assumptions. Discovery may request a highest-reasoning/Fable-class orchestrator and workers, but it must record `requested_model`, `effective_model`, and `fallback_reason` for each. Use exact model IDs only after capability discovery confirms them. Unavailable selection is ordinarily non-blocking.

## Dispatch minimum

Before calling the worker adapter, preflight required inputs, capability, authority, dependencies, and path anchors. If a requirement is missing, do not dispatch: keep completed weight unchanged, set the packet `blocked`, use `effective_model: not_executed` with a non-empty block/fallback reason, use report `none_not_dispatched`, write bounded orchestrator-owned preflight evidence plus canonical `gates/G-###.md`, and append the transition events. Select `capability` for an unavailable host/worker/tool surface, `environment` for filesystem/dependency/path-inspection failures, and `internal_recovery` for an orchestrator-owned contradiction or exhausted recovery; retain the human gate types for actual human decisions. `not_executed` is permitted only when no worker ran.

Every dispatched worker receives the goal, one packet outcome, scope and stop boundary, required instruction paths, portable artifact paths, allowed side effects, requested model preference, verification and fallback, and the at-most-ten-line return contract. It also receives the top-level orchestrator's recorded lexical absolute and physical/canonical `repository_root`, `worktree_root`, `run_root`, `working_directory`, `input_paths`, `output_paths`, `report_path`, and `evidence_paths`, plus preflight containment evidence. The worker does not receive hidden conversation context as a dependency.

The top-level orchestrator establishes physical containment before dispatch: resolve canonical roots, inspect existing components without following links, reject symlink/junction/mount/Windows-reparse traversal, and resolve the nearest existing ancestor plus uncreated suffix for new targets. If the active host cannot perform those checks, open an `environment` or `capability` gate and do not dispatch.

Before its first write, the worker repeats those checks and blocks on mismatch. This is defense in depth, not the trust boundary. After work, it inventories the assigned root and checks scoped repository/worktree surfaces for out-of-root changes. The top-level orchestrator then physically re-resolves every written target and accepts nothing until it remains under the recorded canonical run root. Relative artifact paths never substitute for physical/canonical filesystem targeting when worktrees, nested agents, links/reparse points, or differing patch/shell bases are possible.

## Continuation adapter

Persist `continuation_kind: verified_command | manual_host_action`, `continuation_verification`, and the exact value in `continuation_command`. A `verified_command` requires a harmless check that proves the executable and intended invocation form work. Without that evidence, write a natural-language `manual_host_action` naming `autonomous-project-discovery`, the absolute run root, files to read first, required gate input, and next action. Never synthesize unsupported CLI syntax.
