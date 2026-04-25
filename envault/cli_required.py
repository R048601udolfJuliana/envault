"""CLI subcommand: envault required — check required keys exist in .env."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_required import RequiredError, check_required


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    return EnvaultConfig.load(cfg_path)


def cmd_required(args: argparse.Namespace) -> None:
    try:
        cfg = _load_config(args)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    env_path = Path(getattr(args, "env_file", None) or cfg.env_file)
    keys: list[str] = args.keys
    allow_empty: bool = args.allow_empty

    if not keys:
        print("[envault] no required keys specified.", file=sys.stderr)
        sys.exit(1)

    try:
        result = check_required(env_path, keys, allow_empty=allow_empty)
    except RequiredError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)

    if result.ok:
        print("[envault] all required keys present.")
        return

    print(f"[envault] {len(result.missing)} required key(s) missing or empty:")
    for line in result.summary_lines():
        print(line)

    if args.strict:
        sys.exit(1)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "required",
        help="Check that required keys are present (and non-empty) in .env",
    )
    p.add_argument("keys", nargs="+", metavar="KEY", help="Required key names")
    p.add_argument(
        "--allow-empty",
        dest="allow_empty",
        action="store_true",
        default=False,
        help="Allow keys to be present but empty",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Exit with code 1 when any required key is missing",
    )
    p.add_argument("--env-file", dest="env_file", default=None)
    p.set_defaults(func=cmd_required)
