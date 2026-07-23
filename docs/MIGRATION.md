# Migration Plan

## Source repositories

| Source | Candidate content | Disposition |
| --- | --- | --- |
| `ai/opencode-setup` | agents, prompts, skills, workflow docs | Review and normalize into common content and the OpenCode adapter |
| `ai/opencode-setup/orchestrator` | runtime application and runner scripts | Extract with history into `~/projects/dev/agent-orchestrator` |
| `ai/agents` | Hermes SOUL/persona files and small custom skills | Public/common content or private overlay after sensitivity review |
| `ai/hermes-setup` | Hermes prompts, utilities, crons, operational docs | Refresh against upstream, then classify as bundle content, shared tool, Ansible responsibility, or runtime state |
| starter-kit repositories | project/course instructions and templates | Normalize into reusable templates |
| local CLI configuration | adapter defaults and non-secret preferences | Recreate from reviewed keys; never bulk-copy auth-bearing files |
| `infra/ansible` | service roles, endpoints, model aliases, secret variables | Reference as deployment owner; do not copy roles |

Every reviewed checkout is pinned in `manifests/sources.yaml`. Service contracts
pin the Ansible revision independently so client-visible drift can be reviewed
without treating this repository as the deployment source.

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

The first six phases now have concrete repository artifacts. Shared reset-safe
workflows and native role-routing maps are also implemented. Orchestrator
population, Ansible consumption, template rendering, and live cutover remain
separate tasks.

## Remaining execution sequence

Treat each numbered item as a reviewable migration wave with its own commit or
infrastructure change and rollback evidence.

1. **Clear prerequisites.** Remove and rotate the plaintext credential identified
   in `docs/SECURITY_FINDINGS.md`, resolve the Ollama embedding-model mismatch,
   and review the nine live-file collisions. Do not print secret or config
   content into migration logs.
2. **Populate the orchestrator repository.** Extract
   `opencode-setup/orchestrator` with history, merge it into the existing initial
   `agent-orchestrator` repository, establish its workflow-bundle interface, and
   pass its tests before changing any scheduler command.
3. **Pilot local CLI deployment.** Tag or pin this repository, deploy with
   copy-with-backup to one development system, then audit and run native agent
   discovery. Start with OpenCode, followed by Codex, Claude, Grok, and Copilot;
   preserve tool-owned auth and state throughout.
4. **Expand to development systems.** Use the same pinned revision on each
   workstation. Keep credentials, provider authentication, backups, and drift
   state local to each system. Promote the pin only after the pilot remains
   clean.
5. **Integrate Hermes through Ansible.** Add an Ansible role or task that checks
   out a pinned workflows revision on the controller, renders the Hermes bundle,
   verifies its manifest, resolves Vault data only during target templating, and
   records the deployed revision. Keep Jessica and Rachel in the existing Hermes
   instance and outside the common bundle.
6. **Provision the dedicated OpenCode worker.** After its DNS name, guest type,
   and inventory group are chosen, create the Proxmox guest through Ansible,
   install pinned OpenCode/workflows/orchestrator revisions for a service user,
   isolate workspaces, and validate one non-production loop. Do not expose an
   unauthenticated agent endpoint.
7. **Finish deferred content.** Implement template rendering, classify any new
   shared utilities under `tools/` or a single owning skill, and revisit private
   personal-agent placement only after usage data exists.

## Wave acceptance gates

A wave is complete only when its render is deterministic and secret-free, its
schema/tests pass, live changes were reviewed before writing, backups and
rollback are known, native discovery or the consuming Ansible playbook succeeds,
and the exact deployed repository revision is recorded.

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
