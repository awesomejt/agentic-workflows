"""Command-line interface for workflowctl."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import WorkflowError, find_repository_root, validate_repository
from .engine import (
    audit_target,
    compare_target,
    deploy_target,
    doctor,
    inventory,
    render_target,
    unified_diff,
)


def _root(value: str | None) -> Path:
    return Path(value).resolve() if value else find_repository_root(Path(__file__))


def _home(value: str | None) -> Path | None:
    return Path(value).resolve() if value else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workflowctl")
    parser.add_argument("--repo", help="agentic-workflows repository root")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="validate schemas and cross-references")
    subparsers.add_parser("inventory", help="list repository targets and registries")

    render = subparsers.add_parser("render", help="render a target into staging")
    render.add_argument("--target", required=True)
    render.add_argument("--output")

    diff = subparsers.add_parser("diff", help="compare rendered and deployed files")
    diff.add_argument("--target", required=True)
    diff.add_argument("--home")
    diff.add_argument("--output")
    diff.add_argument("--content", action="store_true", help="include unified text diffs")

    deploy = subparsers.add_parser("deploy", help="deploy or dry-run a target")
    deploy.add_argument("--target", required=True)
    deploy.add_argument("--home")
    deploy.add_argument("--output")
    deploy.add_argument("--dry-run", action="store_true")
    deploy.add_argument("--mode", choices=["copy", "symlink"])

    audit = subparsers.add_parser("audit", help="check deployed files for drift")
    audit.add_argument("--target", required=True)
    audit.add_argument("--home")

    check = subparsers.add_parser("doctor", help="check local tools and optional services")
    check.add_argument("--target", required=True)
    check.add_argument("--home")
    check.add_argument("--network", action="store_true")
    return parser


def _emit(data: object, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
        return
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                status = item.get("status", "info")
                name = item.get("destination") or item.get("check") or item
                detail = item.get("detail")
                print(f"{status:>12}  {name}" + (f" ({detail})" if detail else ""))
            else:
                print(item)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                if value and all(isinstance(item, dict) for item in value):
                    print(f"{key}: {len(value)} entries")
                else:
                    print(f"{key}: {', '.join(str(item) for item in value) or '-'}")
            else:
                print(f"{key}: {value}")
    else:
        print(data)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = _root(args.repo)
        if args.command == "validate":
            _emit(validate_repository(root), args.json)
        elif args.command == "inventory":
            _emit(inventory(root), args.json)
        elif args.command == "render":
            result = render_target(root, args.target, Path(args.output) if args.output else None)
            _emit(result, args.json)
        elif args.command == "diff":
            _, changes = compare_target(
                root, args.target, _home(args.home), Path(args.output) if args.output else None
            )
            _emit(changes, args.json)
            if args.content and not args.json:
                for change in changes:
                    content = unified_diff(change)
                    if content:
                        print(content, end="" if content.endswith("\n") else "\n")
        elif args.command == "deploy":
            result = deploy_target(
                root,
                args.target,
                _home(args.home),
                Path(args.output) if args.output else None,
                args.dry_run,
                args.mode,
            )
            _emit(result, args.json)
        elif args.command == "audit":
            results = audit_target(root, args.target, _home(args.home))
            _emit(results, args.json)
            return 1 if any(item["status"] != "clean" for item in results) else 0
        elif args.command == "doctor":
            _emit(doctor(root, args.target, _home(args.home), args.network), args.json)
        return 0
    except WorkflowError as exc:
        print(f"workflowctl: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
