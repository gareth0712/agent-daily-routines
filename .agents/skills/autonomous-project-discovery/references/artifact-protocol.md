# Autonomous Artifacts Protocol

## Identifier and scope

Use `protocol_version: autonomous-artifacts-v2` for Discovery, Planning, and Implementation runs. Each skill vendors this protocol so it remains usable alone. Durable artifacts are the source of truth; conversation summaries and worker completion messages are claims until reconciled with files and repository evidence.

## Canonical run root

Use the project's established planning location. When none exists, create:

```text
docs/agent-runs/<YYYYMMDD>-<goal-slug>[-N]/
├── AGENT-STATE.md
├── EVENTS.jsonl
├── SCOPE.md
├── DISCOVERY.md
├── MASTER-PLAN.md
├── IMPLEMENTATION-NOTES.md
├── gates/
│   └── G-###.md
├── packets/
│   └── D-001.md, P-001.md, or I-001.md
├── reports/
│   └── D-001-report.md, P-001-report.md, or I-001-report.md
├── evidence/
└── SESSION-HANDOFF.md
```

Append `-2`, `-3`, and so on if the computed run root already exists. Artifacts use portable forward-slash paths even when the active shell needs different quoting.

## Single-writer control plane

`AGENT-STATE.md` is the sole authoritative control-plane index, and only the top-level orchestrator writes it. `EVENTS.jsonl` is bounded audit evidence, not a second state index; only the top-level orchestrator appends it. Workers write only their assigned packet output, report, and evidence paths. A worker must never set its own packet status, append events, or edit another worker's artifact.

The state records at minimum:

- protocol version, workflow type, active pipeline stage, run ID, absolute repository/worktree roots, and the portable run-root path;
- harness, discovered capabilities, unavailable capabilities, and fallback behavior;
- requested/effective orchestrator and worker models plus fallback reasons;
- baseline Git SHA and pre-existing dirty paths when Git exists;
- `SCOPE.md`, stop-boundary, and stage-artifact paths;
- Discovery, Planning, and Implementation readiness values;
- artifact revisions, source revisions, freshness evidence, `derived_from`, and `supersedes` links;
- packet table, dependency, status, report, evidence, requested/effective model, and fallback reason;
- `session_budget`, `completed_weight`, retry counters, risk mode, context telemetry, and UAT state;
- `events_accepted_count`, `events_accepted_tip`, and `events_accepted_file_sha256` from the last successful append, plus the evidence/time that accepted the anchor;
- next stage, next action, `continuation_kind`, `continuation_verification`, exact `continuation_command` value, and whether restart is manual.

Packet statuses are exactly `pending`, `in_progress`, `verified`, `blocked`, or `superseded`.

## Readiness semantics

`discovery_readiness` is the current Discovery artifact's handoff/entry readiness for Planning. Derive the exact `DISCOVERY.md` summary line from it: `ready` maps to `Planning readiness: READY`; `not_ready` and `stale` map to `Planning readiness: NOT_READY`.

`planning_readiness` is different: it describes an actual Planning artifact's readiness for its downstream stage. Keep it `not_assessed` until a Planning artifact exists. Protocol v2 retains both shared field names; do not use `planning_readiness` as a synonym for Discovery handoff readiness.

## Artifact lineage and freshness

Every stage artifact declares a stable revision identifier, the repository/reference revisions it inspected, its upstream `derived_from` revision, freshness evidence, creation/update time, and any revision it supersedes. A content digest, Git SHA, or explicit revision string is acceptable when reproducible.

Before consuming an upstream artifact:

1. Confirm the path exists and the artifact has the required decisions, not merely the expected filename.
2. Compare recorded repository/reference revisions with current evidence.
3. Inspect known contradiction paths and pre-existing dirty changes.
4. Mark the artifact stale when current evidence changes a decision owned by that stage.
5. Preserve the contradiction and supersession link; route to the owning stage.

A framing contradiction routes to Discovery. An architecture, interface, data, sequencing, migration, or verification contradiction routes to Planning. A local reversible choice inside a current contract remains with Implementation.

Equivalent non-canonical artifacts may be consumed only when their content satisfies the required fields and freshness checks. Record the equivalent source path and mapped revision.

## Physical path containment and dispatch anchors

Portable forward-slash paths remain canonical references inside state, packet, report, and gate artifacts. The top-level orchestrator is the containment trust boundary. Before dispatch, it records both lexical absolute and physical/canonical values for these anchors and includes them in the worker contract:

- `repository_root`
- `worktree_root`
- `run_root`
- `working_directory`
- `input_paths`
- `output_paths`
- `report_path`
- `evidence_paths`

