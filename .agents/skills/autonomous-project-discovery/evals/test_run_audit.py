#!/usr/bin/env python3
"""Contained behavioral tests for the vendored runner-owned audit observer."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable
from unittest import mock


HERE = Path(__file__).resolve().parent
OBSERVER = HERE / "run_audit.py"
APPEND_HELPER = HERE.parent / "scripts" / "append_event.py"
SECRET_ENV = "DISCOVERY_RUNNER_AUDIT_HMAC_KEY"
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))

import run_audit as audit_module  # noqa: E402
from run_audit import classify_file  # noqa: E402


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args), cwd=cwd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=True,
    )


def wait_for(predicate: Callable[[], bool], description: str, timeout: float = 10.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.04)
    raise AssertionError(f"timed out waiting for {description}")


def append_jsonl(path: Path, item: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(item, sort_keys=True) + "\n")


def read_events(audit: Path) -> list[dict[str, Any]]:
    path = audit / "runner-audit.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def wait_for_event(audit: Path, event_type: str, **fields: Any) -> dict[str, Any]:
    found: dict[str, Any] | None = None

    def predicate() -> bool:
        nonlocal found
        found = next(
            (
                event for event in read_events(audit)
                if event.get("event_type") == event_type
                and all(event.get(key) == value for key, value in fields.items())
            ),
            None,
        )
        return found is not None

    wait_for(predicate, f"{event_type} {fields}")
    assert found is not None
    return found


def initialize_repo(repo: Path) -> None:
    run("git", "init", "--quiet", cwd=repo)
    run("git", "config", "user.email", "audit-smoke@example.invalid", cwd=repo)
    run("git", "config", "user.name", "Runner Audit Smoke Test", cwd=repo)
    (repo / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    run("git", "add", "tracked.txt", cwd=repo)
    run("git", "commit", "--quiet", "-m", "test: baseline", cwd=repo)


def start_observer(
    repo: Path, output: Path, audit: Path, *, poll_ms: int = 30
) -> tuple[subprocess.Popen[str], Path, Path]:
    stop = audit / "STOP"
    control = audit / "runner-control.jsonl"
    output.mkdir(parents=True)
    child_env = os.environ.copy()
    child_env["PYTHONDONTWRITEBYTECODE"] = "1"
    assert SECRET_ENV in child_env
    process = subprocess.Popen(
        [
            sys.executable, str(OBSERVER), "--repo", str(repo), "--output-root", str(output),
            "--audit-dir", str(audit), "--stop-file", str(stop), "--control-file", str(control),
            "--poll-ms", str(poll_ms),
        ],
        cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", errors="replace", env=child_env,
    )
    wait_for_event(audit, "runner_started")
    return process, stop, control


def finalize_observer(process: subprocess.Popen[str], audit: Path, stop: Path) -> dict[str, Any]:
    stop.touch()
    stdout, stderr = process.communicate(timeout=10)
    assert process.returncode == 0, f"observer failed\nstdout={stdout}\nstderr={stderr}"
    summary = json.loads((audit / "summary.json").read_text(encoding="utf-8"))
    events = read_events(audit)
    assert events[-1]["event_type"] == "runner_finalized"
    assert [event["event_seq"] for event in events] == list(range(1, len(events) + 1))
    assert all(event.get("timestamp") for event in events)
    secret = os.environ[SECRET_ENV]
    assert secret not in json.dumps(events)
    assert secret not in json.dumps(summary)
    return summary


def stop_after_failure(process: subprocess.Popen[str], audit: Path, stop: Path) -> None:
    if process.poll() is not None:
        return
    audit.mkdir(parents=True, exist_ok=True)
    stop.touch()
    try:
        process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.communicate(timeout=5)


def append_control(
    path: Path,
    payload: dict[str, object],
    control_seq: int,
    previous_hmac: str | None,
    *,
    forge: bool = False,
) -> str:
    unsigned = {"control_seq": control_seq, "previous_hmac": previous_hmac, **payload}
    canonical = json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode("utf-8")
    tag = hmac.new(os.environ[SECRET_ENV].encode("utf-8"), canonical, hashlib.sha256).hexdigest()
    if forge:
        tag = "0" * 64 if tag != "0" * 64 else "1" * 64
    append_jsonl(path, {**unsigned, "hmac": tag})
    return tag


def write_and_observe(audit: Path, path: Path, relative: str, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    wait_for_event(audit, "output_file_created", path=relative)


def state_text(status: str) -> str:
    return f"""# Agent State

