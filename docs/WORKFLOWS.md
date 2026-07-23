# Agentic workflows

The shared layer defines role behavior and stage transitions without assuming a
CLI, provider, model, or delegation syntax. Tool adapters decide how a role is
invoked and which concrete model or permission profile it receives.

## Common versus tool-specific concerns

| Shared in `common/` | Owned by each tool adapter |
| --- | --- |
| Role purpose, responsibilities, and output contract | Native agent file and frontmatter |
| Abstract model class (`reasoning`, `coding`, `writing`, `fast`) | Provider and model identifier |
| Reset-safe state and handoff protocol | Agent/subagent invocation syntax |
| Workflow stages, transitions, and completion gates | Native tools and permission policy |
| Example loop prompts | CLI discovery path and optional shortcuts |

`common/roles/catalog.yaml` is the cross-tool role inventory. A native adapter
may inherit the active model or map an abstract class to a concrete model. Such
a choice belongs in that adapter and must not be copied into a common role.

## Reset-safe execution

The canonical protocol is `common/workflows/protocol.md`. A run stores transient
coordination under `.agents/loop/<run-id>/`, which this repository ignores. Each
fresh-context specialist reads the immutable objective, current state, latest
handoff, and only relevant evidence, then performs one bounded role and exits.
The primary orchestrator owns transitions and the state file.

The initial workflows are:

- `software-development`: orchestration, project scoping, planning, design,
  challenge, implementation, validation, testing, review, documentation, SCM,
  and closeout.
- `content-creation`: orchestration, project scoping, planning, research,
  drafting, editing, factual validation, review, and closeout.

These are reusable stage graphs rather than an executable scheduler. The future
`agent-orchestrator` repository owns pass leasing, context creation, recovery,
and actual agent execution. A CLI tool can also run the protocol interactively
from the common prompts.

## Runtime hygiene

Pass notes are coordination records, not memory or raw transcripts. Durable
decisions belong in project documentation, `MEMORY.md`, or the authoritative
task system. State must not contain secrets. A completed run should retain only
what repository policy requires; cleanup still needs normal user authorization.
