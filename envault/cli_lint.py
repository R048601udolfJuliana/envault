"""CLI subcommand: envault lint — check a .env file for issues."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.lint import LintError, lint_env


def cmd_lint(args: argparse.Namespace) -> None:
    path = Path(args.file)
    try:
        result = lint_env(path)
    except LintError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result.summary())

    if not result.ok and args.strict:
        sys.exit(1)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "lint",
        help="Check a .env file for formatting and consistency issues.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=".env",
        help="Path to the .env file to lint (default: .env).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with a non-zero status code if any issues are found.",
    )
    parser.set_defaults(func=cmd_lint)
