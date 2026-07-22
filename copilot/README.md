# GitHub Copilot and VS Code Adapter

The adapter deploys personal instruction files, common Agent Skills, composed
custom agents, and the VS Code user-profile `mcp.json` from one target rooted at
the user's home directory.

Managed locations are:

- `~/.copilot/instructions/`
- `~/.copilot/skills/`
- `~/.copilot/agents/`
- the active VS Code profile's default user `mcp.json` location on this Linux
  workstation

The MCP file contains only non-secret remote HTTP endpoints. Review its dry-run
diff if the selected VS Code profile already has other servers; the current
deployer replaces that one managed file rather than merging arbitrary JSON.

Copilot authentication, IDE locks, extension state, chat history, memory, and
general VS Code settings are not managed.
