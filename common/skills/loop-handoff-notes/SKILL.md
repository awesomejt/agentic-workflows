---
name: loop-handoff-notes
description: Run or resume reset-safe multi-agent loops using concise handoffs under a repository-approved `.agents/loop/` path. Use when agents or subagents must complete bounded passes with fresh contexts, preserve evidence between passes, or summarize a run without storing transcripts.
---

# Loop Handoff Notes

Use the repository's canonical reset-safe loop protocol and selected workflow
when present. Otherwise apply this minimal procedure.

## Procedure

1. Create or resume `.agents/loop/<run-id>/` with immutable `objective.md`, small
   `state.yaml`, append-only `passes/`, optional `evidence/`, and `final.md` at
   completion.
2. In a fresh context, read repository instructions, the objective, state, the
   latest handoff, and only directly relevant evidence.
3. Perform exactly one assigned role and write one zero-padded pass handoff.
4. Let the primary orchestrator validate the evidence and update state. A
   specialist must not claim or advance the next pass itself.
5. Stop on evidenced completion, a specific blocker, the pass limit, repeated
   no-progress results, unsafe action, or missing authority.

## Guardrails

- Use only repository-approved ignored handoff or session paths.
- Keep notes concise, actionable, and secret-free.
- Put durable decisions in the authoritative task system, docs, or `MEMORY.md`.
- Do not put raw transcripts, credentials, tokens, or private keys in notes.
- Never rewrite earlier passes to hide an interruption or failed result.

## Pass handoff

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

At completion, make `final.md` point to durable task state and evidence. Remove
runtime notes only when repository policy and user authorization allow it.
