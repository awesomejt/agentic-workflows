# Grok Build Adapter

This adapter targets the locally installed Grok Build CLI. It deploys global
`AGENTS.md`, common Agent Skills, a focused-task prompt, and composed Markdown
agent definitions beneath `GROK_HOME`.

Grok Build 0.2.14 has a discovery distinction worth preserving in tests:
skills honor `GROK_HOME`, while user agent lookup follows
`$HOME/.grok/agents`. A normal deployment uses that default location and works
as expected. When validating in an isolated staging directory, set `HOME` to a
fake home containing `.grok`, rather than setting only `GROK_HOME`.

The adapter does not replace `config.toml`, which may contain authentication,
models, UI preferences, plugins, or runtime settings. The non-secret desired
fragment is recorded as `config.workflows.toml.example`.

Merge MCP servers safely with Grok's CLI:

```bash
grok mcp add qdrant --url https://mcp-qdrant.taylor.lan/mcp
grok mcp add searxng --url https://mcp-searxng.taylor.lan/mcp
grok mcp list --json
```

Grok-managed `auth.json`, MCP OAuth credentials, sessions, memory, logs,
downloads, and active-session state remain unmanaged.
