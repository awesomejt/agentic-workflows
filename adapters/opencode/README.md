# OpenCode Adapter

The adapter deploys global instructions, common skills and workflows, composed
Markdown subagents, reusable prompts, two reset-safe loop agents, and two
existing primary agents.

`routing.yaml` documents the intentional model exceptions. The generic
orchestrator, implementer, AWB orchestrator, and opt-in AFK build use
`ollama-direct/local-coding`; other roles inherit the active session model.

`opencode.workflows.json` is an additive config overlay rather than a replacement
for the live global config. To test it without overwriting provider or model
settings:

```bash
OPENCODE_CONFIG="$HOME/.config/opencode/opencode.workflows.json" opencode
```

OpenCode merges this custom config with its global configuration. Review the
rendered diff before deployment. `afk-build` has deliberately broad permissions
and must remain an explicit opt-in profile.
