"""CLI subcommand: envault split"""
from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_split import SplitError, split_env


def _load_config(args: Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_split(args: Namespace) -> None:
    cfg = _load_config(args)
    src = Path(cfg.env_file)
    dest_dir = Path(args.dest_dir) if args.dest_dir else src.parent / "split"
    prefixes = [p.strip() for p in args.prefixes.split(",") if p.strip()]

    if not prefixes:
        print("[envault] error: --prefixes must not be empty.", file=sys.stderr)
        sys.exit(1)

    try:
        written = split_env(src, dest_dir, prefixes, default_file=args.default_file)
    except SplitError as exc:
        print(f"[envault] split error: {exc}", file=sys.stderr)
        sys.exit(1)

    if written:
        for name, path in written.items():
            print(f"  wrote {path}")
    else:
        print("[envault] no keys matched — nothing written.")


def register_subcommand(sub: ArgumentParser) -> None:
    p = sub.add_parser("split", help="Split .env file by key prefix into separate files")
    p.add_argument("--config", default=".envault.json", help="Config file path")
    p.add_argument(
        "--prefixes",
        required=True,
        help="Comma-separated list of key prefixes, e.g. DB,AWS,APP",
    )
    p.add_argument("--dest-dir", default=None, help="Output directory (default: <env_dir>/split)")
    p.add_argument(
        "--default-file",
        default=".env.other",
        help="Filename for unmatched keys (default: .env.other)",
    )
    p.set_defaults(func=cmd_split)
