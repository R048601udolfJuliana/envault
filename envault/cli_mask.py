"""CLI subcommand: envault mask."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.env_mask import MaskError, mask_env


def _load_config(args: argparse.Namespace):
    from envault.config import ConfigError, EnvaultConfig

    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_mask(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    source = Path(args.source) if args.source else Path(cfg.env_file)
    dest = Path(args.output) if args.output else None

    keys = args.keys.split(",") if args.keys else None

    try:
        masked = mask_env(
            source,
            dest,
            keys=keys,
            placeholder=args.placeholder,
            auto_detect=not args.no_auto,
        )
    except MaskError as exc:
        print(f"[envault] mask error: {exc}", file=sys.stderr)
        sys.exit(1)

    if masked:
        print(f"Masked {len(masked)} key(s): {', '.join(masked)}.")
        if dest:
            print(f"Output written to: {dest}")
    else:
        print("No sensitive keys detected.")


def register_subcommand(subparsers) -> None:
    p = subparsers.add_parser("mask", help="Mask sensitive .env values for safe display")
    p.add_argument("--config", default=".envault.json")
    p.add_argument("--source", default=None, help="Source .env file (default: from config)")
    p.add_argument("--output", "-o", default=None, help="Write masked output to this file")
    p.add_argument("--keys", default=None, help="Comma-separated list of keys to mask")
    p.add_argument("--placeholder", default="***", help="Replacement string (default: ***)")
    p.add_argument("--no-auto", action="store_true", help="Disable auto-detection of sensitive keys")
    p.set_defaults(func=cmd_mask)
