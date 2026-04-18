"""CLI subcommands: envault set / unset."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_set import SetError, set_key, unset_key


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_set(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    env_file = Path(cfg.env_file)
    try:
        added = set_key(env_file, args.key, args.value, create=args.create)
        action = "added" if added else "updated"
        print(f"[envault] {action} {args.key} in {env_file}")
    except SetError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_unset(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    env_file = Path(cfg.env_file)
    try:
        removed = unset_key(env_file, args.key)
        if removed:
            print(f"[envault] removed {args.key} from {env_file}")
        else:
            print(f"[envault] key {args.key!r} not found in {env_file}", file=sys.stderr)
            sys.exit(1)
    except SetError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_set = sub.add_parser("set", help="Set a key in the .env file")
    p_set.add_argument("key", help="Variable name")
    p_set.add_argument("value", help="Variable value")
    p_set.add_argument("--no-create", dest="create", action="store_false",
                       default=True, help="Fail if .env file does not exist")
    p_set.add_argument("--config", default=".envault.json")
    p_set.set_defaults(func=cmd_set)

    p_unset = sub.add_parser("unset", help="Remove a key from the .env file")
    p_unset.add_argument("key", help="Variable name to remove")
    p_unset.add_argument("--config", default=".envault.json")
    p_unset.set_defaults(func=cmd_unset)
