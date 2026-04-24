"""CLI subcommand: envault whitelist — keep only allowed keys in a .env file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_whitelist import WhitelistError, whitelist_env


def _load_config(config_path: str) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(config_path))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_whitelist(ns: argparse.Namespace) -> None:
    cfg = _load_config(ns.config)
    src = Path(ns.src) if ns.src else Path(cfg.env_file)
    dest = Path(ns.dest) if ns.dest else None
    allowed: list[str] = [k.strip() for k in ns.keys.split(",") if k.strip()]

    try:
        out = whitelist_env(
            src,
            allowed,
            dest=dest,
            keep_comments=not ns.strip_comments,
        )
    except WhitelistError as exc:
        print(f"[envault] whitelist error: {exc}", file=sys.stderr)
        sys.exit(1)

    kept = len(allowed)
    print(f"[envault] whitelist applied — kept {kept} key(s) → {out}")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "whitelist",
        help="Keep only specified keys in a .env file, removing all others.",
    )
    p.add_argument(
        "keys",
        help="Comma-separated list of keys to keep (e.g. 'DB_URL,SECRET_KEY').",
    )
    p.add_argument("--src", default=None, help="Source .env file (default: from config).")
    p.add_argument("--dest", default=None, help="Destination file (default: in-place).")
    p.add_argument(
        "--strip-comments",
        action="store_true",
        default=False,
        help="Remove comment and blank lines from output.",
    )
    p.add_argument("--config", default=".envault.json", help="Path to envault config file.")
    p.set_defaults(func=cmd_whitelist)
