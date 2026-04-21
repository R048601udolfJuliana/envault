"""CLI sub-command: envault replace."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_replace import ReplaceError, replace_value


def _load_config(path: str) -> EnvaultConfig:
    return EnvaultConfig.load(Path(path))


def cmd_replace(ns: argparse.Namespace) -> None:
    try:
        cfg = _load_config(ns.config)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    src = Path(ns.file) if ns.file else Path(cfg.env_file)
    dest = Path(ns.dest) if ns.dest else None
    keys = ns.keys.split(",") if ns.keys else None

    try:
        resolved, n = replace_value(
            src,
            ns.pattern,
            ns.replacement,
            dest=dest,
            keys=keys,
            literal=ns.literal,
            count=ns.count,
        )
    except ReplaceError as exc:
        print(f"[envault] replace error: {exc}", file=sys.stderr)
        sys.exit(1)

    if n:
        print(f"[envault] replaced {n} line(s) → {resolved}")
    else:
        print("[envault] no lines matched.")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "replace",
        help="Find-and-replace values inside a .env file.",
    )
    p.add_argument("pattern", help="Pattern to search for.")
    p.add_argument("replacement", help="Replacement string.")
    p.add_argument("--file", metavar="PATH", help="Source .env file (overrides config).")
    p.add_argument("--dest", metavar="PATH", help="Output file (default: in-place).")
    p.add_argument("--keys", metavar="K1,K2", help="Comma-separated keys to restrict replacement.")
    p.add_argument("--literal", action="store_true", help="Treat pattern as a literal string.")
    p.add_argument("--count", type=int, default=0, metavar="N", help="Max replacements per line (0=all).")
    p.add_argument("--config", default=".envault.json", metavar="PATH")
    p.set_defaults(func=cmd_replace)
