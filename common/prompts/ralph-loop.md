# Reset-safe agentic loop

Run `<WORKFLOW_ID>` for `<TASK_REF>` using the repository's reset-safe loop
protocol.

Objective: `<OBJECTIVE>`

Acceptance criteria:

- `<CRITERION_1>`
- `<CRITERION_2>`

Constraints and authorized side effects:

- `<CONSTRAINT_OR_AUTHORIZATION>`

Use `.agents/loop/<RUN_ID>/` for transient state and handoffs. Read
`common/workflows/protocol.md` in a source checkout or the adapter's installed
`workflows/protocol.md` copy when available; otherwise use the
`loop-handoff-notes` skill. Initialize `objective.md` and `state.yaml` if the run
does not exist. If it exists, resume from state; do not infer progress from chat
history.

For each pass, start a fresh agent context, assign exactly the role named by the
current stage, and require a concise pass handoff. The orchestrator alone checks
the evidence and advances state. Use the tool's native subagent syntax only as an
execution mechanism; do not put that syntax into common artifacts.

Stop when all gates have evidence, a specific blocker prevents progress, the
pass limit is reached, or repeated passes add no new evidence. On completion,
write `final.md`, promote durable decisions to the appropriate project records,
and report the result with validation evidence and residual risk.
