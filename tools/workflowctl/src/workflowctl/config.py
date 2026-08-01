"""Repository configuration loading and validation."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import jsonschema
import yaml


class WorkflowError(RuntimeError):
    """A safe, user-facing workflow configuration error."""


ID_PATTERN = re.compile(r"^[a-z][a-z0-9-]*$")
SOURCE_DIR = "source"
AUTHORING_DIR = "authoring"
COMMON_DIR = "common"
ADAPTERS_DIR = "adapters"
TEMPLATES_DIR = "templates"


def find_repository_root(start: Path | None = None) -> Path:
    """Find the repository root from a path inside the checkout."""
    current = (start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "schemas").is_dir():
            return candidate
    raise WorkflowError(f"cannot find agentic-workflows repository above {current}")


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping and provide a path-specific error."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise WorkflowError(f"cannot load {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise WorkflowError(f"{path} must contain a YAML mapping")
    return data


def runtime_environment(home: Path | None = None) -> dict[str, str]:
    """Build path variables, safely redirecting all defaults for test homes."""
    env = dict(os.environ)
    if home is not None:
        resolved_home = str(home.expanduser().resolve())
        env.update(
            {
                "HOME": resolved_home,
                "XDG_CONFIG_HOME": f"{resolved_home}/.config",
                "XDG_STATE_HOME": f"{resolved_home}/.local/state",
                "CODEX_HOME": f"{resolved_home}/.codex",
                "CLAUDE_HOME": f"{resolved_home}/.claude",
                "GROK_HOME": f"{resolved_home}/.grok",
            }
        )
    else:
        resolved_home = env.get("HOME", str(Path.home()))
        env.setdefault("XDG_CONFIG_HOME", f"{resolved_home}/.config")
        env.setdefault("XDG_STATE_HOME", f"{resolved_home}/.local/state")
        env.setdefault("CODEX_HOME", f"{resolved_home}/.codex")
        env.setdefault("CLAUDE_HOME", f"{resolved_home}/.claude")
        env.setdefault("GROK_HOME", f"{resolved_home}/.grok")
    return env


def expand_path(value: str, env: dict[str, str]) -> Path:
    """Expand only explicit ${VARIABLE} path placeholders."""
    missing = sorted(set(re.findall(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", value)) - env.keys())
    if missing:
        raise WorkflowError(f"unresolved path variable(s): {', '.join(missing)}")
    expanded = value
    for key in sorted(env, key=len, reverse=True):
        expanded = expanded.replace(f"${{{key}}}", env[key])
    return Path(expanded).expanduser()


def safe_relative(value: str, label: str) -> Path:
    """Return a destination path that cannot escape its configured root."""
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise WorkflowError(f"{label} must be a relative path without '..': {value}")
    return path


def source_root(root: Path) -> Path:
    """Return the canonical repository subtree for config source records."""
    return root / SOURCE_DIR


def source_path(root: Path, *parts: str) -> Path:
    """Build a repository path under the source subtree."""
    return source_root(root).joinpath(*parts)


def authoring_root(root: Path) -> Path:
    """Return the canonical repository subtree for authored reusable content."""
    return root / AUTHORING_DIR


def authoring_path(root: Path, *parts: str) -> Path:
    """Build a repository path under the authoring subtree."""
    return authoring_root(root).joinpath(*parts)


def adapter_root(root: Path, adapter_id: str) -> Path:
    """Return the canonical repository path for one adapter."""
    return authoring_path(root, ADAPTERS_DIR, adapter_id)


def adapter_manifest_paths(root: Path) -> list[Path]:
    """Return all adapter deploy manifests in stable order."""
    return sorted(authoring_path(root, ADAPTERS_DIR).glob("*/deploy.yaml"))


def adapter_routing_paths(root: Path) -> list[Path]:
    """Return all adapter routing manifests in stable order."""
    return sorted(authoring_path(root, ADAPTERS_DIR).glob("*/routing.yaml"))


def _validate_document(schema_path: Path, data_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        data = load_yaml(data_path)
        validator = jsonschema.Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{data_path.relative_to(data_path.parents[1])}:{location}: {error.message}")
    except (OSError, json.JSONDecodeError, jsonschema.SchemaError, WorkflowError) as exc:
        errors.append(f"{data_path}: {exc}")
    return errors


def _unique_ids(items: list[dict[str, Any]], label: str, errors: list[str]) -> set[str]:
    ids: set[str] = set()
    for item in items:
        item_id = item.get("id")
        if isinstance(item_id, str) and item_id in ids:
            errors.append(f"duplicate {label} id: {item_id}")
        elif isinstance(item_id, str):
            ids.add(item_id)
    return ids


def _find_embedded_secret_keys(value: Any, prefix: str = "") -> list[str]:
    """Find credential-bearing keys that contracts must replace with secret refs."""
    forbidden = {"api_key", "password", "token", "credential", "credentials", "secret"}
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            location = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower().replace("-", "_") in forbidden:
                findings.append(location)
            findings.extend(_find_embedded_secret_keys(child, location))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_find_embedded_secret_keys(child, f"{prefix}[{index}]"))
    return findings


def validate_repository(root: Path) -> list[str]:
    """Validate schemas and cross-document references. Raise on any error."""
    root = root.resolve()
    schema_dir = root / "schemas"
    bindings: list[tuple[Path, Path]] = [
        (schema_dir / "source-manifest.schema.json", source_path(root, "manifests", "sources.yaml")),
        (schema_dir / "content-manifest.schema.json", source_path(root, "manifests", "content.yaml")),
        (schema_dir / "role-catalog.schema.json", authoring_path(root, "common", "roles", "catalog.yaml")),
        (schema_dir / "service-registry.schema.json", source_path(root, "services", "registry.yaml")),
        (schema_dir / "mcp-registry.schema.json", source_path(root, "services", "mcp", "registry.yaml")),
        (schema_dir / "secret-catalog.schema.json", source_path(root, "secret-references", "catalog.yaml")),
        (schema_dir / "template-catalog.schema.json", authoring_path(root, "templates", "catalog.yaml")),
    ]
    bindings.extend(
        (schema_dir / "environment.schema.json", path)
        for path in sorted(source_path(root, "environments").glob("*.yaml"))
    )
    bindings.extend(
        (schema_dir / "target.schema.json", path)
        for path in sorted(source_path(root, "targets").glob("*.yaml"))
    )
    service_contract_paths = sorted(source_path(root, "services").glob("*/contract.yaml"))
    bindings.extend(
        (schema_dir / "service-contract.schema.json", path)
        for path in service_contract_paths
    )
    adapter_paths = adapter_manifest_paths(root)
    bindings.extend((schema_dir / "adapter.schema.json", path) for path in adapter_paths)
    routing_paths = adapter_routing_paths(root)
    bindings.extend((schema_dir / "role-routing.schema.json", path) for path in routing_paths)
    workflow_paths = sorted(authoring_path(root, "common", "workflows").glob("*.yaml"))
    bindings.extend((schema_dir / "workflow.schema.json", path) for path in workflow_paths)

    errors: list[str] = []
    for schema_path, data_path in bindings:
        if not schema_path.is_file():
            errors.append(f"missing schema: {schema_path.relative_to(root)}")
        elif not data_path.is_file():
            errors.append(f"missing document: {data_path.relative_to(root)}")
        else:
            errors.extend(_validate_document(schema_path, data_path))

    if errors:
        raise WorkflowError("validation failed:\n- " + "\n- ".join(errors))

    sources = load_yaml(source_path(root, "manifests", "sources.yaml"))["sources"]
    source_ids = _unique_ids(sources, "source", errors)
    role_catalog = load_yaml(authoring_path(root, "common", "roles", "catalog.yaml"))
    roles = role_catalog["roles"]
    role_ids = _unique_ids(roles, "role", errors)
    for role in roles:
        source = (root / role["source"]).resolve()
        if root not in source.parents or not source.is_file():
            errors.append(f"role {role['id']} source does not exist: {role['source']}")
    aliases = load_yaml(authoring_path(root, "common", "roles", "aliases.yaml")).get("aliases", {})
    for alias, role_id in aliases.items():
        if role_id not in role_ids:
            errors.append(f"role alias {alias} has unknown role: {role_id}")
    routing_ids: set[str] = set()
    for path in routing_paths:
        routing = load_yaml(path)
        routing_id = routing["id"]
        if routing_id in routing_ids:
            errors.append(f"duplicate role routing id: {routing_id}")
        routing_ids.add(routing_id)
        if path.parent.name != routing_id:
            errors.append(
                f"role routing id {routing_id} does not match directory {path.parent.name}"
            )
        for override in routing["overrides"]:
            if override["role"] not in role_ids:
                errors.append(
                    f"role routing {routing_id} has unknown role: {override['role']}"
                )

    workflow_ids: set[str] = set()
    for path in workflow_paths:
        workflow = load_yaml(path)
        workflow_id = workflow["id"]
        if workflow_id in workflow_ids:
            errors.append(f"duplicate workflow id: {workflow_id}")
        workflow_ids.add(workflow_id)
        stage_ids = _unique_ids(workflow["stages"], f"{workflow_id} stage", errors)
        if workflow["entry_stage"] not in stage_ids:
            errors.append(
                f"workflow {workflow_id} has unknown entry_stage: {workflow['entry_stage']}"
            )
        for stage in workflow["stages"]:
            if stage["role"] not in role_ids:
                errors.append(
                    f"workflow {workflow_id} stage {stage['id']} has unknown role: "
                    f"{stage['role']}"
                )
            for transition_key in ("on_success", "on_failure"):
                transition = stage.get(transition_key)
                if transition and transition not in stage_ids | {"complete", "blocked"}:
                    errors.append(
                        f"workflow {workflow_id} stage {stage['id']} has unknown "
                        f"{transition_key}: {transition}"
                    )
    artifacts = load_yaml(source_path(root, "manifests", "content.yaml"))["artifacts"]
    _unique_ids(artifacts, "content artifact", errors)
    for artifact in artifacts:
        if artifact["source"] not in source_ids:
            errors.append(
                f"content artifact {artifact['id']} has unknown source: {artifact['source']}"
            )
        destination = artifact.get("destination")
        if destination and artifact["disposition"] == "migrate-common":
            destination_path = (root / destination).resolve()
            if root not in destination_path.parents:
                errors.append(f"content artifact {artifact['id']} destination escapes repository")
            elif not destination_path.exists():
                errors.append(
                    f"content artifact {artifact['id']} destination does not exist: {destination}"
                )
    template_catalog = load_yaml(authoring_path(root, "templates", "catalog.yaml"))
    _unique_ids(template_catalog["templates"], "template", errors)
    for template in template_catalog["templates"]:
        if template["source"] not in source_ids:
            errors.append(f"template {template['id']} has unknown source: {template['source']}")
    environments = [load_yaml(path) for path in sorted(source_path(root, "environments").glob("*.yaml"))]
    environment_ids = _unique_ids(environments, "environment", errors)
    services = load_yaml(source_path(root, "services", "registry.yaml"))["services"]
    service_ids = _unique_ids(services, "service", errors)
    secrets = load_yaml(source_path(root, "secret-references", "catalog.yaml"))["secrets"]
    secret_ids = _unique_ids(secrets, "secret", errors)

    service_registry = load_yaml(source_path(root, "services", "registry.yaml"))
    if service_registry["environment"] not in environment_ids:
        errors.append(f"unknown service environment: {service_registry['environment']}")
    for service in services:
        owner = service["owner"]["repository"]
        if owner not in source_ids:
            errors.append(f"service {service['id']} has unknown owner repository: {owner}")
        for secret_ref in service.get("secret_refs", []):
            if secret_ref not in secret_ids:
                errors.append(f"service {service['id']} has unknown secret_ref: {secret_ref}")
        health_secret = service.get("healthcheck", {}).get("secret_ref")
        if health_secret and health_secret not in secret_ids:
            errors.append(f"service {service['id']} has unknown healthcheck secret_ref: {health_secret}")

    for path in service_contract_paths:
        contract = load_yaml(path)
        if contract["service_ref"] not in service_ids:
            errors.append(
                f"service contract {path.relative_to(root)} has unknown service_ref: "
                f"{contract['service_ref']}"
            )
        if contract["owner"]["repository"] not in source_ids:
            errors.append(
                f"service contract {path.relative_to(root)} has unknown owner repository: "
                f"{contract['owner']['repository']}"
            )
        for secret_ref in contract.get("secret_refs", []):
            if secret_ref not in secret_ids:
                errors.append(
                    f"service contract {path.relative_to(root)} has unknown secret_ref: {secret_ref}"
                )
        for location in _find_embedded_secret_keys(contract):
            errors.append(
                f"service contract {path.relative_to(root)} embeds forbidden credential key: "
                f"{location}; use secret_ref"
            )

    mcp_registry = load_yaml(source_path(root, "services", "mcp", "registry.yaml"))
    if mcp_registry["environment"] not in environment_ids:
        errors.append(f"unknown MCP environment: {mcp_registry['environment']}")
    mcp_ids = _unique_ids(mcp_registry["servers"], "MCP server", errors)
    for server in mcp_registry["servers"]:
        service_ref = server.get("service_ref")
        if service_ref and service_ref not in service_ids:
            errors.append(f"MCP server {server['id']} has unknown service_ref: {service_ref}")
        for secret_ref in server.get("secret_refs", []):
            if secret_ref not in secret_ids:
                errors.append(f"MCP server {server['id']} has unknown secret_ref: {secret_ref}")

    adapter_ids: set[str] = set()
    for path in adapter_paths:
        adapter = load_yaml(path)
        adapter_ids.add(adapter["id"])
        if path.parent.name != adapter["id"]:
            errors.append(f"adapter id {adapter['id']} does not match directory {path.parent.name}")
        for artifact in adapter["artifacts"]:
            safe_relative(artifact["destination"], f"{adapter['id']} artifact destination")
            source = (root / artifact["source"]).resolve()
            if root not in source.parents and source != root:
                errors.append(f"adapter {adapter['id']} source escapes repository: {artifact['source']}")
            elif not source.exists():
                errors.append(f"adapter {adapter['id']} source does not exist: {artifact['source']}")
            if source.is_dir() and (artifact.get("header") or artifact.get("footer")):
                errors.append(
                    f"adapter {adapter['id']} cannot wrap directory source: {artifact['source']}"
                )
            for wrapper_key in ("header", "footer"):
                wrapper_value = artifact.get(wrapper_key)
                if not wrapper_value:
                    continue
                wrapper = (root / wrapper_value).resolve()
                if root not in wrapper.parents or not wrapper.is_file():
                    errors.append(
                        f"adapter {adapter['id']} {wrapper_key} does not exist: {wrapper_value}"
                    )

    for path in sorted(source_path(root, "targets").glob("*.yaml")):
        target = load_yaml(path)
        if target["environment"] not in environment_ids:
            errors.append(f"target {target['id']} has unknown environment: {target['environment']}")
        for adapter in target["adapters"]:
            if adapter["id"] not in adapter_ids:
                errors.append(f"target {target['id']} has unknown adapter: {adapter['id']}")

    messages = [
        f"validated {len(bindings)} documents",
        f"resolved {len(source_ids)} sources, {len(service_ids)} services, "
        f"{len(mcp_ids)} MCP servers, and {len(secret_ids)} secret references",
        f"resolved {len(role_ids)} roles and {len(workflow_ids)} workflows",
        f"resolved {len(routing_ids)} tool-specific role routing maps",
    ]
    if errors:
        raise WorkflowError("validation failed:\n- " + "\n- ".join(errors))
    return messages


def load_target(root: Path, target_id: str) -> dict[str, Any]:
    path = source_path(root, "targets", f"{target_id}.yaml")
    if not path.is_file():
        raise WorkflowError(f"unknown target: {target_id}")
    return load_yaml(path)
