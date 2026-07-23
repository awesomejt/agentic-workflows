from __future__ import annotations

import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

import yaml

SOURCE_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SOURCE_ROOT / "tools" / "workflowctl" / "src"))

from workflowctl.engine import render_target  # noqa: E402


def frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path} has no YAML frontmatter")
    _, header, body = text.split("---", 2)
    if not body.strip():
        raise AssertionError(f"{path} has no prompt body")
    parsed = yaml.safe_load(header)
    if not isinstance(parsed, dict):
        raise AssertionError(f"{path} frontmatter is not a mapping")
    return parsed


class AdapterRenderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.temp = Path(self.temporary.name)
        self.workstation = self.temp / "workstation"
        self.hermes = self.temp / "hermes"
        render_target(SOURCE_ROOT, "workstation", self.workstation)
        render_target(SOURCE_ROOT, "hermes", self.hermes)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_json_configuration_is_valid(self) -> None:
        for path in (
            self.workstation / "opencode" / "opencode.workflows.json",
            self.workstation / "copilot" / ".config" / "Code" / "User" / "mcp.json",
        ):
            with self.subTest(path=path):
                parsed = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(parsed, dict)

    def test_codex_configuration_is_valid_toml(self) -> None:
        paths = [self.workstation / "codex" / "workflows.config.toml"]
        paths.extend(sorted((self.workstation / "codex" / "agents").glob("*.toml")))
        self.assertEqual(len(paths), 14)
        for path in paths:
            with self.subTest(path=path):
                parsed = tomllib.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(parsed, dict)

    def test_markdown_agent_frontmatter_is_valid(self) -> None:
        patterns = (
            self.workstation / "opencode" / "agents" / "*.md",
            self.workstation / "claude" / "agents" / "*.md",
            self.workstation / "grok" / "agents" / "*.md",
            self.workstation / "copilot" / ".copilot" / "agents" / "*.agent.md",
        )
        counts = []
        for pattern in patterns:
            paths = sorted(pattern.parent.glob(pattern.name))
            counts.append(len(paths))
            for path in paths:
                with self.subTest(path=path):
                    metadata = frontmatter(path)
                    self.assertIsInstance(metadata.get("description"), str)
        self.assertEqual(counts, [17, 13, 13, 15])

    def test_opencode_concrete_model_overrides_are_rendered(self) -> None:
        agents = self.workstation / "opencode" / "agents"
        for name in ("orchestrator.md", "implementer.md", "awb-orchestrator.md", "afk-build.md"):
            with self.subTest(name=name):
                metadata = frontmatter(agents / name)
                self.assertEqual(metadata.get("model"), "ollama-direct/local-coding")
        self.assertNotIn("model", frontmatter(agents / "planner.md"))

    def test_copilot_loop_agents_have_bounded_subagent_catalogs(self) -> None:
        agents = self.workstation / "copilot" / ".copilot" / "agents"
        for name in ("software-loop.agent.md", "content-loop.agent.md"):
            with self.subTest(name=name):
                metadata = frontmatter(agents / name)
                self.assertIsInstance(metadata.get("agents"), list)
                self.assertNotIn("*", metadata["agents"])

    def test_reset_safe_workflows_are_deployed_to_each_cli(self) -> None:
        roots = (
            self.workstation / "opencode" / "workflows",
            self.workstation / "codex" / "workflows",
            self.workstation / "claude" / "workflows",
            self.workstation / "grok" / "workflows",
            self.workstation / "copilot" / ".copilot" / "workflows",
        )
        for root in roots:
            with self.subTest(root=root):
                self.assertTrue((root / "protocol.md").is_file())
                self.assertTrue((root / "software-development.yaml").is_file())
                self.assertTrue((root / "content-creation.yaml").is_file())

    def test_common_skills_are_present_for_each_cli(self) -> None:
        roots = (
            self.workstation / "opencode" / "skills",
            self.workstation / "codex" / "skills",
            self.workstation / "claude" / "skills",
            self.workstation / "grok" / "skills",
            self.workstation / "copilot" / ".copilot" / "skills",
        )
        for root in roots:
            with self.subTest(root=root):
                self.assertEqual(len(list(root.glob("*/SKILL.md"))), 6)

    def test_hermes_bundle_contracts_are_valid_yaml(self) -> None:
        paths = (
            self.hermes / "hermes" / "hermes" / "profiles.yaml",
            self.hermes / "hermes" / "hermes" / "ansible-contract.yaml",
            self.hermes / "hermes" / "services" / "litellm" / "contract.yaml",
            self.hermes / "hermes" / "services" / "ollama" / "contract.yaml",
            self.hermes / "hermes" / "services" / "mcp" / "registry.yaml",
            self.hermes / "hermes" / "services" / "omlx" / "contract.yaml",
            self.hermes / "hermes" / "services" / "open-webui" / "contract.yaml",
        )
        for path in paths:
            with self.subTest(path=path):
                parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
                self.assertIsInstance(parsed, dict)


if __name__ == "__main__":
    unittest.main()