Containment uses physical filesystem identity and path components, never string prefixes or lexical normalization alone:

1. Resolve the existing repository and worktree roots to physical/canonical paths and record their filesystem identity. Resolve an existing run root the same way; when it does not exist, resolve its nearest existing ancestor first.
2. Walk every existing component from the allowed physical root to each input and assigned write target with no-follow metadata. Reject traversal through symbolic links, junctions, mount points, Windows reparse points, or an ancestor whose physical target escapes the allowed root. If the host cannot inspect a component or distinguish these cases, preflight is blocked.
3. For each not-yet-existing target, record the canonical nearest existing ancestor and uncreated suffix. Prove the ancestor is contained, then create/re-resolve required directory suffix components one at a time; leave the assigned file leaf for the authorized writer and re-resolve it after creation. Reject a component that becomes a link, junction, mount, reparse point, or physical escape.
4. Compare canonical path components using the filesystem's case rules. Inputs must remain under their explicitly allowed physical read root; output, report, and evidence targets must remain under the canonical run root.
5. Record bounded preflight evidence with lexical/canonical roots, inspected components, filesystem identities where exposed, nearest-existing-ancestor results, and the decision. Inability to prove containment opens an `environment` or `capability` gate and no worker runs.

Before substantive analysis, the worker repeats normalization, no-follow component inspection, and physical containment using the recorded anchors, then writes its assigned `evidence/<packet>/worker-progress.md` marker with start time, assigned leaves, anchor digest or bounded anchor summary, and first next action. This is defense in depth and liveness evidence only; worker self-checks and progress markers never establish acceptance. Update the marker only at bounded milestone changes, not as a raw log. After work, the top-level orchestrator re-resolves every written target and existing component, confirms physical containment against the recorded canonical run root, and records post-write evidence before artifact sampling or `verified`. A changed/escaping component blocks acceptance and opens `internal_recovery`; do not normalize it away or ask the worker to certify its own escape.

Never rely on a relative path when a worktree, nested worker, or patch/shell tool may use a different base. After work, the worker also inventories its assigned root and checks scoped repository/worktree surfaces for out-of-root changes; any contradiction is evidence for `blocked`.

## Pre-dispatch blocking

Preflight required inputs, capabilities, authority, dependencies, and all absolute path anchors before invoking `spawn_worker`. When a required item is missing:

1. Do not dispatch a worker.
2. Set the packet to `blocked`; leave `completed_weight` unchanged.
3. Set `effective_model: not_executed` and a non-empty block/fallback reason. `not_executed` is valid only when no worker ran.
4. Set the report field to `none_not_dispatched`; do not create a worker report.
5. Write bounded orchestrator-owned preflight evidence under the packet evidence root and open canonical `gates/G-###.md`. Use `capability`, `environment`, or `internal_recovery` for operational blockers; do not mislabel them as human decisions.
6. Append packet-status, `preflight_blocked`, and `gate_opened` events.

A worker report is valid only after a worker actually ran. Orchestrator preflight evidence must not imitate the reusable worker-report schema.

## Canonical gate classes

Every pause or blocker uses one `gates/G-###.md`, but not every gate asks a human question. Human-decision types are `preference`, `product_decision`, `authority`, `uat`, and `security_legal`. `external_evidence` waits for a named external evidence owner. Operational types are:

- `capability`: a required host/tool/isolated-worker capability is unavailable or unconfirmed; owner is the host operator or parent session, with an observable enablement/check route;
- `environment`: required filesystem, dependency, path-inspection, or execution-environment evidence cannot be established; owner is the environment maintainer or orchestrator when repair is already authorized;
- `internal_recovery`: a contradiction, failed bounded remediation, or post-write containment failure requires orchestrator/stage recovery rather than a product decision.

Every gate records `owner_kind`, whether a human response is required, the exact recovery or question, evidence needed, and the resulting route. Do not use an operational type to hide a required product, authority, UAT, security, or legal decision; do not pause for a human answer when an authorized internal recovery remains available.

## Durable lifecycle audit

`EVENTS.jsonl` is a bounded append-only audit artifact. Each line is one JSON object with a monotonically increasing `event_seq`, a fresh timezone-aware ISO-8601 `timestamp` strictly later than the preceding event, `event_type`, `stage`, optional `packet_id`, `from_status`, `to_status`, `actor`, referenced paths with reproducible SHA-256/revisions, a bounded `evidence_summary`, `previous_event_sha256`, and `event_sha256`. For every referenced local file that exists, compute and record its actual lowercase 64-hex SHA-256 in the field named exactly `sha256`; an informal artifact revision does not substitute for the digest. If the file does not yet exist, omit that reference and cite the expected path only in `evidence_summary`. Read the clock for each append; when clock granularity would repeat or regress, serialize the append and use a later valid timestamp rather than copying the prior value. The top-level orchestrator is the only writer. Never include secrets, chain-of-thought, transcripts, or raw/unbounded logs.

