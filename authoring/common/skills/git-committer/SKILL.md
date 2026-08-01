---
name: git-committer
description: Inspect Git state, stage an explicitly scoped change, create a validated commit, and optionally push when separately authorized. Use when an agent is asked to prepare or create a commit without including unrelated work.
---

# Git Committer

## Guardrails

- Preserve unrelated changes and stage only the explicit task scope.
- Confirm required validation before committing.
- Do not amend, rewrite history, force-push, or discard changes unless explicitly
  authorized.
- Treat commit authorization and push authorization as separate decisions.

## Procedure

```bash
git status --short --branch
git diff --stat
git diff -- <path>
git add <path>
git diff --cached --stat
git diff --cached
git commit -m "<type(scope): summary>"
```

Run `git push` only when explicitly authorized. If a command fails, report the
command, concise error, current repository state, and a safe next step rather
than retrying blindly.

Report the branch, scoped files, validation, commit message, commit hash, push
result, and exclusions.
