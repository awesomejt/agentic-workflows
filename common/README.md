# Common Agentic Content

Files here express tool-agnostic behavior. They intentionally avoid provider
names, model identifiers, native permission schemas, and installation paths.

- `instructions/` contains behavior shared by primary agents.
- `prompts/` contains reusable task prompts.
- `roles/` contains behavioral contracts for focused agents or subagents.
- `skills/` contains portable Agent Skills.

Tool adapters may wrap these files with native frontmatter or configuration but
should not fork their semantic content without documenting an exception.
