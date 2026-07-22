# OpenCode Adapter

The adapter deploys global instructions, common skills, composed Markdown
subagents, the focused-task prompt, and two explicit primary agents.

`opencode.workflows.json` is an additive config overlay rather than a replacement
for the live global config. To test it without overwriting provider or model
settings:

```bash
OPENCODE_CONFIG="$HOME/.config/opencode/opencode.workflows.json" opencode
```

OpenCode merges this custom config with its global configuration. Review the
rendered diff before deployment. `afk-build` has deliberately broad permissions
and must remain an explicit opt-in profile.
