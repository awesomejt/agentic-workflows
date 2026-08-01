# GitHub Copilot and VS Code Adapter

The adapter deploys personal instruction files, common Agent Skills, composed
custom agents, and the VS Code user-profile `mcp.json` from one target rooted at
the user's home directory.

Two primary Chat agents, `Software Development Loop` and `Content Creation
Loop`, carry bounded lists of the custom agents they may invoke. Their bodies
come from common prompts, while Copilot-specific delegation metadata remains in
this adapter. The standalone `Orchestrator` agent is available for other stage
graphs.

Managed locations are:

- `~/.copilot/instructions/`
- `~/.copilot/skills/`
- `~/.copilot/agents/`
- `~/.copilot/workflows/`
- the active VS Code profile's default user `mcp.json` location on this Linux
  workstation

The MCP file contains only non-secret remote HTTP endpoints. Review its dry-run
diff if the selected VS Code profile already has other servers; the current
deployer replaces that one managed file rather than merging arbitrary JSON.

Copilot authentication, IDE locks, extension state, chat history, memory, and
general VS Code settings are not managed.
