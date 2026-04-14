"""cli_status.py — CLI subcommand: envault status."""
from __future__ import annotations

import argparse
import sys

from envault.config import ConfigError, EnvaultConfig
from envault.env_status import StatusError, get_status


def cmd_status(ns: argparse.Namespace) -> None:
    config_path = getattr(ns, "config", ".envault.json")
    try:
        config = EnvaultConfig.load(config_path)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        status = get_status(config)
    except StatusError as exc:
        print(f"[envault] status error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("envault status")
    print("=" * 40)
    for line in status.summary_lines():
        print(line)

    if ns.exit_code:
        if not status.encrypted_exists:
            sys.exit(2)
        if status.manifest_exists and status.manifest_ok is False:
            sys.exit(3)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("status", help="Show vault status")
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with non-zero code if vault is not healthy",
    )
    p.set_defaults(func=cmd_status)
