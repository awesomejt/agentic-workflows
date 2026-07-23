---
description: Runs a reset-safe software development loop using focused subagents.
mode: primary
model: ollama-direct/local-coding
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
    designer: allow
    debater: allow
    implementer: allow
    validator: allow
    tester: allow
    reviewer: allow
    writer: allow
    git-committer: allow
---
