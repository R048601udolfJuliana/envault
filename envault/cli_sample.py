"""CLI subcommand: envault sample — generate a .env.sample file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.env_sample import SampleError, generate_sample


def _load_config(args: argparse.Namespace):
    from envault.config import ConfigError, EnvaultConfig
    try:
        return EnvaultConfig.load(Path(args.config) if getattr(args, "config", None) else Path(".envault.json"))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_sample(args: argparse.Namespace) -> None:
    config = _load_config(args)
    src = Path(getattr(args, "src", None) or config.env_file)
    dest = Path(args.dest) if getattr(args, "dest", None) else None

    try:
        out = generate_sample(src, dest)
        print(f"[envault] sample written to {out}")
    except SampleError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommand(subparsers) -> None:
    p = subparsers.add_parser("sample", help="Generate a .env.sample with values stripped")
    p.add_argument("--src", metavar="FILE", help="Source .env file (default: from config)")
    p.add_argument("--dest", metavar="FILE", help="Destination path (default: <src>.sample)")
    p.set_defaults(func=cmd_sample)
