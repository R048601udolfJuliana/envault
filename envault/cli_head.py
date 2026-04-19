"""CLI subcommand: envault head — show first N keys of the .env file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_head import HeadError, head_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_head(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    env_path = Path(args.file) if args.file else Path(cfg.env_file)
    try:
        pairs = head_env(env_path, n=args.n)
    except HeadError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not pairs:
        print("(no keys found)")
        return

    for key, value in pairs:
        if args.keys_only:
            print(key)
        else:
            print(f"{key}={value}")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("head", help="Show the first N keys of the .env file")
    p.add_argument("-n", type=int, default=10, help="Number of keys to show (default: 10)")
    p.add_argument("--file", default=None, help="Override .env file path")
    p.add_argument("--keys-only", action="store_true", help="Print only key names")
    p.set_defaults(func=cmd_head)
