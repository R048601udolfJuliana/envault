"""CLI sub-commands for managing protected (read-only) env keys."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_protect import ProtectError, load_protected, protect_key, unprotect_key


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    try:
        return EnvaultConfig.load(cfg_path)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_protect_add(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    vault_dir = Path(cfg.vault_dir)
    try:
        protect_key(vault_dir, args.key)
        print(f"[envault] '{args.key}' is now protected.")
    except ProtectError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_protect_remove(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    vault_dir = Path(cfg.vault_dir)
    try:
        unprotect_key(vault_dir, args.key)
        print(f"[envault] '{args.key}' is no longer protected.")
    except ProtectError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_protect_list(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    vault_dir = Path(cfg.vault_dir)
    try:
        keys = load_protected(vault_dir)
    except ProtectError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)
    if not keys:
        print("No keys are currently protected.")
    else:
        for k in keys:
            print(f"  {k}")


def register_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("protect", help="Manage protected (read-only) keys.")
    ps = p.add_subparsers(dest="protect_cmd", required=True)

    pa = ps.add_parser("add", help="Mark a key as protected.")
    pa.add_argument("key", help="Key name to protect.")
    pa.set_defaults(func=cmd_protect_add)

    pr = ps.add_parser("remove", help="Remove protection from a key.")
    pr.add_argument("key", help="Key name to unprotect.")
    pr.set_defaults(func=cmd_protect_remove)

    pl = ps.add_parser("list", help="List all protected keys.")
    pl.set_defaults(func=cmd_protect_list)
