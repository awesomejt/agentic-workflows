#!/usr/bin/env python3
"""Atomic flat-file implementation of the project-state/v1 contract."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import sys
import tempfile
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

CONTRACT = "project-state/v1"
OUTCOMES = {"completed", "partial", "blocked", "failed", "aborted"}
DEFAULT_PHASES = ("discovery", "design", "implementation", "testing", "review")


class StateError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        retryable: bool = False,
        current_revision: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.current_revision = current_revision
        self.details = details or {}

    def payload(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": str(self),
            "retryable": self.retryable,
            "current_revision": self.current_revision,
            "details": self.details,
        }


def now() -> datetime:
    return datetime.now(UTC)


def timestamp(value: datetime | None = None) -> str:
    return (value or now()).isoformat()


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def new_id() -> str:
    return str(uuid.uuid4())


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


@contextmanager
def state_lock(path: Path, *, exclusive: bool) -> Iterator[None]:
    lock_path = path.with_name(f"{path.name}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def load_state(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise StateError("not_found", f"State file does not exist: {path}")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StateError("validation_error", f"Cannot read valid state: {exc}") from exc
    if not isinstance(state, dict) or state.get("contract_version") != CONTRACT:
        raise StateError("validation_error", f"State must use {CONTRACT}")
    if not isinstance(state.get("revision"), int):
        raise StateError("validation_error", "State revision must be an integer")
    return state


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state, indent=2, sort_keys=True) + "\n"
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def task_by_ref(state: dict[str, Any], reference: str) -> dict[str, Any]:
    for task in state["tasks"]:
        if task["id"] == reference or task["task_key"] == reference:
            return task
    raise StateError("not_found", f"Task not found: {reference}")


def pass_by_ref(state: dict[str, Any], reference: str) -> dict[str, Any]:
    for record in state["passes"]:
        if record["id"] == reference:
            return record
    raise StateError("not_found", f"Pass not found: {reference}")


def phase_by_ref(state: dict[str, Any], reference: str) -> dict[str, Any]:
    for phase in state["phases"]:
        if phase["id"] == reference or phase["phase_key"] == reference:
            return phase
    raise StateError("not_found", f"Phase not found: {reference}")


def dependency_ready(state: dict[str, Any], task: dict[str, Any]) -> bool:
    predecessors = [
        relationship["predecessor_task_ref"]
        for relationship in state["relationships"]
        if relationship["successor_task_ref"] == task["id"]
        and relationship["relationship"] == "blocks"
    ]
    return all(
        task_by_ref(state, predecessor)["status"] == "completed"
        for predecessor in predecessors
    )


def snapshot(state: dict[str, Any]) -> dict[str, Any]:
    current_time = now()
    active_passes: list[dict[str, Any]] = []
    stale_passes: list[dict[str, Any]] = []
    for record in state["passes"]:
        if record["status"] != "active":
            continue
        expiry = parse_timestamp(record.get("lease_expires_at"))
        (stale_passes if expiry and expiry <= current_time else active_passes).append(
            record
        )

    active_task_ids = {record["task_ref"] for record in active_passes}
    working_without_lease = [
        task
        for task in state["tasks"]
        if task["status"] == "working" and task["id"] not in active_task_ids
    ]
    current_phase = next(
        (phase for phase in state["phases"] if phase["status"] == "active"), None
    )
    eligible = [
        task
        for task in state["tasks"]
        if task["status"] == "pending"
        and current_phase is not None
        and task["phase"] == current_phase["phase_key"]
        and dependency_ready(state, task)
    ]
    eligible.sort(key=lambda item: (-item["priority"], item["created_at"], item["id"]))
    blocked = [task for task in state["tasks"] if task["status"] == "blocked"]
    warnings: list[str] = []
    limit = state["project"]["concurrency_limit"]
    if len(active_passes) > limit:
        warnings.append("Active pass count exceeds project concurrency limit")

    if warnings:
        action = "reconcile_multiple_active"
    elif stale_passes:
        action = "recover_stale_task"
    elif active_passes:
        action = "resume_active"
    elif working_without_lease:
        action = "recover_stale_task"
    elif eligible:
        action = "select_new_task"
    elif blocked:
        action = "resolve_blocker"
    elif current_phase and any(
        task["phase"] == current_phase["phase_key"] for task in state["tasks"]
    ):
        action = "complete_phase"
    elif all(phase["status"] in {"completed", "skipped"} for phase in state["phases"]):
        action = "complete_project"
    else:
        action = "no_work"

    latest_pass = max(state["passes"], key=lambda item: item["sequence"], default=None)
    counts: dict[str, int] = {}
    for task in state["tasks"]:
        counts[task["status"]] = counts.get(task["status"], 0) + 1
    return {
        "contract_version": CONTRACT,
        "snapshot_at": timestamp(current_time),
        "revision": state["revision"],
        "project": state["project"],
        "current_phase": current_phase,
        "phases": state["phases"],
        "active_tasks": [
            task for task in state["tasks"] if task["id"] in active_task_ids
        ],
        "working_tasks_without_active_lease": working_without_lease,
        "active_passes": active_passes,
        "stale_passes": stale_passes,
        "blocked_tasks": blocked,
        "eligible_tasks": eligible,
        "latest_pass": latest_pass,
        "queue_counts": {
            "by_status": counts,
            "total": len(state["tasks"]),
            "active_passes": len(active_passes),
            "stale_passes": len(stale_passes),
            "eligible": len(eligible),
            "blocked": len(blocked),
        },
        "warnings": warnings,
        "recommended_action": action,
    }


def require_input(request: dict[str, Any]) -> dict[str, Any]:
    value = request.get("input")
    if not isinstance(value, dict):
        raise StateError("validation_error", "Request input must be an object")
    return value


def handle_start(state: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    view = snapshot(state)
    if view["warnings"]:
        raise StateError("reconciliation_required", view["warnings"][0])
    if view["stale_passes"]:
        raise StateError(
            "recovery_required", "Recover stale passes before starting work"
        )
    if len(view["active_passes"]) >= state["project"]["concurrency_limit"]:
        raise StateError("concurrency_limit", "Project already has an active pass")

    data = require_input(request)
    working = view["working_tasks_without_active_lease"]
    explicit = data.get("task_ref")
    if working:
        if explicit and explicit not in {item["id"] for item in working} | {
            item["task_key"] for item in working
        }:
            raise StateError("recovery_required", "Resume working task before new work")
        task = task_by_ref(state, explicit) if explicit else working[0]
    else:
        task = (
            task_by_ref(state, explicit)
            if explicit
            else (view["eligible_tasks"][0] if view["eligible_tasks"] else None)
        )
        if task is None:
            raise StateError(
                "task_not_eligible", "No dependency-ready task is available"
            )
        if task not in view["eligible_tasks"]:
            raise StateError("task_not_eligible", f"Task is not eligible: {task['id']}")

    objective = str(data.get("objective", "")).strip()
    if not objective:
        raise StateError("validation_error", "start_pass requires input.objective")
    lease_seconds = int(data.get("lease_seconds", 1800))
    if lease_seconds <= 0:
        raise StateError("validation_error", "lease_seconds must be positive")

    started = now()
    sequence = max((item["sequence"] for item in state["passes"]), default=0) + 1
    record = {
        "id": new_id(),
        "sequence": sequence,
        "task_ref": task["id"],
        "phase_ref": phase_by_ref(state, task["phase"])["id"],
        "actor": request["actor"],
        "status": "active",
        "outcome": None,
        "objective": objective,
        "summary": None,
        "handoff": None,
        "validation_result": None,
        "evidence": {},
        "participants": [],
        "blocker": None,
        "execution_record": data.get("execution_record") or {},
        "started_at": timestamp(started),
        "last_heartbeat_at": None,
        "completed_at": None,
        "lease_expires_at": timestamp(started + timedelta(seconds=lease_seconds)),
        "lease_version": 1,
    }
    state["passes"].append(record)
    task["status"] = "working"
    task["active_pass_ref"] = record["id"]
    task["updated_at"] = timestamp(started)
    state["project"]["status"] = "working"
    state["project"]["updated_at"] = timestamp(started)
    return {"pass": record, "task": task}


def handle_heartbeat(state: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    data = require_input(request)
    record = pass_by_ref(state, str(data.get("pass_ref", "")))
    if record["status"] != "active":
        raise StateError("lease_conflict", "Pass is not active")
    if record["actor"] != request["actor"]:
        raise StateError("lease_conflict", "Actor does not own this pass")
    expected_lease = int(data.get("lease_version", 0))
    if record["lease_version"] != expected_lease:
        raise StateError(
            "lease_conflict",
            "Pass lease version changed",
            retryable=True,
            details={"current_lease_version": record["lease_version"]},
        )
    expiry = parse_timestamp(record.get("lease_expires_at"))
    if expiry and expiry <= now():
        raise StateError("lease_conflict", "Pass lease has expired")
    lease_seconds = int(data.get("lease_seconds", 1800))
    current_time = now()
    record["lease_version"] += 1
    record["last_heartbeat_at"] = timestamp(current_time)
    record["lease_expires_at"] = timestamp(
        current_time + timedelta(seconds=lease_seconds)
    )
    return {"pass": record}


def handle_finish(state: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    data = require_input(request)
    record = pass_by_ref(state, str(data.get("pass_ref", "")))
    if record["status"] != "active":
        raise StateError("lease_conflict", "Pass is not active")
    if record["actor"] != request["actor"]:
        raise StateError("lease_conflict", "Actor does not own this pass")
    expiry = parse_timestamp(record.get("lease_expires_at"))
    if expiry and expiry <= now():
        raise StateError("lease_conflict", "Pass lease has expired")

    outcome = str(data.get("outcome", ""))
    if outcome not in OUTCOMES:
        raise StateError("validation_error", f"Invalid outcome: {outcome}")
    summary = str(data.get("summary", "")).strip()
    handoff = str(data.get("handoff", "")).strip() or None
    blocker = data.get("blocker")
    if not summary:
        raise StateError("validation_error", "finish_pass requires input.summary")
    if outcome in {"partial", "failed", "aborted"} and not handoff:
        raise StateError("validation_error", f"{outcome} requires a handoff")
    if outcome == "blocked" and (
        not isinstance(blocker, dict) or not str(blocker.get("reason", "")).strip()
    ):
        raise StateError("validation_error", "blocked requires blocker.reason")

    task = task_by_ref(state, record["task_ref"])
    completed = now()
    record.update(
        {
            "status": (
                "failed"
                if outcome == "failed"
                else "aborted"
                if outcome == "aborted"
                else "completed"
            ),
            "outcome": outcome,
            "summary": summary,
            "handoff": handoff,
            "validation_result": data.get("validation_result"),
            "evidence": data.get("evidence") or {},
            "participants": data.get("participants") or [],
            "blocker": blocker,
            "completed_at": timestamp(completed),
            "lease_expires_at": None,
        }
    )
    task["active_pass_ref"] = None
    task["updated_at"] = timestamp(completed)
    if outcome == "completed":
        task["status"] = "completed"
        task["completed_at"] = timestamp(completed)
    elif outcome == "blocked":
        task["status"] = "blocked"
        task["blockers"].append(
            {
                "id": new_id(),
                "reason": str(blocker["reason"]).strip(),
                "blocker_type": blocker.get("blocker_type", "other"),
                "reference": blocker.get("reference"),
                "related_task_ref": blocker.get("related_task_ref"),
                "created_at": timestamp(completed),
                "resolved_at": None,
                "resolution_evidence": None,
            }
        )
    else:
        task["status"] = "working"

    remaining_runnable = any(
        item["status"] in {"pending", "working"} for item in state["tasks"]
    )
    state["project"]["status"] = (
        "active"
        if remaining_runnable
        else "blocked"
        if any(item["status"] == "blocked" for item in state["tasks"])
        else "active"
    )
    state["project"]["updated_at"] = timestamp(completed)
    return {"pass": record, "task": task}


def handle_recover(state: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    view = snapshot(state)
    stale = view["stale_passes"]
    if len(stale) > state["project"]["concurrency_limit"]:
        raise StateError(
            "reconciliation_required", "Too many stale passes for automatic recovery"
        )
    recovered: list[str] = []
    recovered_at = now()
    for record in stale:
        record.update(
            {
                "status": "failed",
                "outcome": "failed",
                "summary": "Recovered an expired flat-file pass lease.",
                "handoff": "Inspect pass handoffs and retry the same working task.",
                "completed_at": timestamp(recovered_at),
                "lease_expires_at": None,
            }
        )
        task = task_by_ref(state, record["task_ref"])
        task["status"] = "working"
        task["active_pass_ref"] = None
        task["updated_at"] = timestamp(recovered_at)
        recovered.append(record["id"])
    state["project"]["status"] = "active"
    state["project"]["updated_at"] = timestamp(recovered_at)
    return {"recovered_pass_refs": recovered}


def handle_create_task(
    state: dict[str, Any], request: dict[str, Any]
) -> dict[str, Any]:
    data = require_input(request)
    task_key = str(data.get("task_key", "")).strip()
    title = str(data.get("title", "")).strip()
    phase = str(data.get("phase", "")).strip()
    if not task_key or not title or not phase:
        raise StateError(
            "validation_error", "create_task requires task_key, title, and phase"
        )
    if any(item["task_key"] == task_key for item in state["tasks"]):
        raise StateError("validation_error", f"Duplicate task_key: {task_key}")
    phase_by_ref(state, phase)
    created = now()
    task = {
        "id": new_id(),
        "task_key": task_key,
        "title": title,
        "description": data.get("description"),
        "phase": phase,
        "role": data.get("role", "orchestrator"),
        "priority": int(data.get("priority", 50)),
        "model_tier": data.get("model_tier"),
        "validation_expectations": data.get("validation_expectations"),
        "status": "pending",
        "active_pass_ref": None,
        "blockers": [],
        "created_at": timestamp(created),
        "updated_at": timestamp(created),
        "completed_at": None,
    }
    state["tasks"].append(task)
    return {"task": task}


def path_exists(state: dict[str, Any], start: str, destination: str) -> bool:
    edges: dict[str, set[str]] = {}
    for relationship in state["relationships"]:
        if relationship["relationship"] == "blocks":
            edges.setdefault(relationship["predecessor_task_ref"], set()).add(
                relationship["successor_task_ref"]
            )
    pending = [start]
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current == destination:
            return True
        if current in visited:
            continue
        visited.add(current)
        pending.extend(edges.get(current, set()))
    return False


def handle_add_dependency(
    state: dict[str, Any], request: dict[str, Any]
) -> dict[str, Any]:
    data = require_input(request)
    predecessor = task_by_ref(state, str(data.get("predecessor_task_ref", "")))
    successor = task_by_ref(state, str(data.get("successor_task_ref", "")))
    relationship_type = str(data.get("relationship", "blocks"))
    if relationship_type != "blocks":
        raise StateError("validation_error", "Only blocks relationships are supported")
    if predecessor["id"] == successor["id"] or path_exists(
        state, successor["id"], predecessor["id"]
    ):
        raise StateError("validation_error", "Dependency would create a cycle")
    relationship = {
        "predecessor_task_ref": predecessor["id"],
        "successor_task_ref": successor["id"],
        "relationship": relationship_type,
    }
    if relationship not in state["relationships"]:
        state["relationships"].append(relationship)
    return {"relationship": relationship}


def handle_resolve_blocker(
    state: dict[str, Any], request: dict[str, Any]
) -> dict[str, Any]:
    data = require_input(request)
    task = task_by_ref(state, str(data.get("task_ref", "")))
    blocker_ref = str(data.get("blocker_ref", "")).strip()
    evidence = str(data.get("evidence", "")).strip()
    if not blocker_ref or not evidence:
        raise StateError(
            "validation_error", "resolve_blocker requires blocker_ref and evidence"
        )
    blocker = next(
        (item for item in task["blockers"] if item["id"] == blocker_ref), None
    )
    if blocker is None:
        raise StateError("not_found", f"Blocker not found: {blocker_ref}")
    if blocker["resolved_at"]:
        raise StateError("validation_error", "Blocker is already resolved")
    resolved = now()
    blocker["resolved_at"] = timestamp(resolved)
    blocker["resolution_evidence"] = evidence
    if not any(item["resolved_at"] is None for item in task["blockers"]):
        task["status"] = "pending"
    task["updated_at"] = timestamp(resolved)
    state["project"]["status"] = "active"
    state["project"]["updated_at"] = timestamp(resolved)
    return {"task": task, "blocker": blocker}


def handle_update_phase(
    state: dict[str, Any], request: dict[str, Any]
) -> dict[str, Any]:
    data = require_input(request)
    phase = phase_by_ref(state, str(data.get("phase_ref", "")))
    phase_version = int(data.get("phase_version", 0))
    if phase["version"] != phase_version:
        raise StateError(
            "state_conflict",
            "Phase version changed",
            retryable=True,
            details={"current_phase_version": phase["version"]},
        )
    transition = str(data.get("transition", ""))
    evidence = data.get("evidence") or {}
    reason = str(data.get("reason", "")).strip() or None
    override = str(data.get("override_reason", "")).strip() or None
    changed = now()

    if transition == "activate":
        other = next(
            (
                item
                for item in state["phases"]
                if item["status"] == "active" and item["id"] != phase["id"]
            ),
            None,
        )
        if other:
            raise StateError(
                "validation_error", f"Phase already active: {other['phase_key']}"
            )
        if phase["status"] != "pending":
            raise StateError("validation_error", "Only pending phases may activate")
        phase["status"] = "active"
        phase["started_at"] = timestamp(changed)
    elif transition == "block":
        if not reason:
            raise StateError("validation_error", "Blocking a phase requires reason")
        phase["status"] = "blocked"
        phase["reason"] = reason
    elif transition in {"complete", "skip"}:
        if not evidence:
            raise StateError("validation_error", f"{transition} requires evidence")
        if transition == "skip" and not reason:
            raise StateError("validation_error", "Skipping a phase requires reason")
        incomplete = [
            task
            for task in state["tasks"]
            if task["phase"] == phase["phase_key"]
            and task["status"] not in {"completed", "rejected", "duplicate"}
        ]
        if transition == "complete" and incomplete and not override:
            raise StateError(
                "validation_error",
                "Phase has incomplete tasks; provide override_reason only when authorized",
            )
        phase["status"] = "completed" if transition == "complete" else "skipped"
        phase["completed_at"] = timestamp(changed)
        phase["reason"] = override or reason
        phase["completion_pass_ref"] = data.get("completion_pass_ref")
        next_phase = next(
            (
                item
                for item in sorted(state["phases"], key=lambda value: value["ordinal"])
                if item["ordinal"] > phase["ordinal"] and item["status"] == "pending"
            ),
            None,
        )
        if next_phase:
            next_phase["status"] = "active"
            next_phase["started_at"] = timestamp(changed)
            next_phase["version"] += 1
    else:
        raise StateError("validation_error", f"Invalid phase transition: {transition}")

    phase["version"] += 1
    phase["evidence"] = evidence
    state["project"]["updated_at"] = timestamp(changed)
    return {"phase": phase}


HANDLERS = {
    "start_pass": handle_start,
    "heartbeat_pass": handle_heartbeat,
    "finish_pass": handle_finish,
    "recover_project": handle_recover,
    "create_task": handle_create_task,
    "add_dependency": handle_add_dependency,
    "resolve_blocker": handle_resolve_blocker,
    "update_phase": handle_update_phase,
}


def read_request(path: str) -> dict[str, Any]:
    try:
        text = (
            sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        )
        request = json.loads(text)
    except (OSError, json.JSONDecodeError) as exc:
        raise StateError(
            "validation_error", f"Cannot read request JSON: {exc}"
        ) from exc
    if not isinstance(request, dict):
        raise StateError("validation_error", "Request must be an object")
    return request


def validate_envelope(
    state: dict[str, Any], request: dict[str, Any], operation: str
) -> tuple[str, str]:
    if request.get("contract_version") != CONTRACT:
        raise StateError("validation_error", f"Request must use {CONTRACT}")
    if request.get("project_ref") != state["project"]["project_ref"]:
        raise StateError("not_found", "Request project_ref does not match state")
    actor = str(request.get("actor", "")).strip()
    request_id = str(request.get("request_id", "")).strip()
    if not actor or not request_id:
        raise StateError("validation_error", "actor and request_id are required")
    fingerprint = hashlib.sha256(
        json.dumps(
            {"operation": operation, "request": request},
            separators=(",", ":"),
            sort_keys=True,
        ).encode()
    ).hexdigest()
    return request_id, fingerprint


def apply_operation(path: Path, operation: str, request_path: str) -> dict[str, Any]:
    request = read_request(request_path)
    with state_lock(path, exclusive=True):
        state = load_state(path)
        request_id, fingerprint = validate_envelope(state, request, operation)
        previous = state["idempotency"].get(request_id)
        if previous:
            if previous["fingerprint"] != fingerprint:
                raise StateError(
                    "validation_error", "request_id was reused with different input"
                )
            return previous["response"]

        expected = request.get("expected_revision")
        if not isinstance(expected, int):
            raise StateError("validation_error", "expected_revision is required")
        if expected != state["revision"]:
            raise StateError(
                "state_conflict",
                "Project state changed; inspect before retrying",
                retryable=True,
                current_revision=state["revision"],
            )

        try:
            data = HANDLERS[operation](state, request)
        except StateError as exc:
            if exc.current_revision is None:
                exc.current_revision = state["revision"]
            raise
        state["revision"] += 1
        response = {
            "contract_version": CONTRACT,
            "operation": operation,
            "revision": state["revision"],
            "data": data,
            "snapshot": snapshot(state),
        }
        state["idempotency"][request_id] = {
            "fingerprint": fingerprint,
            "response": response,
        }
        while len(state["idempotency"]) > 100:
            del state["idempotency"][next(iter(state["idempotency"]))]
        write_state(path, state)
        return response


def initialize(path: Path, args: argparse.Namespace) -> dict[str, Any]:
    phases = tuple(item.strip() for item in args.phases.split(",") if item.strip())
    if not phases:
        raise StateError("validation_error", "At least one phase is required")
    created = now()
    with state_lock(path, exclusive=True):
        if path.exists():
            raise StateError("validation_error", f"State file already exists: {path}")
        state = {
            "contract_version": CONTRACT,
            "revision": 1,
            "project": {
                "project_ref": args.project_ref,
                "status": "active",
                "workflow_id": args.workflow_id,
                "workflow_version": args.workflow_version,
                "concurrency_limit": args.concurrency_limit,
                "created_at": timestamp(created),
                "updated_at": timestamp(created),
            },
            "phases": [
                {
                    "id": new_id(),
                    "phase_key": name,
                    "name": name.replace("-", " ").title(),
                    "ordinal": index,
                    "status": "active" if index == 1 else "pending",
                    "version": 1,
                    "evidence": {},
                    "reason": None,
                    "started_at": timestamp(created) if index == 1 else None,
                    "completed_at": None,
                    "completion_pass_ref": None,
                }
                for index, name in enumerate(phases, 1)
            ],
            "tasks": [],
            "relationships": [],
            "passes": [],
            "idempotency": {},
        }
        write_state(path, state)
        return snapshot(state)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--file", type=Path, default=Path("project.yaml"))
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Create a new project state file")
    init.add_argument("--project-ref", required=True)
    init.add_argument("--workflow-id", required=True)
    init.add_argument("--workflow-version", default="1")
    init.add_argument("--concurrency-limit", type=int, default=1)
    init.add_argument("--phases", default=",".join(DEFAULT_PHASES))

    commands.add_parser("inspect", help="Read one coordination snapshot")
    apply = commands.add_parser("apply", help="Apply one project-state operation")
    apply.add_argument("operation", choices=tuple(HANDLERS))
    apply.add_argument("--request-file", default="-")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            if args.concurrency_limit <= 0:
                raise StateError(
                    "validation_error", "concurrency_limit must be positive"
                )
            result = initialize(args.file, args)
        elif args.command == "inspect":
            with state_lock(args.file, exclusive=False):
                result = snapshot(load_state(args.file))
        else:
            result = apply_operation(args.file, args.operation, args.request_file)
        emit(result)
        return 0
    except StateError as exc:
        emit({"error": exc.payload()})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
