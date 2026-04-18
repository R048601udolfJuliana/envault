"""CLI subcommand: envault rename <old_key> <new_key>."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.env_rename import RenameError, rename_key


def _load_config(args: argparse.Namespace):
    from envault.config import ConfigError, EnvaultConfig
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_rename(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    env_file = Path(cfg.env_file)
    try:
        changed = rename_key(env_file, args.old_key, args.new_key)
    except RenameError as exc:
        print(f"[envault] rename error: {exc}", file=sys.stderr)
        sys.exit(1)

    if changed:
        print(f"Renamed {args.old_key!r} -> {args.new_key!r} in {env_file}")
    else:
        print("No changes made.", file=sys.stderr)
        sys.exit(1)


def register_subcommand(subparsers) -> None:
    p = subparsers.add_parser("rename", help="Rename a key in the .env file")
    p.add_argument("old_key", help="Existing key name")
    p.add_argument("new_key", help="New key name")
    p.add_argument("--config", default=".envault.json", help="Config file path")
    p.set_defaults(func=cmd_rename)
