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


def validate_repository(root: Path) -> list[str]:
    """Validate schemas and cross-document references. Raise on any error."""
    root = root.resolve()
    schema_dir = root / "schemas"
    bindings: list[tuple[Path, Path]] = [
        (schema_dir / "source-manifest.schema.json", root / "manifests/sources.yaml"),
        (schema_dir / "service-registry.schema.json", root / "services/registry.yaml"),
        (schema_dir / "mcp-registry.schema.json", root / "services/mcp/registry.yaml"),
        (schema_dir / "secret-catalog.schema.json", root / "secret-references/catalog.yaml"),
    ]
    bindings.extend(
        (schema_dir / "environment.schema.json", path)
        for path in sorted((root / "environments").glob("*.yaml"))
    )
    bindings.extend(
        (schema_dir / "target.schema.json", path)
        for path in sorted((root / "targets").glob("*.yaml"))
    )
    adapter_paths = [
        path for path in sorted(root.glob("*/deploy.yaml")) if path.parent.parent == root
    ]
    bindings.extend((schema_dir / "adapter.schema.json", path) for path in adapter_paths)

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

    sources = load_yaml(root / "manifests/sources.yaml")["sources"]
    source_ids = _unique_ids(sources, "source", errors)
    environments = [load_yaml(path) for path in sorted((root / "environments").glob("*.yaml"))]
    environment_ids = _unique_ids(environments, "environment", errors)
    services = load_yaml(root / "services/registry.yaml")["services"]
    service_ids = _unique_ids(services, "service", errors)
    secrets = load_yaml(root / "secret-references/catalog.yaml")["secrets"]
    secret_ids = _unique_ids(secrets, "secret", errors)

    service_registry = load_yaml(root / "services/registry.yaml")
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

    mcp_registry = load_yaml(root / "services/mcp/registry.yaml")
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

    for path in sorted((root / "targets").glob("*.yaml")):
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
    ]
    if errors:
        raise WorkflowError("validation failed:\n- " + "\n- ".join(errors))
    return messages


def load_target(root: Path, target_id: str) -> dict[str, Any]:
    path = root / "targets" / f"{target_id}.yaml"
    if not path.is_file():
        raise WorkflowError(f"unknown target: {target_id}")
    return load_yaml(path)
