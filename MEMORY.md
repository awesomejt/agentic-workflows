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

### 2026-07-22: Common content migration

- Added a provenance and disposition manifest covering the reviewed agents,
  prompts, skills, scripts, workflow docs, repository state, and orchestrator in
  `opencode-setup` at revision `cc5b212c0dad8e6ff6f9d940044458c36db842fb`.
- Replaced two byte-identical scheduled prompts with one portable focused-task
  prompt and separated AWB command details into the AWB skill.
- Normalized the role names `implementer`, `writer`, and `git-committer` while
  retaining aliases for `implementor`, `documentor`, `committer`, the misspelled
  `git-commiter`, and the superseded `task-manager`.
- Migrated six skills with concise two-field frontmatter and portable guardrails.
  All six passed the Codex skill `quick_validate.py` validator.
- Kept OpenCode permissions, model selection, unattended-run behavior, and the
  primary AWB orchestrator definition out of common content for adapter-specific
  migration.

### 2026-07-22: Tool adapters

- Activated workstation adapters for OpenCode, Codex, Claude Code, Grok Build,
  and GitHub Copilot/VS Code plus the indirect Hermes bundle adapter.
- Added render-time header and footer composition so one canonical role body can
  become OpenCode, Claude, Grok, Copilot Markdown or Codex TOML without copied
  prompt bodies.
- Kept state-bearing base configuration files unmanaged. Tool-native merge
  commands or explicit overlays carry MCP entries for OpenCode, Codex, Claude,
  and Grok; Copilot's VS Code `mcp.json` is a reviewed, backed-up replacement.
- Preserved the OpenCode AWB orchestrator and broad-permission `afk-build` as
  tool-specific primary agents. `afk-build` remains explicitly opt-in.
- Recorded Hermes profile source revisions and an Ansible handoff contract; no
  direct Hermes host deployment or secret resolution occurs here.
- Verified rendered JSON, TOML, YAML frontmatter, skills, and Hermes contracts.
  Native smoke checks discovered all OpenCode agents and all nine Grok roles.
- Grok Build 0.2.14 discovers user agents through `$HOME/.grok/agents`, even
  when skills are found through `GROK_HOME`; isolated tests must model both.
- Codex CLI 0.145.0 parses the separate `workflows` profile, but its `mcp list`
  output reflects only the base configuration in this environment. The adapter
  documents native CLI merge commands as a fallback.

### 2026-07-22: Services, templates, and extraction boundary

- Pinned all seven reviewed source checkouts and their clean worktree state in
  the source manifest.
- Expanded service coverage to LiteLLM, Ollama, both oMLX hosts, Open WebUI,
  Qdrant, SearXNG, their MCP sidecars, AnythingLLM, and n8n at Ansible revision
  `79944d7875ab1ff1673c16bac79c489d30a7e1a0`.
- Added service contract validation and secret cross-reference checks. Hermes
  now receives the full service contract tree rather than three selected files.
- Identified a contract mismatch: AnythingLLM and Hermes require
  `nomic-embed-text:latest`, while the reviewed Ollama role does not pull it.
- Found a plaintext oMLX credential in `hermes-setup/AGENTS.md`. The value was
  not migrated; removal and rotation are required before that source is safe.
- Cataloged the AI-ready, coding-project, and course-project templates by exact
  source revision. Full template rendering remains a separate implementation
  task so repository task state is not copied accidentally.
- Established an ignored private-overlay boundary for named/personal Hermes
  profiles while retaining only generic profile source mappings in the bundle.
- Wrote a history-preserving orchestrator extraction and rollback plan. The
  repository name and Ansible bundle delivery mechanism remain owner decisions.

### 2026-07-22: Readiness audit

- Validated 23 documents and ran 12 passing tests plus Python and shell syntax
  checks.
- Rendered 87 workstation files and 30 Hermes bundle files. An isolated
  deployment installed all 87 workstation files, and the audit reported all 87
  clean.
- Native discovery found 11 managed OpenCode agents, nine Grok agents, and six
  Grok skills. Claude doctor succeeded against the fake home with expected
  missing-install/auth warnings.
- A read-only live comparison found 78 creates and nine updates: eight existing
  OpenCode agents and VS Code `mcp.json`. No live files were changed and no
  content diff was printed.
- The repository is ready for per-tool dry-run review, not a one-shot cutover.
  External security remediation, the Ollama model gap, owner decisions, and
  collision review remain required.

