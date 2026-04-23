"""CLI subcommand: envault group."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_group import GroupError, group_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_group(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    src = Path(args.src) if args.src else Path(cfg.env_file)
    dest = Path(args.dest) if args.dest else src.with_suffix(".grouped.env")

    try:
        result = group_env(
            src,
            dest,
            separator=args.separator,
            min_group_size=args.min_group_size,
        )
    except GroupError as exc:
        print(f"[envault] group error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        for grp, keys in sorted(result.items()):
            print(f"  [{grp}] {len(keys)} key(s): {', '.join(keys)}")
    print(f"[envault] grouped {sum(len(v) for v in result.values())} key(s) "
          f"into {len(result)} group(s) -> {dest}")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "group",
        help="Group .env keys by prefix into labelled sections.",
    )
    p.add_argument("--src", metavar="FILE", help="Source .env file (default: from config).")
    p.add_argument("--dest", metavar="FILE", help="Output file (default: <src>.grouped.env).")
    p.add_argument(
        "--separator",
        default="_",
        metavar="SEP",
        help="Prefix separator character (default: '_').",
    )
    p.add_argument(
        "--min-group-size",
        type=int,
        default=1,
        dest="min_group_size",
        metavar="N",
        help="Minimum members for a named group; smaller groups go to OTHER (default: 1).",
    )
    p.add_argument("-v", "--verbose", action="store_true", help="Show per-group key list.")
    p.add_argument("--config", default=".envault.json", metavar="FILE")
    p.set_defaults(func=cmd_group)
