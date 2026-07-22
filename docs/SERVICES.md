# AI Service Configuration Contracts

This repository records the client-visible contract for local AI services;
`taylor-ansible` remains authoritative for deployment. The reviewed source is
Ansible revision `79944d7875ab1ff1673c16bac79c489d30a7e1a0`.

## Captured services

| Service | Contract captured here | Deployment owner |
| --- | --- | --- |
| LiteLLM | aliases, routes, fallbacks, required models, PostgreSQL reference | `roles/litellm` |
| Ollama | endpoint, seeded models, consumer-required embedding model | `roles/ollama` |
| oMLX | two endpoints, purpose-specific models, shared credential reference | external hosts via client roles |
| Open WebUI | provider order, task model, LDAP, SearXNG, Qdrant, Ollama | `roles/open-webui` |
| Qdrant | storage boundary and MCP collection/embedding contract | `roles/qdrant` |
| SearXNG | JSON search and MCP/Valkey contract | `roles/searxng` |
| AnythingLLM | LiteLLM chat, Ollama embeddings, Qdrant vector store | `roles/anythingllm` |
| n8n | public endpoint and runtime metadata | `roles/n8n` |

Hermes consumes a generated subset of these contracts through its bundle. MCP
server endpoints are canonical in `services/mcp/registry.yaml` and rendered in
tool-native adapters.

## Ownership rule

Configuration belongs here when agents need it to select a model alias, locate
a service, render a client, or validate compatibility. Container images,
Compose/systemd templates, host paths, service accounts, firewall and proxy
configuration, and secret injection stay in Ansible.

Each contract pins the observed Ansible revision. After an Ansible change,
compare the relevant role defaults/template with the contract and update both
the revision and any changed client behavior in one commit.

## Known configuration gap

AnythingLLM and Hermes reference `nomic-embed-text:latest`, but the reviewed
Ollama role pull list does not seed that model. The contract flags this rather
than silently claiming the runtime already satisfies it. Resolve it in Ansible,
then update the contract status.

## Secrets

`secret-references/catalog.yaml` names the owning Vault variables and validation
mechanism. Contracts refer only to those IDs. Do not render, probe, or log a
credential value from this repository.
