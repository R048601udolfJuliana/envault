"""CLI subcommands for envault schedule management."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.schedule import ScheduleError, check_schedule_due, delete_schedule, load_schedule, save_schedule
from envault.remind import load_last_rotation


def cmd_schedule_set(args: argparse.Namespace) -> None:
    config_dir = Path(args.config_dir)
    try:
        save_schedule(config_dir, args.days)
        print(f"Schedule set: push reminder every {args.days} day(s).")
    except ScheduleError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_schedule_show(args: argparse.Namespace) -> None:
    config_dir = Path(args.config_dir)
    try:
        s = load_schedule(config_dir)
        if s is None:
            print("No schedule configured.")
        else:
            print(f"Interval : {s['interval_days']} day(s)")
            print(f"Created  : {s['created_at']}")
    except ScheduleError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_schedule_delete(args: argparse.Namespace) -> None:
    config_dir = Path(args.config_dir)
    try:
        delete_schedule(config_dir)
        print("Schedule removed.")
    except ScheduleError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_schedule_check(args: argparse.Namespace) -> None:
    config_dir = Path(args.config_dir)
    try:
        last = load_last_rotation(config_dir)
        last_iso = last.isoformat() if last else None
        due = check_schedule_due(config_dir, last_iso)
        if due:
            print("Push is DUE based on your schedule.")
            sys.exit(2)
        else:
            print("Push is not yet due.")
    except ScheduleError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("schedule", help="Manage push schedule reminders")
    ss = p.add_subparsers(dest="schedule_cmd", required=True)

    p_set = ss.add_parser("set", help="Set reminder interval")
    p_set.add_argument("days", type=int, help="Interval in days")
    p_set.add_argument("--config-dir", default=".", dest="config_dir")
    p_set.set_defaults(func=cmd_schedule_set)

    p_show = ss.add_parser("show", help="Show current schedule")
    p_show.add_argument("--config-dir", default=".", dest="config_dir")
    p_show.set_defaults(func=cmd_schedule_show)

    p_del = ss.add_parser("delete", help="Remove schedule")
    p_del.add_argument("--config-dir", default=".", dest="config_dir")
    p_del.set_defaults(func=cmd_schedule_delete)

    p_chk = ss.add_parser("check", help="Check if push is due")
    p_chk.add_argument("--config-dir", default=".", dest="config_dir")
    p_chk.set_defaults(func=cmd_schedule_check)
