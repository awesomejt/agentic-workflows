# Roadmap

This file tracks repository-level implementation work. Checkboxes represent
commit-sized tasks; each completed task should correspond to one focused
commit. Detailed discoveries and decisions belong in `MEMORY.md`.

## Foundation

- [x] Establish requirements, architecture, repository rules, memory, and open
  questions.
- [x] Add schemas, manifests, targets, service registry, and secret-reference
  catalog.
- [x] Implement and test `workflowctl` validation, rendering, diff, deployment,
  audit, and diagnostics.
- [x] Complete an isolated deployment, native CLI discovery checks, live
  hash-only comparison, and migration readiness report.

## Content migration

- [x] Inventory reusable assets with provenance and sensitivity classifications.
- [x] Normalize common agent roles and prompts from `opencode-setup`.
- [x] Import reusable skills after reviewing tool coupling and provenance.
- [ ] Add project and course template bundles.
- [x] Add private-overlay guidance for personal Hermes personas and workflows.

## Tool adapters

- [x] Add OpenCode adapter and migrate the existing deployment safely.
- [x] Add Codex adapter.
- [x] Add Claude Code adapter.
- [x] Add Grok Build adapter.
- [x] Add GitHub Copilot/VS Code adapter.
- [x] Add Hermes bundle adapter and Ansible handoff contract.

## Services and operations

- [x] Add canonical MCP server registry and per-tool renderers.
- [x] Add LiteLLM, Ollama, oMLX, Qdrant, SearXNG, Open WebUI, AnythingLLM,
  and n8n contracts.
- [x] Add non-secret home-lab topology and health checks.
- [x] Add end-to-end dry-run and drift/audit documentation.
- [ ] Extract the current orchestrator into its own repository.

## Discovered follow-up

- [ ] Remove and rotate the plaintext oMLX credential found in
  `hermes-setup/AGENTS.md`; retain only the Vault reference.
- [ ] Add `nomic-embed-text:latest` to the Ansible Ollama pull list or remove
  the stale AnythingLLM/Hermes consumer requirement.
- [ ] Implement `workflowctl template render` and promote the revision-pinned
  template catalog entries from `normalize` to `ready`.
- [ ] Decide the orchestrator repository name and run the history-preserving
  extraction plan.
