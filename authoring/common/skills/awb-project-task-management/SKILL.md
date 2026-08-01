---
name: awb-project-task-management
description: Use the awb CLI as a project-state/v1 backend to inspect and manage Agent Workbench projects, phases, tasks, dependencies, structured blockers, and atomic agentic-loop passes. Use when a repository declares AWB authoritative, when the primary runner starts, heartbeats, finishes, or recovers a pass, or when a project-manager agent must triage durable work.
---

# Manage AWB Project State

Run commands from the target repository. Preserve the primary `AWB_AGENT`;
specialists must not replace the pass identity.

## Inspect before mutating

```bash
awb loop inspect --output json
awb task triage <task-id> --output json
awb task relationship list <task-id> --output json
awb run list --all --output json
```

Use the returned `state_version` for the next concurrency-sensitive mutation.
Recover active, stale, or working state before selecting a pending task. Do not
infer current work from `TODO.md`, conversation history, or a paginated list.

## Manage the primary pass

Only the primary runner or explicitly authorized primary agent may run:

```bash
awb loop start \
  --expected-version <state-version> \
  --objective "<one focused objective>" \
  --workflow-manager agent-orchestrator \
  --tool <resolved-tool> \
  --agent-profile <resolved-profile> \
  --output json

awb loop heartbeat <pass-id> \
  --lease-version <lease-version> \
  --output json

awb loop finish <pass-id> \
  --expected-version <latest-state-version> \
  --outcome <completed|partial|blocked|failed|aborted> \
  --summary "<result>" \
  --evidence-json '<object>' \
  --output json

awb loop recover \
  --expected-version <state-version> \
  --output json
```

Inspect again before `finish`. Replace cached state and lease versions with
values returned by every successful mutation. Require a handoff for `partial`,
`failed`, or `aborted`, and `--blocker-reason` for `blocked`.

When `AGENT_ORCHESTRATOR_RESULT` is set, write the requested result file instead
of finishing AWB directly. The runner validates and closes the pass.

## Plan tasks and phases

```bash
awb task create \
  --title "<title>" \
  --phase <phase> \
  --role <role> \
  --priority <number> \
  --validation "<observable completion checks>"

awb task relationship add <predecessor-id> \
  --to <successor-id> \
  --type blocks

awb task unblock <task-id> <blocker-id> \
  --evidence "<resolution evidence>"
```

Create explicit dependencies during planning. The predecessor blocks the
successor. Check existing tasks before creating follow-up work. Read phase
instances from `awb loop inspect`. AWB 0.2 does not expose phase transitions
through the CLI; do not invent a command or infer completion from a task's
category. Leave the phase at `complete_phase` until an approved API client or a
later matching CLI performs the explicit transition.

## Conflicts and retries

- Supply a stable idempotency key when the CLI operation supports one.
- On `state_conflict` or `lease_conflict`, inspect again and reassess; never
  retry a stale mutation blindly.
- Treat `reconciliation_required` as a project-manager or human review stop.
- Retry only transport failures known to be transient, using the same logical
  request identity.

## Guardrails

- Keep one primary task and pass lease when project concurrency is one.
- Do not claim, complete, block, or finish under a specialist identity.
- Use explicit `--api-url` or `AWB_API_URL` for local validation so repository
  config cannot redirect the command to production.
- Never place credentials or secret values in evidence, handoffs, or fixtures.
