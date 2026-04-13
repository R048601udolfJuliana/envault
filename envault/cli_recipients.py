"""CLI sub-commands for managing envault recipients."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.recipients import (
    RecipientsError,
    add_recipient,
    load_recipients,
    remove_recipient,
    resolve_recipients,
)


def cmd_recipients_list(args: argparse.Namespace) -> int:
    """Print all configured recipients."""
    base = Path(args.dir) if getattr(args, "dir", None) else None
    resolved = resolve_recipients(base)
    fps = load_recipients(base)
    if not fps:
        print("No recipients configured.")
        return 0
    resolved_map = {k.fingerprint: k for k in resolved}
    for fp in fps:
        key = resolved_map.get(fp)
        label = str(key) if key else "(key not in local keyring)"
        print(f"  {fp}  {label}")
    return 0


def cmd_recipients_add(args: argparse.Namespace) -> int:
    """Add a recipient fingerprint."""
    base = Path(args.dir) if getattr(args, "dir", None) else None
    try:
        updated = add_recipient(args.fingerprint, base)
        print(f"Added {args.fingerprint}. Total recipients: {len(updated)}")
        return 0
    except RecipientsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def cmd_recipients_remove(args: argparse.Namespace) -> int:
    """Remove a recipient fingerprint."""
    base = Path(args.dir) if getattr(args, "dir", None) else None
    try:
        updated = remove_recipient(args.fingerprint, base)
        print(f"Removed {args.fingerprint}. Remaining recipients: {len(updated)}")
        return 0
    except RecipientsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def register_subcommands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach recipient sub-commands to an existing subparsers group."""
    rp = subparsers.add_parser("recipients", help="Manage encryption recipients")
    rp.add_argument("--dir", default=None, help="Project directory (default: cwd)")
    rsub = rp.add_subparsers(dest="recipients_cmd", required=True)

    rsub.add_parser("list", help="List current recipients").set_defaults(
        func=cmd_recipients_list
    )

    add_p = rsub.add_parser("add", help="Add a recipient by fingerprint")
    add_p.add_argument("fingerprint", help="GPG key fingerprint")
    add_p.set_defaults(func=cmd_recipients_add)

    rm_p = rsub.add_parser("remove", help="Remove a recipient by fingerprint")
    rm_p.add_argument("fingerprint", help="GPG key fingerprint")
    rm_p.set_defaults(func=cmd_recipients_remove)
