# Common Agentic Content

Files here express tool-agnostic behavior. They intentionally avoid provider
names, model identifiers, native permission schemas, and installation paths.

- `instructions/` contains behavior shared by primary agents.
- `prompts/` contains reusable task prompts.
- `roles/` contains behavioral contracts for focused agents or subagents.
- `skills/` contains portable Agent Skills.
- `workflows/` contains reset-safe stage graphs and the `.agents/loop/` handoff
  protocol used when context is reset between passes.

`roles/catalog.yaml` supplies abstract routing hints such as `coding` or
`reasoning`. It does not select a provider or model. Each tool adapter maps those
hints to native configuration, permissions, and invocation syntax.

Tool adapters may wrap these files with native frontmatter or configuration but
should not fork their semantic content without documenting an exception.
