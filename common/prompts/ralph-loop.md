# Reset-safe agentic loop

Run `<WORKFLOW_ID>` for `<TASK_REF>` using the repository's reset-safe loop
protocol.

Use `agentic-loop-pass` when available. Select the project-state backend named
by repository instructions; do not switch between AWB and `project.yaml` within
one pass.

Objective: `<OBJECTIVE>`

Acceptance criteria:

- `<CRITERION_1>`
- `<CRITERION_2>`

Constraints and authorized side effects:

- `<CONSTRAINT_OR_AUTHORIZATION>`

Use `.agents/loop/<PASS_ID>/` for transient state and handoffs. Read
`common/workflows/protocol.md` in a source checkout or the adapter's installed
`workflows/protocol.md` copy when available; otherwise use the
`loop-handoff-notes` skill. Initialize `objective.md` and `state.yaml` if the run
does not exist. If it exists, resume from state; do not infer progress from chat
history.

Within each outer pass, use fresh specialist contexts for the roles required by
the current objective and require concise handoffs. The orchestrator alone
checks evidence and advances workflow state. A later outer pass starts with a
new primary context. Use the tool's native subagent syntax only as an execution
mechanism; do not put that syntax into common artifacts.

Stop the outer pass when its focused objective has evidence, a specific blocker
prevents progress, or repeated specialist stages add no evidence. Write the
structured result requested by the runner, promote durable decisions to the
appropriate project records, and include validation evidence and residual risk.
