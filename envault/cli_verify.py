"""CLI sub-command: verify — check vault integrity via manifest."""

from __future__ import annotations

import argparse
import sys

from envault.cli import _load_config
from envault.verify import VerifyError, verify_manifest, write_manifest


def cmd_verify(args: argparse.Namespace) -> None:
    """Entry point for `envault verify`."""
    config = _load_config(args)

    if args.write:
        try:
            manifest_path = write_manifest(config)
            print(f"Manifest written: {manifest_path}")
        except VerifyError as exc:
            print(f"error: {exc}", file=sys.stderr)
            sys.exit(1)
        return

    try:
        verify_manifest(config)
        print(f"OK — {config.encrypted_file} matches its manifest.")
    except VerifyError as exc:
        print(f"FAILED — {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach the *verify* sub-command to *subparsers*."""
    p = subparsers.add_parser(
        "verify",
        help="Verify the integrity of the encrypted vault using its manifest.",
    )
    p.add_argument(
        "--write",
        action="store_true",
        help="Write (or overwrite) the manifest instead of verifying.",
    )
    p.add_argument(
        "--config",
        default=".envault.json",
        metavar="FILE",
        help="Path to envault config file (default: .envault.json).",
    )
    p.set_defaults(func=cmd_verify)
