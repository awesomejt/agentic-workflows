# Migration Security Findings

## 2026-07-22 source review

- `hermes-setup/AGENTS.md` contains a
  plaintext oMLX credential. The value was not copied here. Remove it from the
  source file, rotate the credential, and rely on the existing `omlx-api-key`
  Vault reference before treating that repository as migration-safe.
- Several Ansible role defaults use obvious fallback placeholders such as
  `change-me` or `example`. They are not treated as credentials here, but
  deployment validation should fail closed when the Vault variable is absent
  rather than starting a service with a placeholder.
- Tool-native auth, profile memory, transcripts, caches, and OAuth state remain
  excluded from every adapter and bundle.

Do not record discovered credential values in issues, commits, logs, task
evidence, or chat transcripts. Security remediation should reference only the
source path, owning secret ID, and rotation status.
