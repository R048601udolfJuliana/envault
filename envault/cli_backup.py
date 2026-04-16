"""CLI subcommands for backup management."""

from __future__ import annotations

import argparse
import sys

from envault.backup import BackupError, create_backup, list_backups, restore_backup
from envault.config import ConfigError, EnvaultConfig


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    config_path = getattr(args, "config", ".envault.json")
    return EnvaultConfig.load(config_path)


def cmd_backup_create(args: argparse.Namespace) -> None:
    """Create a backup of the current encrypted file."""
    try:
        config = _load_config(args)
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        path = create_backup(config, label=getattr(args, "label", None))
        print(f"Backup created: {path}")
    except BackupError as exc:
        print(f"Backup error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_backup_list(args: argparse.Namespace) -> None:
    """List all available backups."""
    try:
        config = _load_config(args)
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        backups = list_backups(config)
    except BackupError as exc:
        print(f"Backup error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not backups:
        print("No backups found.")
        return

    for entry in backups:
        label = f"  [{entry['label']}]" if entry.get("label") else ""
        print(f"{entry['name']}{label}  {entry['created_at']}")


def cmd_backup_restore(args: argparse.Namespace) -> None:
    """Restore a backup by name."""
    try:
        config = _load_config(args)
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        dest = restore_backup(config, args.name, force=args.force)
        print(f"Restored backup '{args.name}' to {dest}")
    except BackupError as exc:
        print(f"Backup error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register backup subcommands onto the given subparsers action."""
    backup_parser = subparsers.add_parser("backup", help="Manage encrypted file backups")
    backup_sub = backup_parser.add_subparsers(dest="backup_cmd", required=True)

    # backup create
    create_parser = backup_sub.add_parser("create", help="Create a new backup")
    create_parser.add_argument("--label", default=None, help="Optional label for the backup")
    create_parser.set_defaults(func=cmd_backup_create)

    # backup list
    list_parser = backup_sub.add_parser("list", help="List available backups")
    list_parser.set_defaults(func=cmd_backup_list)

    # backup restore
    restore_parser = backup_sub.add_parser("restore", help="Restore a backup")
    restore_parser.add_argument("name", help="Name of the backup to restore")
    restore_parser.add_argument(
        "--force", action="store_true", help="Overwrite existing encrypted file"
    )
    restore_parser.set_defaults(func=cmd_backup_restore)
