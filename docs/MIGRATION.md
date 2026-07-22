# Migration Plan

## Source repositories

| Source | Candidate content | Disposition |
| --- | --- | --- |
| `ai/opencode-setup` | agents, prompts, skills, workflow docs | Review and normalize into common content and the OpenCode adapter |
| `ai/opencode-setup/orchestrator` | runtime application and runner scripts | Extract to a separate repository with history preserved |
| `ai/agents` | Hermes SOUL/persona files and small custom skills | Public/common content or private overlay after sensitivity review |
| `ai/hermes-setup` | Hermes prompts, utilities, crons, operational docs | Refresh against upstream, then classify as bundle content, shared tool, Ansible responsibility, or runtime state |
| starter-kit repositories | project/course instructions and templates | Normalize into reusable templates |
| local CLI configuration | adapter defaults and non-secret preferences | Recreate from reviewed keys; never bulk-copy auth-bearing files |
| `infra/ansible` | service roles, endpoints, model aliases, secret variables | Reference as deployment owner; do not copy roles |

## Phases

1. Establish governance, requirements, design, memory, and task tracking.
2. Define schemas, manifests, targets, service contracts, and secret references.
3. Implement deterministic validation, rendering, diff, deployment, and audit.
4. Inventory and normalize common agents, prompts, roles, and skills.
5. Add and test one tool adapter per commit.
6. Add the Hermes bundle and Ansible handoff.
7. Extract the orchestrator with preserved history and a stable workflow-bundle
   interface.
8. Cut over live configurations one tool at a time and verify drift detection.

## Import classifications

Every source artifact receives one disposition:

- `migrate-common`
- `migrate-adapter`
- `reference-upstream`
- `move-orchestrator`
- `keep-ansible`
- `private-overlay`
- `runtime-excluded`
- `superseded`
- `deferred`

The inventory is complete only when no reviewed artifact remains unclassified.

## Cutover rules

- Never overwrite a live file on the first pass; render and diff it.
- Back up before replacing any managed destination.
- Do not delete the old source until the new adapter passes isolated-home and
  live dry-run validation.
- Preserve temporary aliases where naming changes could break automation.
- Roll back by restoring the recorded backup and deployment state manifest.
