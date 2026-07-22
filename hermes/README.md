# Hermes Adapter

The Hermes adapter produces a versioned bundle; it does not deploy the Hermes
host. The bundle contains common behavior, profile source mappings, and the
client-facing LiteLLM, Ollama, and MCP contracts.

```bash
bin/workflowctl render --target hermes
```

The Ansible `roles/hermes` role remains responsible for installation paths,
profile instances, services, environment files, and secret injection. Its
integration contract is recorded in `ansible-contract.yaml`.

SOUL files are referenced by source repository and exact revision rather than
duplicated here. Personal identities and private workflows require an explicit
private overlay decision before migration.