The first record uses `previous_event_sha256` equal to 64 lowercase zeroes. Every later record's `previous_event_sha256` equals the immediately preceding validated `event_sha256`. Calculate `event_sha256` over canonical UTF-8 JSON for the complete event excluding `event_sha256`: sort object keys lexically, use `,` and `:` with no insignificant whitespace, preserve Unicode rather than ASCII-escaping it, and reject non-finite numbers. Every existing record must carry a valid lowercase 64-hex link and canonical digest.

The chain detects missing/forged fields and unrecomputed edits inside the stream. Across calls, compare the actual stream with the durable accepted anchor from state: record count, final `event_sha256` tip, and SHA-256 of the complete exact `EVENTS.jsonl` bytes. This anchor detects a chain-valid whole-history rewrite, tail truncation, or deletion only when the prior accepted anchor remains trustworthy. It does not resist an actor that can rewrite both the stream and every durable accepted anchor; do not claim that stronger property. Runner-owned immutable evidence may add an external trust anchor but is not assumed available.

Append one fully serialized, newline-terminated JSON object through the verified `append_event` adapter. Never use an editor, patch operation, truncate-and-rewrite, or read/concatenate/write cycle on an existing event stream; those destroy independent append-history evidence and can expose partial JSON to observers.

For every append, enforce this byte contract:

1. Validate all CLI/event fields and hash/contain every referenced file before stream preflight. An invalid CLI field, partial/invalid expected-anchor tuple, or invalid/missing/escaping reference fails without creating `EVENTS.FROZEN`.
2. After those preflight checks pass, atomically arm the exact `EVENTS.FROZEN` marker before reading the actual stream prefix. Read the current bytes. An empty stream is valid; a non-empty stream must end at one complete newline boundary and every line must parse with valid monotonic sequence/timestamp and cryptographic-chain fields. Any malformed, partial, containment-invalid, or chain-invalid actual stream leaves the exact marker in place, refuses every later append/self-test, and is never repaired in place.
3. Compare actual record count, final chain tip, and exact full-prefix SHA-256 with `events_accepted_count`, `events_accepted_tip`, and `events_accepted_file_sha256`. For a genuinely empty new stream, the explicit genesis anchor is count `0`, tip 64 lowercase zeroes, and SHA-256 of empty bytes; omission is tolerated only for that clean empty stream. Any non-empty stream requires all three expected values. A mismatch or missing non-empty anchor leaves the stream frozen before write.
4. Record the prefix byte length and SHA-256. Set the new record's previous link, calculate its canonical `event_sha256`, serialize the complete stored object to UTF-8 without embedded record separators, then add exactly one `\n` byte.
5. Open the existing file through a true append-capable filesystem API, submit the complete new bytes in one write call, flush/close, and perform no other event-stream write in that operation.
6. Re-read the bytes and prove: the original prefix length/hash/bytes are unchanged; total length increased by exactly the new byte count; the delta equals the submitted bytes; the new last line parses to the same object and validates its chain digest; and the stream ends at one complete newline boundary. Only then remove the marker and return/persist the new accepted record count, chain tip, and exact full-file SHA-256. A failed postcondition freezes further appends and routes recovery without rewriting history.

The default adapter is the skill's bundled `scripts/append_event.py`. After confirming Python is available, run `python <absolute-skill-root>/scripts/append_event.py --self-test --run-root <absolute-run-root>` and record its bounded JSON success signal before the first real event. For each event, invoke the same script with `--run-root`, `--stage`, `--event-type`, optional packet/status fields, repeated portable `--reference` paths, one bounded `--evidence-summary`, and the durable anchor flags `--expected-event-count`, `--expected-event-tip`, and `--expected-events-sha256`. It derives `EVENTS.jsonl`; callers cannot select another stream path. Genesis values are `0`, 64 lowercase zeroes, and `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. After success, persist the returned `accepted_event_count`, `accepted_event_tip`, and `accepted_events_sha256` before another append.