## Packets

| Packet | Goal | Size | Weight | Dependencies | Status | Report | Evidence | Requested model | Effective model | Fallback | Retries |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | inspect | Small | 1 | none | {status} | reports/D-001-report.md | evidence/D-001/result.txt | host_default | host_default | none | 0 |
"""


def write_state(output: Path, audit: Path, status: str, *, first: bool = False) -> None:
    path = output / "AGENT-STATE.md"
    path.write_text(state_text(status), encoding="utf-8")
    if first:
        wait_for_event(audit, "runner_packet_state_observed", packet_id="D-001", status=status)
    else:
        wait_for_event(
            audit, "runner_packet_state_transition_observed", packet_id="D-001", to_status=status
        )


def update_state_outside_packet_row(output: Path, audit: Path, next_action: str) -> None:
    path = output / "AGENT-STATE.md"
    updated = state_text("verified") + f"\n## Next action\n\nnext_action: {next_action}\n"
    path.write_text(updated, encoding="utf-8")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    wait_for_event(audit, "output_file_modified", path="AGENT-STATE.md", sha256=digest)


def write_canonical_lifecycle(output: Path, audit: Path) -> tuple[Path, Path]:
    write_state(output, audit, "in_progress", first=True)
    report = output / "reports" / "D-001-report.md"
    write_and_observe(
        audit, report, "reports/D-001-report.md", "# Discovery Packet D-001 Report\n\nPASS\n"
    )
    evidence = output / "evidence" / "D-001" / "result.txt"
    write_and_observe(audit, evidence, "evidence/D-001/result.txt", "observed signal\n")
    write_and_observe(
        audit,
        output / "evidence" / "D-001" / "path-containment-postwrite.md",
        "evidence/D-001/path-containment-postwrite.md",
        "post-write physical containment: PASS\n",
    )
    write_state(output, audit, "verified")
    return report, evidence


def sample_and_verify(
    audit: Path,
    control: Path,
    *,
    after_sample: Callable[[], None] | None = None,
) -> tuple[str, str]:
    first_tag = append_control(
        control,
        {"request_id": "sample-D-001", "action": "sample", "packet_id": "D-001"},
        1,
        None,
    )
    wait_for_event(audit, "runner_sample_completed", request_id="sample-D-001")
    if after_sample is not None:
        after_sample()
    second_tag = append_control(
        control,
        {
            "request_id": "verify-D-001", "action": "verify", "packet_id": "D-001",
            "sample_request_id": "sample-D-001",
        },
        2,
        first_tag,
    )
    wait_for_event(audit, "runner_verification_observed", request_id="verify-D-001")
    return first_tag, second_tag


def test_gate_roles_are_neutral() -> None:
    gate_types = (
        "preference", "product_decision", "authority", "uat", "security_legal",
        "external_evidence", "capability", "environment", "internal_recovery",
    )
    for index, gate_type in enumerate(gate_types, start=1):
        assert classify_file(f"gates/G-{index:03d}-{gate_type}.md") == "canonical_gate"


def test_invalid_root_relationships_are_rejected() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-roots-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output = repo / "eval" / "outputs"
        output.mkdir(parents=True)
        invalid_audits = [output / "audit", repo, repo / "eval", repo / "other" / "audit"]
        for index, audit in enumerate(invalid_audits):
            result = subprocess.run(
                [
                    sys.executable, str(OBSERVER), "--repo", str(repo), "--output-root", str(output),
                    "--audit-dir", str(audit), "--stop-file", str(audit / f"STOP-{index}"),
                ],
                cwd=repo, capture_output=True, text=True, encoding="utf-8", errors="replace",
                check=False, env=os.environ.copy(),
            )
            assert result.returncode != 0
            assert "physically disjoint siblings" in result.stderr


def test_snapshot_files_defers_a_path_deleted_during_hash() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-snapshot-race-") as raw:
        root = Path(raw).resolve()
        transient = root / "transient.txt"
        transient.write_text("ephemeral\n", encoding="utf-8")

        def delete_during_hash(path: Path) -> str:
            assert path == transient
            path.unlink()
            raise FileNotFoundError(path)

        with mock.patch.object(audit_module, "sha256", delete_during_hash):
            files, deferred = audit_module.snapshot_files(root)

        assert files == {}
        assert deferred == [{"path": "transient.txt", "reason": "path_disappeared"}]


def test_deferred_path_preserves_prior_stable_sample() -> None:
    prior = {
        "AGENT-STATE.md": {
            "absolute_path": "C:/fixture/AGENT-STATE.md",
            "size": 10,
            "mtime_ns": 1,
            "sha256": "a" * 64,
        }
    }
    merged = audit_module.preserve_deferred_previous_files(
        {}, prior, [{"path": "AGENT-STATE.md", "reason": "path_changed_during_sample"}]
    )
    assert merged == prior


def test_root_enumeration_defer_preserves_history_then_real_deletion_resets() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-root-enumeration-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output, audit_root = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
        output.mkdir(parents=True)
        audit_root.mkdir(parents=True)
        observer = audit_module.Audit(
            repo, output, audit_root, audit_root / "STOP",
            audit_root / "runner-control.jsonl", b"r" * 32, 30,
        )
        state = output / "AGENT-STATE.md"
        state.write_text(state_text("in_progress"), encoding="utf-8")
        observer.observe_files()
        prior_files = dict(observer.files)
        assert observer.packet_rows["D-001"]["status"] == "in_progress"

        with mock.patch.object(
            audit_module,
            "snapshot_files",
            return_value=({}, [{"path": ".", "reason": "root_enumeration_unavailable"}]),
        ):
            observer.observe_files()

        assert observer.files == prior_files
        assert observer.packet_rows["D-001"]["status"] == "in_progress"
        assert observer.state_epoch == 0
        events_after_defer = read_events(audit_root)
        assert not any(item["event_type"] == "output_file_deleted" for item in events_after_defer)
        assert not any(item["event_type"] == "runner_state_history_reset" for item in events_after_defer)

        state.unlink()
        observer.observe_files()
        assert observer.files == {}
        assert observer.packet_rows == {}
        assert observer.state_epoch == 1
        events_after_deletion = read_events(audit_root)
        assert any(item["event_type"] == "output_file_deleted" for item in events_after_deletion)
        assert any(item["event_type"] == "runner_state_history_reset" for item in events_after_deletion)


def test_canonical_state_secondary_read_race_retries_without_reset() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-state-read-race-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output, audit_root = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
        output.mkdir(parents=True)
        audit_root.mkdir(parents=True)
        observer = audit_module.Audit(
            repo, output, audit_root, audit_root / "STOP",
            audit_root / "runner-control.jsonl", b"r" * 32, 30,
        )
        state = output / "AGENT-STATE.md"
        state.write_text(state_text("in_progress"), encoding="utf-8")
        observer.observe_files()
        assert observer.packet_rows["D-001"]["status"] == "in_progress"

        state.write_text(state_text("verified"), encoding="utf-8")
        original_read_bytes = Path.read_bytes

        def fail_state_read(path: Path) -> bytes:
            if path == state:
                raise FileNotFoundError(path)
            return original_read_bytes(path)

        with mock.patch.object(Path, "read_bytes", fail_state_read):
            observer.observe_files()
        assert observer.packet_rows["D-001"]["status"] == "in_progress"
        assert observer.secondary_read_deferred == {
            "AGENT-STATE.md": "path_unreadable_after_snapshot"
        }

        observer.observe_files()
        assert observer.packet_rows["D-001"]["status"] == "verified"
        assert observer.secondary_read_deferred == {}
        event_types = [item["event_type"] for item in read_events(audit_root)]
        assert "output_secondary_read_deferred" in event_types
        assert "output_secondary_read_deferred_resolved" in event_types


def test_production_reference_hash_race_is_invalid_not_fatal() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-reference-race-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output, audit_root = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
        output.mkdir(parents=True)
        audit_root.mkdir(parents=True)
        observer = audit_module.Audit(
            repo, output, audit_root, audit_root / "STOP",
            audit_root / "runner-control.jsonl", b"r" * 32, 30,
        )
        reference = output / "reference.txt"
        reference.write_text("stable before race\n", encoding="utf-8")
        expected = hashlib.sha256(reference.read_bytes()).hexdigest()
        original_sha256 = audit_module.sha256

        def fail_reference_hash(path: Path) -> str:
            if path == reference:
                raise FileNotFoundError(path)
            return original_sha256(path)

        with mock.patch.object(audit_module, "sha256", fail_reference_hash):
            resolved, errors = observer.validate_production_references(
                [{"path": "reference.txt", "sha256": expected}]
            )
        assert resolved == []
        assert errors == ["reference_0_read_failed"]


def test_append_self_test_scratch_is_ephemeral_not_production() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-self-test-race-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output, audit = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
        process, stop, _control = start_observer(repo, output, audit, poll_ms=100)
        try:
            for _index in range(3):
                completed = subprocess.run(
                    [sys.executable, str(APPEND_HELPER), "--self-test", "--run-root", str(output)],
                    cwd=repo, capture_output=True, text=True, encoding="utf-8",
                    errors="replace", check=False,
                )
                assert completed.returncode == 0, completed.stderr
            initialized = subprocess.run(
                [
                    sys.executable, str(APPEND_HELPER), "--run-root", str(output),
                    "--stage", "DISCOVERY", "--event-type", "run_initialized",
                    "--evidence-summary", "canonical runner cross-check",
                ],
                cwd=repo, capture_output=True, text=True, encoding="utf-8",
                errors="replace", check=False,
            )
            assert initialized.returncode == 0, initialized.stderr
            wait_for_event(
                audit, "production_event_observed", path="EVENTS.jsonl", production_event_seq=1
            )
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_after_failure(process, audit, stop)

        assert not list(output.glob(".append-event-self-test-*"))
        assert set(summary["production_cross_checks"]["files"]) == {"EVENTS.jsonl"}
        assert summary["production_cross_checks"]["files"]["EVENTS.jsonl"]["valid"] is True
        assert summary["observation_integrity"]["complete_at_finalize"] is True
        event_types = [event["event_type"] for event in read_events(audit)]
        assert "runner_stop_requested" in event_types
        assert event_types[-1] == "runner_finalized"


def test_malformed_canonical_production_stream_remains_invalid() -> None:
    cases = (
        ("invalid-json", "{not-json}\n", "production_event_parse_error"),
        ("incomplete-tail", "{not-json", "production_stream_incomplete_record"),
    )
    for name, contents, expected_event in cases:
        with tempfile.TemporaryDirectory(
            prefix=f"discovery-audit-malformed-production-{name}-"
        ) as raw:
            repo = Path(raw).resolve()
            initialize_repo(repo)
            output, audit = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
            process, stop, _control = start_observer(repo, output, audit)
            try:
                (output / "EVENTS.jsonl").write_text(contents, encoding="utf-8")
                wait_for_event(audit, expected_event, path="EVENTS.jsonl")
                summary = finalize_observer(process, audit, stop)
            finally:
                stop_after_failure(process, audit, stop)

            stream = summary["production_cross_checks"]["files"]["EVENTS.jsonl"]
            assert stream["read_observation_complete"] is True
            assert stream["parse_valid"] is False
            assert stream["valid"] is False


def test_positive_strict_order_and_outside_reporting() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-positive-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output, audit = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
        process, stop, control = start_observer(repo, output, audit)
        try:
            report, _evidence = write_canonical_lifecycle(output, audit)
            update_state_outside_packet_row(output, audit, "write handoff")
            sample_and_verify(
                audit,
                control,
                after_sample=lambda: update_state_outside_packet_row(
                    output, audit, "finish handoff"
                ),
            )
            (repo / "executor-outside.txt").write_text("outside\n", encoding="utf-8")
            audit.mkdir(exist_ok=True)
            (audit / "executor-sneak.txt").write_text("not runner-owned\n", encoding="utf-8")
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_after_failure(process, audit, stop)
        lifecycle = summary["lifecycle"]["D-001"]
        assert summary["schema"] == "runner-audit-v2"
        assert lifecycle["strictly_ordered"] is True
        assert lifecycle["active_to_verified_transition_event_seq"] is not None
        assert lifecycle["containment_before_sampling"] is True
        assert summary["runner_control_integrity"]["authenticated_hmac_chain_valid"] is True
        outside = summary["new_nonignored_untracked_outside_output"]
        assert "executor-outside.txt" in outside
        assert "eval/runner-audit/executor-sneak.txt" in outside
        events = read_events(audit)
        sample = next(
            event for event in events
            if event.get("event_type") == "runner_artifact_sampled"
            and event.get("path") == "reports/D-001-report.md"
        )
        assert sample["sha256"] == hashlib.sha256(report.read_bytes()).hexdigest()


def test_first_seen_verified_and_empty_noncanonical_artifacts_reject() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-no-transition-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output, audit = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
        process, stop, control = start_observer(repo, output, audit)
        try:
            write_and_observe(audit, output / "reports" / "D-001-report.md", "reports/D-001-report.md", "")
            write_and_observe(
                audit, output / "evidence" / "D-001.txt", "evidence/D-001.txt", "noncanonical\n"
            )
            write_and_observe(
                audit,
                output / "evidence" / "D-001" / "path-containment-postwrite.md",
                "evidence/D-001/path-containment-postwrite.md",
                "",
            )
            write_state(output, audit, "verified", first=True)
            append_control(
                control,
                {"request_id": "sample-D-001", "action": "sample", "packet_id": "D-001"},
                1,
                None,
            )
            rejected = wait_for_event(audit, "runner_control_rejected", request_id="sample-D-001")
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_after_failure(process, audit, stop)
        errors = rejected["validation_errors"]
        assert any("canonical_artifact_empty:reports/D-001-report.md" == error for error in errors)
        assert any(
            "canonical_artifact_empty:evidence/D-001/path-containment-postwrite.md" == error
            for error in errors
        )
        assert "canonical_worker_evidence_missing" in errors
        assert "active_to_verified_state_transition_not_observed" in errors
        assert summary["lifecycle"]["D-001"]["strictly_ordered"] is False


def test_verified_packet_row_change_rejects() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-row-change-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output, audit = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
        process, stop, control = start_observer(repo, output, audit)
        try:
            write_canonical_lifecycle(output, audit)
            state = output / "AGENT-STATE.md"
            state.write_text(state_text("verified").replace("| none | 0 |", "| changed | 0 |"), encoding="utf-8")
            wait_for_event(audit, "runner_packet_state_row_updated", packet_id="D-001")
            state.write_text(state_text("verified"), encoding="utf-8")
            wait_for(
                lambda: sum(
                    event.get("event_type") == "runner_packet_state_row_updated"
                    and event.get("packet_id") == "D-001"
                    for event in read_events(audit)
                )
                >= 2,
                "verified packet row mutation and restoration",
            )
            append_control(
                control,
                {"request_id": "sample-D-001", "action": "sample", "packet_id": "D-001"},
                1,
                None,
            )
            rejected = wait_for_event(audit, "runner_control_rejected", request_id="sample-D-001")
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_after_failure(process, audit, stop)
        assert (
            "verified_transition_invalidated_by_later_packet_row_event"
            in rejected["validation_errors"]
        )
        assert summary["lifecycle"]["D-001"]["strictly_ordered"] is False


def test_verified_state_before_artifacts_in_same_poll_rejects() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-same-poll-order-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output, audit = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
        process, stop, control = start_observer(repo, output, audit, poll_ms=500)
        try:
            write_state(output, audit, "in_progress", first=True)
            (output / "AGENT-STATE.md").write_text(state_text("verified"), encoding="utf-8")
            time.sleep(0.05)
            report = output / "reports" / "D-001-report.md"
            report.parent.mkdir(parents=True)
            report.write_text("# Discovery Packet D-001 Report\n\nPASS\n", encoding="utf-8")
            evidence = output / "evidence" / "D-001" / "result.txt"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("observed signal\n", encoding="utf-8")
            (evidence.parent / "path-containment-postwrite.md").write_text(
                "post-write physical containment: PASS\n", encoding="utf-8"
            )
            wait_for_event(
                audit,
                "runner_packet_state_transition_observed",
                packet_id="D-001",
                to_status="verified",
            )
            append_control(
                control,
                {"request_id": "sample-D-001", "action": "sample", "packet_id": "D-001"},
                1,
                None,
            )
            rejected = wait_for_event(audit, "runner_control_rejected", request_id="sample-D-001")
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_after_failure(process, audit, stop)
        assert "canonical_artifacts_not_observed_before_state_transition" in rejected[
            "validation_errors"
        ]
        assert summary["lifecycle"]["D-001"]["strictly_ordered"] is False


def test_forged_and_replayed_controls_reject() -> None:
    for mode in ("forged", "replayed"):
        with tempfile.TemporaryDirectory(prefix=f"discovery-audit-{mode}-") as raw:
            repo = Path(raw).resolve()
            initialize_repo(repo)
            output, audit = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
            process, stop, control = start_observer(repo, output, audit)
            try:
                write_canonical_lifecycle(output, audit)
                tag = append_control(
                    control,
                    {"request_id": "sample-D-001", "action": "sample", "packet_id": "D-001"},
                    1,
                    None,
                    forge=mode == "forged",
                )
                terminal = "runner_control_rejected" if mode == "forged" else "runner_sample_completed"
                wait_for_event(audit, terminal, request_id="sample-D-001")
                if mode == "replayed":
                    append_control(
                        control,
                        {"request_id": "sample-D-001", "action": "sample", "packet_id": "D-001"},
                        1,
                        None,
                    )
                    wait_for_event(audit, "runner_control_rejected", request_id="sample-D-001")
                summary = finalize_observer(process, audit, stop)
            finally:
                stop_after_failure(process, audit, stop)
            assert summary["runner_control_integrity"]["authenticated_hmac_chain_valid"] is False
            assert summary["lifecycle"]["D-001"]["strictly_ordered"] is False
            assert tag != os.environ[SECRET_ENV]


def test_rewritten_and_truncated_controls_invalidate() -> None:
    for mutation in ("rewritten", "truncated"):
        with tempfile.TemporaryDirectory(prefix=f"discovery-audit-control-{mutation}-") as raw:
            repo = Path(raw).resolve()
            initialize_repo(repo)
            output, audit = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
            process, stop, control = start_observer(repo, output, audit)
            try:
                write_canonical_lifecycle(output, audit)
                append_control(
                    control,
                    {"request_id": "sample-D-001", "action": "sample", "packet_id": "D-001"},
                    1,
                    None,
                )
                wait_for_event(audit, "runner_sample_completed", request_id="sample-D-001")
                original = control.read_text(encoding="utf-8")
                if mutation == "rewritten":
                    control.write_text(original.replace("sample-D-001", "tamper-D-001"), encoding="utf-8")
                else:
                    control.write_text("", encoding="utf-8")
                wait_for_event(
                    audit, "runner_control_stream_mutation_observed", mutation=mutation
                )
                summary = finalize_observer(process, audit, stop)
            finally:
                stop_after_failure(process, audit, stop)
            assert summary["runner_control_integrity"]["append_only_valid"] is False
            assert summary["lifecycle"]["D-001"]["strictly_ordered"] is False


def test_production_claims_rewrite_and_reference_escape_remain_cross_checks() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-production-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output, audit = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
        process, stop, _control = start_observer(repo, output, audit)
        try:
            report, _evidence = write_canonical_lifecycle(output, audit)
            outside = repo / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            production = output / "EVENTS.jsonl"
            append_jsonl(
                production,
                {
                    "event_seq": 1, "timestamp": "2026-01-01T00:00:00Z",
                    "event_type": "artifact_sampled", "packet_id": "D-001",
                    "references": [
                        {"path": "../../outside.txt", "sha256": hashlib.sha256(outside.read_bytes()).hexdigest()},
                        {"path": "reports/D-001-report.md", "sha256": "0" * 64},
                    ],
                },
            )
            wait_for_event(audit, "production_event_observed", production_event_seq=1)
            original = production.read_text(encoding="utf-8")
            production.write_text(original.replace('"event_seq": 1', '"event_seq": 2'), encoding="utf-8")
            wait_for_event(audit, "production_stream_mutation_observed", mutation="rewritten")
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_after_failure(process, audit, stop)
        stream = summary["production_cross_checks"]["files"]["EVENTS.jsonl"]
        assert stream["append_only_valid"] is False
        assert stream["references_valid"] is False
        errors = "\n".join(stream["errors"])
        assert "path_outside_or_not_file" in errors
        assert "sha256_mismatch" in errors
        lifecycle = summary["lifecycle"]["D-001"]
        assert lifecycle["sampling_event_seq"] is None
        assert lifecycle["verified_event_seq"] is None
        assert lifecycle["strictly_ordered"] is False
        assert report.is_file()


def test_valid_production_only_claims_cannot_pass() -> None:
    with tempfile.TemporaryDirectory(prefix="discovery-audit-valid-production-") as raw:
        repo = Path(raw).resolve()
        initialize_repo(repo)
        output, audit = repo / "eval" / "outputs", repo / "eval" / "runner-audit"
        process, stop, _control = start_observer(repo, output, audit)
        try:
            report, evidence = write_canonical_lifecycle(output, audit)
            production = output / "EVENTS.jsonl"
            append_jsonl(
                production,
                {
                    "event_seq": 1, "timestamp": "2026-01-01T00:00:00Z",
                    "event_type": "artifact_sampled", "packet_id": "D-001",
                    "references": [{
                        "path": "reports/D-001-report.md",
                        "sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
                    }],
                },
            )
            append_jsonl(
                production,
                {
                    "event_seq": 2, "timestamp": "2026-01-01T00:00:01Z",
                    "event_type": "packet_verified", "packet_id": "D-001",
                    "references": [{
                        "path": "evidence/D-001/result.txt",
                        "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
                    }],
                },
            )
            wait_for_event(audit, "production_event_observed", production_event_seq=2)
            summary = finalize_observer(process, audit, stop)
        finally:
            stop_after_failure(process, audit, stop)
        assert summary["production_cross_checks"]["files"]["EVENTS.jsonl"]["valid"] is True
        lifecycle = summary["lifecycle"]["D-001"]
        assert lifecycle["sampling_event_seq"] is None
        assert lifecycle["verified_event_seq"] is None
        assert lifecycle["strictly_ordered"] is False


def main() -> None:
    assert OBSERVER.is_file(), f"observer missing: {OBSERVER}"
    os.environ[SECRET_ENV] = secrets.token_hex(32)
    try:
        test_gate_roles_are_neutral()
        test_invalid_root_relationships_are_rejected()
        test_snapshot_files_defers_a_path_deleted_during_hash()
        test_deferred_path_preserves_prior_stable_sample()
        test_root_enumeration_defer_preserves_history_then_real_deletion_resets()
        test_canonical_state_secondary_read_race_retries_without_reset()
        test_production_reference_hash_race_is_invalid_not_fatal()
        test_append_self_test_scratch_is_ephemeral_not_production()
        test_malformed_canonical_production_stream_remains_invalid()
        test_positive_strict_order_and_outside_reporting()
        test_first_seen_verified_and_empty_noncanonical_artifacts_reject()
        test_verified_packet_row_change_rejects()
        test_verified_state_before_artifacts_in_same_poll_rejects()
        test_forged_and_replayed_controls_reject()
        test_rewritten_and_truncated_controls_invalidate()
        test_production_claims_rewrite_and_reference_escape_remain_cross_checks()
        test_valid_production_only_claims_cannot_pass()
    finally:
        os.environ.pop(SECRET_ENV, None)
    print("runner audit smoke test: PASS")


if __name__ == "__main__":
    main()
