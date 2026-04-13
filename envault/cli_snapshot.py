"""CLI subcommands for snapshot management."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.cli import _load_config
from envault.snapshot import (
    SnapshotError,
    delete_snapshot,
    list_snapshots,
    restore_snapshot,
    save_snapshot,
)


def cmd_snapshot_save(ns: argparse.Namespace) -> None:
    cfg = _load_config(ns)
    enc = Path(cfg.encrypted_file)
    base = enc.parent
    try:
        entry = save_snapshot(enc, ns.snapshot_name, base=base)
        print(f"Snapshot '{entry['name']}' saved at {entry['timestamp']}.")
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_snapshot_restore(ns: argparse.Namespace) -> None:
    cfg = _load_config(ns)
    enc = Path(cfg.encrypted_file)
    base = enc.parent
    try:
        restore_snapshot(ns.snapshot_name, enc, base=base)
        print(f"Snapshot '{ns.snapshot_name}' restored to {enc}.")
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_snapshot_list(ns: argparse.Namespace) -> None:
    cfg = _load_config(ns)
    enc = Path(cfg.encrypted_file)
    base = enc.parent
    try:
        entries = list_snapshots(base)
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not entries:
        print("No snapshots found.")
        return
    for e in entries:
        print(f"  {e['name']:20s}  {e['timestamp']}")


def cmd_snapshot_delete(ns: argparse.Namespace) -> None:
    cfg = _load_config(ns)
    enc = Path(cfg.encrypted_file)
    base = enc.parent
    try:
        delete_snapshot(ns.snapshot_name, base=base)
        print(f"Snapshot '{ns.snapshot_name}' deleted.")
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("snapshot", help="Manage encrypted file snapshots")
    ss = p.add_subparsers(dest="snapshot_cmd", required=True)

    p_save = ss.add_parser("save", help="Save a snapshot")
    p_save.add_argument("snapshot_name", help="Unique snapshot name")
    p_save.set_defaults(func=cmd_snapshot_save)

    p_restore = ss.add_parser("restore", help="Restore a snapshot")
    p_restore.add_argument("snapshot_name", help="Snapshot name to restore")
    p_restore.set_defaults(func=cmd_snapshot_restore)

    p_list = ss.add_parser("list", help="List all snapshots")
    p_list.set_defaults(func=cmd_snapshot_list)

    p_del = ss.add_parser("delete", help="Delete a snapshot")
    p_del.add_argument("snapshot_name", help="Snapshot name to delete")
    p_del.set_defaults(func=cmd_snapshot_delete)
