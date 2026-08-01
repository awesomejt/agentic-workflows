---
name: loop-handoff-notes
description: Create and resume concise reset-safe handoffs under per-pass `.agents/loop/` directories for multi-agent outer passes. Use when fresh-context specialists must exchange scoped findings and evidence, when a later outer pass must continue without conversation memory, or when an executor must produce the structured result consumed by an agentic-loop runner.
---

# Maintain Loop Handoffs

Use the deployed workflow's `protocol.md` when present. Otherwise apply this
minimal contract.

## Runtime layout

```text
.agents/loop/<pass-id>/
├── objective.md
├── state.yaml
├── handoffs/
├── evidence/
├── result.template.json
└── result.json
```

Keep `objective.md` immutable. Let only the primary orchestrator replace
`state.yaml`. Append specialist notes under `handoffs/`; never rewrite prior
history.

## Specialist procedure

1. Read repository instructions, the objective, current state, assigned
   workflow stage, and only the latest relevant handoff and evidence.
2. Perform exactly the assigned bounded role without claiming or finishing the
   durable task or outer pass.
3. Write `handoffs/<sequence>-<role>.md`, or return the same content for the
   primary orchestrator to record.
4. Include evidence, failures, blockers, and a recommended next stage. Do not
   infer completion outside the assigned role.

## Handoff format

```text
Pass and stage:
Role:
Objective addressed:
Inputs read:
Work performed:
Files changed:
Decisions:
Evidence and commands:
Findings or failures:
Blockers:
Recommended next stage:
Outer-pass outcome recommendation:
```

## Structured result

Before the executor returns, write `result.json` at
`AGENT_ORCHESTRATOR_RESULT` when that variable is set. Follow
`result.template.json` and use only `completed`, `partial`, `blocked`, `failed`,
or `aborted`. Require a handoff for continuation outcomes and
`blocker.reason` for `blocked`.

Keep handoffs concise and secret-free. Promote durable decisions to project
documentation or the authoritative task system.
