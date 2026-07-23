---
description: Coordinates reset-safe loops by delegating one bounded specialist pass at a time.
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
    researcher: allow
    implementer: allow
    validator: allow
    tester: allow
    reviewer: allow
    writer: allow
    editor: allow
    git-committer: allow
---