### 2026-07-22: Owner deployment decisions

- Confirmed `/shared/projects/dev/agent-orchestrator` as the extraction target;
  it currently contains only initial commit
  `7337f2a81ce308d65b3c1090b221199345a28b88`.
- Local development systems use copy-with-backup into normal per-user tool
  directories. Every system deploys from the same pinned workflows revision and
  keeps independent state and backups.
- Stable DNS names replace literal home-lab service addresses. Only the Ansible
  controller at `192.168.50.11` and DNS server at `192.168.50.53` retain IPs.
- Jessica and Rachel remain isolated in the existing Hermes instance and are
  excluded from the common bundle until usage informs a permanent decision.
- Ansible-first Hermes deployment is recommended: render a pinned workflows
  revision on the controller, copy the bundle through the Hermes role, and
  resolve secrets only from Vault.
- Added an `opencode-server` bundle target for a future Proxmox worker. Ansible
  should own the guest and install pinned workflow/orchestrator revisions; its
  DNS name and inventory identity remain undecided.

### 2026-07-22: Reset-safe workflow model

- Added a tool-agnostic catalog of 13 roles. Abstract model classes communicate
  workload intent while concrete providers, models, permissions, and invocation
  syntax remain adapter-owned.
- Added software-development and content-creation stage graphs with explicit
  success/failure transitions, completion gates, and bounded pass limits.
- Standardized transient coordination under ignored
  `.agents/loop/<run-id>/` directories. Each fresh-context specialist performs
  one role and appends a concise handoff; the primary orchestrator alone updates
  state and chooses the next transition.
- The shared repository owns the protocol and examples. The extracted
  `agent-orchestrator` will own leasing, context reset, recovery, and execution.
- Expanded the loop handoff skill using the skill-authoring guidance: the skill
  stays concise and operational, while the detailed protocol and stage graphs
  remain canonical shared resources.

### 2026-07-22: Native role routing and loop surfaces

- Added validated routing maps for OpenCode, Claude Code, Codex, Grok Build, and
  Copilot. Common role bodies remain provider-neutral; concrete model and
  permission exceptions remain in native adapters.
- Preserved `ollama-direct/local-coding` for the OpenCode orchestrator,
  implementer, AWB orchestrator, and opt-in AFK build. Other roles inherit the
  active model.
- Added native variants for orchestrator, designer, researcher, and editor to
  all five workstation adapters. Copilot and OpenCode also receive primary
  software/content loop agents with bounded specialist catalogs.
- Read-only specialists may return a handoff for the runner to record verbatim;
  they do not need broad write access merely to participate in a loop.
- Validation covered 32 schema-bound documents, 13 roles, two workflows, five
  routing maps, and 18 passing tests. Rendered totals are 132 workstation files,
  41 Hermes files, and 32 future OpenCode-server files.
- OpenCode native discovery loaded all 17 managed agents from an isolated
  render. A hash-only live comparison found 123 creates and nine updates; no
  live file was changed.
- Finalized the remaining migration into seven gated waves: prerequisite
  remediation, orchestrator extraction, one-system CLI pilot, workstation
  expansion, Ansible-managed Hermes, a dedicated OpenCode worker, and deferred
  template/personal content.

### 2026-07-23: Orchestrator extraction and local AWB validation

- Preserved the `opencode-setup/orchestrator` commit history with a subtree
  split and merged it into the existing `agent-orchestrator` repository without
  rewriting its remote. The implementation revision is
  `8f8f24185d0b0cd17ab4dd124ad41ed53a580b09`.
- Refactored the application around a small common runtime plus project-state
  and execution adapters. AWB and OpenCode are current implementations, not
  hard-coded responsibilities of the loop core.
- Defined one AWB pass as one focused task that may employ several
  fresh-context specialists. The primary runner alone owns the lease and
  validates the final structured result.
- Expanded the AWB skill to cover atomic loop inspect/start/heartbeat/finish
  and recovery, while retaining task planning, dependencies, blockers, and
  project status in AWB.
- Built AWB 0.2 locally with Docker Compose and validated complete,
  partial/resume, blocked/unblock, recovery selection, and repeated heartbeat
  behavior against `http://127.0.0.1:8000`. Production AWB was not accessed.
- The original setup-repository implementation remains available for rollback.
  A workstation pilot, scheduler cutover, push, and production deployment are
  deliberately deferred.
