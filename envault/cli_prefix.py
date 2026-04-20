"""CLI sub-commands for adding/stripping key prefixes."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_prefix import PrefixError, add_prefix, strip_prefix


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_prefix_add(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    src = Path(args.file) if args.file else Path(cfg.env_file)
    dest = Path(args.dest) if args.dest else None
    try:
        out = add_prefix(src, args.prefix, dest)
        print(f"[envault] prefix '{args.prefix}' added → {out}")
    except PrefixError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_prefix_strip(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    src = Path(args.file) if args.file else Path(cfg.env_file)
    dest = Path(args.dest) if args.dest else None
    try:
        out = strip_prefix(src, args.prefix, dest)
        print(f"[envault] prefix '{args.prefix}' stripped → {out}")
    except PrefixError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # add
    p_add = sub.add_parser("prefix-add", help="add a prefix to all .env keys")
    p_add.add_argument("prefix", help="prefix string to prepend")
    p_add.add_argument("--file", default="", help="source .env file (default: from config)")
    p_add.add_argument("--dest", default="", help="output file (default: in-place)")
    p_add.add_argument("--config", default=".envault.json")
    p_add.set_defaults(func=cmd_prefix_add)

    # strip
    p_strip = sub.add_parser("prefix-strip", help="strip a prefix from all .env keys")
    p_strip.add_argument("prefix", help="prefix string to remove")
    p_strip.add_argument("--file", default="", help="source .env file (default: from config)")
    p_strip.add_argument("--dest", default="", help="output file (default: in-place)")
    p_strip.add_argument("--config", default=".envault.json")
    p_strip.set_defaults(func=cmd_prefix_strip)
