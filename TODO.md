# Roadmap

This file tracks repository-level implementation work. Checkboxes represent
commit-sized tasks; each completed task should correspond to one focused
commit. Detailed discoveries and decisions belong in `MEMORY.md`.

## Foundation

- [x] Establish requirements, architecture, repository rules, memory, and open
  questions.
- [ ] Add schemas, manifests, targets, service registry, and secret-reference
  catalog.
- [ ] Implement and test `workflowctl` validation, rendering, diff, deployment,
  audit, and diagnostics.

## Content migration

- [ ] Inventory reusable assets with provenance and sensitivity classifications.
- [ ] Normalize common agent roles and prompts from `opencode-setup`.
- [ ] Import reusable skills after reviewing tool coupling and provenance.
- [ ] Add project and course template bundles.
- [ ] Add private-overlay guidance for personal Hermes personas and workflows.

## Tool adapters

- [ ] Add OpenCode adapter and migrate the existing deployment safely.
- [ ] Add Codex adapter.
- [ ] Add Claude Code adapter.
- [ ] Add Grok Build adapter.
- [ ] Add GitHub Copilot/VS Code adapter.
- [ ] Add Hermes bundle adapter and Ansible handoff contract.

## Services and operations

- [ ] Add canonical MCP server registry and per-tool renderers.
- [ ] Add LiteLLM, Ollama, oMLX, Qdrant, SearXNG, and Open WebUI contracts.
- [ ] Add non-secret home-lab topology and health checks.
- [ ] Add end-to-end dry-run and drift/audit documentation.
- [ ] Extract the current orchestrator into its own repository.
