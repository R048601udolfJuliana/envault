"""CLI subcommand: envault typecheck."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_typecheck import TypeCheckError, typecheck_env


def _load_config(config_path: str) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(config_path))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_typecheck(ns: argparse.Namespace) -> None:
    cfg = _load_config(ns.config)
    env_file = Path(ns.env_file) if ns.env_file else Path(cfg.env_file)

    # Load schema: accept --schema key:type pairs or a JSON file
    schema: dict[str, str] = {}
    if ns.schema_file:
        schema_path = Path(ns.schema_file)
        if not schema_path.exists():
            print(f"[envault] schema file not found: {schema_path}", file=sys.stderr)
            sys.exit(1)
        try:
            schema = json.loads(schema_path.read_text())
        except json.JSONDecodeError as exc:
            print(f"[envault] invalid JSON schema: {exc}", file=sys.stderr)
            sys.exit(1)
    for pair in ns.schema or []:
        if ":" not in pair:
            print(f"[envault] invalid schema entry (expected KEY:TYPE): {pair}", file=sys.stderr)
            sys.exit(1)
        key, _, type_name = pair.partition(":")
        schema[key.strip()] = type_name.strip()

    if not schema:
        print("[envault] no schema provided (use --schema or --schema-file)", file=sys.stderr)
        sys.exit(1)

    try:
        result = typecheck_env(env_file, schema)
    except TypeCheckError as exc:
        print(f"[envault] typecheck error: {exc}", file=sys.stderr)
        sys.exit(1)

    for line in result.summary_lines():
        print(line)

    if not result.ok and ns.strict:
        sys.exit(1)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "typecheck",
        help="Validate .env value types against a schema.",
    )
    p.add_argument(
        "--env-file",
        metavar="FILE",
        default=None,
        help="Path to .env file (defaults to config env_file).",
    )
    p.add_argument(
        "--schema",
        metavar="KEY:TYPE",
        nargs="+",
        help="One or more KEY:TYPE pairs (e.g. PORT:int DEBUG:bool).",
    )
    p.add_argument(
        "--schema-file",
        metavar="FILE",
        default=None,
        help="Path to a JSON file mapping keys to types.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 when type issues are found.",
    )
    p.add_argument("--config", default=".envault.json", help="Config file path.")
    p.set_defaults(func=cmd_typecheck)
