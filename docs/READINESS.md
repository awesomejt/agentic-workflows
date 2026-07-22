# Migration Readiness Report

Date: 2026-07-22

## Outcome

The repository is ready for per-tool dry-run review and staged cutover. It is
not approved for a one-shot live deployment because nine existing files would
be updated and two external security/configuration findings remain unresolved.
No live configuration was changed during this audit.

## Validation evidence

- `workflowctl validate`: 23 documents, 7 sources, 11 services, 2 MCP servers,
  and 11 secret references validated.
- Unit/integration tests: 12 passed.
- Workstation render: 87 managed files.
- Hermes render: 30 bundle files.
- Isolated-home deployment: 87 files installed by copy.
- Isolated-home audit: 87 clean, 0 drifted or missing.
- OpenCode 1.18.4: 11 managed agents discovered (two primary, nine subagents).
- Grok Build 0.2.14: nine custom agents and six custom skills discovered.
- Claude Code 2.1.206: isolated doctor exited successfully; its warnings were
  expected because the fake home contained configuration but no installation or
  authentication.
- Codex CLI 0.145.0: custom TOML and the selected `workflows` profile parse;
  `codex mcp list` still reports base configuration only, as documented in the
  adapter.
- JSON, TOML, YAML, Markdown frontmatter, Python bytecode compilation, and shell
  syntax checks passed.
- Targeted credential-pattern scan found no matching committed value. No
  dedicated secret-scanning CLI was installed, so contract validation provides
  an additional guard by rejecting credential-bearing keys.

## Live read-only comparison

A hash-only comparison against current workstation destinations found 78 new
files and nine updates:

- OpenCode: 12 new, eight updates.
- Codex: 17 new.
- Claude Code: 16 new.
- Grok Build: 17 new.
- Copilot/VS Code: 16 new, one update.

The existing update paths are eight OpenCode agent definitions and VS Code's
`mcp.json`. Their content was not printed during the audit. Review those diffs
locally before deployment; VS Code's MCP document is the highest-risk collision
because it may contain unrelated server definitions.

## Staged cutover

1. Resolve or accept the open decisions in `docs/OPEN_QUESTIONS.md`.
2. Remove and rotate the source credential documented in
   `docs/SECURITY_FINDINGS.md`.
3. Resolve the missing Ollama embedding-model seed in Ansible.
4. Review OpenCode's eight content diffs, then deploy only after confirming the
   normalized agents supersede the installed versions.
5. Merge or back up VS Code `mcp.json`; do not replace unrelated MCP servers.
6. Deploy the workstation with copy-with-backup and immediately run the drift
   audit and native discovery checks.
7. Merge native MCP entries for Claude, Grok, and Codex as documented by their
   adapters.
8. Choose the Hermes Ansible delivery mechanism, render the bundle, and validate
   the consuming playbook before changing the host.
9. Extract the orchestrator after its repository name is chosen.

Rollback uses the timestamped deployment backups and the prior scheduler command
for the orchestrator. Keep `opencode-setup` and `hermes-setup` intact until their
respective cutovers have passed acceptance checks.
