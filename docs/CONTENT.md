# Common Content Model

## Purpose

The `common/` tree is the semantic source for behavior shared across agent
tools. It is the default place to edit shared agent definitions and skills.
Tool adapters under `adapters/` add only native metadata, permission syntax,
destination paths, and justified exceptions.

## Roles

Roles are concise behavioral contracts rather than complete tool-native agent
definitions. `common/roles/catalog.yaml` is the machine-readable inventory:

- coordination: `orchestrator`, `project-manager`
- analysis: `planner`, `designer`, `debater`, `researcher`
- production: `implementer`, `writer`, `editor`
- assurance: `validator`, `tester`, `reviewer`
- source control: `git-committer`

The catalog's model classes are workload hints, not provider selections. Native
models and permission profiles belong in `adapters/<tool>/routing.yaml` and
frontmatter.

Compatibility aliases live in `common/roles/aliases.yaml`. New content should
use canonical names; adapters may emit aliases during migration when existing
automation still refers to an old name.

## Prompts and instructions

Instructions describe always-on behavior. Prompts describe a reusable task or
session workflow. The focused-task prompt deliberately avoids a specific CLI,
task database, or model provider. Repository instructions decide which task
system and documentation files are authoritative. Reset-safe stage graphs and
the `.agents/loop/` handoff contract live in `common/workflows/`.

## Skills

Shared skills follow the portable Agent Skills directory shape:

```text
common/skills/<skill-name>/
└── SKILL.md
```

Each `SKILL.md` has only `name` and `description` in frontmatter. Triggering
conditions belong in the description; the body contains concise imperative
procedures and guardrails. Add `scripts/`, `references/`, or `assets/` only
when the skill genuinely needs them.

A deterministic helper used by several skills belongs under top-level `tools/`.
A helper exclusive to one skill belongs inside that skill's `scripts/` folder.

Loop capabilities are split by responsibility:

- `agentic-loop-pass` owns backend-neutral pass policy and outcome rules.
- `loop-handoff-notes` owns transient specialist exchanges and result files.
- `awb-project-task-management` maps durable operations to AWB.
- `project-yaml-state-management` provides the local flat-file alternative with
  an exclusive helper script; agents must not hand-edit active state.

## Provenance

`manifests/content.yaml` records the source repository, path, exact source
revision, sensitivity, chosen disposition, and destination. Normalized content
is not expected to remain byte-identical to its source, so the source revision
and migration notes are the durable audit trail.

Supported dispositions are documented in `docs/MIGRATION.md`. A source artifact
is not considered reviewed until it has one explicit disposition.
