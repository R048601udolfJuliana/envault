"""CLI sub-command: envault placeholder — scan for unresolved placeholder values."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_placeholder import PlaceholderError, scan_placeholders


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    return EnvaultConfig.load(cfg_path)


def cmd_placeholder(args: argparse.Namespace) -> None:
    try:
        cfg = _load_config(args)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    src = Path(getattr(args, "file", None) or cfg.env_file)

    try:
        result = scan_placeholders(src)
    except PlaceholderError as exc:
        print(f"[envault] placeholder scan error: {exc}", file=sys.stderr)
        sys.exit(1)

    for line in result.summary_lines():
        print(line)

    if result.found and args.strict:
        sys.exit(1)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "placeholder",
        help="Scan .env file for unresolved placeholder values.",
    )
    p.add_argument(
        "--file",
        metavar="PATH",
        default=None,
        help="Path to .env file (default: from config).",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any placeholders are found.",
    )
    p.set_defaults(func=cmd_placeholder)
