# Design

## Architecture

The repository separates semantic content from native tool configuration:

```text
common content ─┐
tool adapter ───┼─> renderer ─> staging tree ─> diff ─> local deployment
target config ──┘                         └─────> Hermes bundle ─> Ansible

service registry ─> tool adapter MCP/client configuration
secret catalog ───> reference validation only; values resolve outside Git
```

## Configuration layers

Configuration is resolved from lowest to highest precedence:

1. Shared defaults under `common/`.
2. Tool adapter defaults.
3. Tracked environment topology and service contracts.
4. Tracked deployment target settings.
5. Optional ignored host-local overlay.
6. Secret resolver or tool-native authentication at deployment/runtime.

The renderer must make the origin of a winning value inspectable.

## Domain model

### Content records

Agents, roles, prompts, personas, and skills have a stable ID, source path,
supported tools, sensitivity classification, and provenance. Shared content is
stored once; adapters may add tool-native frontmatter or wrappers.

### Service records

A service record contains a stable ID, capability, environment endpoint,
protocol, owning repository/path, consumers, health check, and secret
references. It describes a client contract and does not duplicate deployment
templates from Ansible.

### Secret references

A secret reference contains metadata such as purpose, consumers, source type,
logical locator, variable name, owner, and validation method. The schema must
not contain a field intended for the value itself.

### Deployment targets

A target selects adapters and maps rendered artifacts to destinations. Paths
support home expansion at runtime but committed defaults must avoid a specific
user's absolute home directory.

## Rendering and deployment

`workflowctl` performs these stages:

1. Load and schema-check manifests.
2. Resolve content, environment, target, and adapter references.
3. Reject unsafe destinations, secret-like material, and collisions.
4. Render deterministically into `.build/<target>/`.
5. Compare rendered files with the destination.
6. For deployment, back up changed destination files under a user-state
   directory outside the repository.
7. Install by atomic copy or explicitly configured symlink.
8. Write a state manifest containing source revision, hashes, destinations, and
   deployment time.

Dry-run executes through comparison but never backs up or writes destinations.

## Adapter boundaries

- **OpenCode:** native config, agents, permissions, prompts, and skills.
- **Codex:** `AGENTS.md`, config/rules, agents, skills, and plugin references.
- **Claude Code:** `CLAUDE.md`, settings, agents, rules, and skills.
- **Grok Build:** `AGENTS.md`, `.grok/config.toml`, agents, roles, personas,
  skills, and MCP definitions.
- **GitHub Copilot/VS Code:** repository instructions, prompt files, supported
  agent files, and VS Code MCP configuration. Extension auth/state is excluded.
- **Hermes:** profiles, SOUL mappings, selected skill sources, model/service
  references, and a bundle manifest consumed by Ansible.

## External ownership

Ansible remains responsible for actual LiteLLM routing, Ollama installation and
model pulls, MCP sidecars, Hermes services, Open WebUI, Qdrant, SearXNG, and
health-check cron jobs. This repository may assert the client contract and
detect drift but does not deploy those services.

The `agent-orchestrator` repository owns runtime scheduling and consumes a
workflow root or released bundle through a stable interface.

## Security model

- Deny secret-value fields in tracked schemas.
- Permit environment-variable placeholders and logical secret IDs.
- Ignore rendered trees, overlays, backups, state, logs, sessions, and auth.
- Validate imports before copying them into the repository.
- Redact sensitive command output in diagnostics.
- Never infer that a broad permission rule is portable between tools or hosts.