The script pre-arms `EVENTS.FROZEN` after CLI/reference preflight but before reading the actual stream prefix or performing any possible event-stream write. It removes the marker only after chain/anchor validation, write, durability, close, identity, prefix, delta, JSON, chain, newline, and returned-anchor postconditions pass. After every event postcondition passes, the helper may retry only its marker unlink for Windows sharing/lock errors `32` or `33`, using four total attempts with 25ms between failures. Before every unlink attempt it must revalidate the original marker identity, physical containment, regular single-link type, and exact fixed bytes; the retry path must never repeat the event write. Exhaustion, any other error, marker disappearance, or validation change returns failure and leaves/restores the stream frozen. If a marker remains or an append returns failure, callers stop all later event appends. Callers never delete the marker, retry the same stream, or repair old event bytes.

The marker immediately freezes the predecessor event stream; it does not justify continuing ordinary work without an audit trail. Perform one bounded recovery closure in the predecessor and nothing else: the top-level orchestrator may update only `AGENT-STATE.md`, one canonical `internal_recovery` gate, and `SESSION-HANDOFF.md`. Do not dispatch a worker or modify scope, discovery, packet, report, or evidence artifacts. Keep every closure write inside the already verified canonical run root, close/flush it, reopen it, and compute its final SHA-256. Then treat the entire predecessor run root as immutable. If the final predecessor state, event stream, freeze marker, or closure evidence cannot be reopened and hashed, recovery is blocked; do not create a successor that claims verified lineage.

An authorized recovery creates a distinct new run root. Before its first event, write immutable `evidence/recovery/frozen-predecessor.md` using the binding template and populate these exact `AGENT-STATE.md` lineage fields: `predecessor_run_root`, `predecessor_state_sha256`, `predecessor_events_sha256`, `predecessor_freeze_sha256`, `recovery_evidence_path`, and `recovery_reason`. The predecessor path is portable and project-relative; the three digests are the final lowercase 64-hex SHA-256 values observed after predecessor closure. Initialize the successor's own stream with `run_initialized`, then append `frozen_predecessor_reconciled` referencing only immutable successor-contained recovery evidence. Never append a reconciliation event to the frozen predecessor.

### Binding `evidence/recovery/frozen-predecessor.md` template

Write this immutable artifact inside the physically verified successor run root before initializing the successor event stream. Reopen and hash every predecessor closure file after its final flush; never trust conversation state or a pre-closure digest. The six lineage values in successor `AGENT-STATE.md` must exactly match this artifact.

```markdown
# Frozen Predecessor Recovery

protocol_version: autonomous-artifacts-v2
successor_run_id: {new run ID}
successor_run_root: {portable project-relative new run root}
successor_canonical_run_root: {physical/canonical new run root}
successor_recovery_evidence_path: evidence/recovery/frozen-predecessor.md
successor_first_event: run_initialized
successor_reconciliation_event: frozen_predecessor_reconciled

predecessor_run_root: {portable project-relative frozen run root}
predecessor_canonical_run_root: {physical/canonical frozen run root observed after closure}
predecessor_state_path: {portable path to final predecessor AGENT-STATE.md}
predecessor_state_sha256: {final lowercase 64-hex SHA-256}
predecessor_events_path: {portable path to predecessor EVENTS.jsonl}
predecessor_events_sha256: {final lowercase 64-hex SHA-256}
predecessor_freeze_path: {portable path to predecessor EVENTS.FROZEN}
predecessor_freeze_sha256: {final lowercase 64-hex SHA-256}
predecessor_gate_path: {portable path to final internal_recovery gate}
predecessor_gate_sha256: {final lowercase 64-hex SHA-256}
predecessor_handoff_path: {portable path to predecessor SESSION-HANDOFF.md}
predecessor_handoff_sha256: {final lowercase 64-hex SHA-256}

predecessor_containment_evidence: {portable successor-contained evidence path proving both run roots and every sampled predecessor file were physically contained}
predecessor_closure_observed_at: {timezone-aware ISO-8601 timestamp after reopen/hash}
recovery_evidence_created_at: {timezone-aware ISO-8601 timestamp}
recovery_reason: {bounded reason the predecessor stream froze}
contradictions_reconciled:
- {unsupported state/event claim and disposition | none}
```

Missing, unreadable, mutable, placeholder, escaping, or mismatched predecessor evidence blocks recovery. The successor `run_initialized` event may name this expected path only in its bounded summary because the stream does not yet exist; `frozen_predecessor_reconciled` then references this existing immutable successor-contained artifact by actual SHA-256. The predecessor receives no later event append.

If Python is unavailable, an existing host append API may substitute only after it passes the same scratch, pre-armed-freeze, failure, and byte-invariant checks. Do not generate a helper source file inside the run root or switch syntax/interpreters to bypass a denied operation. If no adapter passes, block bootstrap with a `capability` gate instead of weakening the audit.

