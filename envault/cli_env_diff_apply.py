"""CLI subcommands for applying diff patches to .env files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.env_diff_apply import ApplyError, apply_additions, apply_removals


def cmd_apply_set(ns: argparse.Namespace) -> None:
    """Add or overwrite KEY=VALUE pairs in a .env file."""
    env_path = Path(ns.env_file)
    pairs: dict[str, str] = {}
    for item in ns.pairs:
        if "=" not in item:
            print(f"[envault] invalid pair (expected KEY=VALUE): {item}", file=sys.stderr)
            sys.exit(1)
        key, _, value = item.partition("=")
        pairs[key.strip()] = value.strip()
    try:
        applied = apply_additions(env_path, pairs)
        for key in applied:
            print(f"[envault] set {key}")
    except ApplyError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_apply_remove(ns: argparse.Namespace) -> None:
    """Remove keys from a .env file."""
    env_path = Path(ns.env_file)
    try:
        removed = apply_removals(env_path, ns.keys)
        for key in removed:
            print(f"[envault] removed {key}")
        missing = set(ns.keys) - set(removed)
        for key in missing:
            print(f"[envault] key not found: {key}")
    except ApplyError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(sub: argparse.Action) -> None:
    p_set = sub.add_parser("apply-set", help="set KEY=VALUE pairs in a .env file")
    p_set.add_argument("env_file", help="path to .env file")
    p_set.add_argument("pairs", nargs="+", metavar="KEY=VALUE")
    p_set.set_defaults(func=cmd_apply_set)

    p_rm = sub.add_parser("apply-remove", help="remove keys from a .env file")
    p_rm.add_argument("env_file", help="path to .env file")
    p_rm.add_argument("keys", nargs="+", metavar="KEY")
    p_rm.set_defaults(func=cmd_apply_remove)
