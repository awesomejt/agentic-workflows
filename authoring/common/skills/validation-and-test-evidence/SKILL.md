---
name: validation-and-test-evidence
description: Select proportionate validation and test commands, capture reproducible evidence, and distinguish blocking failures from residual risk. Use when implementing, validating, testing, or reviewing changes that need defensible pass/fail evidence.
---

# Validation and Test Evidence

## Inputs

- Read the task requirements and affected behavior.
- Read repository-local validation commands and conventions.
- Inspect the changed files and relevant contracts.

## Procedure

1. Run the fastest targeted check that covers the changed behavior.
2. Broaden checks when risk is medium or high, contracts span components, or a
   targeted check fails.
3. Capture exact commands, exit outcomes, and the behavior each check covers.
4. Separate blocking failures from non-blocking limitations and residual risk.
5. If a command cannot run, state the dependency, environment, permission, or
   fixture gap; do not convert an unrun check into a pass.

## Evidence format

```text
Checks run:
Passed:
Failed:
Evidence:
Blocking issues:
Residual risk:
Recommended next role:
```

Do not claim success without direct evidence. Return reproducible failures to
the implementer and material risk questions to the reviewer.
