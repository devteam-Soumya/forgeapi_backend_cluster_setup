from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from mini_agent.orchestrator import Orchestrator
from mini_agent.spec import build_delete_spec, build_resource_spec


def parse_bool(value: str) -> bool:
    value = value.strip().lower()
    if value in {"true", "1", "yes", "y"}:
        return True
    if value in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def parse_field(raw_field: str) -> dict[str, Any]:
    parts = [part.strip() for part in raw_field.split(":")]
    if len(parts) < 2:
        raise ValueError(
            f"Invalid field format: '{raw_field}'. Expected format: name:type:required:unique"
        )

    name = parts[0]
    field_type = parts[1]
    required = parse_bool(parts[2]) if len(parts) > 2 and parts[2] else True
    unique = parse_bool(parts[3]) if len(parts) > 3 and parts[3] else False

    return {
        "name": name,
        "type": field_type,
        "required": required,
        "unique": unique,
    }


def build_spec_from_args(args):
    raw_fields = getattr(args, "field", []) or []
    access_modes = getattr(args, "access", []) or ["public"]

    spec_dict = {
        "module_name": args.module_name.strip().lower(),
        "tenant_id": args.tenant_id.strip(),
        "database_mode": args.database_mode,
        "database_name": args.database_name,
        "access_modes": access_modes,
        "fields": [parse_field(raw_field) for raw_field in raw_fields],
    }

    return build_resource_spec(spec_dict)


def build_delete_spec_from_args(args):
    return build_delete_spec({"module_name": args.module_name.strip().lower()})


def handle_create(args) -> None:
    orchestrator = Orchestrator(base_dir=args.base_dir)
    spec = build_spec_from_args(args)
    generated = orchestrator.create(spec)

    print(f"[OK] Created module: {spec.module_name}")
    for path in generated:
        print(path)


def handle_delete(args) -> None:
    orchestrator = Orchestrator(base_dir=args.base_dir)
    spec = build_delete_spec_from_args(args)
    deleted = orchestrator.delete(spec.module_name)

    print(f"[OK] Deleted module: {spec.module_name}")
    for path in deleted:
        print(path)


def handle_show(args) -> None:
    orchestrator = Orchestrator(base_dir=args.base_dir)
    result = orchestrator.show(args.module_name.strip().lower())
    print(json.dumps(result, indent=2))


def handle_list(args) -> None:
    orchestrator = Orchestrator(base_dir=args.base_dir)
    result = orchestrator.list_modules()
    print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forgeapi")
    parser.add_argument("--base-dir", default=str(Path.cwd()), help="Base project directory")

    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create or update a backend module")
    create_parser.add_argument("--module-name", required=True, help="Resource/module name")
    create_parser.add_argument("--tenant-id", required=True, help="Tenant ID")
    create_parser.add_argument(
        "--database-mode",
        choices=["same", "different"],
        default="same",
        help="Use same tenant DB or different DB",
    )
    create_parser.add_argument(
        "--database-name",
        default=None,
        help="Database name when database-mode is different",
    )
    create_parser.add_argument(
        "--access",
        action="append",
        choices=["public", "auth", "rbac"],
        default=[],
        help="Access mode for generated API. Can be repeated.",
    )
    create_parser.add_argument(
        "--field",
        action="append",
        default=[],
        help="Field format: name:type:required:unique",
    )
    create_parser.set_defaults(func=handle_create)

    delete_parser = subparsers.add_parser("delete", help="Delete a backend module")
    delete_parser.add_argument("--module-name", required=True, help="Resource/module name")
    delete_parser.set_defaults(func=handle_delete)

    show_parser = subparsers.add_parser("show", help="Show module metadata")
    show_parser.add_argument("--module-name", required=True, help="Resource/module name")
    show_parser.set_defaults(func=handle_show)

    list_parser = subparsers.add_parser("list", help="List generated modules")
    list_parser.set_defaults(func=handle_list)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()