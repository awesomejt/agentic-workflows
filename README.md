# Agentic Workflows

`agentic-workflows` is the source of truth for reusable agent instructions,
prompts, roles, skills, tool-specific configuration, and client-facing AI
service definitions.

The repository renders and deploys configuration for local agent tools and
produces a configuration bundle for Hermes. It does not own AI service
deployment, orchestration runtime code, credentials, transcripts, or other
runtime state.

## Project status

The repository has versioned schemas and registries, a tested deployment
utility, and active adapters for OpenCode, Codex, Claude Code, Grok Build,
GitHub Copilot/VS Code, and Hermes. Each roadmap task is committed separately so
architectural and migration decisions remain traceable. See [TODO.md](TODO.md)
for current work and [MEMORY.md](MEMORY.md) for durable decisions.

## What to edit

- `common/` is the primary authoring surface for shared instructions, prompts,
  roles, skills, and workflows.
- `adapters/` contains provider-specific wrappers, routing, frontmatter,
  config overlays, and justified exceptions.
- `templates/` is the revision-pinned catalog for reusable project templates.
- `.build/` is generated render output; do not edit files there.

## Quick start

```bash
# Validate schemas and cross-references
bin/workflowctl validate

# See configured sources, targets, services, MCP servers, and adapters
bin/workflowctl inventory

# Render and inspect local changes without writing the live home
bin/workflowctl diff --target workstation --content
./deploy.sh --dry-run

# Render bundles for managed remote systems
bin/workflowctl render --target hermes
bin/workflowctl render --target opencode-server

# Prove deployment behavior against an isolated home
bin/workflowctl deploy --target workstation --home /tmp/workflows-test-home
bin/workflowctl audit --target workstation --home /tmp/workflows-test-home
```

Do not perform a live deployment until the relevant adapter is marked active
and its dry-run diff has been reviewed.

## Ownership boundaries

| Concern | Owner |
| --- | --- |
| Shared prompts, roles, agents, and skills | This repository |
| Claude, Codex, OpenCode, Grok, Copilot, and Hermes adapters | This repository |
| MCP and AI-service client contracts | This repository |
| Local rendering, validation, diff, and deployment | This repository |
| Network service deployment | `infra/ansible` |
| Agent scheduling, leasing, and execution | `agent-orchestrator` repository |
| Secret values | Ansible Vault, HashiCorp Vault, environment, or tool-native auth |
| Runtime memory, sessions, logs, and transcripts | The relevant target system |

## Planned structure

```text
common/               tool-agnostic instructions, roles, prompts, skills, and workflows
adapters/             tool-specific adapters and config overlays
adapters/claude/      Claude Code adapter and exceptions
adapters/codex/       Codex adapter and exceptions
adapters/opencode/    OpenCode adapter and exceptions
adapters/grok/        Grok Build adapter and exceptions
adapters/copilot/     GitHub Copilot/VS Code adapter and exceptions
adapters/hermes/      Hermes profiles, mappings, and bundle definition
services/             MCP and AI-service client contracts
environments/         non-secret environment topology
targets/              deployment target definitions
secret-references/    secret metadata; never secret values
manifests/            provenance, versions, and migration sources
templates/            revision-pinned reusable project template catalog
overlays/             private-overlay rules; private content is ignored
tools/workflowctl/    renderer, validator, deployer, and diagnostics
docs/                 requirements, design, and operational documentation
```

## Deployment model

The `workflowctl` utility will render a target into an ignored staging
directory, validate it, show a diff, back up an existing destination, and then
copy or link managed files. Copy-with-backup is the default; symlinks are an
explicit target option.

Hermes deployment is indirect: this repository produces a bundle and the
Ansible Hermes role installs it while resolving target-side secrets.

## Security

- Never commit API keys, tokens, passwords, OAuth state, `.env` files, or
  machine credential files.
- A secret reference may record its purpose, variable name, owner, and logical
  retrieval location, but never its value.
- Rendered output and deployment backups are ignored.
- Imported files must be reviewed for private data and provenance before they
  are committed.

## Documentation

- [Requirements](docs/REQUIREMENTS.md)
- [Design](docs/DESIGN.md)
- [Common content model](docs/CONTENT.md)
- [Agentic workflow model](docs/WORKFLOWS.md)
- [Migration plan](docs/MIGRATION.md)
- [Deployment guide](docs/DEPLOYMENT.md)
- [Tool adapter guide](docs/ADAPTERS.md)
- [AI service contracts](docs/SERVICES.md)
- [Orchestrator extraction](docs/ORCHESTRATOR_EXTRACTION.md)
- [Migration security findings](docs/SECURITY_FINDINGS.md)
- [Migration readiness report](docs/READINESS.md)
- [Open questions](docs/OPEN_QUESTIONS.md)
- [Decision memory](MEMORY.md)
- [Task roadmap](TODO.md)