Append events for: `run_initialized`; `frozen_predecessor_reconciled` when this run succeeds a frozen predecessor; `packet_created`; every `packet_status_transition`; `path_containment_preflight`; `preflight_blocked`; `worker_dispatched`; `report_observed`; `evidence_observed`; `path_containment_postwrite`; `artifact_sampled`; `packet_verified`; `gate_opened`; `gate_resolved`; `handoff_written`; `stage_routed`; and `reconciliation_contradiction` when the current stream is not frozen.

A transition to `verified` is invalid unless earlier events for that packet record passing post-write physical containment, an existing report, existing evidence, and orchestrator artifact sampling. During recovery, reconcile state, files, and events. Downgrade unsupported `verified` status in `AGENT-STATE.md`. If the current stream is healthy, append `reconciliation_contradiction` with bounded references and never rewrite earlier lines. If it is frozen, record the contradiction in the predecessor's bounded recovery closure and the successor's immutable recovery evidence, then append only `frozen_predecessor_reconciled` to the successor stream. This production log strengthens resumable handoff, but it does not replace runner-owned audit evidence required by evaluations.

## Report-before-state acceptance ordering

Use this order for every packet or stage:

1. After preflight passes, the orchestrator writes the packet, appends creation/status events, and sets status to `in_progress`.
2. After its containment self-check, the worker writes the bounded worker-progress marker before substantive analysis.
3. The worker performs only authorized work and writes its reusable report.
4. The worker writes or cites bounded evidence under the assigned evidence path.
5. The worker returns at most ten lines pointing to the report and evidence.
6. The orchestrator rechecks physical containment of every written target against the recorded canonical run root and records the result.
7. The orchestrator opens the report and representative artifacts, checks cited paths, and reruns a relevant verification when possible.
8. The orchestrator appends report-observation, evidence-observation, and artifact-sampling events.
9. Only after successful containment and inspection may the orchestrator set status to `verified`, append the verified transition, and update derived artifacts.

If containment cannot be re-established, the report is absent, required evidence is absent, an evidence path does not exist, or inspection contradicts the report, status cannot be `verified`. Use `blocked` or keep `in_progress` while bounded remediation remains.

## Reusable report content

Each worker report preserves:

- verdict and primary outcome;
- conclusions and decisions unlocked;
- assumptions and unresolved questions with owners;
- source paths, source revisions, and relevant excerpts;
- commands and bounded relevant output excerpts;
- created/changed files and intentionally untouched paths;
- failures, retry count, and fallback used;
- verification evidence paths and observed signals;
- recommended next action and route.

Reports store work products and evidence, not private reasoning. Never request or persist chain-of-thought, secrets, credentials, tokens, full transcripts, or unbounded raw logs. Redact sensitive values. Keep large raw output outside Git when possible; cite a reproducible command, bounded redacted excerpt, and storage/disposal location.

## Worker return contract

The worker's chat return is at most ten lines and contains only:

1. verdict: `PASS`, `FAIL`, `BLOCKED`, or the packet-specific readiness value;
2. report path;
3. evidence paths;
4. created/changed paths;
5. one-line verification summary;
6. one-line blocker or next-action summary when applicable.

The return never substitutes for the report and never contains chain-of-thought or a full log.

## Compaction, resumption, and handoff

After compaction, interruption, or handoff, treat conversation summaries as unverified. Before dispatching another worker:

1. Read `AGENT-STATE.md`, `SCOPE.md`, the current stage artifact, active packet, packet report, and `SESSION-HANDOFF.md` when present.
2. Reconcile packet statuses with actual report/evidence files.
3. Recheck Git/filesystem state, artifact lineage, and freshness evidence. Validate every event-chain record, then compare actual event count, final tip, and exact full-file SHA-256 with the durable accepted anchor. Any mismatch freezes/routs recovery; never update the anchor to bless unexplained current bytes.
4. Downgrade any unsupported `verified` claim. Append `reconciliation_contradiction` only when the current stream is not frozen. When it is frozen, perform the bounded predecessor closure and successor-lineage procedure above; the frozen predecessor receives no event append.
5. Recompute remaining session budget from verified packet weights.
6. Choose the next action from evidence and rewrite state only as the orchestrator.

Persist `continuation_kind: verified_command | manual_host_action`, `continuation_verification`, and the exact continuation value in the existing `continuation_command` field. Use `verified_command` only after a harmless capability check proves both the executable and invocation form; cite the check and observed signal in `continuation_verification`. Otherwise use `manual_host_action` and write precise natural language naming the skill, absolute run root, files to read first, required gate input, and next action. Set `restart_mode: manual` when the host cannot create a new top-level session. Never invent CLI syntax or claim unattended continuation when a person must restart or answer a preference/UAT gate.
