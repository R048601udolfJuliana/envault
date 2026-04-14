"""CLI subcommand: envault compare <file_a> <file_b>"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.compare import compare_encrypted, CompareError
from envault.passphrase import passphrase_from_env


def cmd_compare(ns: argparse.Namespace) -> None:
    file_a = Path(ns.file_a)
    file_b = Path(ns.file_b)
    passphrase = passphrase_from_env()

    try:
        result = compare_encrypted(file_a, file_b, passphrase=passphrase)
    except CompareError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not result.has_differences:
        print("No differences found.")
        if ns.exit_code:
            sys.exit(0)
        return

    print(f"Differences between {file_a.name} and {file_b.name}:")
    for line in result.summary_lines():
        print(line)

    stats = (
        f"{len(result.only_in_a)} removed, "
        f"{len(result.only_in_b)} added, "
        f"{len(result.changed)} changed"
    )
    print(f"\n{stats}")

    if ns.exit_code:
        sys.exit(1_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_
        help="Compare two encrypted .env files",
        description="Decrypt and diff two encrypted .env vault files.",
    )
    p.add_argument("file_a", help="First encrypted file (A)")
    p.add_argument("file_b", help="Second encrypted file (B)")
    p.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 when differences are found",
    )
    p.set_defaults(func=cmd_compare)
