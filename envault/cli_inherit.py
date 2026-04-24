"""cli_inherit.py – CLI subcommand for env-inherit."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_inherit import InheritError, inherit_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config) if getattr(args, "config", None) else None)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_inherit(args: argparse.Namespace) -> None:
    cfg = _load_config(args)

    parent = Path(args.parent)
    child = Path(args.child) if args.child else Path(cfg.env_file)
    dest = Path(args.dest) if getattr(args, "dest", None) else None

    try:
        out_path, inherited = inherit_env(
            parent,
            child,
            dest=dest,
            show_source=args.show_source,
        )
    except InheritError as exc:
        print(f"[envault] inherit error: {exc}", file=sys.stderr)
        sys.exit(1)

    if inherited:
        print(f"Inherited {len(inherited)} key(s) from {parent} → {out_path}:")
        for key in inherited:
            print(f"  + {key}")
    else:
        print("No new keys to inherit; child already defines all parent keys.")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "inherit",
        help="Merge a parent .env into a child .env (child values win).",
    )
    p.add_argument("parent", help="Path to the parent .env file.")
    p.add_argument(
        "child",
        nargs="?",
        default=None,
        help="Path to the child .env file (default: env_file from config).",
    )
    p.add_argument("--dest", default=None, help="Write result to this path instead of child.")
    p.add_argument(
        "--show-source",
        action="store_true",
        default=False,
        help="Add a comment above inherited keys indicating the parent file.",
    )
    p.set_defaults(func=cmd_inherit)
