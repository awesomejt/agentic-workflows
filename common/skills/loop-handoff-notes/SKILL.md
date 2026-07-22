---
name: loop-handoff-notes
description: Create, update, summarize, or clean concise multi-agent handoff and session notes in repository-approved ignored paths. Use when task context is too large for a direct reply or a workflow requires a local session record.
---

# Loop Handoff Notes

## Guardrails

- Use only repository-approved ignored handoff or session paths.
- Keep notes concise, actionable, and secret-free.
- Put durable decisions in the authoritative task system, docs, or `MEMORY.md`.
- Do not put raw transcripts, credentials, tokens, or private keys in notes.
- Do not edit product files for a note-only task.

## Handoff template

```text
Task:
Current state:
What changed:
Validation status:
Open issues:
Suggested next role:
```

## Session template

```text
Objective:
Task id:
Files changed:
Validation:
Decisions:
Blockers:
Follow-up:
```

Keep handoff notes while downstream roles need them. After durable context is
captured, summarize or remove stale transient notes only when repository rules
allow it. Never delete session logs without explicit authorization.
