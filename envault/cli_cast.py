"""cli_cast.py — CLI subcommand for envault cast."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_cast import CastError, cast_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    try:
        return EnvaultConfig.load(cfg_path)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_cast(args: argparse.Namespace) -> None:
    """Cast .env values to typed Python objects and print as JSON."""
    cfg = _load_config(args)
    src = Path(args.file) if args.file else Path(cfg.env_file)

    hints: dict[str, str] = {}
    for item in args.hint or []:
        if ":" not in item:
            print(f"[envault] invalid hint {item!r} (expected KEY:TYPE)", file=sys.stderr)
            sys.exit(1)
        key, _, typ = item.partition(":")
        hints[key.strip()] = typ.strip()

    try:
        result = cast_env(src, hints)
    except CastError as exc:
        print(f"[envault] cast error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("cast", help="Cast .env values to typed Python objects")
    p.add_argument("--file", metavar="PATH", help="Path to .env file (overrides config)")
    p.add_argument(
        "--hint",
        metavar="KEY:TYPE",
        action="append",
        help="Type hint for a key, e.g. PORT:int (repeatable). Types: str, int, float, bool, list",
    )
    p.set_defaults(func=cmd_cast)
