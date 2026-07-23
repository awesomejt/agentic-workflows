from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = (
    SOURCE_ROOT
    / "common"
    / "skills"
    / "project-yaml-state-management"
    / "scripts"
    / "project_state.py"
)


class ProjectYamlStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.state = Path(self.temporary.name) / "project.yaml"
        self.invoke(
            "init",
            "--project-ref",
            "example",
            "--workflow-id",
            "software-development",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def invoke(
        self,
        *arguments: str,
        request: dict[str, object] | None = None,
        check: bool = True,
    ) -> dict[str, object]:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--file", str(self.state), *arguments],
            input=json.dumps(request) if request is not None else None,
            text=True,
            capture_output=True,
            check=False,
        )
        if check and completed.returncode != 0:
            self.fail(completed.stdout or completed.stderr)
        if not check:
            self.assertEqual(completed.returncode, 2)
        return json.loads(completed.stdout)

    def request(
        self,
        request_id: str,
        revision: int,
        input_value: dict[str, object],
    ) -> dict[str, object]:
        return {
            "contract_version": "project-state/v1",
            "project_ref": "example",
            "actor": "test-runner",
            "request_id": request_id,
            "expected_revision": revision,
            "input": input_value,
        }

    def apply(
        self,
        operation: str,
        request_id: str,
        revision: int,
        input_value: dict[str, object],
        *,
        check: bool = True,
    ) -> dict[str, object]:
        return self.invoke(
            "apply",
            operation,
            "--request-file",
            "-",
            request=self.request(request_id, revision, input_value),
            check=check,
        )

    def test_partial_pass_resumes_before_dependent_task(self) -> None:
        first = self.apply(
            "create_task",
            "create-plan",
            1,
            {
                "task_key": "plan",
                "title": "Plan change",
                "phase": "discovery",
                "priority": 80,
            },
        )
        second = self.apply(
            "create_task",
            "create-implement",
            2,
            {
                "task_key": "implement",
                "title": "Implement change",
                "phase": "discovery",
                "priority": 90,
            },
        )
        dependency = self.apply(
            "add_dependency",
            "dependency",
            3,
            {
                "predecessor_task_ref": "plan",
                "successor_task_ref": "implement",
                "relationship": "blocks",
            },
        )
        self.assertEqual(
            dependency["snapshot"]["eligible_tasks"][0]["task_key"], "plan"
        )

        started = self.apply(
            "start_pass",
            "start-plan",
            4,
            {"objective": "Plan the change", "lease_seconds": 300},
        )
        pass_ref = started["data"]["pass"]["id"]
        heartbeat = self.apply(
            "heartbeat_pass",
            "heartbeat-plan",
            5,
            {
                "pass_ref": pass_ref,
                "lease_version": 1,
                "lease_seconds": 300,
            },
        )
        self.assertEqual(heartbeat["data"]["pass"]["lease_version"], 2)
        partial = self.apply(
            "finish_pass",
            "partial-plan",
            6,
            {
                "pass_ref": pass_ref,
                "outcome": "partial",
                "summary": "Plan partially complete",
                "handoff": "Finish dependency analysis",
            },
        )
        self.assertEqual(
            partial["snapshot"]["recommended_action"], "recover_stale_task"
        )

        resumed = self.apply(
            "start_pass",
            "resume-plan",
            7,
            {"objective": "Finish the plan"},
        )
        self.assertEqual(resumed["data"]["task"]["task_key"], "plan")
        completed = self.apply(
            "finish_pass",
            "complete-plan",
            8,
            {
                "pass_ref": resumed["data"]["pass"]["id"],
                "outcome": "completed",
                "summary": "Plan complete",
                "evidence": {"checks": ["dependency graph reviewed"]},
            },
        )
        self.assertEqual(
            completed["snapshot"]["eligible_tasks"][0]["task_key"], "implement"
        )
        self.assertEqual(first["revision"], 2)
        self.assertEqual(second["revision"], 3)

    def test_conflict_cycle_and_idempotent_replay_are_safe(self) -> None:
        request = self.request(
            "create-a",
            1,
            {"task_key": "a", "title": "A", "phase": "discovery"},
        )
        created = self.invoke(
            "apply", "create_task", "--request-file", "-", request=request
        )
        replay = self.invoke(
            "apply", "create_task", "--request-file", "-", request=request
        )
        self.assertEqual(created, replay)

        conflict = self.apply(
            "create_task",
            "stale",
            1,
            {"task_key": "stale", "title": "Stale", "phase": "discovery"},
            check=False,
        )
        self.assertEqual(conflict["error"]["code"], "state_conflict")

        self.apply(
            "create_task",
            "create-b",
            2,
            {"task_key": "b", "title": "B", "phase": "discovery"},
        )
        self.apply(
            "add_dependency",
            "a-blocks-b",
            3,
            {
                "predecessor_task_ref": "a",
                "successor_task_ref": "b",
                "relationship": "blocks",
            },
        )
        cycle = self.apply(
            "add_dependency",
            "b-blocks-a",
            4,
            {
                "predecessor_task_ref": "b",
                "successor_task_ref": "a",
                "relationship": "blocks",
            },
            check=False,
        )
        self.assertEqual(cycle["error"]["code"], "validation_error")
        self.assertEqual(self.invoke("inspect")["revision"], 4)

    def test_phase_completion_requires_evidence_and_completed_tasks(self) -> None:
        missing_evidence = self.apply(
            "update_phase",
            "phase-no-evidence",
            1,
            {
                "phase_ref": "discovery",
                "phase_version": 1,
                "transition": "complete",
            },
            check=False,
        )
        self.assertEqual(missing_evidence["error"]["code"], "validation_error")

        completed = self.apply(
            "update_phase",
            "phase-complete",
            1,
            {
                "phase_ref": "discovery",
                "phase_version": 1,
                "transition": "complete",
                "evidence": {"checks": ["scope approved"]},
            },
        )
        self.assertEqual(completed["snapshot"]["current_phase"]["phase_key"], "design")

    def test_structured_blocker_can_be_resolved_with_evidence(self) -> None:
        self.apply(
            "create_task",
            "create-blocked",
            1,
            {"task_key": "blocked", "title": "Blocked task", "phase": "discovery"},
        )
        started = self.apply(
            "start_pass",
            "start-blocked",
            2,
            {"objective": "Discover a blocker"},
        )
        blocked = self.apply(
            "finish_pass",
            "finish-blocked",
            3,
            {
                "pass_ref": started["data"]["pass"]["id"],
                "outcome": "blocked",
                "summary": "External decision required",
                "blocker": {"reason": "Need an owner decision"},
            },
        )
        task = blocked["data"]["task"]
        blocker = task["blockers"][0]
        self.assertEqual(blocked["snapshot"]["recommended_action"], "resolve_blocker")

        resolved = self.apply(
            "resolve_blocker",
            "resolve-blocked",
            4,
            {
                "task_ref": task["id"],
                "blocker_ref": blocker["id"],
                "evidence": "Owner approved option A",
            },
        )
        self.assertEqual(resolved["data"]["task"]["status"], "pending")
        self.assertEqual(resolved["snapshot"]["recommended_action"], "select_new_task")


if __name__ == "__main__":
    unittest.main()
