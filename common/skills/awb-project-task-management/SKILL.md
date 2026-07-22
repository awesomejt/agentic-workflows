---
name: awb-project-task-management
description: Read Agent Workbench project information and manage AWB task selection, claim, heartbeat, completion, blocking, and follow-up creation with the awb CLI. Use when a repository declares AWB as its authoritative project or task system.
---

# AWB Project and Task Management

Run commands from the target repository so `.awb/config.yaml` is discovered.
Use the inherited `AWB_AGENT` identity; subagents must not replace the primary
agent's lease identity.

## Commands

```bash
awb project get
awb status show
awb task next --output json
awb task list --available
awb task claim <task-id>
awb task heartbeat <task-id>
awb task complete <task-id> --evidence "<summary>"
awb task block <task-id> --reason "<reason>"
awb task create --title "<title>" --phase <phase> --role <role>
```

## Guardrails

- Treat AWB as the source of truth when repository instructions say so.
- Do not edit a historical `TODO.md` as a substitute for AWB task state.
- Do not invent alternate flags or task state after a command fails.
- Retry once only for a clearly transient error.
- Use a file-based fallback only when repository instructions or the primary
  agent explicitly authorize it.

Report the project, selected task, status, dependencies, action taken, evidence
or blocker, and any follow-up task IDs.
