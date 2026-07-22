# Tool Adapter Guide

Every active adapter maps canonical files from `common/` into a tool's native
layout. `workflowctl` composes tool-specific headers and footers during render,
so shared role bodies do not need to be duplicated.

## Managed surfaces

| Adapter | Managed content | Deliberately unmanaged |
| --- | --- | --- |
| OpenCode | `AGENTS.md`, roles, two primary agents, skills, prompt, optional config overlay | provider credentials, live model/provider config, sessions |
| Codex | `AGENTS.md`, standalone agent TOML, skills, `workflows` profile | base `config.toml`, `auth.json`, history, trust and runtime state |
| Claude Code | `CLAUDE.md`, Markdown subagents, skills | settings, plugins, `.claude.json`, OAuth and credentials |
| Grok Build | `AGENTS.md`, Markdown agents, skills, prompt | base config, auth, MCP OAuth, sessions, memory and logs |
| Copilot/VS Code | personal instructions, agents, skills, VS Code MCP file | extension auth/state, chat history, general editor settings |
| Hermes | versioned behavior and client-contract bundle | host installation, services, secrets and runtime state |

The VS Code MCP file is the one intentionally managed monolithic file. Always
review its dry-run diff because deployment replaces that JSON document after
backing it up. Other state-bearing base configuration files are represented by
tracked overlays, examples, or CLI merge commands instead of being overwritten.

## Validation

```bash
bin/workflowctl validate
python -m unittest discover -s tools/workflowctl/tests -v
bin/workflowctl render --target workstation
bin/workflowctl render --target hermes
```

Native smoke checks can be run against the staged workstation tree without
using live credentials. OpenCode loads its catalog from an isolated
`XDG_CONFIG_HOME`; Grok requires a fake `HOME/.grok` path for agent discovery.
Codex validates the tracked profile when selected with `--profile workflows`.

## Deployment sequence

1. Render and inspect the complete target.
2. Run `bin/workflowctl diff --target workstation --content`.
3. Resolve any collision with an unmanaged file, especially VS Code `mcp.json`.
4. Run `./deploy.sh --dry-run` and save the summary as review evidence.
5. Deploy with the default copy-with-backup mode.
6. Merge MCP entries for Claude, Grok, or Codex with their native CLI where the
   adapter README specifies it.
7. Run `bin/workflowctl audit --target workstation` and native tool discovery
   checks.

Hermes stops after rendering. Hand the bundle to Ansible using
`hermes/ansible-contract.yaml`; do not copy it directly to the host.
