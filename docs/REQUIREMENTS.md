# Requirements

## Purpose

Provide one version-controlled repository for reusable agentic configuration
and a safe, repeatable way to deploy it to local CLI tools and Hermes.

## Functional requirements

### Content management

1. Store tool-agnostic instructions, prompts, roles, personas, and Agent Skills.
2. Store tool-specific configuration and exceptions for OpenCode, Codex,
   Claude Code, Grok Build, GitHub Copilot/VS Code, and Hermes.
3. Preserve provenance for imported and third-party content.
4. Support private or ignored overlays for personal content that should not be
   shared with the repository.

### Service configuration

5. Describe MCP servers once and render supported client formats.
6. Record non-secret client contracts for LiteLLM, Ollama, oMLX, Qdrant,
   SearXNG, Open WebUI, and related network AI services.
7. Link service records to the owning Ansible playbook or role.
8. Record secret purpose and retrieval metadata without storing secret values.

### Deployment

9. Validate source configuration and references before rendering.
10. Render deterministic target trees for supported tools.
11. Show changes before deployment and support a no-write dry run.
12. Back up overwritten files and use atomic writes.
13. Support copied files by default and optional managed symlinks.
14. Record deployed hashes and report drift.
15. Produce a Hermes bundle for installation by Ansible.
16. Provide diagnostics that test configuration and non-destructive service
    health without exposing credentials.

### Migration and traceability

17. Implement each roadmap task in a separate commit.
18. Maintain design decisions, task state, open questions, and migration
    provenance in the repository.
19. Preserve compatibility aliases during role-name normalization where useful.

## Non-functional requirements

- A fresh clone must contain no secret values or private runtime state.
- Rendering must be deterministic for the same repository revision and inputs.
- Deployment must be idempotent and must not silently overwrite unmanaged data.
- YAML, JSON, JSONC, TOML, and Markdown output must use tool-native schemas.
- Python tooling should have minimal dependencies and run on maintained Python
  versions available on the workstation and Hermes hosts.
- Errors should identify the source record and remediation without printing
  resolved credentials.

## Out of scope

- Installing or operating AI network services; Ansible owns that work.
- Scheduling agents, leasing tasks, or supervising execution; the future
  orchestrator repository owns that work.
- Synchronizing transcripts, model caches, memory databases, OAuth tokens, or
  other runtime state.
- Vendoring complete third-party skill catalogs.

## Acceptance criteria

The initial migration is complete when:

1. All supported targets validate and render from a clean clone.
2. Dry-run deployment works for every local adapter.
3. Deployment to an isolated temporary home is covered by automated tests.
4. Hermes produces a versioned bundle with an Ansible handoff document.
5. MCP definitions render for each supported client without embedded secrets.
6. The source inventory accounts for every reviewed reusable asset as migrated,
   referenced, intentionally private, superseded, or deferred.
7. A secret scan and end-to-end audit pass without unresolved high-risk items.
