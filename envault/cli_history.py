"""CLI sub-commands for viewing and clearing envault operation history."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.history import HistoryError, clear_history, load_history


def cmd_history_list(args: argparse.Namespace) -> None:
    base_dir = Path(args.dir) if hasattr(args, "dir") and args.dir else Path.cwd()
    try:
        entries = load_history(base_dir)
    except HistoryError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not entries:
        print("No history recorded yet.")
        return

    limit = getattr(args, "limit", None)
    shown = entries[-limit:] if limit else entries
    for entry in reversed(shown):
        recipients_str = ", ".join(entry.recipients) if entry.recipients else "(none)"
        note_str = f"  [{entry.note}]" if entry.note else ""
        print(f"{entry.human_time()}  {entry.action:<6}  {entry.encrypted_file}  recipients={recipients_str}{note_str}")


def cmd_history_clear(args: argparse.Namespace) -> None:
    base_dir = Path(args.dir) if hasattr(args, "dir") and args.dir else Path.cwd()
    try:
        clear_history(base_dir)
        print("History cleared.")
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    hist = subparsers.add_parser("history", help="View or clear operation history.")
    hist_sub = hist.add_subparsers(dest="history_cmd", required=True)

    lst = hist_sub.add_parser("list", help="List recent operations.")
    lst.add_argument("--limit", type=int, default=None, metavar="N",
                     help="Show only the last N entries.")
    lst.add_argument("--dir", default=None, metavar="DIR",
                     help="Base directory for history file (default: cwd).")
    lst.set_defaults(func=cmd_history_list)

    clr = hist_sub.add_parser("clear", help="Delete all history entries.")
    clr.add_argument("--dir", default=None, metavar="DIR",
                     help="Base directory for history file (default: cwd).")
    clr.set_defaults(func=cmd_history_clear)
