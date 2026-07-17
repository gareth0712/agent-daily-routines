#!/usr/bin/env python3
"""Behavioral and adversarial tests for the byte-safe event append helper."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest import mock


HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
SCRIPT = SKILL_ROOT / "scripts" / "append_event.py"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPT.parent))

import append_event as append_module  # noqa: E402


PLATFORM_NOTES: list[str] = []
GENESIS_EVENT_SHA256 = "0" * 64
EMPTY_EVENTS_SHA256 = hashlib.sha256(b"").hexdigest()


def run_cli(run_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--run-root", str(run_root), *args],
        cwd=SKILL_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env=env,
    )


def append_args(
    *,
    stage: str = "DISCOVERY",
    event_type: str = "run_initialized",
    packet_id: str | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    references: tuple[str, ...] = (),
    evidence_summary: str = "bounded test evidence",
    expected_event_count: int = 0,
    expected_event_tip: str = GENESIS_EVENT_SHA256,
    expected_events_sha256: str = EMPTY_EVENTS_SHA256,
) -> list[str]:
    result = [
        "--stage",
        stage,
        "--event-type",
        event_type,
        "--evidence-summary",
        evidence_summary,
        "--expected-event-count",
        str(expected_event_count),
        "--expected-event-tip",
        expected_event_tip,
        "--expected-events-sha256",
        expected_events_sha256,
    ]
    if packet_id is not None:
        result.extend(["--packet-id", packet_id])
    if from_status is not None:
        result.extend(["--from-status", from_status])
    if to_status is not None:
        result.extend(["--to-status", to_status])
    for reference in references:
        result.extend(["--reference", reference])
    return result


def accepted_anchor(metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "expected_event_count": metadata["accepted_event_count"],
        "expected_event_tip": metadata["accepted_event_tip"],
        "expected_events_sha256": metadata["accepted_events_sha256"],
    }


def read_objects(path: Path) -> tuple[bytes, list[dict[str, Any]]]:
    raw = path.read_bytes()
    objects = [json.loads(line) for line in raw.splitlines()]
    assert all(isinstance(item, dict) for item in objects)
    return raw, objects


def parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() is not None
    return parsed


def assert_rejected_without_mutation(
    run_root: Path,
    args: list[str],
    *,
    expect_frozen: bool = False,
) -> None:
    events = run_root / "EVENTS.jsonl"
    existed = events.exists()
    before = events.read_bytes() if existed else None
    result = run_cli(run_root, *args)
    assert result.returncode != 0, result.stdout
    assert result.stdout == ""
    assert result.stderr.startswith("error: ")
    assert len(result.stderr) <= 160
    assert events.exists() is existed
    if existed:
        assert events.read_bytes() == before
    marker = run_root / "EVENTS.FROZEN"
    if expect_frozen:
        assert marker.read_bytes() == append_module.FREEZE_BYTES
        frozen_bytes = marker.read_bytes()
        refused_append = run_cli(run_root, *append_args())
        refused_self_test = run_cli(run_root, "--self-test")
        assert refused_append.returncode != 0
        assert refused_self_test.returncode != 0
        assert "frozen" in refused_append.stderr
        assert "frozen" in refused_self_test.stderr
        assert marker.read_bytes() == frozen_bytes
    else:
        assert not marker.exists()


def test_new_and_empty_streams_append_exact_records() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-new-") as raw:
        run_root = Path(raw).resolve()
        report = run_root / "reports" / "D-001-report.md"
        report.parent.mkdir()
        report.write_bytes("evidence: 已驗證\n".encode("utf-8"))
        secret_summary = "bounded-summary-must-not-be-echoed"

        first = run_cli(
            run_root,
            *append_args(
                event_type="packet_status_transition",
                packet_id="D-001",
                from_status="pending",
                to_status="in_progress",
                references=("reports/D-001-report.md",),
                evidence_summary=secret_summary,
            ),
        )
        assert first.returncode == 0, first.stderr
        assert first.stderr == ""
        first_metadata = json.loads(first.stdout)
        assert first_metadata["ok"] is True
        assert first_metadata["event_seq"] == 1
        assert first_metadata["accepted_event_count"] == 1
        assert len(first_metadata["accepted_event_tip"]) == 64
        assert len(first_metadata["accepted_events_sha256"]) == 64
        assert secret_summary not in first.stdout
        assert not (run_root / "EVENTS.FROZEN").exists()

        second = run_cli(
            run_root,
            *append_args(
                stage="PLANNING",
                event_type="stage_routed",
                evidence_summary="routed to planning",
                **accepted_anchor(first_metadata),
            ),
        )
        assert second.returncode == 0, second.stderr
        assert json.loads(second.stdout)["event_seq"] == 2
        assert not (run_root / "EVENTS.FROZEN").exists()

        events = run_root / "EVENTS.jsonl"
        appended, objects = read_objects(events)
        assert appended.endswith(b"\n")
        assert appended.count(b"\n") == 2
        assert b"\r" not in appended
        expected_bytes = b"".join(
            json.dumps(item, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            + b"\n"
            for item in objects
        )
        assert appended == expected_bytes
        assert [item["event_seq"] for item in objects] == [1, 2]
        assert parse_timestamp(objects[0]["timestamp"]) < parse_timestamp(
            objects[1]["timestamp"]
        )
        assert objects[0]["actor"] == "top_level_orchestrator"
        assert objects[0]["previous_event_sha256"] == GENESIS_EVENT_SHA256
        assert objects[0]["event_sha256"] == first_metadata["accepted_event_tip"]
        assert objects[1]["previous_event_sha256"] == objects[0]["event_sha256"]
        assert objects[1]["event_sha256"] == json.loads(second.stdout)[
            "accepted_event_tip"
        ]
        assert objects[0]["references"] == [
            {
                "path": "reports/D-001-report.md",
                "sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            }
        ]
        assert "revision" not in objects[0]["references"][0]
        assert "packet_id" not in objects[1]
        assert "from_status" not in objects[1]
        assert "to_status" not in objects[1]

    with tempfile.TemporaryDirectory(prefix="append-event-empty-") as raw:
        run_root = Path(raw).resolve()
        events = run_root / "EVENTS.jsonl"
        events.write_bytes(b"")
        result = run_cli(run_root, *append_args())
        assert result.returncode == 0, result.stderr
        appended, objects = read_objects(events)
        assert appended.endswith(b"\n")
        assert [item["event_seq"] for item in objects] == [1]
        assert not (run_root / "EVENTS.FROZEN").exists()


def test_invalid_prefixes_never_mutate() -> None:
    invalid_prefixes = (
        b'{"event_seq":1,"timestamp":"2026-01-01T00:00:00Z"',
        b"not-json\n",
        b'{"event_seq":1,"timestamp":"2026-01-01T00:00:00Z"}\n\n',
        b'{"event_seq":2,"timestamp":"2026-01-01T00:00:00Z"}\n',
        (
            b'{"event_seq":1,"timestamp":"2026-01-01T00:00:00Z"}\n'
            b'{"event_seq":3,"timestamp":"2026-01-01T00:00:01Z"}\n'
        ),
        b'{"event_seq":1,"timestamp":"2026-01-01T00:00:00"}\n',
        (
            b'{"event_seq":1,"timestamp":"2026-01-01T00:00:00Z"}\n'
            b'{"event_seq":2,"timestamp":"2026-01-01T00:00:00Z"}\n'
        ),
        b'{"event_seq":1,"timestamp":"2026-01-01T00:00:00Z","value":NaN}\n',
        b'{"event_seq":1,"timestamp":"2026-01-01T00:00:00Z","value":Infinity}\n',
        b'{"event_seq":1,"timestamp":"2026-01-01T00:00:00Z","value":-Infinity}\n',
    )
    for index, prefix in enumerate(invalid_prefixes):
        with tempfile.TemporaryDirectory(prefix=f"append-event-prefix-{index}-") as raw:
            run_root = Path(raw).resolve()
            events = run_root / "EVENTS.jsonl"
            events.write_bytes(prefix)
            assert_rejected_without_mutation(
                run_root,
                append_args(),
                expect_frozen=True,
            )


def test_hard_linked_event_stream_rejects_without_alias_mutation() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-hard-link-") as raw:
        parent = Path(raw).resolve()
        run_root = parent / "run"
        run_root.mkdir()
        outside = parent / "outside.jsonl"
        original = b'{"event_seq":1,"timestamp":"2026-01-01T00:00:00Z"}\n'
        outside.write_bytes(original)
        events = run_root / "EVENTS.jsonl"
        try:
            os.link(outside, events)
        except OSError as error:
            PLATFORM_NOTES.append(
                "hard-link test skipped: "
                f"errno={error.errno} winerror={getattr(error, 'winerror', None)}"
            )
            return
        assert events.samefile(outside)
        assert events.stat().st_nlink > 1
        assert_rejected_without_mutation(
            run_root,
            append_args(),
            expect_frozen=True,
        )
        assert outside.read_bytes() == original
        assert events.read_bytes() == original


def test_reference_escapes_and_non_regular_files_reject() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-reference-") as raw:
        parent = Path(raw).resolve()
        run_root = parent / "run"
        run_root.mkdir()
        outside = parent / "outside.txt"
        outside.write_text("outside\n", encoding="utf-8")
        target = run_root / "target.txt"
        target.write_text("inside\n", encoding="utf-8")
        linked = run_root / "linked.txt"
        linked_reference = "linked.txt"
        try:
            os.symlink(target, linked)
        except OSError as error:
            if getattr(error, "winerror", None) != 1314:
                raise
            junction_target = run_root / "junction-target"
            junction_target.mkdir()
            (junction_target / "payload.txt").write_text("linked\n", encoding="utf-8")
            junction = run_root / "linked-dir"
            created = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(junction), str(junction_target)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            assert created.returncode == 0, created.stderr
            linked_reference = "linked-dir/payload.txt"

        rejected = (
            "../outside.txt",
            str(outside),
            "missing.txt",
            linked_reference,
            "target\\.txt",
            "target.txt/../target.txt",
        )
        for reference in rejected:
            assert_rejected_without_mutation(
                run_root,
                append_args(references=(reference,)),
            )


def test_invalid_and_bounded_inputs_reject_before_stream_creation() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-input-") as raw:
        run_root = Path(raw).resolve()
        reference = run_root / "reference.txt"
        reference.write_text("reference\n", encoding="utf-8")
        invalid_args = (
            append_args(stage="UNKNOWN"),
            append_args(from_status="complete"),
            append_args(to_status="complete"),
            append_args(packet_id="D-01"),
            append_args(stage="PLANNING", packet_id="D-001"),
            append_args(evidence_summary="x" * 10_000),
            append_args(references=("reference.txt",) * 100),
        )
        for args in invalid_args:
            assert_rejected_without_mutation(run_root, args)

        secret = "secret-must-not-appear"
        rejected = run_cli(
            run_root,
            "--stage",
            secret,
            "--event-type",
            "run_initialized",
            "--evidence-summary",
            "bounded",
        )
        assert rejected.returncode != 0
        assert secret not in rejected.stderr

        partial_anchor = run_cli(
            run_root,
            "--stage",
            "DISCOVERY",
            "--event-type",
            "run_initialized",
            "--evidence-summary",
            "bounded",
            "--expected-event-count",
            "0",
        )
        assert partial_anchor.returncode != 0
        assert not (run_root / "EVENTS.FROZEN").exists()


def rewrite_as_valid_chain(objects: list[dict[str, Any]]) -> bytes:
    previous = GENESIS_EVENT_SHA256
    records: list[bytes] = []
    for event in objects:
        event.pop("event_sha256", None)
        event["previous_event_sha256"] = previous
        event["event_sha256"] = append_module.canonical_event_sha256(event)
        previous = event["event_sha256"]
        records.append(
            json.dumps(event, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            + b"\n"
        )
    return b"".join(records)


def append_two_events(run_root: Path) -> dict[str, Any]:
    first = run_cli(run_root, *append_args())
    assert first.returncode == 0, first.stderr
    first_metadata = json.loads(first.stdout)
    second = run_cli(
        run_root,
        *append_args(
            stage="PLANNING",
            event_type="stage_routed",
            evidence_summary="second accepted event",
            **accepted_anchor(first_metadata),
        ),
    )
    assert second.returncode == 0, second.stderr
    return json.loads(second.stdout)


def test_valid_json_history_rewrite_rejected_by_durable_anchor() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-history-rewrite-") as raw:
        run_root = Path(raw).resolve()
        accepted = append_two_events(run_root)
        events = run_root / "EVENTS.jsonl"
        _, objects = read_objects(events)
        objects[0]["evidence_summary"] = "tampered but rechained history"
        rewritten = rewrite_as_valid_chain(objects)
        events.write_bytes(rewritten)
        append_module._validate_prefix(rewritten, None)
        assert_rejected_without_mutation(
            run_root,
            append_args(**accepted_anchor(accepted)),
            expect_frozen=True,
        )


def test_tail_truncation_and_stream_deletion_rejected_by_durable_anchor() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-tail-truncate-") as raw:
        run_root = Path(raw).resolve()
        accepted = append_two_events(run_root)
        events = run_root / "EVENTS.jsonl"
        first_line = events.read_bytes().splitlines(keepends=True)[0]
        events.write_bytes(first_line)
        assert_rejected_without_mutation(
            run_root,
            append_args(**accepted_anchor(accepted)),
            expect_frozen=True,
        )

    with tempfile.TemporaryDirectory(prefix="append-event-stream-delete-") as raw:
        run_root = Path(raw).resolve()
        first = run_cli(run_root, *append_args())
        assert first.returncode == 0, first.stderr
        accepted = json.loads(first.stdout)
        (run_root / "EVENTS.jsonl").unlink()
        assert_rejected_without_mutation(
            run_root,
            append_args(**accepted_anchor(accepted)),
            expect_frozen=True,
        )


def test_missing_and_forged_chain_fields_freeze() -> None:
    base: dict[str, Any] = {
        "event_seq": 1,
        "timestamp": "2026-01-01T00:00:00Z",
        "event_type": "run_initialized",
        "stage": "DISCOVERY",
        "actor": "top_level_orchestrator",
        "references": [],
        "evidence_summary": "bounded",
    }
    missing = dict(base)
    forged_previous = dict(base)
    forged_previous["previous_event_sha256"] = "f" * 64
    forged_previous["event_sha256"] = append_module.canonical_event_sha256(
        forged_previous
    )
    forged_event = dict(base)
    forged_event["previous_event_sha256"] = GENESIS_EVENT_SHA256
    forged_event["event_sha256"] = "f" * 64

    for index, event in enumerate((missing, forged_previous, forged_event)):
        with tempfile.TemporaryDirectory(
            prefix=f"append-event-forged-chain-{index}-"
        ) as raw:
            run_root = Path(raw).resolve()
            serialized = (
                json.dumps(event, ensure_ascii=False, separators=(",", ":")).encode(
                    "utf-8"
                )
                + b"\n"
            )
            (run_root / "EVENTS.jsonl").write_bytes(serialized)
            assert_rejected_without_mutation(
                run_root,
                append_args(
                    expected_event_count=1,
                    expected_event_tip=event.get(
                        "event_sha256", GENESIS_EVENT_SHA256
                    ),
                    expected_events_sha256=hashlib.sha256(serialized).hexdigest(),
                ),
                expect_frozen=True,
            )


def test_expected_count_tip_and_file_digest_mismatches_freeze() -> None:
    mutations = (
        {"expected_event_count": 0},
        {"expected_event_tip": "f" * 64},
        {"expected_events_sha256": "f" * 64},
    )
    for index, mutation in enumerate(mutations):
        with tempfile.TemporaryDirectory(
            prefix=f"append-event-anchor-mismatch-{index}-"
        ) as raw:
            run_root = Path(raw).resolve()
            first = run_cli(run_root, *append_args())
            assert first.returncode == 0, first.stderr
            anchor = accepted_anchor(json.loads(first.stdout))
            anchor.update(mutation)
            assert_rejected_without_mutation(
                run_root,
                append_args(**anchor),
                expect_frozen=True,
            )

    with tempfile.TemporaryDirectory(prefix="append-event-anchor-missing-") as raw:
        run_root = Path(raw).resolve()
        first = run_cli(run_root, *append_args())
        assert first.returncode == 0, first.stderr
        assert_rejected_without_mutation(
            run_root,
            [
                "--stage",
                "DISCOVERY",
                "--event-type",
                "stage_routed",
                "--evidence-summary",
                "missing durable anchor",
            ],
            expect_frozen=True,
        )


def test_run_root_symlink_rejects_without_target_mutation() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-root-link-") as raw:
        parent = Path(raw).resolve()
        physical_root = parent / "physical"
        physical_root.mkdir()
        linked_root = parent / "linked"
        try:
            os.symlink(physical_root, linked_root, target_is_directory=True)
        except OSError as error:
            if getattr(error, "winerror", None) != 1314:
                raise
            created = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(linked_root), str(physical_root)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            assert created.returncode == 0, created.stderr
        result = run_cli(linked_root, *append_args())
        assert result.returncode != 0
        assert result.stdout == ""
        assert not (physical_root / "EVENTS.jsonl").exists()


def append_in_process(run_root: Path, *, stage: str = "DISCOVERY") -> None:
    append_module.append_event(
        run_root,
        stage=stage,
        event_type="run_initialized" if stage == "DISCOVERY" else "stage_routed",
        evidence_summary="failure injection",
    )


def assert_frozen_failure(run_root: Path, call_count: int) -> None:
    marker = run_root / "EVENTS.FROZEN"
    events = run_root / "EVENTS.jsonl"
    assert call_count >= 2
    assert marker.is_file()
    marker_stat = marker.lstat()
    marker_bytes = marker.read_bytes()
    assert marker_stat.st_nlink == 1
    assert 0 < len(marker_bytes) <= 256
    assert marker_bytes.endswith(b"\n")
    failed_bytes = events.read_bytes()
    try:
        append_in_process(run_root, stage="PLANNING")
    except append_module.AppendEventError as error:
        assert "frozen" in str(error)
    else:
        raise AssertionError("frozen stream accepted a later-stage append")
    assert events.read_bytes() == failed_bytes
    assert marker.read_bytes() == marker_bytes


def test_short_stream_write_freezes_later_appends() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-short-write-") as raw:
        run_root = Path(raw).resolve()
        original_write = os.write
        calls = 0

        def short_second_write(descriptor: int, data: bytes) -> int:
            nonlocal calls
            calls += 1
            if calls == 2:
                return original_write(descriptor, data[:-1])
            return original_write(descriptor, data)

        with mock.patch.object(append_module.os, "write", short_second_write):
            try:
                append_in_process(run_root)
            except append_module.AppendEventError:
                pass
            else:
                raise AssertionError("short stream write was accepted")
        assert_frozen_failure(run_root, calls)


def test_stream_fsync_failure_freezes_later_appends() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-fsync-") as raw:
        run_root = Path(raw).resolve()
        original_fsync = os.fsync
        calls = 0

        def fail_second_fsync(descriptor: int) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected stream fsync failure")
            original_fsync(descriptor)

        with mock.patch.object(append_module.os, "fsync", fail_second_fsync):
            try:
                append_in_process(run_root)
            except append_module.AppendEventError:
                pass
            else:
                raise AssertionError("stream fsync failure was accepted")
        assert_frozen_failure(run_root, calls)


def test_stream_close_failure_freezes_later_appends() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-close-") as raw:
        run_root = Path(raw).resolve()
        original_close = os.close
        calls = 0

        def fail_second_close(descriptor: int) -> None:
            nonlocal calls
            calls += 1
            original_close(descriptor)
            if calls == 2:
                raise OSError("injected stream close failure")

        with mock.patch.object(append_module.os, "close", fail_second_close):
            try:
                append_in_process(run_root)
            except append_module.AppendEventError:
                pass
            else:
                raise AssertionError("stream close failure was accepted")
        assert_frozen_failure(run_root, calls)


def test_freeze_cleanup_failure_remains_frozen() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-freeze-cleanup-") as raw:
        run_root = Path(raw).resolve()
        original_unlink = os.unlink
        calls = 0

        def fail_marker_unlink(path: str | bytes | os.PathLike[str]) -> None:
            nonlocal calls
            calls += 1
            if Path(path).name == "EVENTS.FROZEN":
                raise OSError("injected marker cleanup failure")
            original_unlink(path)

        with mock.patch.object(append_module.os, "unlink", fail_marker_unlink):
            try:
                append_in_process(run_root)
            except append_module.AppendEventError:
                pass
            else:
                raise AssertionError("marker cleanup failure was accepted")
        assert calls == 1
        assert_frozen_failure(run_root, 2)


def injected_windows_error(winerror: int) -> PermissionError:
    error = PermissionError(13, "injected Windows marker cleanup failure")
    error.winerror = winerror
    return error


def test_transient_windows_freeze_cleanup_retries_without_reappending() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-freeze-transient-") as raw:
        run_root = Path(raw).resolve()
        original_unlink = os.unlink
        original_write = os.write
        unlink_calls = 0
        write_calls = 0

        def transient_then_unlink(path: str | bytes | os.PathLike[str]) -> None:
            nonlocal unlink_calls
            unlink_calls += 1
            if unlink_calls == 1:
                raise injected_windows_error(32)
            if unlink_calls == 2:
                raise injected_windows_error(33)
            original_unlink(path)

        def count_writes(descriptor: int, data: bytes) -> int:
            nonlocal write_calls
            write_calls += 1
            return original_write(descriptor, data)

        with (
            mock.patch.object(append_module.os, "unlink", transient_then_unlink),
            mock.patch.object(append_module.os, "write", count_writes),
        ):
            try:
                append_in_process(run_root)
            except append_module.AppendEventError as error:
                raise AssertionError(
                    "transient Windows marker cleanup was not tolerated"
                ) from error

        _, records = read_objects(run_root / "EVENTS.jsonl")
        assert unlink_calls == 3
        assert write_calls == 2
        assert [record["event_seq"] for record in records] == [1]
        assert not (run_root / "EVENTS.FROZEN").exists()


def test_transient_windows_freeze_cleanup_exhaustion_remains_frozen() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-freeze-exhaustion-") as raw:
        run_root = Path(raw).resolve()
        unlink_calls = 0

        def always_locked(path: str | bytes | os.PathLike[str]) -> None:
            nonlocal unlink_calls
            unlink_calls += 1
            raise injected_windows_error(32)

        with mock.patch.object(append_module.os, "unlink", always_locked):
            try:
                append_in_process(run_root)
            except append_module.AppendEventError:
                pass
            else:
                raise AssertionError("transient Windows cleanup exhaustion was accepted")

        assert unlink_calls == 4
        _, records = read_objects(run_root / "EVENTS.jsonl")
        assert [record["event_seq"] for record in records] == [1]
        assert (run_root / "EVENTS.FROZEN").read_bytes() == append_module.FREEZE_BYTES
        assert_frozen_failure(run_root, 2)


def test_nontransient_windows_freeze_cleanup_does_not_retry() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-freeze-nontransient-") as raw:
        run_root = Path(raw).resolve()
        unlink_calls = 0

        def access_denied(path: str | bytes | os.PathLike[str]) -> None:
            nonlocal unlink_calls
            unlink_calls += 1
            raise injected_windows_error(5)

        with mock.patch.object(append_module.os, "unlink", access_denied):
            try:
                append_in_process(run_root)
            except append_module.AppendEventError:
                pass
            else:
                raise AssertionError("nontransient Windows cleanup failure was accepted")

        assert unlink_calls == 1
        assert (run_root / "EVENTS.FROZEN").read_bytes() == append_module.FREEZE_BYTES
        _, records = read_objects(run_root / "EVENTS.jsonl")
        assert [record["event_seq"] for record in records] == [1]


def test_freeze_cleanup_retry_rejects_marker_identity_change() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-freeze-identity-") as raw:
        run_root = Path(raw).resolve()
        marker = run_root / "EVENTS.FROZEN"
        displaced = run_root / "EVENTS.FROZEN.displaced"
        unlink_calls = 0

        def replace_marker_then_lock(path: str | bytes | os.PathLike[str]) -> None:
            nonlocal unlink_calls
            unlink_calls += 1
            os.replace(path, displaced)
            marker.write_bytes(append_module.FREEZE_BYTES)
            raise injected_windows_error(32)

        with mock.patch.object(append_module.os, "unlink", replace_marker_then_lock):
            try:
                append_in_process(run_root)
            except append_module.AppendEventError:
                pass
            else:
                raise AssertionError("changed marker identity was deleted")

        assert unlink_calls == 1
        assert marker.read_bytes() == append_module.FREEZE_BYTES
        assert displaced.read_bytes() == append_module.FREEZE_BYTES
        _, records = read_objects(run_root / "EVENTS.jsonl")
        assert [record["event_seq"] for record in records] == [1]


def test_freeze_cleanup_retry_restores_disappeared_marker() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-freeze-disappeared-") as raw:
        run_root = Path(raw).resolve()
        original_unlink = os.unlink
        unlink_calls = 0

        def remove_marker_then_lock(path: str | bytes | os.PathLike[str]) -> None:
            nonlocal unlink_calls
            unlink_calls += 1
            original_unlink(path)
            raise injected_windows_error(33)

        with mock.patch.object(append_module.os, "unlink", remove_marker_then_lock):
            try:
                append_in_process(run_root)
            except append_module.AppendEventError:
                pass
            else:
                raise AssertionError("disappeared marker was treated as clean success")

        assert unlink_calls == 1
        assert (run_root / "EVENTS.FROZEN").read_bytes() == append_module.FREEZE_BYTES
        _, records = read_objects(run_root / "EVENTS.jsonl")
        assert [record["event_seq"] for record in records] == [1]


def test_existing_freeze_blocks_append_and_self_test_first() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-pre-frozen-") as raw:
        run_root = Path(raw).resolve()
        marker = run_root / "EVENTS.FROZEN"
        frozen_bytes = b"pre-existing freeze evidence\n"
        marker.write_bytes(frozen_bytes)
        append_result = run_cli(run_root, *append_args(stage="UNKNOWN"))
        self_test_result = run_cli(run_root, "--self-test")
        assert append_result.returncode != 0
        assert self_test_result.returncode != 0
        assert "frozen" in append_result.stderr
        assert "frozen" in self_test_result.stderr
        assert marker.read_bytes() == frozen_bytes
        assert not (run_root / "EVENTS.jsonl").exists()
        assert not list(run_root.glob(".append-event-self-test-*"))


def test_self_test_is_isolated_and_removes_scratch() -> None:
    with tempfile.TemporaryDirectory(prefix="append-event-self-test-") as raw:
        run_root = Path(raw).resolve()
        real_events = run_root / "EVENTS.jsonl"
        sentinel = b"REAL-EVENT-STREAM-MUST-NOT-BE-TOUCHED"
        real_events.write_bytes(sentinel)
        before_entries = {path.name for path in run_root.iterdir()}
        result = run_cli(run_root, "--self-test")
        assert result.returncode == 0, result.stderr
        assert result.stderr == ""
        metadata = json.loads(result.stdout)
        assert metadata == {"ok": True, "self_test": True, "checks": 7}
        assert real_events.read_bytes() == sentinel
        assert {path.name for path in run_root.iterdir()} == before_entries
        assert not list(run_root.glob(".append-event-self-test-*"))
        assert not (run_root / "EVENTS.FROZEN").exists()


def cache_artifacts() -> set[Path]:
    return {
        path.relative_to(SKILL_ROOT)
        for path in SKILL_ROOT.rglob("*")
        if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}
    }


def main() -> None:
    before_cache = cache_artifacts()
    assert SCRIPT.is_file(), f"append helper missing: {SCRIPT}"
    test_new_and_empty_streams_append_exact_records()
    test_hard_linked_event_stream_rejects_without_alias_mutation()
    test_invalid_prefixes_never_mutate()
    test_reference_escapes_and_non_regular_files_reject()
    test_invalid_and_bounded_inputs_reject_before_stream_creation()
    test_valid_json_history_rewrite_rejected_by_durable_anchor()
    test_tail_truncation_and_stream_deletion_rejected_by_durable_anchor()
    test_missing_and_forged_chain_fields_freeze()
    test_expected_count_tip_and_file_digest_mismatches_freeze()
    test_run_root_symlink_rejects_without_target_mutation()
    test_short_stream_write_freezes_later_appends()
    test_stream_fsync_failure_freezes_later_appends()
    test_stream_close_failure_freezes_later_appends()
    test_freeze_cleanup_failure_remains_frozen()
    test_transient_windows_freeze_cleanup_retries_without_reappending()
    test_transient_windows_freeze_cleanup_exhaustion_remains_frozen()
    test_nontransient_windows_freeze_cleanup_does_not_retry()
    test_freeze_cleanup_retry_rejects_marker_identity_change()
    test_freeze_cleanup_retry_restores_disappeared_marker()
    test_existing_freeze_blocks_append_and_self_test_first()
    test_self_test_is_isolated_and_removes_scratch()
    assert cache_artifacts() == before_cache
    for note in PLATFORM_NOTES:
        print(note)
    print("append event tests: PASS")


if __name__ == "__main__":
    main()
