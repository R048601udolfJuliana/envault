"""CLI subcommand: envault count — count keys in the .env file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_count import CountError, count_keys


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    return EnvaultConfig.load(cfg_path)


def cmd_count(args: argparse.Namespace) -> None:
    try:
        cfg = _load_config(args)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    env_path = Path(cfg.env_file)
    pattern: str | None = getattr(args, "pattern", None)
    case_sensitive: bool = getattr(args, "case_sensitive", False)

    try:
        result = count_keys(env_path, pattern=pattern, case_sensitive=case_sensitive)
    except CountError as exc:
        print(f"[envault] count error: {exc}", file=sys.stderr)
        sys.exit(1)

    for line in result.summary_lines():
        print(line)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("count", help="Count keys in the .env file")
    p.add_argument(
        "pattern",
        nargs="?",
        default=None,
        help="Optional regex pattern to filter key names",
    )
    p.add_argument(
        "--case-sensitive",
        action="store_true",
        default=False,
        help="Make pattern matching case-sensitive",
    )
    p.set_defaults(func=cmd_count)
