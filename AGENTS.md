# Instructions for AI Coding Assistants

This repository owns reusable agentic workflow assets and the tooling used to
deploy them. It must remain safe to clone without exposing credentials or
runtime data.

## Required first reads

Before changing the repository, read:

- `README.md`
- `docs/REQUIREMENTS.md`
- `docs/DESIGN.md`
- `MEMORY.md`
- `TODO.md`
- Relevant adapter, service, or tool documentation

## Working rules

1. Implement one roadmap task per commit.
2. Keep commits independently reviewable and validated.
3. Update `TODO.md` as task state changes.
4. Record durable decisions and meaningful sessions in `MEMORY.md`.
5. Record questions requiring owner input in `docs/OPEN_QUESTIONS.md`.
6. Prefer shared definitions under `authoring/common/`; adapter-specific files
   live under `authoring/adapters/` and contain only rendering logic,
   exceptions, and tool-native configuration.
7. Put a helper used by multiple skills or agents under `tools/`. Keep a helper
   used by one skill inside that skill's `scripts/` directory.
8. Do not copy orchestration runtime code or Ansible service roles here.
9. Do not commit secrets, raw transcripts, auth state, generated output, or
   machine-specific caches.

## Validation

- Run the repository test suite for code changes.
- Run `workflowctl validate` once it is available.
- Exercise deployments with `--dry-run` before writing a live target.
- Review staged changes for secret-like values before every commit.
