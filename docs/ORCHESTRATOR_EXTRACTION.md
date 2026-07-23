# Orchestrator Repository Extraction

Status: completed locally at `agent-orchestrator`
`8f8f24185d0b0cd17ab4dd124ad41ed53a580b09`. The repository has not been
pushed and no live scheduler has been changed.

The original OpenCode orchestrator remains at `opencode-setup/orchestrator` at
revision `cc5b212c0dad8e6ff6f9d940044458c36db842fb`. It is retained temporarily
for rollback.

## Target boundary

The target is `/shared/projects/dev/agent-orchestrator` (user-facing path
`~/projects/dev/agent-orchestrator`) with remote
`git@github.com:awesomejt/agent-orchestrator.git`. Its original initial commit
was `7337f2a81ce308d65b3c1090b221199345a28b88`. The populated repository owns:

- orchestration Python package, CLI, tests, lockfile, and installation;
- backend-neutral scheduling and structured-result validation;
- AWB inspection, atomic pass start/finish, lease heartbeat, and recovery
  through a project-state adapter;
- OpenCode and deterministic fixture execution adapters;
- compatibility wrappers for `opencode-orchestrator`, `afk-run.sh`, and
  `automated-run.sh`;
- runtime handoff, logging, and locking policy, but not runtime artifacts.

This repository owns prompts, role IDs and aliases, OpenCode agents, skills,
MCP configuration, and deployment. The orchestrator consumes those assets as
data through a separately deployed workflow bundle.

## History-preserving extraction used

`git-filter-repo` was not installed. The equivalent safe extraction used
`git subtree split`, followed by an unrelated-history merge into the existing
target. This preserved the source commits without rewriting the target remote:

```bash
git clone --no-local /shared/projects/ai/opencode-setup /tmp/agent-orchestrator-extract
cd /tmp/agent-orchestrator-extract
git subtree split --prefix=orchestrator -b extracted

cd ~/projects/dev/agent-orchestrator
git remote add extraction /tmp/agent-orchestrator-extract
git fetch extraction extracted
git merge --allow-unrelated-histories extraction/extracted
```

The expected README collision was resolved, the temporary remote was removed,
and local runtime artifacts were excluded. The merge commit is `624bc6f`; the
backend-neutral implementation commit is `8f8f241`.

## Bundle interface

The implementation replaced `OPENCODE_SETUP_ASSET_DIR` coupling with:

- `AGENTIC_WORKFLOWS_ROOT`: checkout or installed bundle root;
- `AGENTIC_WORKFLOW`: selected declarative workflow ID;
- native execution-adapter selection and tool-specific agent/model overrides;
- `AGENT_ORCHESTRATOR_RESULT`: structured result path supplied to the executor.

The application treats bundle files as immutable data. It does not import
`workflowctl`, mutate common assets, or own native agent definitions.

## Cutover sequence

1. [x] Freeze the source orchestrator revision in the content manifest.
2. [x] Transfer its history into the named repository.
3. [x] Update installer defaults and retain compatibility command names.
4. [x] Add workflow loading, pass lifecycle, result, and failure-path tests.
5. [x] Validate the installer and local AWB complete, partial/resume, blocked,
   recovery-selection, and repeated-heartbeat paths.
6. [ ] Install both old and new commands side by side on a pilot workstation.
7. [ ] Switch scheduler entries to the new command after pilot review.
8. [ ] Remove compatibility scripts from `opencode-setup` only after rollback
   has been tested.
9. [x] Record the extracted repository revision in repository manifests.

Rollback is a scheduler change back to the old installed command; do not delete
the source directory until the new repository has been backed up and tagged.
