# Orchestrator Repository Extraction Plan

The OpenCode orchestrator currently lives at `opencode-setup/orchestrator` at
revision `cc5b212c0dad8e6ff6f9d940044458c36db842fb`. It is a UV-managed Python
application with a compatibility installer, one package, and unit tests. Its
runtime responsibility is AWB task selection, lease ownership, heartbeat, and
launching one OpenCode process; it must not own agent definitions or tool
configuration after extraction.

## Target boundary

The confirmed target is `/shared/projects/dev/agent-orchestrator` (user-facing
path `~/projects/dev/agent-orchestrator`) with remote
`git@github.com:awesomejt/agent-orchestrator.git`. At reviewed revision
`7337f2a81ce308d65b3c1090b221199345a28b88`, it contains only its initial
README commit. The extracted repository owns:

- orchestration Python package, CLI, tests, lockfile, and installation;
- AWB selection, claim, lease heartbeat, status gating, and loop scheduling;
- compatibility wrappers currently implemented by `afk-run.sh` and
  `automated-run.sh`;
- runtime logs and locking policy, but not the logs themselves.

This repository owns prompts, role IDs and aliases, OpenCode agents, skills,
MCP configuration, and deployment. The orchestrator consumes those assets only
through deployed tool configuration or a rendered workflow bundle.

## History-preserving extraction

Use a temporary filtered clone so the existing target repository and remote are
not rewritten in place:

```bash
git clone --no-local /shared/projects/ai/opencode-setup /tmp/agent-orchestrator-extract
cd /tmp/agent-orchestrator-extract
git filter-repo \
  --path orchestrator/ \
  --path scripts/afk-run.sh \
  --path scripts/automated-run.sh \
  --path-rename orchestrator/: \
  --path-rename scripts/afk-run.sh:compat/afk-run.sh \
  --path-rename scripts/automated-run.sh:compat/automated-run.sh

cd ~/projects/dev/agent-orchestrator
git remote add extraction /tmp/agent-orchestrator-extract
git fetch extraction
git merge --allow-unrelated-histories extraction/main
```

Resolve the expected README collision, then inspect and test before removing the
temporary remote. Do not force-push or replace the existing remote. Exclude local
`.venv`, cache, log, and transcript artifacts even if they exist in the source
checkout. No push is part of this repository's migration task.

## Bundle interface

Replace `OPENCODE_SETUP_ASSET_DIR` coupling with these inputs:

- `AGENTIC_WORKFLOWS_ROOT`: optional checkout or installed bundle root;
- `AGENTIC_WORKFLOWS_PROMPT`: explicit rendered prompt path;
- `OPENCODE_AGENT`: native primary-agent ID, default `awb-orchestrator`;
- a workflow render manifest path when provenance must be recorded.

The application must treat bundle files as data. It must not import
`workflowctl`, reach into this Git checkout by relative path, or mutate common
assets. Canonical role names are `implementer`, `writer`, and `git-committer`;
legacy names remain bundle aliases during cutover.

## Cutover sequence

1. Freeze and tag the source orchestrator revision.
2. Rewrite history into the named repository and remove setup-repository paths.
3. Update installer defaults from `opencode-setup` to the new application name.
4. Add bundle-path tests and retain all existing AWB lease/heartbeat tests.
5. Install both old and new commands side by side and compare dry-run prompts.
6. Switch scheduler entries to the new command.
7. Observe at least one successful claim, heartbeat, completion/block cycle.
8. Remove compatibility scripts from `opencode-setup` only after rollback has
   been tested.
9. Update `manifests/content.yaml` with the new remote and extraction commit.

Rollback is a scheduler change back to the old installed command; do not delete
the source directory until the new repository has been backed up and tagged.
