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

## Multiple development systems

Each development system should clone this repository and use the same tagged or
pinned revision. Run the workstation target locally with the default copy mode;
do not share one rendered home directory over the network. Each machine keeps
its own backups and deployment state, so `workflowctl audit` can report drift
per system.

Machine-specific provider credentials and tool authentication remain native to
that machine. Concrete model routes belong in the relevant tool adapter, while
common role behavior remains identical across systems.

## Hermes recommendation

Use Ansible as the only writer of Hermes runtime configuration. The recommended
flow is:

1. Pin this repository by tag or commit in Ansible inventory or role defaults.
2. Check out that revision on the Ansible controller.
3. Run `workflowctl render --target hermes` on the controller.
4. Validate the render manifest and copy the bundle through the Hermes role.
5. Resolve Vault references while templating on the target; never write secret
   values into the rendered workflow bundle.
6. Record the workflows revision in the deployed host metadata and validate
   drift through Ansible.

A checksummed release archive is a good future optimization. A Git clone plus a
target-side sync script is useful for development, but it creates a second
deployment authority and is not recommended for the managed Hermes host.

Jessica and Rachel remain owned by the existing Hermes instance and are excluded
from the common bundle until their usage establishes a long-term home.

## Dedicated OpenCode worker

`opencode-server` renders an OpenCode-only bundle for a future Proxmox guest.
Ansible should own the guest's service account, package versions, repository
checkouts, credentials, resource limits, scheduler/service units, and bundle
installation. The worker should run the orchestrator and OpenCode locally inside
the guest rather than exposing an unauthenticated OpenCode endpoint.

Keep its workspaces and runtime state separate from desktop homes. Pin both the
`agent-orchestrator` and workflow repository revisions, use copy deployment, and
retain rollback bundles. DNS name, Proxmox guest type, and Ansible inventory
group remain open decisions.
