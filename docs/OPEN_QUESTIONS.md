# Open Questions

Questions here need repository-owner input. They do not block work that can use
a reversible default.

## Awaiting input

1. **Orchestrator repository name:** Should the extracted application be named
   `agent-orchestrator`, `opencode-orchestrator`, or something else? Design
   references use `agent-orchestrator` provisionally.
2. **Deployment mode:** Should local targets ultimately default to copied files
   with backups or managed symlinks? The provisional default is copy-with-backup
   with symlinks available per target.
3. **Topology sensitivity:** May the private repository track home-lab IP
   addresses as well as DNS names, or should committed topology use DNS names
   only? The provisional design prefers DNS and permits IPs in a tracked private
   environment overlay.
4. **Personal agents:** Should the Jessica and other personally identifying
   Hermes profiles live in this private repository, or should they remain in a
   separate ignored/private overlay?
5. **Copilot scope:** Should deployment manage selected global VS Code settings,
   or only repository instructions, prompt files, agents, and MCP definitions?
   The provisional scope excludes general editor settings.
6. **Grok scope:** Should Grok Build use the same MCP registry and common skills
   as the other CLIs immediately, or first receive only instructions and agents?
   The provisional design supports the full adapter.
7. **Cross-repository contract:** Should Ansible consume a released workflows
   archive, a checked-out path, or a Git URL/revision when installing Hermes?

## Resolved

- The orchestrator application will live in its own repository.
- Shared agentic content belongs in tool-agnostic directories with native
  exceptions in tool-specific directories.
- General-purpose Python and other utilities belong under `tools/`; helpers
  exclusive to one skill stay with that skill.
- Secret locations and variable names may be documented, but secret values may
  not be committed.
