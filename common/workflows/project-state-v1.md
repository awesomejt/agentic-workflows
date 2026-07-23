# Project-state contract v1

The primary orchestrator uses this backend-neutral contract for durable project
coordination. A backend may be Agent Workbench, atomic `project.yaml`, or
another implementation with equivalent concurrency guarantees.

## Request envelope

Every mutation carries:

```json
{
  "contract_version": "project-state/v1",
  "project_ref": "example",
  "actor": "orchestrator",
  "request_id": "stable-logical-request-id",
  "expected_revision": 12,
  "input": {}
}
```

Reuse `request_id` only when retrying the identical logical mutation. Treat
backend resource IDs as opaque. Re-inspect after any conflict.

## Operations

- `inspect_project`: return one unpaginated snapshot containing project,
  ordered phases, active and stale passes, working tasks without a lease,
  structured blockers, dependency-ready tasks, warnings, and a recommended
  action.
- `start_pass`: select or recover one task and atomically create its pass lease.
- `heartbeat_pass`: renew the matching pass and task lease using the current
  lease version.
- `finish_pass`: atomically record the pass result and update task/project
  state.
- `recover_project`: repair only unambiguous expired pass and task leases.
- `create_task`: add one task with phase, role, priority, and validation
  expectations.
- `add_dependency`: add a cycle-checked `blocks` edge from predecessor to
  successor.
- `resolve_blocker`: resolve one structured task blocker with evidence.
- `update_phase`: explicitly activate, block, complete, or skip a phase.

## Result rules

Valid pass outcomes are `completed`, `partial`, `blocked`, `failed`, and
`aborted`. Require a handoff for `partial`, `failed`, and `aborted`. Require a
structured reason for `blocked`. A partial pass releases its execution lease
while its task remains logically working.

At project concurrency one, recover active, stale, or logically working state
before selecting a pending task. A blocked task does not prevent an independent
dependency-ready task from running.

## Errors

Normalize errors to `not_found`, `validation_error`, `state_conflict`,
`lease_conflict`, `concurrency_limit`, `task_not_eligible`,
`recovery_required`, `reconciliation_required`, or `backend_unavailable`.
Include whether a retry is safe and the current revision when known.

Never store credentials, provider authentication, secret values, or raw
transcripts in requests, state, evidence, or handoffs.
