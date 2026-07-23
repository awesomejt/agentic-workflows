---
name: awb-project-task-management
description: Inspect and manage Agent Workbench project, task, dependency, blocker, phase, and atomic agentic-loop pass state with the awb CLI. Use when a repository declares AWB authoritative, when an orchestrator starts or recovers a pass, or when a project-manager agent must create or triage durable follow-up work.
---

# Manage AWB Project State

Run commands from the target repository. Preserve the inherited `AWB_AGENT`;
specialists must not replace the primary pass identity.

## Inspect before acting

```bash
awb loop inspect --output json
awb task triage <task-id> --output json
awb task relationship list <task-id> --output json
awb run list --all --output json
```

Use the returned `state_version` for the next concurrency-sensitive mutation.
Do not infer current work from `TODO.md`, chat history, or a paginated task list.

## Primary runner lifecycle

Only the primary runner or explicitly authorized primary agent performs these
operations:

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

Inspect again before `finish`; other durable project changes may have advanced
the state version. Require a handoff for `partial`, `failed`, or `aborted`.
Require `--blocker-reason` for `blocked`.

When `AGENT_ORCHESTRATOR_RESULT` is set, write the structured result requested
by the orchestrator instead of finishing the pass directly. This lets the
runner validate and atomically close the pass.

## Planning and triage

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
successor. Check existing tasks before creating follow-up work.

## Guardrails

- Keep one primary task and pass lease at a time when project concurrency is one.
- Recover working/stale work before selecting a new pending task.
- Do not claim, complete, block, or finish under a specialist identity.
- Do not retry conflicts blindly; inspect and reassess.
- Use explicit `--api-url` or `AWB_API_URL` for local validation so repository
  config cannot redirect the command to production.
- Never place credentials or secret values in evidence, handoffs, or fixtures.
