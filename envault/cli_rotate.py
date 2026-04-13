"""CLI sub-command: envault rotate."""

from __future__ import annotations

import argparse
import sys

from envault.cli import _load_config
from envault.rotate import rotate, RotationError
from envault.passphrase import passphrase_from_env
from envault.audit import AuditLog
from envault.config import ConfigError


def cmd_rotate(args: argparse.Namespace) -> None:
    """Handle the *rotate* sub-command."""
    try:
        config = _load_config(args)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    new_recipients: list[str] = args.recipient
    if not new_recipients:
        # Fall back to existing recipients when none are provided.
        new_recipients = list(config.recipients)

    passphrase = passphrase_from_env()

    audit_log: AuditLog | None = None
    if hasattr(args, "audit_file") and args.audit_file:
        audit_log = AuditLog(args.audit_file)

    try:
        result = rotate(
            config,
            new_recipients=new_recipients,
            passphrase=passphrase,
            audit_log=audit_log,
            dry_run=getattr(args, "dry_run", False),
        )
    except RotationError as exc:
        print(f"[envault] rotation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if getattr(args, "dry_run", False):
        print("[envault] dry-run: rotation validated successfully (no files changed).")
    else:
        print(f"[envault] rotated → {result}")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *rotate* sub-command on *subparsers*."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "rotate",
        help="Re-encrypt the vault for a new set of GPG recipients.",
    )
    parser.add_argument(
        "-r",
        "--recipient",
        action="append",
        default=[],
        metavar="KEY_ID",
        help="GPG key ID to encrypt for (repeatable). Defaults to current recipients.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Validate the rotation without writing any files.",
    )
    parser.add_argument(
        "--audit-file",
        default=None,
        metavar="PATH",
        help="Append a rotation event to this audit log file.",
    )
    parser.set_defaults(func=cmd_rotate)
