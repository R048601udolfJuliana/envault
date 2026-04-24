"""CLI sub-commands: namespace apply / strip."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_namespace import NamespaceError, apply_namespace, strip_namespace


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config) if hasattr(args, "config") and args.config else None)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_namespace_apply(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    src = Path(args.file) if args.file else Path(cfg.env_file)
    dest = Path(args.dest) if args.dest else None
    try:
        out = apply_namespace(src, args.namespace, dest)
        print(f"[envault] namespace '{args.namespace}' applied → {out}")
    except NamespaceError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_namespace_strip(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    src = Path(args.file) if args.file else Path(cfg.env_file)
    dest = Path(args.dest) if args.dest else None
    try:
        out, count = strip_namespace(src, args.namespace, dest)
        print(f"[envault] stripped {count} key(s) with namespace '{args.namespace}' → {out}")
    except NamespaceError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # apply
    p_apply = sub.add_parser("namespace-apply", help="Prefix all keys with a namespace")
    p_apply.add_argument("namespace", help="Namespace prefix, e.g. 'APP_'")
    p_apply.add_argument("--file", default=None, help="Source .env file (default: from config)")
    p_apply.add_argument("--dest", default=None, help="Destination file (default: overwrite source)")
    p_apply.set_defaults(func=cmd_namespace_apply)

    # strip
    p_strip = sub.add_parser("namespace-strip", help="Remove a namespace prefix from all matching keys")
    p_strip.add_argument("namespace", help="Namespace prefix to remove, e.g. 'APP_'")
    p_strip.add_argument("--file", default=None, help="Source .env file (default: from config)")
    p_strip.add_argument("--dest", default=None, help="Destination file (default: overwrite source)")
    p_strip.set_defaults(func=cmd_namespace_strip)
