---
description: Runs a reset-safe research, writing, editing, and review loop using focused subagents.
mode: primary
temperature: 0.2
permission:
  edit: allow
  bash: ask
  webfetch: ask
  external_directory: ask
  task:
    "*": deny
    project-manager: allow
    planner: allow
    researcher: allow
    writer: allow
    editor: allow
    validator: allow
    reviewer: allow
---
