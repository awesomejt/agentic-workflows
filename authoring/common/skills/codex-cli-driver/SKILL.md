---
name: codex-cli-driver
description: Delegate a focused task to the OpenAI Codex CLI with version-aware preflight, explicit repository scope, and reproducible evidence capture. Use when one agent should invoke Codex non-interactively as an external worker.
---

# Codex CLI Driver

## Preconditions

- Require `codex` on `PATH` and existing tool-managed authentication.
- Know the target repository and focused task scope.
- Redact sensitive prompt material before recording evidence.

## Procedure

1. Run `command -v codex`, `codex --version`, and `codex --help`.
2. Determine the installed version's supported non-interactive invocation from
   its help output; do not assume flags from memory.
3. Invoke Codex with an explicit working directory, bounded task, required
   output, and validation expectations.
4. Capture the command shape, exit status, affected files, concise output, and
   residual risk without recording credentials.
5. Retry at most once and only when the failure is clearly transient.

## Output

```text
Tool: codex
Preflight:
Command shape:
Exit status:
Key output:
Files affected:
Validation:
Residual risks:
Recommended next role:
```
