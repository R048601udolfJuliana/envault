"""CLI subcommand: envault tokenize — inspect value types in a .env file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.env_tokenize import TokenizeError, tokenize_env


def _load_config(args: argparse.Namespace):
    from envault.config import ConfigError, EnvaultConfig
    try:
        return EnvaultConfig.load(Path(args.config) if getattr(args, "config", None) else Path(".envault.json"))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tokenize(args: argparse.Namespace) -> None:
    config = _load_config(args)
    src = Path(getattr(args, "file", None) or config.env_file)
    try:
        result = tokenize_env(src)
    except TokenizeError as exc:
        print(f"[envault] tokenize error: {exc}", file=sys.stderr)
        sys.exit(1)

    filter_type = getattr(args, "type", None)
    entries = result.by_type(filter_type) if filter_type else result.entries

    if getattr(args, "summary", False):
        for line in result.summary_lines():
            print(line)
        return

    if not entries:
        print("No matching entries.")
        return

    for entry in entries:
        print(entry)


def register_subcommand(subparsers) -> None:
    p = subparsers.add_parser(
        "tokenize",
        help="Classify each .env value by type (url, email, integer, …)",
    )
    p.add_argument("--file", metavar="PATH", help="Path to .env file (overrides config)")
    p.add_argument("--type", metavar="TYPE", help="Filter output to a specific token type")
    p.add_argument("--summary", action="store_true", help="Print a type-count summary instead of individual entries")
    p.set_defaults(func=cmd_tokenize)
