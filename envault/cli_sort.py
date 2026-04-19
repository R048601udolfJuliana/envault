"""CLI subcommand: envault sort — sort keys in the .env file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_sort import SortError, sort_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    return EnvaultConfig.load(cfg_path)


def cmd_sort(args: argparse.Namespace) -> None:
    try:
        cfg = _load_config(args)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    src = Path(cfg.env_file)

    if not src.exists():
        print(f"[envault] sort error: env file not found: {src}", file=sys.stderr)
        sys.exit(1)

    dest = Path(args.output) if getattr(args, "output", None) else None

    try:
        out = sort_env(src, dest, reverse=args.reverse)
        print(f"[envault] sorted: {out}")
    except SortError as exc:
        print(f"[envault] sort error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("sort", help="Sort keys in the .env file alphabetically")
    p.add_argument("--output", metavar="FILE", help="Write sorted output to FILE instead of in-place")
    p.add_argument("--reverse", action="store_true", help="Sort in reverse (Z-A) order")
    p.set_defaults(func=cmd_sort)
