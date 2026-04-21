"""CLI sub-commands for env-scope filtering."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_scope import ScopeError, scope_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_scope(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    src = Path(args.src) if args.src else Path(cfg.env_file)
    dest = Path(args.dest) if args.dest else None

    try:
        out = scope_env(
            src,
            args.scope,
            dest=dest,
            strip_prefix=args.strip_prefix,
            keep_unscoped=not args.scoped_only,
        )
    except ScopeError as exc:
        print(f"[envault] scope error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[envault] scoped file written to {out}")


def register_subcommand(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("scope", help="Filter .env keys by scope prefix (e.g. DEV_, PROD_)")
    p.add_argument("scope", help="Scope name (e.g. dev, prod, test)")
    p.add_argument("--src", default=None, help="Source .env file (default: from config)")
    p.add_argument("--dest", default=None, help="Destination file (default: .env.<scope>)")
    p.add_argument("--strip-prefix", action="store_true", help="Remove scope prefix from output keys")
    p.add_argument("--scoped-only", action="store_true", help="Drop keys that have no scope prefix")
    p.add_argument("--config", default=".envault.json", help="Config file path")
    p.set_defaults(func=cmd_scope)
