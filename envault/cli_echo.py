"""cli_echo.py — CLI sub-command for echoing resolved .env variables."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_echo import EchoError, echo_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    return EnvaultConfig.load(cfg_path)


def cmd_echo(args: argparse.Namespace) -> None:
    """Handle the 'envault echo' sub-command."""
    try:
        cfg = _load_config(args)
    except ConfigError as exc:
        print(f"[error] config: {exc}", file=sys.stderr)
        sys.exit(1)

    env_file = Path(getattr(args, "file", None) or cfg.env_file)
    keys = args.keys or None

    try:
        lines = echo_env(
            env_file,
            fmt=args.fmt,
            keys=keys,
            mask=args.mask,
        )
    except EchoError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)

    for line in lines:
        print(line)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "echo",
        help="Print resolved .env variables to stdout.",
    )
    p.add_argument(
        "--file",
        metavar="PATH",
        help="Path to .env file (defaults to config env_file).",
    )
    p.add_argument(
        "--fmt",
        choices=["plain", "export", "json"],
        default="plain",
        help="Output format (default: plain).",
    )
    p.add_argument(
        "--keys",
        nargs="+",
        metavar="KEY",
        help="Only print these keys.",
    )
    p.add_argument(
        "--mask",
        action="store_true",
        help="Replace values with *** for safe display.",
    )
    p.set_defaults(func=cmd_echo)
