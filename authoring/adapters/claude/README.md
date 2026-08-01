# Claude Code Adapter

The adapter safely deploys additive files beneath `~/.claude`: global
`CLAUDE.md`, common Agent Skills and workflows, and composed custom subagents. It intentionally
does not deploy `settings.json`, `.claude.json`, credentials, OAuth state, or
managed plugin state.

The orchestrator agent may delegate and maintain `.agents/loop/` state. Read-only
specialists return their handoff for the orchestrator to record rather than
receiving broad workspace write access.

`settings.base.json` records a reviewed non-secret baseline but is not deployed
because replacing the live settings file could remove existing permissions,
hooks, or plugins.

Claude stores user-scoped MCP definitions in a state-bearing global file. Add
the tracked remote servers with the installed CLI so Claude merges them safely:

```bash
claude mcp add --transport http --scope user qdrant https://mcp-qdrant.taylor.lan/mcp
claude mcp add --transport http --scope user searxng https://mcp-searxng.taylor.lan/mcp
```

Run `claude mcp list` afterward. These commands do not embed credentials; any
future authenticated server should use the tool's supported environment or
OAuth mechanism rather than a committed token.
