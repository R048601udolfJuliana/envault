"""CLI subcommand: envault secret — scan for secrets in .env files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_secret import SecretError, scan_secrets


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    return EnvaultConfig.load(cfg_path)


def cmd_secret_scan(args: argparse.Namespace) -> None:
    try:
        cfg = _load_config(args)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    target = Path(getattr(args, "file", None) or cfg.env_file)

    try:
        result = scan_secrets(
            target,
            check_entropy=not args.no_entropy,
            check_names=not args.no_names,
        )
    except SecretError as exc:
        print(f"[envault] secret scan error: {exc}", file=sys.stderr)
        sys.exit(1)

    for line in result.summary_lines():
        print(line)

    if result.found and args.strict:
        sys.exit(1)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "secret",
        help="Scan .env file for potential secrets or high-entropy values.",
    )
    p.add_argument("--file", metavar="PATH", help="Path to .env file (overrides config).")
    p.add_argument(
        "--no-entropy",
        action="store_true",
        default=False,
        help="Skip entropy-based detection.",
    )
    p.add_argument(
        "--no-names",
        action="store_true",
        default=False,
        help="Skip sensitive key-name detection.",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 if any secrets are found.",
    )
    p.set_defaults(func=cmd_secret_scan)
