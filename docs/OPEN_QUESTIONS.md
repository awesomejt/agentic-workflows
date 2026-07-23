# Open Questions

Questions here need repository-owner input. They do not block work that can use
a reversible default.

## Awaiting input

1. **Personal agents:** After Jessica and Rachel have established usage, should
   their profiles remain inside the existing Hermes setup or move to a separate
   private overlay repository?
2. **Cross-repository contract:** Should Ansible consume a released workflows
   archive, a checked-out path, or a Git URL/revision when installing Hermes?
   The recommendation is a pinned Git tag or commit rendered on the Ansible
   controller, with a checksummed release bundle as a future alternative.
3. **OpenCode server identity:** What DNS name, Proxmox guest type, and Ansible
   inventory group should own the future dedicated OpenCode worker?

## Resolved

- The orchestrator application will live in its own repository.
- The repository is `~/projects/dev/agent-orchestrator` with remote
  `awesomejt/agent-orchestrator`.
- Local CLI deployment uses copy-with-backup into each user's normal home and
  XDG paths. Symlinks remain an opt-in development mode.
- Committed topology uses stable DNS names. Only the Ansible controller
  (`192.168.50.11`) and DNS server (`192.168.50.53`) use literal addresses.
- Jessica and Rachel remain isolated in the existing Hermes instance for now.
- Copilot scope is custom agents, subagents, loop prompts, shared skills, and MCP;
  general editor configuration remains unmanaged.
- Shared agentic content belongs in tool-agnostic directories with native
  exceptions in tool-specific directories.
- General-purpose Python and other utilities belong under `tools/`; helpers
  exclusive to one skill stay with that skill.
- Secret locations and variable names may be documented, but secret values may
  not be committed.
- Grok Build receives the common instructions, roles, skills, prompt, and MCP
  registry rather than a reduced first-stage adapter.
