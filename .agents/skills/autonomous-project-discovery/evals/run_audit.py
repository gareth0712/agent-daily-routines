#!/usr/bin/env python3
"""Runner-owned filesystem/Git observer for cold-start skill evaluations."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKET_RE = re.compile(r"(?:^|[^A-Z0-9])(D-\d{3})(?:[^A-Z0-9]|$)", re.I)
PACKET_ID_RE = re.compile(r"D-\d{3}", re.I)
CONTROL_SECRET_ENV = "DISCOVERY_RUNNER_AUDIT_HMAC_KEY"
ACTIVE_PACKET_STATUSES = {"pending", "in_progress", "blocked"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(repo: Path, *args: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "command": ["git", *args],
        "exit_code": completed.returncode,
        "stdout_lines": completed.stdout.splitlines(),
        "stderr_excerpt": completed.stderr[:1000],
    }


def git_snapshot(repo: Path) -> dict[str, Any]:
    head = run_git(repo, "rev-parse", "HEAD")
    tracked = run_git(repo, "status", "--porcelain=v1", "--untracked-files=no")
    untracked = run_git(repo, "ls-files", "--others", "--exclude-standard")
    return {
        "captured_at": utc_now(),
        "head": head["stdout_lines"][0] if head["exit_code"] == 0 and head["stdout_lines"] else None,
        "tracked_status": tracked,
        "nonignored_untracked": untracked,
    }


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def snapshot_files(
    root: Path,
) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    if not root.exists():
        return {}, []
    result: dict[str, dict[str, Any]] = {}
    deferred: list[dict[str, str]] = []
    try:
        candidates = sorted(root.rglob("*"))
    except OSError:
        return {}, [{"path": ".", "reason": "root_enumeration_unavailable"}]
    for path in candidates:
        try:
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            before = path.stat()
            digest = sha256(path)
            after = path.stat()
        except FileNotFoundError:
            relative = path.relative_to(root).as_posix()
            deferred.append({"path": relative, "reason": "path_disappeared"})
            continue
        except OSError:
            relative = path.relative_to(root).as_posix()
            deferred.append({"path": relative, "reason": "path_unreadable"})
            continue
        if (
            (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)
            or before.st_size != after.st_size
            or before.st_mtime_ns != after.st_mtime_ns
        ):
            deferred.append({"path": relative, "reason": "path_changed_during_sample"})
            continue
        result[relative] = {
            "absolute_path": str(path),
            "size": after.st_size,
            "mtime_ns": after.st_mtime_ns,
            "sha256": digest,
        }
    return result, deferred


def preserve_deferred_previous_files(
    current: dict[str, dict[str, Any]],
    previous: dict[str, dict[str, Any]],
    deferred: list[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    if any(
        item["path"] == "." and item["reason"] == "root_enumeration_unavailable"
        for item in deferred
    ):
        preserved = dict(previous)
        preserved.update(current)
        return preserved
    preserved = dict(current)
    for item in deferred:
        path = item["path"]
        if path in previous:
            preserved[path] = previous[path]
    return preserved


def packet_from(*values: str | None) -> str | None:
    for value in values:
        if not value:
            continue
        match = PACKET_RE.search(value)
        if match:
            return match.group(1).upper()
    return None


def classify_file(relative: str) -> str:
    lowered = relative.lower()
    name = Path(relative).name.lower()
    if "/reports/" in f"/{lowered}" or re.match(r"d-\d{3}-report\.md$", name):
        return "worker_report"
    if "/evidence/" in f"/{lowered}" and name in {"preflight.md", "path-containment-preflight.md"}:
        return "orchestrator_preflight_evidence"
    if "/evidence/" in f"/{lowered}" and name == "path-containment-postwrite.md":
        return "orchestrator_postwrite_containment"
    if "/evidence/" in f"/{lowered}":
        return "worker_evidence"
    if lowered == "events.jsonl":
        return "production_events"
    if name == "agent-state.md":
        return "control_state"
    if "/packets/" in f"/{lowered}":
        return "packet_contract"
    if "/gates/" in f"/{lowered}":
        return "canonical_gate"
    return "other_output"


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def parse_packet_table(text: str) -> dict[str, dict[str, str]]:
    """Read the canonical Packets markdown table from root AGENT-STATE.md."""
    lines = text.splitlines()
    in_packets = False
    header: list[str] | None = None
    result: dict[str, dict[str, str]] = {}
    for line in lines:
        stripped = line.strip()
        if stripped.lower() == "## packets":
            in_packets = True
            continue
        if in_packets and stripped.startswith("## "):
            break
        if not in_packets or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if header is None:
            lowered = [cell.lower() for cell in cells]
            if "packet" in lowered and "status" in lowered:
                header = lowered
            continue
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        if len(cells) != len(header):
            continue
        packet = cells[header.index("packet")].upper()
        status = cells[header.index("status")].lower()
        if PACKET_ID_RE.fullmatch(packet):
            canonical_row = json.dumps(cells, ensure_ascii=False, separators=(",", ":"))
            result[packet] = {
                "status": status,
                "row_sha256": hashlib.sha256(canonical_row.encode("utf-8")).hexdigest(),
            }
    return result


class Audit:
    def __init__(
        self,
        repo: Path,
        output: Path,
        audit_dir: Path,
        stop_file: Path,
        control_file: Path,
        control_secret: bytes,
        poll_ms: int,
    ):
        self.repo = repo.resolve()
        self.output = output.resolve()
        self.audit_dir = audit_dir.resolve()
        self.stop_file = stop_file.resolve()
        self.control_file = control_file.resolve()
        self.control_secret = control_secret
        self.poll_seconds = poll_ms / 1000
        self.events_path = self.audit_dir / "runner-audit.jsonl"
        self.summary_path = self.audit_dir / "summary.json"
        self.seq = 0
        self.events: list[dict[str, Any]] = []
        self.files: dict[str, dict[str, Any]] = {}
        self.production_lines_seen: dict[str, int] = {}
        self.production_streams: dict[str, dict[str, Any]] = {}
        self.production_claims: list[dict[str, Any]] = []
        self.production_read_deferred: dict[str, str] = {}
        self.deferred_file_observations: dict[str, str] = {}
        self.deferred_file_observation_count = 0
        self.secondary_read_deferred: dict[str, str] = {}
        self.control_lines_seen = 0
        self.control_line_hashes: list[str] = []
        self.control_append_only_valid = True
        self.control_authentication_valid = True
        self.control_last_seq = 0
        self.control_last_hmac: str | None = None
        self.control_request_ids: set[str] = set()
        self.samples: dict[str, dict[str, Any]] = {}
        self.packet_rows: dict[str, dict[str, str]] = {}
        self.state_transitions: dict[str, list[dict[str, Any]]] = {}
        self.state_epoch = 0
        self.initial_git = git_snapshot(self.repo)

    def emit(self, event_type: str, **fields: Any) -> None:
        self.seq += 1
        event = {
            "event_seq": self.seq,
            "timestamp": utc_now(),
            "event_type": event_type,
            **fields,
        }
        self.events.append(event)
        with self.events_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def observe_files(self) -> None:
        current, deferred = snapshot_files(self.output)
        next_deferred = {item["path"]: item["reason"] for item in deferred}
        for path, reason in sorted(next_deferred.items()):
            if self.deferred_file_observations.get(path) == reason:
                continue
            self.deferred_file_observation_count += 1
            self.emit(
                "output_file_observation_deferred",
                path=path,
                reason=reason,
            )
        for path, prior_reason in sorted(self.deferred_file_observations.items()):
            if path in next_deferred:
                continue
            self.emit(
                "output_file_observation_deferred_resolved",
                path=path,
                prior_reason=prior_reason,
                resolution="stable_sample" if path in current else "path_no_longer_present",
            )
        self.deferred_file_observations = next_deferred
        current = preserve_deferred_previous_files(current, self.files, deferred)
        changed = [
            (relative, metadata)
            for relative, metadata in current.items()
            if relative not in self.files or self.files[relative]["sha256"] != metadata["sha256"]
        ]
        # Detection order is not creation order when several writes land inside one
        # polling interval. NTFS mtimes preserve the stronger runner-observed signal.
        for relative, metadata in sorted(changed, key=lambda item: (item[1]["mtime_ns"], item[0])):
            previous = self.files.get(relative)
            role = classify_file(relative)
            self.emit(
                "output_file_created" if previous is None else "output_file_modified",
                path=relative,
                absolute_path=metadata["absolute_path"],
                sha256=metadata["sha256"],
                size=metadata["size"],
                mtime_ns=metadata["mtime_ns"],
                role=role,
                packet_id=packet_from(relative),
            )
        for relative, metadata in self.files.items():
            if relative not in current:
                self.emit(
                    "output_file_deleted",
                    path=relative,
                    sha256=metadata["sha256"],
                    role=classify_file(relative),
                    packet_id=packet_from(relative),
                )
                if relative == "AGENT-STATE.md":
                    self.state_epoch += 1
                    self.packet_rows = {}
                    self.emit("runner_state_history_reset", reason="canonical_state_deleted", state_epoch=self.state_epoch)
        self.observe_canonical_state(current)
        self.files = current

    def observe_canonical_state(self, current: dict[str, dict[str, Any]]) -> None:
        metadata = current.get("AGENT-STATE.md")
        previous = self.files.get("AGENT-STATE.md")
        if metadata is None or (
            previous is not None
            and previous["sha256"] == metadata["sha256"]
            and "AGENT-STATE.md" not in self.secondary_read_deferred
        ):
            return
        state_path = self.output / "AGENT-STATE.md"
        state_write_event = next(
            (
                event
                for event in reversed(self.events)
                if event.get("path") == "AGENT-STATE.md"
                and event.get("sha256") == metadata["sha256"]
                and event.get("event_type") in {"output_file_created", "output_file_modified"}
            ),
            None,
        )
        if state_write_event is None:
            return
        try:
            state_bytes = state_path.read_bytes()
        except OSError:
            self._defer_secondary_read("AGENT-STATE.md", "path_unreadable_after_snapshot")
            return
        if hashlib.sha256(state_bytes).hexdigest() != metadata["sha256"]:
            self._defer_secondary_read("AGENT-STATE.md", "path_changed_after_snapshot")
            return
        self._resolve_secondary_read("AGENT-STATE.md")
        rows = parse_packet_table(state_bytes.decode("utf-8", errors="replace"))
        for packet_id, row in sorted(rows.items()):
            status = row["status"]
            prior_row = self.packet_rows.get(packet_id)
            prior = prior_row["status"] if prior_row else None
            if prior is None:
                self.emit(
                    "runner_packet_state_observed",
                    packet_id=packet_id,
                    status=status,
                    packet_row_sha256=row["row_sha256"],
                    state_path="AGENT-STATE.md",
                    state_sha256=metadata["sha256"],
                    state_write_event_seq=state_write_event["event_seq"],
                    state_write_mtime_ns=state_write_event["mtime_ns"],
                    state_epoch=self.state_epoch,
                )
            elif prior != status:
                self.emit(
                    "runner_packet_state_transition_observed",
                    packet_id=packet_id,
                    from_status=prior,
                    to_status=status,
                    packet_row_sha256=row["row_sha256"],
                    state_path="AGENT-STATE.md",
                    state_sha256=metadata["sha256"],
                    state_write_event_seq=state_write_event["event_seq"],
                    state_write_mtime_ns=state_write_event["mtime_ns"],
                    state_epoch=self.state_epoch,
                )
                self.state_transitions.setdefault(packet_id, []).append(self.events[-1])
            elif prior_row["row_sha256"] != row["row_sha256"]:
                self.emit(
                    "runner_packet_state_row_updated",
                    packet_id=packet_id,
                    status=status,
                    prior_packet_row_sha256=prior_row["row_sha256"],
                    packet_row_sha256=row["row_sha256"],
                    state_path="AGENT-STATE.md",
                    state_sha256=metadata["sha256"],
                    state_write_event_seq=state_write_event["event_seq"],
                    state_write_mtime_ns=state_write_event["mtime_ns"],
                    state_epoch=self.state_epoch,
                )
            self.packet_rows[packet_id] = row
        for packet_id in set(self.packet_rows) - set(rows):
            self.emit(
                "runner_packet_state_disappeared",
                packet_id=packet_id,
                prior_status=self.packet_rows[packet_id]["status"],
                state_sha256=metadata["sha256"],
                state_write_event_seq=state_write_event["event_seq"],
                state_write_mtime_ns=state_write_event["mtime_ns"],
                state_epoch=self.state_epoch,
            )
            del self.packet_rows[packet_id]

    def _defer_secondary_read(self, path: str, reason: str) -> None:
        if self.secondary_read_deferred.get(path) != reason:
            self.emit("output_secondary_read_deferred", path=path, reason=reason)
        self.secondary_read_deferred[path] = reason

    def _resolve_secondary_read(self, path: str) -> None:
        prior_reason = self.secondary_read_deferred.pop(path, None)
        if prior_reason is not None:
            self.emit(
                "output_secondary_read_deferred_resolved",
                path=path,
                prior_reason=prior_reason,
            )

    def observe_production_events(self) -> None:
        path = self.output / "EVENTS.jsonl"
        relative = "EVENTS.jsonl"
        try:
            canonical_exists = path.is_file()
        except OSError:
            canonical_exists = True
        if not canonical_exists:
            stream = self.production_streams.get(relative)
            if stream is not None and stream["observed_line_count"]:
                stream["read_observation_complete"] = False
                stream["append_only_valid"] = False
                if "stream_missing_after_observation" not in stream["errors"]:
                    stream["errors"].append("stream_missing_after_observation")
                    self.emit("production_stream_missing", path=relative)
            return

        stream = self.production_streams.setdefault(
            relative,
            {
                "observed_line_count": 0,
                "parse_valid": True,
                "append_only_valid": True,
                "source_sequence_valid": True,
                "source_timestamps_valid": True,
                "references_valid": True,
                "read_observation_complete": False,
                "last_source_seq": None,
                "last_source_timestamp": None,
                "line_hashes": [],
                "errors": [],
            },
        )
        try:
            raw_text = path.read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            stream["read_observation_complete"] = False
            reason = "path_disappeared"
            if self.production_read_deferred.get(relative) != reason:
                self.emit("production_stream_read_deferred", path=relative, reason=reason)
            self.production_read_deferred[relative] = reason
            return
        except OSError:
            stream["read_observation_complete"] = False
            reason = "path_unreadable"
            if self.production_read_deferred.get(relative) != reason:
                self.emit("production_stream_read_deferred", path=relative, reason=reason)
            self.production_read_deferred[relative] = reason
            return
        stream["read_observation_complete"] = True
        prior_read_defer = self.production_read_deferred.pop(relative, None)
        if prior_read_defer is not None:
            self.emit(
                "production_stream_read_deferred_resolved",
                path=relative,
                prior_reason=prior_read_defer,
            )
        for _canonical_path in (path,):
            lines = raw_text.splitlines()
            if raw_text and not raw_text.endswith(("\n", "\r")):
                stream["parse_valid"] = False
                if "incomplete_terminal_record" not in stream["errors"]:
                    stream["errors"].append("incomplete_terminal_record")
                    self.emit("production_stream_incomplete_record", path=relative)
                lines = lines[:-1]
            start = self.production_lines_seen.get(relative, 0)
            current_hashes = [hashlib.sha256(line.encode("utf-8")).hexdigest() for line in lines]
            previous_hashes = stream["line_hashes"]
            prefix_length = min(start, len(lines))
            prefix_changed = current_hashes[:prefix_length] != previous_hashes[:prefix_length]
            truncated = len(lines) < start
            if prefix_changed or truncated:
                stream["append_only_valid"] = False
                mutation = "truncated" if truncated else "rewritten"
                stream["errors"].append(f"stream_{mutation}_after_observation")
                self.emit(
                    "production_stream_mutation_observed",
                    path=relative,
                    mutation=mutation,
                    previously_observed_lines=start,
                    current_complete_lines=len(lines),
                )
                # Do not reinterpret rewritten history as fresh append evidence.
                start = len(lines)
            for line_number, raw in enumerate(lines[start:], start=start + 1):
                try:
                    item = json.loads(raw)
                except json.JSONDecodeError as error:
                    stream["parse_valid"] = False
                    stream["errors"].append(f"line {line_number}: invalid JSON")
                    self.emit(
                        "production_event_parse_error",
                        path=relative,
                        line_number=line_number,
                        error=str(error),
                    )
                    continue
                source_type = str(item.get("event_type", "unknown"))
                packet_id = item.get("packet_id") or packet_from(json.dumps(item, ensure_ascii=False))
                errors: list[str] = []
                source_seq = item.get("event_seq")
                if not isinstance(source_seq, int) or isinstance(source_seq, bool) or source_seq < 1:
                    errors.append("invalid_event_seq")
                    stream["source_sequence_valid"] = False
                else:
                    previous_seq = stream["last_source_seq"]
                    if previous_seq is not None and source_seq <= previous_seq:
                        errors.append("non_monotonic_event_seq")
                        stream["source_sequence_valid"] = False
                    stream["last_source_seq"] = source_seq

                source_timestamp = parse_timestamp(item.get("timestamp"))
                if source_timestamp is None:
                    errors.append("missing_or_invalid_timestamp")
                    stream["source_timestamps_valid"] = False
                else:
                    previous_timestamp = stream["last_source_timestamp"]
                    if previous_timestamp is not None and source_timestamp <= previous_timestamp:
                        errors.append("non_monotonic_timestamp")
                        stream["source_timestamps_valid"] = False
                    stream["last_source_timestamp"] = source_timestamp

                references = item.get("references", [])
                requires_references = source_type in {"artifact_sampled", "packet_verified"} or (
                    source_type == "packet_status_transition" and item.get("to_status") == "verified"
                )
                resolved_references, reference_errors = self.validate_production_references(references)
                if requires_references and not references:
                    reference_errors.append("required_references_empty")
                if reference_errors:
                    errors.extend(reference_errors)
                    stream["references_valid"] = False

                for error_name in errors:
                    stream["errors"].append(f"line {line_number}: {error_name}")
                stream["observed_line_count"] += 1
                self.emit(
                    "production_event_observed",
                    path=relative,
                    line_number=line_number,
                    line_sha256=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                    production_event_type=source_type,
                    production_event_seq=source_seq,
                    production_timestamp=item.get("timestamp"),
                    packet_id=packet_id,
                    referenced_paths=references,
                    resolved_references=resolved_references,
                    cross_check_valid=not errors,
                    validation_errors=errors,
                )
                if source_type == "artifact_sampled" or source_type == "packet_verified" or (
                    source_type == "packet_status_transition" and item.get("to_status") == "verified"
                ):
                    self.production_claims.append(
                        {
                            "packet_id": packet_id,
                            "claim_kind": "sampling" if source_type == "artifact_sampled" else "verification",
                            "source_path": relative,
                            "source_line": line_number,
                            "cross_check_valid": not errors,
                            "validation_errors": errors,
                            "resolved_references": resolved_references,
                        }
                    )
            stream["line_hashes"] = current_hashes
            self.production_lines_seen[relative] = len(lines)

    def validate_production_references(self, references: Any) -> tuple[list[dict[str, Any]], list[str]]:
        if not isinstance(references, list):
            return [], ["references_not_array"]
        resolved: list[dict[str, Any]] = []
        errors: list[str] = []
        for index, reference in enumerate(references):
            prefix = f"reference_{index}"
            if not isinstance(reference, dict):
                errors.append(f"{prefix}_not_object")
                continue
            raw_path = reference.get("path")
            if not isinstance(raw_path, str) or not raw_path.strip():
                errors.append(f"{prefix}_path_missing")
                continue
            candidate_input = Path(raw_path)
            if candidate_input.is_absolute():
                errors.append(f"{prefix}_path_not_relative")
                continue
            try:
                candidate = (self.output / candidate_input).resolve(strict=True)
            except (OSError, RuntimeError):
                errors.append(f"{prefix}_path_missing")
                continue
            if not is_relative_to(candidate, self.output) or not candidate.is_file():
                errors.append(f"{prefix}_path_outside_or_not_file")
                continue
            try:
                before = candidate.stat()
                observed_hash = sha256(candidate)
                after = candidate.stat()
            except OSError:
                errors.append(f"{prefix}_read_failed")
                continue
            if (
                (before.st_dev, before.st_ino) != (after.st_dev, after.st_ino)
                or before.st_size != after.st_size
                or before.st_mtime_ns != after.st_mtime_ns
            ):
                errors.append(f"{prefix}_changed_during_hash")
                continue
            declared_hash = reference.get("sha256")
            declared_revision = reference.get("revision")
            validation_kind: str | None = None
            if isinstance(declared_hash, str) and re.fullmatch(r"[0-9a-fA-F]{64}", declared_hash):
                if declared_hash.lower() != observed_hash:
                    errors.append(f"{prefix}_sha256_mismatch")
                    continue
                validation_kind = "sha256"
            elif isinstance(declared_revision, str) and declared_revision.strip():
                revision_check = self.validate_git_revision(candidate, declared_revision.strip(), observed_hash)
                if not revision_check["valid"]:
                    errors.append(f"{prefix}_{revision_check['error']}")
                    continue
                validation_kind = "git_revision"
            else:
                errors.append(f"{prefix}_hash_or_revision_missing")
                continue
            resolved.append(
                {
                    "path": candidate.relative_to(self.output).as_posix(),
                    "sha256": observed_hash,
                    "validation_kind": validation_kind,
                    "declared_revision": declared_revision if validation_kind == "git_revision" else None,
                }
            )
        return resolved, errors

    def validate_git_revision(self, candidate: Path, revision: str, observed_hash: str) -> dict[str, Any]:
        try:
            repo_relative = candidate.relative_to(self.repo).as_posix()
        except ValueError:
            return {"valid": False, "error": "revision_path_outside_repo"}
        revision_result = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "--verify", f"{revision}^{{commit}}"],
            capture_output=True,
            check=False,
        )
        if revision_result.returncode != 0:
            return {"valid": False, "error": "revision_invalid"}
        blob_result = subprocess.run(
            ["git", "-C", str(self.repo), "show", f"{revision}:{repo_relative}"],
            capture_output=True,
            check=False,
        )
        if blob_result.returncode != 0:
            return {"valid": False, "error": "revision_path_missing"}
        blob_hash = hashlib.sha256(blob_result.stdout).hexdigest()
        if blob_hash != observed_hash:
            return {"valid": False, "error": "revision_content_mismatch"}
        return {"valid": True, "error": None}

    def observe_control(self) -> None:
        if not self.control_file.exists():
            return
        raw_text = self.control_file.read_text(encoding="utf-8", errors="replace")
        lines = raw_text.splitlines()
        if raw_text and not raw_text.endswith(("\n", "\r")):
            lines = lines[:-1]
        current_hashes = [hashlib.sha256(line.encode("utf-8")).hexdigest() for line in lines]
        prefix_length = min(self.control_lines_seen, len(lines))
        prefix_changed = current_hashes[:prefix_length] != self.control_line_hashes[:prefix_length]
        truncated = len(lines) < self.control_lines_seen
        if (prefix_changed or truncated) and self.control_append_only_valid:
            self.control_append_only_valid = False
            self.emit(
                "runner_control_stream_mutation_observed",
                mutation="truncated" if truncated else "rewritten",
                previously_observed_lines=self.control_lines_seen,
                current_complete_lines=len(lines),
            )
            self.emit(
                "runner_control_rejected",
                request_event_seq=self.events[-1]["event_seq"],
                request_id=None,
                action="control_stream",
                packet_id=None,
                validation_errors=["control_stream_truncated" if truncated else "control_stream_rewritten"],
            )
        if not self.control_append_only_valid:
            return
        for line_number, raw in enumerate(lines[self.control_lines_seen :], start=self.control_lines_seen + 1):
            line_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            try:
                command = json.loads(raw)
            except json.JSONDecodeError as error:
                self.emit(
                    "runner_control_parse_error",
                    line_number=line_number,
                    line_sha256=line_hash,
                    error=str(error),
                )
                self.control_authentication_valid = False
                continue
            if not isinstance(command, dict):
                self.control_authentication_valid = False
                observed = self.emit_control_observed(line_number, line_hash, None, None, None, None)
                self.reject_control(observed, None, None, None, ["request_not_object"])
                continue
            request_id = command.get("request_id") if isinstance(command, dict) else None
            action = command.get("action") if isinstance(command, dict) else None
            packet_id = command.get("packet_id") if isinstance(command, dict) else None
            control_seq = command.get("control_seq")
            observed = self.emit_control_observed(
                line_number, line_hash, request_id, action, packet_id, control_seq
            )
            authentication_errors = self.authenticate_control(command)
            if authentication_errors:
                self.control_authentication_valid = False
                self.reject_control(observed, request_id, action, packet_id, authentication_errors)
                continue
            provided_hmac = command["hmac"].lower()
            self.control_last_seq = control_seq
            self.control_last_hmac = provided_hmac
            if not isinstance(request_id, str) or not request_id.strip():
                self.reject_control(observed, request_id, action, packet_id, ["request_id_missing"])
                continue
            if request_id in self.control_request_ids:
                self.reject_control(observed, request_id, action, packet_id, ["request_id_duplicate"])
                continue
            self.control_request_ids.add(request_id)
            if not isinstance(packet_id, str) or not PACKET_ID_RE.fullmatch(packet_id):
                self.reject_control(observed, request_id, action, packet_id, ["packet_id_invalid"])
                continue
            packet_id = packet_id.upper()
            if action == "sample":
                self.handle_sample(observed, request_id, packet_id, command.get("paths"))
            elif action == "verify":
                self.handle_verify(observed, request_id, packet_id, command.get("sample_request_id"))
            else:
                self.reject_control(observed, request_id, action, packet_id, ["action_invalid"])
        self.control_lines_seen = len(lines)
        self.control_line_hashes = current_hashes

    def authenticate_control(self, command: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        provided = command.get("hmac")
        control_seq = command.get("control_seq")
        previous_hmac = command.get("previous_hmac")
        if not isinstance(control_seq, int) or isinstance(control_seq, bool):
            errors.append("control_seq_invalid")
        elif control_seq != self.control_last_seq + 1:
            errors.append("control_seq_replayed_or_out_of_order")
        if previous_hmac != self.control_last_hmac:
            errors.append("previous_hmac_chain_mismatch")
        if not isinstance(provided, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", provided):
            errors.append("hmac_missing_or_invalid")
            return errors
        unsigned = {key: value for key, value in command.items() if key != "hmac"}
        canonical = json.dumps(
            unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        expected = hmac.new(self.control_secret, canonical, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(provided.lower(), expected):
            errors.append("hmac_authentication_failed")
        return errors

    def emit_control_observed(
        self,
        line_number: int,
        line_hash: str,
        request_id: Any,
        action: Any,
        packet_id: Any,
        control_seq: Any,
    ) -> dict[str, Any]:
        self.emit(
            "runner_control_request_observed",
            line_number=line_number,
            line_sha256=line_hash,
            request_id=request_id,
            action=action,
            packet_id=packet_id,
            control_seq=control_seq,
        )
        return self.events[-1]

    def reject_control(
        self,
        observed: dict[str, Any],
        request_id: Any,
        action: Any,
        packet_id: Any,
        errors: list[str],
    ) -> None:
        self.emit(
            "runner_control_rejected",
            request_event_seq=observed["event_seq"],
            request_id=request_id,
            action=action,
            packet_id=packet_id,
            validation_errors=errors,
        )

    def handle_sample(
        self,
        observed: dict[str, Any],
        request_id: str,
        packet_id: str,
        paths: Any,
    ) -> None:
        sampled_items, transition, errors = self.collect_canonical_packet_artifacts(
            packet_id, observed["event_seq"]
        )
        if paths is not None:
            supplied = paths if isinstance(paths, list) else []
            canonical_paths = [item["path"] for item in sampled_items]
            if supplied != canonical_paths:
                errors.append("paths_not_exact_canonical_manifest")
        if errors:
            self.reject_control(observed, request_id, "sample", packet_id, errors)
            return
        for item in sampled_items:
            self.emit(
                "runner_artifact_sampled",
                request_id=request_id,
                request_event_seq=observed["event_seq"],
                **item,
            )
        immutable_items = [item for item in sampled_items if item["path"] != "AGENT-STATE.md"]
        manifest_hash = hashlib.sha256(
            json.dumps(immutable_items, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        self.emit(
            "runner_sample_completed",
            request_id=request_id,
            request_event_seq=observed["event_seq"],
            packet_id=packet_id,
            sampled_paths=sampled_items,
            immutable_manifest_sha256=manifest_hash,
            state_transition_event_seq=transition["event_seq"],
            state_sha256=next(
                item["sha256"] for item in sampled_items if item["path"] == "AGENT-STATE.md"
            ),
            packet_row_sha256=transition["packet_row_sha256"],
        )
        self.samples[request_id] = self.events[-1]

    def collect_canonical_packet_artifacts(
        self, packet_id: str, before_event_seq: int
    ) -> tuple[list[dict[str, Any]], dict[str, Any] | None, list[str]]:
        errors: list[str] = []
        state_path = self.output / "AGENT-STATE.md"
        report_path = self.output / "reports" / f"{packet_id}-report.md"
        packet_evidence_root = self.output / "evidence" / packet_id
        containment_path = packet_evidence_root / "path-containment-postwrite.md"
        worker_evidence = []
        if packet_evidence_root.exists():
            worker_evidence = sorted(
                path
                for path in packet_evidence_root.rglob("*")
                if path.is_file()
                and path.name not in {
                    "preflight.md",
                    "path-containment-preflight.md",
                    "path-containment-postwrite.md",
                }
            )
        candidates = [state_path, report_path, *worker_evidence, containment_path]
        if not worker_evidence:
            errors.append("canonical_worker_evidence_missing")
        items: list[dict[str, Any]] = []
        for candidate in candidates:
            try:
                resolved = candidate.resolve(strict=True)
            except (OSError, RuntimeError):
                errors.append(f"canonical_artifact_missing:{candidate.relative_to(self.output).as_posix()}")
                continue
            if not is_relative_to(resolved, self.output) or not resolved.is_file():
                errors.append(f"canonical_artifact_outside_or_not_file:{candidate.name}")
                continue
            relative = resolved.relative_to(self.output).as_posix()
            size = resolved.stat().st_size
            if size == 0:
                errors.append(f"canonical_artifact_empty:{relative}")
                continue
            observed_hash = sha256(resolved)
            writes = [
                event
                for event in self.events
                if event.get("path") == relative
                and event.get("sha256") == observed_hash
                and event.get("event_type") in {"output_file_created", "output_file_modified"}
                and event["event_seq"] < before_event_seq
            ]
            if not writes:
                errors.append(f"canonical_artifact_write_not_observed:{relative}")
                continue
            items.append(
                {
                    "path": relative,
                    "sha256": observed_hash,
                    "size": size,
                    "role": classify_file(relative),
                    "packet_id": packet_id,
                    "observed_write_event_seq": writes[-1]["event_seq"],
                    "observed_write_mtime_ns": writes[-1]["mtime_ns"],
                }
            )
        expected_report = f"reports/{packet_id}-report.md"
        expected_containment = f"evidence/{packet_id}/path-containment-postwrite.md"
        if not any(
            item["path"] == expected_report and item["role"] == "worker_report" for item in items
        ):
            errors.append("canonical_worker_report_invalid")
        if not any(item["role"] == "worker_evidence" for item in items):
            errors.append("canonical_worker_evidence_invalid")
        if not any(
            item["path"] == expected_containment
            and item["role"] == "orchestrator_postwrite_containment"
            for item in items
        ):
            errors.append("canonical_postwrite_containment_invalid")
        transitions = [
            event
            for event in self.state_transitions.get(packet_id, [])
            if event.get("from_status") in ACTIVE_PACKET_STATUSES
            and event.get("to_status") == "verified"
            and event.get("state_epoch") == self.state_epoch
            and event["event_seq"] < before_event_seq
        ]
        transition = transitions[-1] if transitions else None
        if transition is None:
            errors.append("active_to_verified_state_transition_not_observed")
        else:
            later_row_events = [
                event
                for event in self.events
                if event.get("packet_id") == packet_id
                and event.get("state_epoch") == self.state_epoch
                and event["event_seq"] > transition["event_seq"]
                and event.get("event_type")
                in {
                    "runner_packet_state_row_updated",
                    "runner_packet_state_disappeared",
                    "runner_packet_state_transition_observed",
                }
            ]
            if later_row_events:
                errors.append("verified_transition_invalidated_by_later_packet_row_event")
        current_row = self.packet_rows.get(packet_id)
        if transition is not None and (current_row is None or current_row["status"] != "verified"):
            errors.append("current_packet_status_not_verified")
        elif transition is not None and items:
            state_item = next((item for item in items if item["path"] == "AGENT-STATE.md"), None)
            if state_item is None:
                errors.append("canonical_state_artifact_invalid")
            if current_row is None or current_row["row_sha256"] != transition["packet_row_sha256"]:
                errors.append("verified_packet_row_changed_after_transition")
            artifact_items = [item for item in items if item["path"] != "AGENT-STATE.md"]
            if any(
                item["observed_write_event_seq"] >= transition["state_write_event_seq"]
                or item["observed_write_mtime_ns"] >= transition["state_write_mtime_ns"]
                for item in artifact_items
            ):
                errors.append("canonical_artifacts_not_observed_before_state_transition")
        return items, transition, errors

    def handle_verify(
        self,
        observed: dict[str, Any],
        request_id: str,
        packet_id: str,
        sample_request_id: Any,
    ) -> None:
        errors: list[str] = []
        if not isinstance(sample_request_id, str) or sample_request_id not in self.samples:
            errors.append("accepted_sample_request_missing")
            sample = None
        else:
            sample = self.samples[sample_request_id]
        if sample is not None:
            if sample.get("packet_id") != packet_id:
                errors.append("sample_packet_mismatch")
            current_items, transition, current_errors = self.collect_canonical_packet_artifacts(
                packet_id, observed["event_seq"]
            )
            errors.extend(current_errors)
            current_immutable_items = [
                item for item in current_items if item["path"] != "AGENT-STATE.md"
            ]
            current_manifest = hashlib.sha256(
                json.dumps(current_immutable_items, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()
            if current_manifest != sample.get("immutable_manifest_sha256"):
                errors.append("canonical_manifest_changed_after_sample")
            if transition is None or transition["event_seq"] != sample.get("state_transition_event_seq"):
                errors.append("sample_not_bound_to_current_state_transition")
            if not (sample["event_seq"] < observed["event_seq"]):
                errors.append("sample_verify_order_invalid")
        if errors:
            self.reject_control(observed, request_id, "verify", packet_id, errors)
            return
        self.emit(
            "runner_verification_observed",
            request_id=request_id,
            request_event_seq=observed["event_seq"],
            packet_id=packet_id,
            sample_request_id=sample_request_id,
            sample_event_seq=sample["event_seq"],
            state_transition_event_seq=sample["state_transition_event_seq"],
            state_sha256=sample["state_sha256"],
            packet_row_sha256=sample["packet_row_sha256"],
            canonical_manifest_sha256=sample["immutable_manifest_sha256"],
            canonical_paths=sample["sampled_paths"],
            sampled_state_sha256=sample["state_sha256"],
            verified_state_sha256=next(
                item["sha256"] for item in current_items if item["path"] == "AGENT-STATE.md"
            ),
        )

    def production_cross_check_summary(self) -> dict[str, Any]:
        files: dict[str, Any] = {}
        for path, stream in self.production_streams.items():
            files[path] = {
                key: value.isoformat().replace("+00:00", "Z") if isinstance(value, datetime) else value
                for key, value in stream.items()
            }
            files[path]["valid"] = bool(
                stream["read_observation_complete"]
                and stream["parse_valid"]
                and stream["append_only_valid"]
                and stream["source_sequence_valid"]
                and stream["source_timestamps_valid"]
                and stream["references_valid"]
            )
        return {
            "files": files,
            "claims": self.production_claims,
            "boundary": "Production EVENTS claims are validated cross-checks only and never runner sampling or verification evidence.",
        }

    def lifecycle_summary(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        packet_ids = sorted({event.get("packet_id") for event in self.events if event.get("packet_id")})
        for packet_id in packet_ids:
            verified = next((e for e in self.events if e.get("packet_id") == packet_id and e["event_type"] == "runner_verification_observed"), None)
            sampled = next(
                (
                    e
                    for e in self.events
                    if verified
                    and e.get("packet_id") == packet_id
                    and e["event_type"] == "runner_sample_completed"
                    and e["event_seq"] == verified.get("sample_event_seq")
                ),
                None,
            )
            if verified is None:
                sampled = next(
                    (
                        e
                        for e in self.events
                        if e.get("packet_id") == packet_id
                        and e["event_type"] == "runner_sample_completed"
                    ),
                    None,
                )
            transition = None
            report_item = None
            evidence_items: list[dict[str, Any]] = []
            containment_item = None
            if sampled:
                transition = next(
                    (
                        e
                        for e in self.events
                        if e["event_seq"] == sampled.get("state_transition_event_seq")
                        and e.get("event_type") == "runner_packet_state_transition_observed"
                    ),
                    None,
                )
                report_item = next(
                    (item for item in sampled["sampled_paths"] if item["role"] == "worker_report"),
                    None,
                )
                evidence_items = [
                    item for item in sampled["sampled_paths"] if item["role"] == "worker_evidence"
                ]
                containment_item = next(
                    (
                        item
                        for item in sampled["sampled_paths"]
                        if item["role"] == "orchestrator_postwrite_containment"
                    ),
                    None,
                )
            artifacts_before_transition = bool(
                transition
                and report_item
                and evidence_items
                and containment_item
                and all(
                    item["observed_write_event_seq"] < transition["state_write_event_seq"]
                    and item["observed_write_mtime_ns"] < transition["state_write_mtime_ns"]
                    for item in [report_item, *evidence_items, containment_item]
                )
            )
            ordered = bool(
                artifacts_before_transition
                and sampled
                and verified
                and transition["event_seq"] < sampled["event_seq"] < verified["event_seq"]
                and self.control_append_only_valid
                and self.control_authentication_valid
            )
            result[packet_id] = {
                "report_write_event_seq": report_item["observed_write_event_seq"] if report_item else None,
                "evidence_write_event_seq": min(
                    (item["observed_write_event_seq"] for item in evidence_items), default=None
                ),
                "postwrite_containment_event_seq": (
                    containment_item["observed_write_event_seq"] if containment_item else None
                ),
                "active_to_verified_transition_event_seq": transition["event_seq"] if transition else None,
                "verified_state_write_event_seq": (
                    transition["state_write_event_seq"] if transition else None
                ),
                "containment_before_sampling": bool(
                    containment_item
                    and sampled
                    and containment_item["observed_write_event_seq"] < sampled["event_seq"]
                ),
                "sampling_event_seq": sampled["event_seq"] if sampled else None,
                "verified_event_seq": verified["event_seq"] if verified else None,
                "strictly_ordered": ordered,
                "note": "Strict order requires observer-hashed canonical artifacts, an earlier active-to-verified AGENT-STATE transition bound to the exact state hash, authenticated sampling, and an independent verification re-sample. Production EVENTS claims are cross-checks only.",
            }
        return result

    def finalize(self) -> None:
        self.observe_files()
        self.observe_production_events()
        self.observe_control()
        final_git = git_snapshot(self.repo)
        initial_untracked = set(self.initial_git["nonignored_untracked"]["stdout_lines"])
        final_untracked = set(final_git["nonignored_untracked"]["stdout_lines"])

        def runner_owned(relative: str) -> bool:
            absolute = (self.repo / relative).resolve()
            return absolute in {
                self.events_path,
                self.summary_path,
                self.control_file,
                self.stop_file,
            }

        new_untracked = sorted(final_untracked - initial_untracked)
        new_untracked_outside_output = [
            value
            for value in new_untracked
            if not is_relative_to((self.repo / value).resolve(), self.output) and not runner_owned(value)
        ]
        code_suffixes = {".c", ".cpp", ".go", ".java", ".js", ".jsx", ".py", ".rb", ".rs", ".swift", ".ts", ".tsx"}
        production_code_candidates = sorted(
            relative
            for relative in self.files
            if Path(relative).suffix.lower() in code_suffixes and "/evidence/" not in f"/{relative.lower()}" and "/prototypes/" not in f"/{relative.lower()}"
        )
        summary = {
            "schema": "runner-audit-v2",
            "created_at": utc_now(),
            "repo_root": str(self.repo),
            "assigned_output_root": str(self.output),
            "runner_audit_root": str(self.audit_dir),
            "initial_git": self.initial_git,
            "final_git": final_git,
            "tracked_head_unchanged": self.initial_git["head"] == final_git["head"],
            "tracked_status_unchanged": self.initial_git["tracked_status"]["stdout_lines"] == final_git["tracked_status"]["stdout_lines"],
            "created_or_final_output_files": sorted(self.files),
            "new_nonignored_untracked_outside_output": new_untracked_outside_output,
            "production_code_candidates_under_output": production_code_candidates,
            "lifecycle": self.lifecycle_summary(),
            "production_cross_checks": self.production_cross_check_summary(),
            "runner_control_integrity": {
                "authenticated_hmac_chain_valid": self.control_authentication_valid,
                "append_only_valid": self.control_append_only_valid,
                "accepted_control_count": self.control_last_seq,
                "secret_environment_variable": CONTROL_SECRET_ENV,
                "secret_persisted": False,
            },
            "observation_integrity": {
                "deferred_observation_count": self.deferred_file_observation_count,
                "unresolved_paths": [
                    {"path": path, "reason": reason}
                    for path, reason in sorted(self.deferred_file_observations.items())
                ],
                "unresolved_production_reads": [
                    {"path": path, "reason": reason}
                    for path, reason in sorted(self.production_read_deferred.items())
                ],
                "unresolved_secondary_reads": [
                    {"path": path, "reason": reason}
                    for path, reason in sorted(self.secondary_read_deferred.items())
                ],
                "complete_at_finalize": (
                    not self.deferred_file_observations
                    and not self.production_read_deferred
                    and not self.secondary_read_deferred
                ),
                "note": "A same-poll disappearance/change is deferred rather than treated as a stable byte sample; every defer/resolution is runner-owned evidence.",
            },
            "observation_scope": {
                "observed": [
                    "assigned output-root file creation/modification/deletion with SHA-256 and mtime",
                    "repository tracked HEAD and tracked status at runner start/end",
                    "repository nonignored untracked path set at runner start/end",
                    "production EVENTS.jsonl append lines as cross-check claims",
                    "HMAC-authenticated runner control requests and observer-owned canonical artifact reads/hashes",
                ],
                "unaudited": [
                    "network and remote service side effects",
                    "filesystem writes outside the repository/worktree",
                    "ignored paths outside the assigned output and runner-audit roots",
                    "credential stores, messages, publishing, purchases, deployments, and external process state",
                    "host-private tool transcripts and read syscalls outside explicit runner sample requests",
                ],
                "clean_claim_boundary": "Only observed scopes above are eligible for clean/no-change claims. Every listed external channel remains unaudited.",
            },
        }
        self.summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.emit("runner_finalized", summary_path=str(self.summary_path), summary_sha256=sha256(self.summary_path))

    def run(self) -> None:
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        if self.control_file.exists() and self.control_file.stat().st_size:
            raise SystemExit("control file must be absent or empty at runner start")
        self.events_path.write_text("", encoding="utf-8")
        self.emit(
            "runner_started",
            repo_root=str(self.repo),
            assigned_output_root=str(self.output),
            runner_control_file=str(self.control_file),
            runner_control_authentication="HMAC-SHA256 chained requests",
            initial_git_head=self.initial_git["head"],
            initial_tracked_status=self.initial_git["tracked_status"]["stdout_lines"],
        )
        while not self.stop_file.exists():
            self.observe_files()
            self.observe_production_events()
            self.observe_control()
            time.sleep(self.poll_seconds)
        self.emit("runner_stop_requested", stop_file=str(self.stop_file))
        self.finalize()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--audit-dir", type=Path, required=True)
    parser.add_argument("--stop-file", type=Path, required=True)
    parser.add_argument("--control-file", type=Path)
    parser.add_argument("--poll-ms", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo = args.repo.resolve()
    output = args.output_root.resolve()
    audit_dir = args.audit_dir.resolve()
    stop_file = args.stop_file.resolve()
    control_file = (args.control_file or (audit_dir / "runner-control.jsonl")).resolve()
    secret_value = os.environ.get(CONTROL_SECRET_ENV)
    if secret_value is None or len(secret_value.encode("utf-8")) < 32:
        raise SystemExit(f"{CONTROL_SECRET_ENV} must contain at least 32 UTF-8 bytes")
    if not is_relative_to(output, repo):
        raise SystemExit("output root must be inside repository/worktree")
    if not is_relative_to(audit_dir, repo):
        raise SystemExit("audit dir must be inside repository/worktree")
    if (
        is_relative_to(audit_dir, output)
        or is_relative_to(output, audit_dir)
        or audit_dir.parent != output.parent
    ):
        raise SystemExit("audit dir and output root must be physically disjoint siblings")
    if stop_file.parent != audit_dir:
        raise SystemExit("stop file must be directly inside audit dir")
    if control_file.parent != audit_dir or control_file == stop_file:
        raise SystemExit("control file must be distinct and directly inside audit dir")
    if args.poll_ms < 20:
        raise SystemExit("poll interval must be at least 20 ms")
    Audit(
        repo,
        output,
        audit_dir,
        stop_file,
        control_file,
        secret_value.encode("utf-8"),
        args.poll_ms,
    ).run()


if __name__ == "__main__":
    main()
