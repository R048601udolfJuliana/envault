"""CLI subcommand: envault validate"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_validate import ValidateError, validate_env


def _load_config(path: str) -> EnvaultConfig:
    return EnvaultConfig.load(Path(path))


def cmd_validate(ns: argparse.Namespace) -> None:
    try:
        cfg = _load_config(ns.config)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    required = ns.require or []
    pattern_rules: dict = {}
    for item in ns.pattern or []:
        if ":" not in item:
            print(f"[envault] invalid --pattern format (expected KEY:REGEX): {item}", file=sys.stderr)
            sys.exit(1)
        k, _, v = item.partition(":")
        pattern_rules[k.strip()] = v.strip()

    try:
        result = validate_env(cfg.env_file, required, pattern_rules or None)
    except ValidateError as exc:
        print(f"[envault] {exc}", file=sys.stderr)
        sys.exit(1)

    if result.ok:
        print("✓ " + result.summary())
    else:
        print(result.summary())
        if ns.strict:
            sys.exit(1)


def register_subcommand(subparsers) -> None:
    p = subparsers.add_parser("validate", help="Validate .env file against required keys")
    p.add_argument("--config", default=".envault.json", help="Config file path")
    p.add_argument("--require", metavar="KEY", nargs="+", help="Required keys")
    p.add_argument("--pattern", metavar="KEY:REGEX", nargs="+", help="Key/regex pattern rules")
    p.add_argument("--strict", action="store_true", help="Exit non-zero if issues found")
    p.set_defaults(func=cmd_validate)
