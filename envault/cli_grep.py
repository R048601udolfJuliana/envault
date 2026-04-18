"""CLI subcommand: envault grep"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.env_grep import GrepError, grep_env


def _load_config(args):
    from envault.config import ConfigError, EnvaultConfig
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_grep(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    env_file = Path(args.file) if args.file else Path(cfg.env_file)

    try:
        result = grep_env(
            env_file,
            args.pattern,
            search_keys=not args.values_only,
            search_values=not args.keys_only,
            case_sensitive=args.case_sensitive,
        )
    except GrepError as exc:
        print(f"[envault] grep error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not result.found:
        print("No matches found.")
        if args.exit_code:
            sys.exit(1)
        return

    print(result.summary())


def register_subcommand(subparsers) -> None:
    p = subparsers.add_parser("grep", help="Search for keys/values in a .env file")
    p.add_argument("pattern", help="Regex pattern to search for")
    p.add_argument("--file", "-f", default=None, help="Path to .env file (overrides config)")
    p.add_argument("--keys-only", action="store_true", help="Search keys only")
    p.add_argument("--values-only", action="store_true", help="Search values only")
    p.add_argument("--case-sensitive", action="store_true", help="Case-sensitive matching")
    p.add_argument("--exit-code", action="store_true", help="Exit 1 when no matches found")
    p.add_argument("--config", default=".envault.json", help="Config file path")
    p.set_defaults(func=cmd_grep)
