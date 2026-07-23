# Reset-safe loop protocol

This protocol lets successive agents work on one objective without sharing a
conversation context. Repository files and the authoritative task system are the
only coordination channel.

## Run layout

Create one runtime directory per run. It must be ignored by Git:

```text
.agents/loop/<run-id>/
├── objective.md
├── state.yaml
├── passes/
│   ├── 0001-orchestrator.md
│   └── 0002-planner.md
├── evidence/
└── final.md
```

- `objective.md` is immutable after the first specialist pass. It contains the
  task reference, scope, acceptance criteria, constraints, and authorized side
  effects.
- `state.yaml` is the small machine-readable pointer to current workflow state.
- `passes/` is an append-only sequence of concise handoffs, not transcripts.
- `evidence/` may contain small generated summaries or references to durable
  evidence. Avoid copying large logs when a path and command are enough.
- `final.md` summarizes the result, evidence, unresolved risk, and durable
  records updated.

## State contract

```yaml
schema_version: 1
run_id: <stable-run-id>
workflow: <workflow-id>
task_ref: <task-id-or-path>
status: active # active | complete | blocked | stopped
pass: 2
max_passes: 20
current_stage: plan
current_role: planner
next_stage: design
next_role: designer
acceptance_criteria:
  - <observable criterion>
blocking_issue: null
last_handoff: passes/0002-planner.md
updated_at: <RFC-3339 timestamp>
```

Only the primary orchestrator or runner owns `state.yaml`. The orchestrator
validates each specialist handoff and replaces state using an atomic write. If
the tool cannot make an atomic replacement, write a temporary file in the run
directory, validate it, then rename it.

## Pass protocol

Each fresh-context pass does the following:

1. Read repository instructions, `objective.md`, `state.yaml`, the selected
   workflow, and only the latest handoff plus directly relevant evidence.
2. Confirm the assigned stage and role. Stop if state is not `active`, another
   pass owns the same lease, or the requested action is outside authorization.
3. Perform exactly one bounded role. A pass must not implement, validate, test,
   review, and close the task itself.
4. Produce `passes/<zero-padded-pass>-<role>.md` using the handoff contract
   below. A specialist may write it directly when its native permissions allow;
   otherwise the runner records the specialist's returned handoff verbatim.
5. Return control. The orchestrator checks evidence, selects the configured
   transition, updates state, and starts the next pass with fresh context.

## Handoff contract

```text
Run and pass:
Role and stage:
Objective addressed:
Inputs read:
Work performed:
Files changed:
Decisions:
Evidence and commands:
Findings or failures:
Blockers:
Recommended transition:
Completion recommendation:
```

A handoff must be concise, secret-free, and sufficient for the next role to
continue without the prior conversation. Put durable decisions in project docs,
memory, or the authoritative task system instead of relying on a runtime note.

## Termination and recovery

Complete only when every workflow gate has direct evidence. Mark blocked when a
specific dependency or authority is missing. Stop for human review when the pass
limit is reached, the same failure recurs without new evidence, state conflicts
with the repository, or the next action would be unsafe or out of scope.

After an interrupted pass, keep the incomplete note if it contains useful
evidence, record the interruption in a new orchestrator handoff, and retry only
with a new pass number. Never rewrite prior pass history to make the loop appear
successful.
