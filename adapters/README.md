# Tool Adapters

This directory contains provider-specific adapter surfaces only.

- Edit `common/` first when the change is shared behavior, prompt logic, role
  content, skill instructions, or workflow structure.
- Edit one adapter here only when the change is native metadata, routing,
  frontmatter, destination mapping, config overlay, or a justified behavioral
  exception for that tool.
- Rendered output under `.build/` is generated from these sources and should
  not be edited directly.