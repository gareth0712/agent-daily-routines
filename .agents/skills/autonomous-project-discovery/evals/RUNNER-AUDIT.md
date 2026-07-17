# Runner-owned Discovery eval audit

`run_audit.py` is a reproducible eval-harness observer. It is not part of a Discovery run's production control plane and does not replace canonical `AGENT-STATE.md` or production `EVENTS.jsonl`.

## Isolation and secret contract

- Start the observer before the cold-start executor.
- Put `--output-root` inside the evaluated Git repository/worktree.
- Put `--audit-dir` beside `--output-root`. The resolved roots must be physical siblings; neither may contain the other. Use fresh directories such as `run-1/outputs/` and `run-1/runner-audit/`.
- Put `--stop-file` and `--control-file` directly inside `--audit-dir`. The four exact runner-owned files are `runner-audit.jsonl`, `summary.json`, the configured control file, and the configured stop file. Other descendants of `--audit-dir` remain ordinary outside-output writes.
- Generate at least 32 random bytes and supply them only through `DISCOVERY_RUNNER_AUDIT_HMAC_KEY` to the observer and the parent runner that signs controls. Never pass the variable to the cold-start executor. Never put the secret in a command line, file, log, event, summary, prompt, report, or evidence artifact. HMAC tags are not the secret.
- Do not expose audit/control/stop paths to the executor. Only the parent eval runner signs controls.
- Use a fresh audit directory for every run. A non-empty control file is rejected at startup.

Example observer invocation after setting the environment variable in the private parent/observer environment:

```text
python skills/autonomous-project-discovery/evals/run_audit.py --repo <absolute-repository-or-worktree> --output-root <absolute-run-dir>/outputs --audit-dir <absolute-run-dir>/runner-audit --stop-file <absolute-run-dir>/runner-audit/STOP --control-file <absolute-run-dir>/runner-audit/runner-control.jsonl --poll-ms 100
```

Wait for `runner_started`, run one cold-start executor without the HMAC environment variable, then append authenticated controls one at a time. Stop only after the requested terminal events. A run is final only when the process exits successfully, `summary.json` exists, and the last event is `runner_finalized` with the summary hash.

## Authenticated append-only control

Each newline-terminated control object contains:

- `control_seq`: positive integers starting at 1 with no gaps;
- `previous_hmac`: `null` for sequence 1, then the prior line's lowercase HMAC;
- unique `request_id`, `action`, and `packet_id`;
- action fields;
- `hmac`: lowercase HMAC-SHA256 over canonical UTF-8 JSON of every other field (`sort_keys=true`, compact separators).

The observer validates the complete-line prefix on every poll. Forged, replayed, out-of-order, rewritten, or truncated controls are rejected or invalidate the channel; lifecycle acceptance is false whenever authentication or append-only history is invalid. Audit events never copy the HMAC or secret.

An authenticated sample request has no executor-selected path list:

```json
{"control_seq":1,"previous_hmac":null,"request_id":"sample-D-001","action":"sample","packet_id":"D-001","hmac":"<parent-computed-tag>"}
```

The observer independently requires and hashes this exact canonical set:

- root `AGENT-STATE.md`;
- `reports/D-001-report.md`;
- every non-empty worker-evidence file under `evidence/D-001/` (excluding the two containment files);
- non-empty `evidence/D-001/path-containment-postwrite.md`.

It also requires an earlier observer-visible status for the same packet in the canonical `## Packets` table, followed by a later active (`pending`, `in_progress`, or `blocked`) to `verified` transition. A first-seen already-verified row is insufficient. Every canonical report/evidence/post-write file write must precede the corresponding verified `AGENT-STATE.md` write by both observer event order and filesystem mtime; equal/ambiguous timing rejects. The transition is bound to a digest of the canonical packet row. Any later observed mutation, disappearance, or incompatible transition permanently invalidates that verified transition even if the old row bytes are restored. Updates elsewhere in `AGENT-STATE.md` remain allowed.

After `runner_sample_completed`, append a chained verification trigger:

```json
{"control_seq":2,"previous_hmac":"<prior-tag>","request_id":"verify-D-001","action":"verify","packet_id":"D-001","sample_request_id":"sample-D-001","hmac":"<parent-computed-tag>"}
```

The request is only a trigger. The observer reopens and rehashes the entire canonical set, confirms the current verified packet row and the same observed transition, and compares the immutable report/evidence/containment manifest to the sampled manifest. It records both full-state hashes but does not require unrelated mutable state sections to remain byte-identical between sample and verify. Only then does it emit `runner_verification_observed`. Any immutable sampled-artifact mutation, missing/empty/noncanonical artifact, missing/invalidated transition, verified-row rewrite, or manifest mismatch emits `runner_control_rejected`.

## Evidence boundary

`runner-audit.jsonl` is append-only runner evidence with monotonic `event_seq`, timezone-aware timestamps, hashes, sizes, roles, and packet IDs. Files under `gates/` always use neutral `canonical_gate` roles.

Production `EVENTS.jsonl` is only a cross-check. The observer validates observed complete-line append-only history, source sequence/timestamps, contained references, and SHA-256 or Git-revision content. Production claims never create runner sample, transition, or verification events. Polling proves only mutations visible across snapshots.

`summary.json` uses `runner-audit-v2` and records Git snapshots, exact outside-output changes, output files, production-code candidates, authenticated control integrity, per-packet lifecycle ordering, production cross-checks, and observed/unaudited channels. Strict order requires canonical artifact writes < observed active-to-verified state transition < authenticated sample < independent verification re-sample. Network, remote services, out-of-repository or ignored writes outside assigned roots, credentials, external processes, publishing, deployment, messaging, purchases, and host-private tool activity remain `unaudited`.

## Smoke test

```text
python skills/autonomous-project-discovery/evals/test_run_audit.py
```

The behavioral suite covers positive strict ordering with legitimate non-row state updates before sampling and between sampling/verification, plus: verified state written before later artifacts in the same polling snapshot; no state transition; first-seen verified state; verified-row mutate-and-restore; empty/noncanonical artifacts; forged, replayed, rewritten, and truncated control; audit/output ancestor rejection; a real outside-output write; valid/invalid production-only claims; production stream rewriting; path/hash escape; neutral roles for all nine gates; Git isolation; exact hashes; and secret non-persistence. Temporary repositories are removed automatically and Python bytecode is disabled.
