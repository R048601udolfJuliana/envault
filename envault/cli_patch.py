"""CLI sub-commands for env-patch: apply key-value overrides to a .env file."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_patch import PatchError, patch_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    try:
        return EnvaultConfig.load(cfg_path)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_patch(args: argparse.Namespace) -> None:
    """Apply one or more KEY=VALUE overrides to the .env file."""
    cfg = _load_config(args)
    src = Path(cfg.env_file)

    overrides: dict[str, str] = {}
    for pair in args.overrides:
        if "=" not in pair:
            print(f"[envault] invalid override (expected KEY=VALUE): {pair}", file=sys.stderr)
            sys.exit(1)
        key, _, value = pair.partition("=")
        overrides[key.strip()] = value

    dest = Path(args.dest) if args.dest else None
    no_add = getattr(args, "no_add", False)

    try:
        out = patch_env(src, overrides, dest=dest, add_missing=not no_add)
    except PatchError as exc:
        print(f"[envault] patch error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[envault] patched {len(overrides)} key(s) -> {out}")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("patch", help="Apply key-value overrides to the .env file")
    p.add_argument(
        "overrides",
        nargs="+",
        metavar="KEY=VALUE",
        help="One or more KEY=VALUE pairs to apply",
    )
    p.add_argument(
        "--dest",
        default=None,
        metavar="FILE",
        help="Write result to FILE instead of patching in-place",
    )
    p.add_argument(
        "--no-add",
        action="store_true",
        help="Do not append keys that are absent from the source file",
    )
    p.set_defaults(func=cmd_patch)
