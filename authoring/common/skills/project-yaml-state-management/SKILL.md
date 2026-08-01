---
name: project-yaml-state-management
description: Use an atomic local project.yaml file as a project-state/v1 backend for projects that do not use Agent Workbench. Use when an agentic loop needs durable project, phase, task, dependency, blocker, revision, lease, and pass state in Git-adjacent flat files, or when validating backend-neutral workflows without a service.
---

# Manage Atomic Project YAML State

Use `scripts/project_state.py`; do not hand-edit `project.yaml` during an active
loop. The helper uses an exclusive lock, optimistic revisions, idempotent
mutation requests, and atomic replacement. It writes JSON syntax, which is
valid YAML 1.2 and requires only Python's standard library.

Set the helper path for deployed or source use:

```bash
STATE_TOOL="<skill-directory>/scripts/project_state.py"
```

## Initialize and inspect

```bash
python3 "$STATE_TOOL" --file project.yaml init \
  --project-ref example \
  --workflow-id software-development \
  --workflow-version 1

python3 "$STATE_TOOL" --file project.yaml inspect
```

Treat `revision` in the snapshot as the expected revision for the next
mutation. Re-inspect after every successful write.

## Apply a project-state operation

Write a short request envelope under an ignored `.agents/` path and pass it on
standard input:

```bash
python3 "$STATE_TOOL" --file project.yaml apply <operation> --request-file - \
  < .agents/request.json
```

Supported operations are `start_pass`, `heartbeat_pass`, `finish_pass`,
`recover_project`, `create_task`, `add_dependency`, `resolve_blocker`, and
`update_phase`.
Requests use this envelope:

```json
{
  "contract_version": "project-state/v1",
  "project_ref": "example",
  "actor": "orchestrator",
  "request_id": "stable-logical-request-id",
  "expected_revision": 3,
  "input": {}
}
```

Use a new `request_id` for each logical mutation and reuse it only when retrying
the identical request. Read `workflows/project-state-v1.md` for the portable
operation contract.

## Guardrails

- Recover stale or logically working state before selecting a new task.
- Keep one active pass unless the initialized concurrency limit says otherwise.
- Let only the primary runner apply pass lifecycle operations.
- Treat `state_conflict`, `lease_conflict`, and
  `reconciliation_required` as inspect-and-reassess conditions.
- Keep `project.yaml.lock`, transient request files, and pass handoffs ignored.
- Do not store secrets, credentials, provider authentication, or transcripts.
- Use AWB instead when several machines or independent processes need a
  networked coordination service.
