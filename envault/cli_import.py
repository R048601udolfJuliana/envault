"""CLI subcommand: envault import — import vault variables into the environment."""

from __future__ import annotations

import argparse
import sys

from envault.config import EnvaultConfig, ConfigError
from envault.import_env import import_env, ImportError  # noqa: A004
from envault.passphrase import passphrase_from_env


def cmd_import(ns: argparse.Namespace) -> None:
    """Handle the `envault import` subcommand."""
    try:
        config = EnvaultConfig.load(ns.config)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    passphrase = passphrase_from_env()
    keys = ns.keys if ns.keys else None

    try:
        imported = import_env(
            config,
            overwrite=ns.overwrite,
            dry_run=ns.dry_run,
            passphrase=passphrase,
            keys=keys,
        )
    except ImportError as exc:
        print(f"[envault] import error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not imported:
        print("[envault] nothing to import (all keys already set or vault empty).")
        return

    label = "Would import" if ns.dry_run else "Imported"
    for key in sorted(imported):
        print(f"  {label}: {key}")

    if not ns.dry_run:
        print(f"[envault] {len(imported)} variable(s) imported into environment.")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the `import` subcommand."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "import",
        help="Import variables from the encrypted vault into the current environment.",
    )
    parser.add_argument(
        "--config",
        default=".envault.json",
        help="Path to envault config file (default: .envault.json).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing environment variables.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be imported without modifying the environment.",
    )
    parser.add_argument(
        "keys",
        nargs="*",
        metavar="KEY",
        help="Specific keys to import (imports all if omitted).",
    )
    parser.set_defaults(func=cmd_import)
