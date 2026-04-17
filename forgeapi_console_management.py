from __future__ import annotations

import argparse
import json
import sys

from mini_agent.orchestrator import ForgeAPIOrchestrator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="forgeapi", description="ForgeAPI backend generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    update_parser = subparsers.add_parser("update", help="Create or update a backend module")
    update_parser.add_argument("module_name", help="Module name, e.g. customer")
    update_parser.add_argument("--prompt", required=True, help="Natural language prompt")
    update_parser.add_argument("--auto-validate", action="store_true", help="Run validation after generation")

    validate_parser = subparsers.add_parser("validate", help="Validate a generated backend module")
    validate_parser.add_argument("module_name", help="Module name, e.g. customer")
    validate_parser.add_argument("--auto-fix", action="store_true", help="Attempt automatic fixing before re-validation")

    show_parser = subparsers.add_parser("show", help="Show module info")
    show_parser.add_argument("module_name", help="Module name, e.g. customer")

    delete_parser = subparsers.add_parser("delete", help="Delete a generated module")
    delete_parser.add_argument("module_name", help="Module name, e.g. customer")

    return parser


def print_json(data) -> None:
    print(json.dumps(data, indent=2))


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    orchestrator = ForgeAPIOrchestrator()

    if args.command == "update":
        result = orchestrator.update_module(
            module_name=args.module_name,
            prompt=args.prompt,
            auto_validate=args.auto_validate,
        )
        print_json(result)
        return 0 if result.get("success") else 1

    if args.command == "validate":
        result = orchestrator.validate_module(
            module_name=args.module_name,
            auto_fix=args.auto_fix,
        )
        print_json(result)
        return 0 if result.get("success") else 1

    if args.command == "show":
        result = orchestrator.show_module(args.module_name)
        print_json(result)
        return 0 if result.get("success") else 1

    if args.command == "delete":
        result = orchestrator.delete_module(args.module_name)
        print_json(result)
        return 0 if result.get("success") else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())