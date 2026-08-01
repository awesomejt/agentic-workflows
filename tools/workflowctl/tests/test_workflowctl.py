from __future__ import annotations

import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SOURCE_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SOURCE_ROOT / "tools" / "workflowctl" / "src"))

from workflowctl.cli import _emit  # noqa: E402
from workflowctl.config import WorkflowError, validate_repository  # noqa: E402
from workflowctl.engine import (  # noqa: E402
    audit_target,
    deploy_target,
    render_target,
)


class WorkflowctlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.temp = Path(self.temporary.name)
        self.repo = self.temp / "repo"
        shutil.copytree(
            SOURCE_ROOT,
            self.repo,
            ignore=shutil.ignore_patterns(".git", ".build", "__pycache__", ".pytest_cache"),
        )
        (self.repo / "authoring" / "adapters" / "opencode" / "fixture.txt").write_text(
            "managed content\n", encoding="utf-8"
        )
        (self.repo / "authoring" / "adapters" / "opencode" / "header.txt").write_text(
            "header\n", encoding="utf-8"
        )
        (self.repo / "authoring" / "adapters" / "opencode" / "footer.txt").write_text(
            "footer\n", encoding="utf-8"
        )
        (self.repo / "authoring" / "adapters" / "opencode" / "deploy.yaml").write_text(
            """schema_version: 1
id: opencode
description: Test adapter.
status: active
artifacts:
  - source: authoring/adapters/opencode/fixture.txt
    destination: fixture.txt
  - source: authoring/adapters/opencode/fixture.txt
    destination: wrapped.txt
    header: authoring/adapters/opencode/header.txt
    footer: authoring/adapters/opencode/footer.txt
""",
            encoding="utf-8",
        )
        (self.repo / "source" / "targets" / "workstation.yaml").write_text(
            """schema_version: 1
id: workstation
description: Isolated workflowctl test target.
kind: local
environment: home-lab
deployment:
  mode: copy
  backup_root: ${XDG_STATE_HOME}/agentic-workflows/backups
  state_root: ${XDG_STATE_HOME}/agentic-workflows
adapters:
  - id: opencode
    enabled: true
    destination: ${XDG_CONFIG_HOME}/opencode
""",
            encoding="utf-8",
        )
        self.home = self.temp / "home"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_repository_validates(self) -> None:
        messages = validate_repository(self.repo)
        self.assertTrue(any(message.startswith("validated ") for message in messages))

    def test_service_contract_rejects_embedded_credential_key(self) -> None:
        contract = self.repo / "source" / "services" / "litellm" / "contract.yaml"
        contract.write_text(contract.read_text(encoding="utf-8") + "api_key: forbidden\n")
        with self.assertRaisesRegex(WorkflowError, "forbidden credential key"):
            validate_repository(self.repo)

    def test_workflow_rejects_unknown_role(self) -> None:
        workflow = self.repo / "authoring" / "common" / "workflows" / "software-development.yaml"
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "role: designer", "role: imaginary-specialist", 1
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(WorkflowError, "unknown role: imaginary-specialist"):
            validate_repository(self.repo)

    def test_workflow_rejects_unknown_transition(self) -> None:
        workflow = self.repo / "authoring" / "common" / "workflows" / "content-creation.yaml"
        workflow.write_text(
            workflow.read_text(encoding="utf-8").replace(
                "on_success: scope", "on_success: missing-stage", 1
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(WorkflowError, "unknown on_success: missing-stage"):
            validate_repository(self.repo)

    def test_routing_rejects_unknown_role(self) -> None:
        routing = self.repo / "authoring" / "adapters" / "opencode" / "routing.yaml"
        routing.write_text(
            routing.read_text(encoding="utf-8").replace(
                "role: implementer", "role: imaginary-specialist", 1
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(WorkflowError, "role routing opencode has unknown role"):
            validate_repository(self.repo)

    def test_render_creates_manifest_and_file(self) -> None:
        output = self.temp / "rendered"
        manifest = render_target(self.repo, "workstation", output)
        self.assertEqual(manifest["target"], "workstation")
        self.assertEqual(len(manifest["files"]), 2)
        self.assertEqual((output / "opencode" / "fixture.txt").read_text(), "managed content\n")
        self.assertEqual(
            (output / "opencode" / "wrapped.txt").read_text(),
            "header\nmanaged content\nfooter\n",
        )
        self.assertTrue((output / ".workflow-manifest.json").is_file())

    def test_dry_run_does_not_write_destination(self) -> None:
        result = deploy_target(
            self.repo,
            "workstation",
            home=self.home,
            output=self.temp / "dry-render",
            dry_run=True,
        )
        self.assertEqual(result["changes"][0]["status"], "create")
        self.assertFalse((self.home / ".config" / "opencode" / "fixture.txt").exists())

    def test_deploy_backup_and_audit(self) -> None:
        destination = self.home / ".config" / "opencode" / "fixture.txt"
        destination.parent.mkdir(parents=True)
        destination.write_text("unmanaged content\n", encoding="utf-8")

        result = deploy_target(
            self.repo,
            "workstation",
            home=self.home,
            output=self.temp / "live-render",
        )
        self.assertEqual(destination.read_text(), "managed content\n")
        self.assertTrue(Path(result["state"]).is_file())
        backups = list((self.home / ".local" / "state" / "agentic-workflows" / "backups").rglob("fixture.txt"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "unmanaged content\n")
        self.assertTrue(
            all(item["status"] == "clean" for item in audit_target(self.repo, "workstation", self.home))
        )

        destination.write_text("drift\n", encoding="utf-8")
        audit = audit_target(self.repo, "workstation", self.home)
        self.assertEqual(next(item for item in audit if item["destination"] == str(destination))["status"], "drifted")

    def test_state_manifest_contains_no_file_content(self) -> None:
        result = deploy_target(
            self.repo,
            "workstation",
            home=self.home,
            output=self.temp / "state-render",
        )
        state = json.loads(Path(result["state"]).read_text())
        self.assertNotIn("content", state["files"][0])

    def test_human_output_summarizes_structured_lists(self) -> None:
        output = io.StringIO()
        with mock.patch("sys.stdout", output):
            _emit({"files": [{"path": "one"}, {"path": "two"}]}, False)
        self.assertEqual(output.getvalue(), "files: 2 entries\n")


if __name__ == "__main__":
    unittest.main()
