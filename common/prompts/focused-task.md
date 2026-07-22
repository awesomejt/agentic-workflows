# Focused Task Workflow

Complete one coherent unit of work in the active repository, validate it, update
the repository's required coordination artifacts, and stop at a reviewable
boundary.

## Preflight

1. Confirm the working directory and inspect version-control status.
2. Read repository instructions, the README, durable memory, current task state,
   and relevant design or requirements documents.
3. Use the user's explicit request first. Otherwise, use the repository's
   authoritative task system to choose the highest-priority unblocked task.
4. Identify success evidence and any unsafe or external actions before editing.

## Work discipline

- Preserve unrelated user changes.
- Prefer the smallest complete change that satisfies the selected task.
- Keep public contracts aligned across code, configuration, tests, and docs.
- Use specialized roles only where their independent context or review adds
  value.
- Validate the specific behavior changed; broaden checks in proportion to risk.
- If validation cannot run, record the exact gap and do not claim it passed.
- Commit only when authorized by the repository or user. Push only when
  explicitly authorized.

## Completion

1. Inspect the final diff and version-control status.
2. Confirm requirements against direct evidence.
3. Update the repository's task state and durable decision record as required.
4. Report the outcome, files changed, validation, residual risk, and follow-up.
