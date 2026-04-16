"""CLI subcommands for rotation reminders."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.remind import RemindError, check_rotation_due, days_since_rotation, record_rotation


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_remind_check(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    config_dir = Path(args.config).parent
    max_age = args.max_age
    try:
        due = check_rotation_due(config_dir, max_age_days=max_age)
        days = days_since_rotation(config_dir)
    except RemindError as exc:
        print(f"[envault] remind error: {exc}", file=sys.stderr)
        sys.exit(1)

    if days is None:
        print("[envault] No rotation recorded. Consider running 'envault rotate'.")
    else:
        print(f"[envault] Last rotation: {days:.1f} days ago (limit: {max_age} days).")

    if due:
        print("[envault] WARNING: Rotation is overdue!")
        if args.exit_code:
            sys.exit(2)
    else:
        print("[envault] Rotation is up to date.")


def cmd_remind_record(args: argparse.Namespace) -> None:
    _load_config(args)
    config_dir = Path(args.config).parent
    record_rotation(config_dir)
    print("[envault] Rotation timestamp recorded.")


def register_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_check = sub.add_parser("remind-check", help="Check if key rotation is overdue")
    p_check.add_argument("--max-age", type=int, default=30, metavar="DAYS",
                         help="Maximum days before rotation is considered overdue (default: 30)")
    p_check.add_argument("--exit-code", action="store_true",
                         help="Exit with code 2 if rotation is overdue")
    p_check.set_defaults(func=cmd_remind_check)

    p_record = sub.add_parser("remind-record", help="Record a rotation timestamp now")
    p_record.set_defaults(func=cmd_remind_record)
