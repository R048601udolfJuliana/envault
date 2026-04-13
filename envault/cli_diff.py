"""CLI subcommands for diffing .env files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.diff import DiffError, diff_env_files, unified_diff


def cmd_diff(args: argparse.Namespace) -> int:
    """Compare two .env files and print a human-readable diff."""
    old_path = Path(args.old)
    new_path = Path(args.new)

    try:
        if args.unified:
            output = unified_diff(old_path, new_path)
            if output:
                print(output, end="")
            else:
                print("No changes.")
        else:
            result = diff_env_files(old_path, new_path)
            print(result.summary())
            if result.has_changes and args.exit_code:
                return 1
    except DiffError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    return 0


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'diff' subcommand."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "diff",
        help="Compare two .env files and show what changed.",
    )
    parser.add_argument("old", help="Path to the original .env file.")
    parser.add_argument("new", help="Path to the new .env file.")
    parser.add_argument(
        "-u", "--unified",
        action="store_true",
        help="Output in unified diff format.",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when differences are found.",
    )
    parser.set_defaults(func=cmd_diff)
