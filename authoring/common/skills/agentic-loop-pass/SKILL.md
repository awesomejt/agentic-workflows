---
name: agentic-loop-pass
description: Coordinate one reset-safe agentic-loop pass against one focused project task, including recovery-first selection, fresh-context specialist delegation, evidence review, and a structured result. Use when acting as the primary loop agent or when an interactive CLI session must execute or resume a Ralph-style pass without assuming AWB, a provider, or tool-specific delegation syntax.
---

# Coordinate an Agentic Loop Pass

Read the deployed workflow's `protocol.md`, `project-state-v1.md`, selected
workflow YAML, repository instructions, and authoritative project-state
snapshot before acting.

## Run one outer pass

1. Inspect project state through the configured backend skill.
2. Reconcile active, stale, or logically working tasks before selecting new
   work. Stop for human review when state is ambiguous.
3. Select one dependency-ready primary task and define one focused objective.
4. Start the durable pass through the backend. Keep its actor and lease identity
   stable for the entire outer pass.
5. Create or resume `.agents/loop/<pass-id>/` using the canonical protocol.
6. Delegate the required workflow stages to fresh-context specialists. Give
   each specialist only the objective, current state, relevant handoff, and
   evidence needed for its bounded role.
7. Validate every returned handoff before advancing the local stage pointer.
   Heartbeat the durable pass while work continues.
8. Write the structured result requested by the runner. Let the runner or
   backend-owning primary agent finish the durable pass atomically.

## Outcome rules

- Use `completed` only when the focused objective and required gates have direct
  evidence.
- Use `partial` when useful work should continue in the next outer pass.
- Use `blocked` only with a specific blocker reason.
- Use `failed` for execution or validation failure and `aborted` for an
  intentional early stop. Include a retry handoff for every continuation
  outcome.
- Never treat a successful tool exit or a specialist's recommendation as
  completion evidence by itself.

## Ownership boundaries

- Let the project-state backend own revisions, leases, dependencies, blockers,
  phases, and durable pass transitions.
- Let the execution adapter own provider, model, native agent IDs, permissions,
  and delegation syntax.
- Let specialists write or return handoffs; do not let them claim or finish the
  primary task or pass.
- Keep transcripts, secrets, credentials, and provider authentication out of
  project state and handoffs.
