from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SOURCE_ROOT / "tools" / "workflowctl" / "src"))

from workflowctl.config import validate_repository  # noqa: E402
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
        (self.repo / "opencode" / "fixture.txt").write_text("managed content\n", encoding="utf-8")
        (self.repo / "opencode" / "deploy.yaml").write_text(
            """schema_version: 1
id: opencode
description: Test adapter.
status: active
artifacts:
  - source: opencode/fixture.txt
    destination: fixture.txt
""",
            encoding="utf-8",
        )
        self.home = self.temp / "home"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_repository_validates(self) -> None:
        messages = validate_repository(self.repo)
        self.assertTrue(any(message.startswith("validated ") for message in messages))

    def test_render_creates_manifest_and_file(self) -> None:
        output = self.temp / "rendered"
        manifest = render_target(self.repo, "workstation", output)
        self.assertEqual(manifest["target"], "workstation")
        self.assertEqual(len(manifest["files"]), 1)
        self.assertEqual((output / "opencode" / "fixture.txt").read_text(), "managed content\n")
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
        self.assertEqual(audit_target(self.repo, "workstation", self.home)[0]["status"], "clean")

        destination.write_text("drift\n", encoding="utf-8")
        self.assertEqual(audit_target(self.repo, "workstation", self.home)[0]["status"], "drifted")

    def test_state_manifest_contains_no_file_content(self) -> None:
        result = deploy_target(
            self.repo,
            "workstation",
            home=self.home,
            output=self.temp / "state-render",
        )
        state = json.loads(Path(result["state"]).read_text())
        self.assertNotIn("content", state["files"][0])


if __name__ == "__main__":
    unittest.main()
