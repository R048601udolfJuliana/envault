"""CLI subcommands for env-filter."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_filter import FilterError, filter_env


def _load_config(path: str) -> EnvaultConfig:
    return EnvaultConfig.load(Path(path))


def cmd_filter(ns: argparse.Namespace) -> None:
    try:
        cfg = _load_config(ns.config)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    src = Path(ns.src) if ns.src else cfg.env_file
    dest = Path(ns.dest)

    try:
        count = filter_env(
            src,
            dest,
            prefix=ns.prefix or None,
            pattern=ns.pattern or None,
            keys=ns.keys or None,
            exclude=ns.exclude,
        )
    except FilterError as exc:
        print(f"[envault] filter error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[envault] wrote {count} key(s) to {dest}")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("filter", help="Filter .env keys into a new file")
    p.add_argument("dest", help="Destination .env file")
    p.add_argument("--src", default="", help="Source .env file (default: from config)")
    p.add_argument("--prefix", default="", help="Keep keys starting with prefix")
    p.add_argument("--pattern", default="", help="Keep keys matching regex pattern")
    p.add_argument("--keys", nargs="+", metavar="KEY", help="Explicit list of keys")
    p.add_argument("--exclude", action="store_true", help="Exclude matched keys instead")
    p.add_argument("--config", default=".envault.json", help="Config file path")
    p.set_defaults(func=cmd_filter)
