"""CLI sub-commands for env-defaults feature."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_defaults import DefaultsError, apply_defaults


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    return EnvaultConfig.load(cfg_path)


def cmd_defaults(
    args: argparse.Namespace,
    _config: EnvaultConfig | None = None,
) -> None:
    """Apply default key=value pairs to the project .env file."""
    try:
        cfg = _config or _load_config(args)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    raw: list[str] = args.defaults or []
    defaults: dict[str, str] = {}
    for item in raw:
        if "=" not in item:
            print(f"[envault] invalid default (expected KEY=VALUE): {item}", file=sys.stderr)
            sys.exit(1)
        k, _, v = item.partition("=")
        defaults[k.strip()] = v.strip()

    if not defaults:
        print("[envault] no defaults specified.", file=sys.stderr)
        sys.exit(1)

    dest = Path(args.dest) if getattr(args, "dest", None) else None
    overwrite_empty = not getattr(args, "no_overwrite_empty", False)

    try:
        out_path, applied = apply_defaults(
            Path(cfg.env_file),
            defaults,
            dest=dest,
            overwrite_empty=overwrite_empty,
        )
    except DefaultsError as exc:
        print(f"[envault] defaults error: {exc}", file=sys.stderr)
        sys.exit(1)

    if applied:
        print(f"Applied {len(applied)} default(s) to {out_path}:")
        for key in applied:
            print(f"  + {key}")
    else:
        print("No defaults were applied (all keys already present).")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "defaults",
        help="Apply default values to missing/empty keys in the .env file.",
    )
    p.add_argument(
        "defaults",
        nargs="+",
        metavar="KEY=VALUE",
        help="Default key=value pairs to apply.",
    )
    p.add_argument(
        "--dest",
        metavar="FILE",
        help="Write output to FILE instead of modifying in place.",
    )
    p.add_argument(
        "--no-overwrite-empty",
        action="store_true",
        default=False,
        help="Do not overwrite keys that exist but have empty values.",
    )
    p.set_defaults(func=cmd_defaults)
