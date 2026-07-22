# Deployment Guide

## Prerequisites

- Python 3.11 or newer
- PyYAML 6.x
- jsonschema 4.x

Run from a checkout without installing the package:

```bash
bin/workflowctl --help
```

For an editable installation:

```bash
python3 -m pip install -e tools/workflowctl
```

## Safe workflow

Always validate, render, and compare before a live deployment:

```bash
bin/workflowctl validate
bin/workflowctl render --target workstation
bin/workflowctl diff --target workstation --content
bin/workflowctl deploy --target workstation --dry-run
```

The convenience wrapper deploys the workstation target by default:

```bash
./deploy.sh --dry-run
```

Set `WORKFLOWS_TARGET` to choose another deployable target. Bundle targets such
as Hermes render an artifact and do not write target hosts directly.

## Isolated-home validation

The `--home` option redirects `HOME`, XDG configuration/state roots, and the
Claude, Codex, and Grok home directories. Use it to exercise real deployment
behavior without modifying live files:

```bash
test_home="$(mktemp -d)"
bin/workflowctl deploy --target workstation --home "$test_home"
bin/workflowctl audit --target workstation --home "$test_home"
```

## Live deployment

After reviewing the diff:

```bash
bin/workflowctl deploy --target workstation
```

Changed files are backed up beneath the target's configured `backup_root`.
Deployment state, including expected hashes and destinations, is written beneath
`state_root`. Neither location is inside the repository.

Use symlinks only when intentionally requested:

```bash
bin/workflowctl deploy --target workstation --mode symlink
```

Symlinks point at the rendered staging tree, so that tree must remain available.
Copy mode is the default and recommended mode.

## Drift audit

```bash
bin/workflowctl audit --target workstation
```

Audit states are `clean`, `drifted`, `missing`, and `broken-symlink`. Audit
returns a non-zero status if any managed file is not clean.

## Diagnostics

Local diagnostics validate the repository, locate installed CLIs, and report
configured destination paths:

```bash
bin/workflowctl doctor --target workstation
```

Network checks are opt-in:

```bash
bin/workflowctl doctor --target workstation --network
```

Health checks requiring authentication are skipped rather than resolving or
printing a secret. Network failures never reveal credential values.

## Recovery

If a deployment needs to be rolled back:

1. Locate the timestamped backup under `backup_root`.
2. Restore only the affected files.
3. Rerun `workflowctl diff` and `workflowctl audit`.
4. Correct the adapter or target before deploying again.

The deployer never deletes unmanaged files from a destination.
