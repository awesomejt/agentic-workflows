# Reset-safe loop protocol

An outer pass is one context-bounded execution against one primary project
task. It may employ several fresh-context specialist agents. AWB or another
project-state backend owns the outer pass lease; repository files carry concise
handoffs between specialists and across later outer passes.

## Runtime layout

Create one ignored directory per outer pass:

```text
.agents/loop/<pass-id>/
├── objective.md
├── state.yaml
├── handoffs/
│   ├── 0001-project-manager.md
│   ├── 0002-planner.md
│   └── 0003-implementer.md
├── evidence/
├── result.template.json
└── result.json
```

- `objective.md` is immutable and identifies the primary task, objective,
  acceptance criteria, constraints, and authorized side effects.
- `state.yaml` is owned by the primary orchestrator and points at the current
  specialist stage and latest handoff.
- `handoffs/` is append-only and contains concise specialist results, not
  transcripts.
- `evidence/` stores small summaries or references to durable evidence.
- `result.json` is the validated outer-pass outcome consumed by the runner.

## Specialist protocol

For each workflow stage:

1. Start a fresh specialist context.
2. Read repository instructions, `objective.md`, `state.yaml`, the selected
   workflow, the latest relevant handoff, and only directly relevant evidence.
3. Confirm the assigned role and scope.
4. Perform exactly that bounded role. A specialist must not impersonate the
   primary pass owner or close the outer pass.
5. Write `handoffs/<sequence>-<role>.md` or return the same concise structure
   for the primary orchestrator to record.
6. Let the primary orchestrator validate evidence, update `state.yaml`
   atomically, and choose the next stage.

The primary may employ several specialists in one outer pass. A later outer
pass starts with a new primary context and uses durable backend state plus the
prior handoff/result; it does not rely on conversation memory.

## Handoff contract

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

Keep handoffs secret-free and sufficient for the next context. Promote durable
decisions to project docs, memory, or the authoritative task system.

## Structured result

Before the executor returns, write the path named by
`AGENT_ORCHESTRATOR_RESULT`:

```json
{
  "schema_version": 1,
  "outcome": "completed",
  "summary": "What changed",
  "validation_result": "Commands and results",
  "evidence": {},
  "participants": [
    {"role": "planner", "result": "planned"},
    {"role": "tester", "result": "passed"}
  ],
  "blocker": null
}
```

Valid outcomes are `completed`, `partial`, `blocked`, `failed`, and `aborted`.
Continuation outcomes require `handoff`. Blocked outcomes require
`blocker.reason`. Never recommend completion without direct evidence for every
required gate.

## Termination and recovery

Finish the outer pass when its focused objective has an evidenced outcome, a
specific blocker prevents progress, the pass budget is exhausted, or repeated
specialist stages add no evidence. Use `partial` when safe work should continue
in the next outer pass. Preserve useful interrupted handoffs and never rewrite
prior history to make the loop appear successful.
