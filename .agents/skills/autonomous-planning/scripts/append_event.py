#!/usr/bin/env python3
"""Append one byte-verified event to an autonomous artifact event stream."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path, PureWindowsPath
from typing import Any, NoReturn, Sequence


EVENTS_NAME = "EVENTS.jsonl"
FREEZE_NAME = "EVENTS.FROZEN"
FREEZE_BYTES = b'{"state":"append_in_progress_or_failed","version":1}\n'
STAGES = {"DISCOVERY": "D", "PLANNING": "P", "IMPLEMENTATION": "I"}
STATUSES = {"pending", "in_progress", "verified", "blocked", "superseded"}
PACKET_ID_RE = re.compile(r"([DPI])-\d{3}")
SHA256_RE = re.compile(r"[0-9a-f]{64}")
GENESIS_EVENT_SHA256 = "0" * 64
EMPTY_EVENTS_SHA256 = hashlib.sha256(b"").hexdigest()
MAX_REFERENCES = 32
MAX_REFERENCE_BYTES = 512
MAX_EVIDENCE_SUMMARY_BYTES = 4096
MAX_EVENT_TYPE_BYTES = 128
READ_CHUNK_BYTES = 1024 * 1024
FREEZE_CLEANUP_ATTEMPTS = 4
FREEZE_CLEANUP_RETRY_SECONDS = 0.025
WINDOWS_TRANSIENT_CLEANUP_ERRORS = {32, 33}


class AppendEventError(Exception):
    """An expected validation or append failure with a bounded public message."""


class SafeArgumentParser(argparse.ArgumentParser):
    """Avoid reflecting untrusted CLI values in parser errors."""

    def error(self, message: str) -> NoReturn:
        del message
        raise AppendEventError("invalid arguments")


def _reject_json_constant(value: str) -> NoReturn:
    del value
    raise ValueError("non-finite JSON constant")


@dataclass(frozen=True)
class PrefixState:
    data: bytes
    sha256: str
    last_seq: int
    last_timestamp: datetime | None
    last_event_sha256: str
    identity: tuple[int, int] | None
    existed: bool


@dataclass(frozen=True)
class FreezeState:
    identity: tuple[int, int]


def _identity(metadata: os.stat_result) -> tuple[int, int]:
    return metadata.st_dev, metadata.st_ino


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    if is_junction and is_junction():
        return True
    try:
        file_attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except OSError:
        return False
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return bool(file_attributes & reparse_point)


def resolve_run_root(raw_root: str | Path) -> Path:
    candidate = Path(raw_root)
    if not candidate.is_absolute():
        raise AppendEventError("invalid run root")
    try:
        metadata = candidate.lstat()
        if _is_link_or_junction(candidate) or not stat.S_ISDIR(metadata.st_mode):
            raise AppendEventError("invalid run root")
        resolved = candidate.resolve(strict=True)
    except AppendEventError:
        raise
    except (OSError, RuntimeError) as error:
        raise AppendEventError("invalid run root") from error
    if not resolved.is_dir():
        raise AppendEventError("invalid run root")
    return resolved


def _require_not_frozen(root: Path) -> None:
    if os.path.lexists(root / FREEZE_NAME):
        raise AppendEventError("event stream frozen")


def _freeze_marker_stat(
    marker_path: Path,
    root: Path,
    expected_identity: tuple[int, int] | None = None,
) -> os.stat_result:
    try:
        metadata = marker_path.lstat()
        resolved = marker_path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise AppendEventError("freeze marker invalid") from error
    if (
        _is_link_or_junction(marker_path)
        or not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
        or metadata.st_size != len(FREEZE_BYTES)
        or not _is_relative_to(resolved, root)
        or (
            expected_identity is not None
            and _identity(metadata) != expected_identity
        )
    ):
        raise AppendEventError("freeze marker invalid")
    return metadata


def _arm_freeze_marker(root: Path) -> FreezeState:
    marker_path = root / FREEZE_NAME
    _require_not_frozen(root)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(marker_path, flags, 0o600)
    except OSError as error:
        if os.path.lexists(marker_path):
            raise AppendEventError("event stream frozen") from error
        raise AppendEventError("freeze marker setup failed") from error

    written = -1
    setup_failed = False
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or opened.st_size != 0
        ):
            raise AppendEventError("freeze marker setup failed")
        try:
            written = os.write(descriptor, FREEZE_BYTES)
        except OSError:
            setup_failed = True
        try:
            os.fsync(descriptor)
        except OSError:
            setup_failed = True
    finally:
        try:
            os.close(descriptor)
        except OSError:
            setup_failed = True
    marker = _freeze_marker_stat(marker_path, root, _identity(opened))
    if setup_failed or written != len(FREEZE_BYTES):
        raise AppendEventError("freeze marker setup failed")
    return FreezeState(identity=_identity(marker))


def _restore_freeze_marker(root: Path) -> None:
    if os.path.lexists(root / FREEZE_NAME):
        return
    _arm_freeze_marker(root)


def _validate_freeze_marker_for_cleanup(
    marker_path: Path,
    root: Path,
    freeze: FreezeState,
) -> None:
    marker = _freeze_marker_stat(marker_path, root, freeze.identity)
    marker_bytes = _read_regular_bytes(
        marker_path,
        marker,
        "freeze marker invalid",
        require_single_link=True,
    )
    if marker_bytes != FREEZE_BYTES:
        raise AppendEventError("freeze marker invalid")


def _is_transient_windows_cleanup_error(error: OSError) -> bool:
    return getattr(error, "winerror", None) in WINDOWS_TRANSIENT_CLEANUP_ERRORS


def _remove_freeze_marker(root: Path, freeze: FreezeState) -> None:
    marker_path = root / FREEZE_NAME
    try:
        for attempt in range(FREEZE_CLEANUP_ATTEMPTS):
            _validate_freeze_marker_for_cleanup(marker_path, root, freeze)
            try:
                os.unlink(marker_path)
            except OSError as error:
                if (
                    not _is_transient_windows_cleanup_error(error)
                    or attempt + 1 == FREEZE_CLEANUP_ATTEMPTS
                ):
                    raise
                time.sleep(FREEZE_CLEANUP_RETRY_SECONDS)
                continue
            if os.path.lexists(marker_path):
                raise AppendEventError("freeze cleanup failed")
            return
    except (AppendEventError, OSError) as error:
        try:
            _restore_freeze_marker(root)
        except AppendEventError as restore_error:
            raise AppendEventError("freeze cleanup failed") from restore_error
        raise AppendEventError("freeze cleanup failed") from error


def _read_regular_bytes(
    path: Path,
    expected: os.stat_result,
    error_message: str,
    *,
    require_single_link: bool = False,
) -> bytes:
    flags = os.O_RDONLY
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise AppendEventError(error_message) from error
    chunks: list[bytes] = []
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or _identity(opened) != _identity(expected)
            or (require_single_link and opened.st_nlink != 1)
        ):
            raise AppendEventError(error_message)
        while True:
            chunk = os.read(descriptor, READ_CHUNK_BYTES)
            if not chunk:
                break
            chunks.append(chunk)
    except OSError as error:
        raise AppendEventError(error_message) from error
    finally:
        os.close(descriptor)
    try:
        after = path.lstat()
    except OSError as error:
        raise AppendEventError(error_message) from error
    if (
        _is_link_or_junction(path)
        or _identity(after) != _identity(expected)
        or (require_single_link and after.st_nlink != 1)
    ):
        raise AppendEventError(error_message)
    return b"".join(chunks)


def _event_file_stat(path: Path, root: Path, error_message: str) -> os.stat_result | None:
    if not os.path.lexists(path):
        return None
    try:
        metadata = path.lstat()
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise AppendEventError(error_message) from error
    if (
        _is_link_or_junction(path)
        or not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
        or not _is_relative_to(resolved, root)
    ):
        raise AppendEventError(error_message)
    return metadata


def _parse_timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise AppendEventError("invalid event prefix")
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise AppendEventError("invalid event prefix") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AppendEventError("invalid event prefix")
    return parsed.astimezone(timezone.utc)


def canonical_event_sha256(event: dict[str, Any]) -> str:
    canonical = dict(event)
    canonical.pop("event_sha256", None)
    try:
        body = json.dumps(
            canonical,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as error:
        raise AppendEventError("event chain invalid") from error
    return hashlib.sha256(body).hexdigest()


def _validate_prefix(data: bytes, identity: tuple[int, int] | None) -> PrefixState:
    digest = hashlib.sha256(data).hexdigest()
    if not data:
        return PrefixState(
            data,
            digest,
            0,
            None,
            GENESIS_EVENT_SHA256,
            identity,
            identity is not None,
        )
    if not data.endswith(b"\n"):
        raise AppendEventError("invalid event prefix")

    previous_timestamp: datetime | None = None
    previous_event_sha256 = GENESIS_EVENT_SHA256
    expected_seq = 1
    for raw_line in data[:-1].split(b"\n"):
        try:
            parsed = json.loads(
                raw_line.decode("utf-8"),
                parse_constant=_reject_json_constant,
            )
        except (UnicodeDecodeError, ValueError) as error:
            raise AppendEventError("invalid event prefix") from error
        if not isinstance(parsed, dict):
            raise AppendEventError("invalid event prefix")
        event_seq = parsed.get("event_seq")
        if (
            not isinstance(event_seq, int)
            or isinstance(event_seq, bool)
            or event_seq != expected_seq
        ):
            raise AppendEventError("invalid event prefix")
        timestamp = _parse_timestamp(parsed.get("timestamp"))
        if previous_timestamp is not None and timestamp <= previous_timestamp:
            raise AppendEventError("invalid event prefix")
        linked_previous = parsed.get("previous_event_sha256")
        event_sha256 = parsed.get("event_sha256")
        if (
            not isinstance(linked_previous, str)
            or SHA256_RE.fullmatch(linked_previous) is None
            or linked_previous != previous_event_sha256
            or not isinstance(event_sha256, str)
            or SHA256_RE.fullmatch(event_sha256) is None
            or canonical_event_sha256(parsed) != event_sha256
        ):
            raise AppendEventError("invalid event prefix")
        previous_timestamp = timestamp
        previous_event_sha256 = event_sha256
        expected_seq += 1
    return PrefixState(
        data,
        digest,
        expected_seq - 1,
        previous_timestamp,
        previous_event_sha256,
        identity,
        identity is not None,
    )


def _read_prefix(events_path: Path, root: Path) -> PrefixState:
    metadata = _event_file_stat(events_path, root, "invalid event stream")
    if metadata is None:
        return _validate_prefix(b"", None)
    data = _read_regular_bytes(
        events_path,
        metadata,
        "invalid event stream",
        require_single_link=True,
    )
    return _validate_prefix(data, _identity(metadata))


def _validate_portable_reference(raw_path: str) -> tuple[str, ...]:
    try:
        encoded_length = len(raw_path.encode("utf-8"))
    except UnicodeEncodeError as error:
        raise AppendEventError("invalid reference") from error
    windows_path = PureWindowsPath(raw_path)
    parts = raw_path.split("/")
    if (
        not raw_path
        or encoded_length > MAX_REFERENCE_BYTES
        or "\\" in raw_path
        or ":" in raw_path
        or "\x00" in raw_path
        or windows_path.is_absolute()
        or bool(windows_path.drive)
        or any(part in {"", ".", ".."} for part in parts)
        or any(ord(character) < 32 for character in raw_path)
    ):
        raise AppendEventError("invalid reference")
    return tuple(parts)


def _hash_reference(root: Path, raw_path: str) -> dict[str, str]:
    parts = _validate_portable_reference(raw_path)
    candidate = root
    metadata: os.stat_result | None = None
    for index, part in enumerate(parts):
        candidate = candidate / part
        try:
            metadata = candidate.lstat()
        except OSError as error:
            raise AppendEventError("invalid reference") from error
        if _is_link_or_junction(candidate):
            raise AppendEventError("invalid reference")
        if index < len(parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise AppendEventError("invalid reference")
    if metadata is None or not stat.S_ISREG(metadata.st_mode):
        raise AppendEventError("invalid reference")
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise AppendEventError("invalid reference") from error
    if not _is_relative_to(resolved, root):
        raise AppendEventError("invalid reference")
    contents = _read_regular_bytes(candidate, metadata, "invalid reference")
    return {"path": raw_path, "sha256": hashlib.sha256(contents).hexdigest()}


def _validate_inputs(
    stage: str,
    event_type: str,
    packet_id: str | None,
    from_status: str | None,
    to_status: str | None,
    references: Sequence[str],
    evidence_summary: str,
) -> None:
    try:
        event_type_bytes = event_type.encode("utf-8")
        evidence_bytes = evidence_summary.encode("utf-8")
    except UnicodeEncodeError as error:
        raise AppendEventError("invalid event fields") from error
    if stage not in STAGES:
        raise AppendEventError("invalid stage")
    if (
        not event_type.strip()
        or len(event_type_bytes) > MAX_EVENT_TYPE_BYTES
        or any(ord(character) < 32 for character in event_type)
    ):
        raise AppendEventError("invalid event fields")
    if (
        not evidence_summary.strip()
        or len(evidence_bytes) > MAX_EVIDENCE_SUMMARY_BYTES
        or "\x00" in evidence_summary
    ):
        raise AppendEventError("invalid evidence summary")
    if len(references) > MAX_REFERENCES:
        raise AppendEventError("too many references")
    if from_status is not None and from_status not in STATUSES:
        raise AppendEventError("invalid status")
    if to_status is not None and to_status not in STATUSES:
        raise AppendEventError("invalid status")
    if packet_id is not None:
        match = PACKET_ID_RE.fullmatch(packet_id)
        if match is None or match.group(1) != STAGES[stage]:
            raise AppendEventError("invalid packet id")


def _validate_expected_anchor_inputs(
    expected_event_count: int | None,
    expected_event_tip: str | None,
    expected_events_sha256: str | None,
) -> None:
    supplied = (
        expected_event_count is not None,
        expected_event_tip is not None,
        expected_events_sha256 is not None,
    )
    if any(supplied) and not all(supplied):
        raise AppendEventError("invalid accepted event anchor")
    if not any(supplied):
        return
    if (
        not isinstance(expected_event_count, int)
        or isinstance(expected_event_count, bool)
        or expected_event_count < 0
        or not isinstance(expected_event_tip, str)
        or SHA256_RE.fullmatch(expected_event_tip) is None
        or not isinstance(expected_events_sha256, str)
        or SHA256_RE.fullmatch(expected_events_sha256) is None
    ):
        raise AppendEventError("invalid accepted event anchor")


def _require_expected_anchor(
    prefix: PrefixState,
    expected_event_count: int | None,
    expected_event_tip: str | None,
    expected_events_sha256: str | None,
) -> None:
    if expected_event_count is None:
        if prefix.last_seq == 0:
            return
        raise AppendEventError("accepted event anchor required")
    if (
        prefix.last_seq != expected_event_count
        or prefix.last_event_sha256 != expected_event_tip
        or prefix.sha256 != expected_events_sha256
    ):
        raise AppendEventError("accepted event anchor mismatch")


def _next_timestamp(previous: datetime | None) -> tuple[datetime, str]:
    current = datetime.now(timezone.utc)
    if previous is not None and current <= previous:
        try:
            current = previous + timedelta(microseconds=1)
        except OverflowError as error:
            raise AppendEventError("timestamp unavailable") from error
    return current, current.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _serialize_event(event: dict[str, Any]) -> bytes:
    try:
        body = json.dumps(
            event,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as error:
        raise AppendEventError("event serialization failed") from error
    if b"\n" in body or b"\r" in body:
        raise AppendEventError("event serialization failed")
    return body + b"\n"


def _append_once(
    events_path: Path,
    prefix: PrefixState,
    record: bytes,
) -> tuple[os.stat_result, int, bool]:
    flags = os.O_WRONLY | os.O_APPEND
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    if prefix.existed:
        open_flags = flags
    else:
        open_flags = flags | os.O_CREAT | os.O_EXCL
    try:
        descriptor = os.open(events_path, open_flags, 0o600)
    except OSError as error:
        raise AppendEventError("append write failed") from error

    written = -1
    write_failed = False
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_nlink != 1
            or opened.st_size != len(prefix.data)
        ):
            raise AppendEventError("append precondition changed")
        if prefix.identity is not None and _identity(opened) != prefix.identity:
            raise AppendEventError("append precondition changed")
        try:
            written = os.write(descriptor, record)
        except OSError:
            write_failed = True
        try:
            os.fsync(descriptor)
        except OSError:
            write_failed = True
    finally:
        try:
            os.close(descriptor)
        except OSError:
            write_failed = True
    return opened, written, write_failed


def _verify_postcondition(
    events_path: Path,
    root: Path,
    prefix: PrefixState,
    record: bytes,
    event: dict[str, Any],
    opened: os.stat_result,
) -> str:
    metadata = _event_file_stat(events_path, root, "append postcondition failed")
    if metadata is None or _identity(metadata) != _identity(opened):
        raise AppendEventError("append postcondition failed")
    final = _read_regular_bytes(
        events_path,
        metadata,
        "append postcondition failed",
        require_single_link=True,
    )
    prefix_length = len(prefix.data)
    if (
        len(final) != prefix_length + len(record)
        or final[:prefix_length] != prefix.data
        or hashlib.sha256(final[:prefix_length]).hexdigest() != prefix.sha256
        or final[prefix_length:] != record
        or not final.endswith(b"\n")
    ):
        raise AppendEventError("append postcondition failed")
    try:
        parsed = json.loads(
            final[prefix_length:-1].decode("utf-8"),
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, ValueError) as error:
        raise AppendEventError("append postcondition failed") from error
    if parsed != event:
        raise AppendEventError("append postcondition failed")
    return hashlib.sha256(final).hexdigest()


def append_event(
    run_root: str | Path,
    *,
    stage: str,
    event_type: str,
    packet_id: str | None = None,
    from_status: str | None = None,
    to_status: str | None = None,
    references: Sequence[str] = (),
    evidence_summary: str,
    expected_event_count: int | None = None,
    expected_event_tip: str | None = None,
    expected_events_sha256: str | None = None,
) -> dict[str, object]:
    root = resolve_run_root(run_root)
    _require_not_frozen(root)
    _validate_inputs(
        stage,
        event_type,
        packet_id,
        from_status,
        to_status,
        references,
        evidence_summary,
    )
    _validate_expected_anchor_inputs(
        expected_event_count,
        expected_event_tip,
        expected_events_sha256,
    )
    hashed_references = [_hash_reference(root, path) for path in references]
    events_path = root / EVENTS_NAME
    freeze = _arm_freeze_marker(root)
    prefix = _read_prefix(events_path, root)
    _require_expected_anchor(
        prefix,
        expected_event_count,
        expected_event_tip,
        expected_events_sha256,
    )
    _current, serialized_timestamp = _next_timestamp(prefix.last_timestamp)
    event: dict[str, Any] = {
        "event_seq": prefix.last_seq + 1,
        "timestamp": serialized_timestamp,
        "event_type": event_type,
        "stage": stage,
    }
    if packet_id is not None:
        event["packet_id"] = packet_id
    if from_status is not None:
        event["from_status"] = from_status
    if to_status is not None:
        event["to_status"] = to_status
    event["actor"] = "top_level_orchestrator"
    event["references"] = hashed_references
    event["evidence_summary"] = evidence_summary
    event["previous_event_sha256"] = prefix.last_event_sha256
    event["event_sha256"] = canonical_event_sha256(event)
    record = _serialize_event(event)

    opened, written, write_failed = _append_once(events_path, prefix, record)
    accepted_events_sha256 = _verify_postcondition(
        events_path,
        root,
        prefix,
        record,
        event,
        opened,
    )
    if write_failed or written != len(record):
        raise AppendEventError("append write failed")
    _remove_freeze_marker(root, freeze)
    return {
        "ok": True,
        "event_seq": event["event_seq"],
        "bytes_appended": len(record),
        "prefix_length": len(prefix.data),
        "prefix_sha256": prefix.sha256,
        "accepted_event_count": event["event_seq"],
        "accepted_event_tip": event["event_sha256"],
        "accepted_events_sha256": accepted_events_sha256,
    }


def run_self_test(run_root: str | Path) -> dict[str, object]:
    root = resolve_run_root(run_root)
    _require_not_frozen(root)
    scratch_path: Path | None = None
    failure: Exception | None = None
    try:
        scratch_path = Path(
            tempfile.mkdtemp(prefix=".append-event-self-test-", dir=root)
        ).resolve(strict=True)
        if not _is_relative_to(scratch_path, root):
            raise AppendEventError("self-test failed")
        reference = scratch_path / "reference.txt"
        reference.write_bytes(b"append-event-self-test-reference\n")
        first = append_event(
            scratch_path,
            stage="DISCOVERY",
            event_type="run_initialized",
            references=("reference.txt",),
            evidence_summary="self-test first append",
        )
        second = append_event(
            scratch_path,
            stage="DISCOVERY",
            event_type="stage_routed",
            references=("reference.txt",),
            evidence_summary="self-test second append",
            expected_event_count=int(first["accepted_event_count"]),
            expected_event_tip=str(first["accepted_event_tip"]),
            expected_events_sha256=str(first["accepted_events_sha256"]),
        )
        scratch_events = scratch_path / EVENTS_NAME
        complete = scratch_events.read_bytes()
        parsed = [json.loads(line) for line in complete.splitlines()]
        expected_hash = hashlib.sha256(reference.read_bytes()).hexdigest()
        if (
            first.get("event_seq") != 1
            or second.get("event_seq") != 2
            or [item.get("event_seq") for item in parsed] != [1, 2]
            or parsed[0].get("previous_event_sha256")
            != GENESIS_EVENT_SHA256
            or parsed[1].get("previous_event_sha256")
            != parsed[0].get("event_sha256")
            or any(canonical_event_sha256(item) != item.get("event_sha256") for item in parsed)
            or second.get("accepted_event_count") != 2
            or second.get("accepted_event_tip") != parsed[1].get("event_sha256")
            or second.get("accepted_events_sha256")
            != hashlib.sha256(complete).hexdigest()
            or _parse_timestamp(parsed[0].get("timestamp"))
            >= _parse_timestamp(parsed[1].get("timestamp"))
            or any(
                item.get("references")
                != [{"path": "reference.txt", "sha256": expected_hash}]
                for item in parsed
            )
        ):
            raise AppendEventError("self-test failed")

        partial = b'{"partial":'
        with scratch_events.open("ab", buffering=0) as handle:
            if handle.write(partial) != len(partial):
                raise AppendEventError("self-test failed")
            os.fsync(handle.fileno())
        rejected_prefix = scratch_events.read_bytes()
        try:
            append_event(
                scratch_path,
                stage="DISCOVERY",
                event_type="stage_routed",
                evidence_summary="self-test rejection",
                expected_event_count=int(second["accepted_event_count"]),
                expected_event_tip=str(second["accepted_event_tip"]),
                expected_events_sha256=str(second["accepted_events_sha256"]),
            )
        except AppendEventError:
            pass
        else:
            raise AppendEventError("self-test failed")
        if scratch_events.read_bytes() != rejected_prefix:
            raise AppendEventError("self-test failed")
        marker = scratch_path / FREEZE_NAME
        if marker.read_bytes() != FREEZE_BYTES:
            raise AppendEventError("self-test failed")
        try:
            append_event(
                scratch_path,
                stage="PLANNING",
                event_type="stage_routed",
                evidence_summary="self-test frozen refusal",
            )
        except AppendEventError:
            pass
        else:
            raise AppendEventError("self-test failed")
    except Exception as error:
        failure = error
    finally:
        if scratch_path is not None:
            try:
                shutil.rmtree(scratch_path)
            except OSError as error:
                failure = error
    if failure is not None:
        raise AppendEventError("self-test failed") from failure
    return {"ok": True, "self_test": True, "checks": 7}


def build_parser() -> SafeArgumentParser:
    parser = SafeArgumentParser(description="Append one verified event record.")
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--stage")
    parser.add_argument("--event-type")
    parser.add_argument("--packet-id")
    parser.add_argument("--from-status")
    parser.add_argument("--to-status")
    parser.add_argument("--reference", action="append", default=[])
    parser.add_argument("--evidence-summary")
    parser.add_argument("--expected-event-count", type=int)
    parser.add_argument("--expected-event-tip")
    parser.add_argument("--expected-events-sha256")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    try:
        arguments = build_parser().parse_args(argv)
        if arguments.self_test:
            append_fields = (
                arguments.stage,
                arguments.event_type,
                arguments.packet_id,
                arguments.from_status,
                arguments.to_status,
                arguments.evidence_summary,
                arguments.expected_event_count,
                arguments.expected_event_tip,
                arguments.expected_events_sha256,
            )
            if any(value is not None for value in append_fields) or arguments.reference:
                raise AppendEventError("invalid arguments")
            metadata = run_self_test(arguments.run_root)
        else:
            if (
                arguments.stage is None
                or arguments.event_type is None
                or arguments.evidence_summary is None
            ):
                raise AppendEventError("invalid arguments")
            metadata = append_event(
                arguments.run_root,
                stage=arguments.stage,
                event_type=arguments.event_type,
                packet_id=arguments.packet_id,
                from_status=arguments.from_status,
                to_status=arguments.to_status,
                references=tuple(arguments.reference),
                evidence_summary=arguments.evidence_summary,
                expected_event_count=arguments.expected_event_count,
                expected_event_tip=arguments.expected_event_tip,
                expected_events_sha256=arguments.expected_events_sha256,
            )
        sys.stdout.write(json.dumps(metadata, separators=(",", ":")) + "\n")
        return 0
    except AppendEventError as error:
        sys.stderr.write(f"error: {error}\n")
        return 2
    except Exception:
        sys.stderr.write("error: append operation failed\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
