"""CLI subcommand: envault fmt — format a .env file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.env_fmt import FmtError, format_env


def _load_config(args: argparse.Namespace):
    from envault.config import ConfigError, EnvaultConfig
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_fmt(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    src = Path(args.file) if args.file else Path(cfg.env_file)
    dest = Path(args.output) if args.output else None
    try:
        out = format_env(src, dest=dest, quote_values=args.quote)
        print(f"[envault] formatted: {out}")
    except FmtError as exc:
        print(f"[envault] fmt error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommand(subparsers) -> None:
    p = subparsers.add_parser("fmt", help="Format a .env file")
    p.add_argument("--file", default=None, help="Path to .env file (overrides config)")
    p.add_argument("--output", "-o", default=None, help="Write result to this path instead of in-place")
    p.add_argument("--quote", action="store_true", help="Wrap all values in double quotes")
    p.add_argument("--config", default=".envault.json", help="Config file path")
    p.set_defaults(func=cmd_fmt)
