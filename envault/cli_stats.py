"""CLI subcommand: envault stats"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_stats import StatsError, compute_stats


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    return EnvaultConfig.load(cfg_path)


def cmd_stats(args: argparse.Namespace) -> None:
    try:
        cfg = _load_config(args)
        target = Path(getattr(args, "file", None) or cfg.env_file)
    except ConfigError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        stats = compute_stats(target)
    except StatsError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    for line in stats.summary_lines():
        print(line)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("stats", help="Show statistics for a .env file")
    p.add_argument(
        "--file",
        metavar="PATH",
        default=None,
        help="Path to .env file (default: from config)",
    )
    p.set_defaults(func=cmd_stats)
