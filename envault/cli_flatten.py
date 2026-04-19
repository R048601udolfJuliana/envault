"""CLI subcommand: envault flatten."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.env_flatten import FlattenError, flatten_env


def _load_config(args: argparse.Namespace):
    from envault.config import ConfigError, EnvaultConfig
    try:
        return EnvaultConfig.load(Path(args.config) if getattr(args, "config", None) else None)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_flatten(args: argparse.Namespace) -> None:
    sources = [Path(s) for s in args.sources]
    dest = Path(args.dest)

    try:
        merged = flatten_env(
            sources,
            dest,
            last_wins=not args.first_wins,
            comment_source=args.comment_source,
        )
    except FlattenError as exc:
        print(f"[envault] flatten error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[envault] merged {len(sources)} file(s) -> {dest} ({len(merged)} keys)")


def register_subcommand(subparsers) -> None:
    p = subparsers.add_parser("flatten", help="Merge multiple .env files into one")
    p.add_argument("sources", nargs="+", metavar="SOURCE", help="Source .env files (in order)")
    p.add_argument("--dest", required=True, help="Output .env file")
    p.add_argument(
        "--first-wins",
        action="store_true",
        default=False,
        help="Keep first occurrence of duplicate keys (default: last wins)",
    )
    p.add_argument(
        "--comment-source",
        action="store_true",
        default=False,
        help="Add comments indicating which file each key came from",
    )
    p.set_defaults(func=cmd_flatten)
