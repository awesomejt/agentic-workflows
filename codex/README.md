# Codex Adapter

The adapter deploys global `AGENTS.md`, common Agent Skills, composed standalone
custom-agent TOML files, and `workflows.config.toml`.

The profile file is deliberately separate from the live `config.toml`, which
may contain trusted-project state, provider configuration, hooks, plugins, or
local permission decisions. Select the tracked profile explicitly:

```bash
codex --profile workflows
```

The profile enables multi-agent operation and the non-secret Qdrant and SearXNG
MCP endpoints. It does not set a model, provider, authentication value, approval
policy, or global sandbox mode.

Codex CLI 0.145.0 parses the separate profile, but `codex mcp list` currently
reports only the base configuration in this environment. If runtime profile
MCP discovery is not visible after an upgrade, merge the same tracked endpoints
into the base config with the native CLI:

```bash
codex mcp add qdrant --url https://mcp-qdrant.taylor.lan/mcp
codex mcp add searxng --url https://mcp-searxng.taylor.lan/mcp
```

The CLI merge preserves unrelated base configuration. Reapply the tracked tool
approval modes afterward if those policy settings are required in the base
layer.

Codex authentication remains tool-managed in `auth.json`; `workflowctl` never
reads, renders, or deploys that file.
