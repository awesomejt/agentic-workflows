# Project Memory

Durable decisions, constraints, and session summaries live here. Task status
belongs in `TODO.md`; detailed runtime transcripts do not belong in Git.

## Decisions

### 2026-07-22: Repository responsibility

- `agentic-workflows` is the declarative source of truth for reusable agent
  behavior, tool adapters, deployment targets, and client-facing service
  contracts.
- `infra/ansible` remains authoritative for installing and configuring network
  services such as LiteLLM, Ollama, Open WebUI, Qdrant, SearXNG, and Hermes.
- The OpenCode orchestrator will move to a separate repository. It will consume
  workflow bundles through a path or versioned artifact rather than importing
  this repository's internals.

### 2026-07-22: Common versus tool-specific assets

- Tool-agnostic instructions, roles, prompts, personas, and Agent Skills belong
  under `common/`.
- Tool directories contain native configuration, render mappings, and genuine
  behavioral exceptions.
- Reusable utilities belong under `tools/`; skill-specific scripts remain with
  their skill.
- Common role names will be normalized while temporary aliases preserve
  compatibility with existing names and misspellings.

### 2026-07-22: Deployment safety

- The default local deployment mode is copy-with-backup. Symlinks are opt-in.
- Rendering occurs in an ignored staging directory before live files change.
- A deployment records hashes and destinations so drift can be audited.
- Hermes receives a generated bundle through Ansible rather than direct SSH
  deployment from this repository.

### 2026-07-22: Secrets and runtime data

- The repository records secret metadata and retrieval locations, never values.
- Tool-native authentication, OAuth state, transcripts, memory databases,
  caches, logs, rendered output, and backups are excluded.
- Third-party skill collections are referenced by source, revision, and license
  instead of being copied wholesale.

## Inventory observations

- `opencode-setup` contains the richest existing set of authored agents,
  prompts, skills, helper scripts, and the orchestrator slated for extraction.
- The Ansible repository already models LiteLLM aliases/routing, Ollama models,
  Qdrant and SearXNG MCP sidecars, Hermes profiles, and AI-stack validation.
- The local Grok Build CLI supports `AGENTS.md`, Agent Skills, agent/persona
  definitions, project `.grok/config.toml`, and native MCP servers.
- GitHub Copilot runtime/auth state is not suitable for migration; repository
  instructions, prompts, and relevant VS Code/MCP configuration are suitable.
- The checked-out `hermes-setup` repository is behind its upstream branch and
  must be refreshed or compared before importing content.

## Session log

### 2026-07-22: Foundation

- Reviewed the empty target repository and existing AI-related repositories.
- Confirmed ownership boundaries and an incremental, one-task-per-commit plan.
- Identified Grok Build locally and reviewed its bundled configuration docs
  without reading authentication values.
- Created the project requirements, design, migration, roadmap, memory, and
  open-question documents.

### 2026-07-22: Schemas and registries

- Added versioned JSON Schemas for source manifests, deployment targets,
  environments, service registries, MCP registries, and secret catalogs.
- Recorded the existing source repositories with portable checkout hints and
  migration status.
- Added workstation and Hermes bundle targets using copy-with-backup defaults.
- Captured the non-secret home-lab topology, current LiteLLM aliases and model
  routes, expected Ollama models, and Qdrant/SearXNG MCP endpoints.
- Added secret locators for Ansible Vault and tool-native authentication without
  reading or storing any secret value.

### 2026-07-22: Deployment utility

- Implemented `workflowctl` with validation, inventory, rendering, diff,
  deployment, audit, and diagnostic commands.
- Added repository-local `bin/workflowctl` and `deploy.sh` entry points.
- Deployment renders into a marked staging tree, backs up existing files,
  installs by atomic copy or optional symlink, and records expected hashes in a
  target-side state manifest.
- Added isolated-home tests proving dry-run safety, deterministic rendering,
  backups, deployment state, and drift detection.
- Added planned adapter manifests so targets and cross-references validate before
  the content migration activates each adapter.
