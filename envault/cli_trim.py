"""CLI subcommand: envault trim."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_trim import TrimError, trim_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_trim(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    src = Path(args.file) if args.file else Path(cfg.env_file)
    dest = Path(args.dest) if getattr(args, "dest", None) else None

    try:
        count = trim_env(src, dest, dry_run=args.dry_run)
    except TrimError as exc:
        print(f"[envault] trim error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"[envault] dry-run: {count} line(s) would be trimmed in {src}")
    elif count:
        out = dest or src
        print(f"[envault] trimmed {count} line(s) → {out}")
    else:
        print(f"[envault] nothing to trim in {src}")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("trim", help="Trim whitespace from .env values")
    p.add_argument("--file", metavar="PATH", help="Source .env file (overrides config)")
    p.add_argument("--dest", metavar="PATH", help="Write output to a separate file")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing",
    )
    p.add_argument("--config", default=".envault.json", metavar="PATH")
    p.set_defaults(func=cmd_trim)
