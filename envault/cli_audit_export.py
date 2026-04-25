"""CLI subcommands for exporting the audit log."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.audit import AuditLog
from envault.config import ConfigError, EnvaultConfig
from envault.env_audit_export import AuditExportError, export_audit


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    return EnvaultConfig.load(cfg_path)


def cmd_audit_export(args: argparse.Namespace) -> None:
    try:
        cfg = _load_config(args)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    log_path = Path(cfg.base_dir) / ".envault_audit.jsonl"
    dest = Path(args.output)
    fmt = args.format
    limit = args.limit

    try:
        count = export_audit(log_path, dest, fmt=fmt, limit=limit)
        print(f"Exported {count} audit entries to {dest} ({fmt})")
    except AuditExportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("audit-export", help="Export audit log to a file")
    p.add_argument("output", help="Destination file path")
    p.add_argument(
        "--format",
        choices=["json", "csv", "text"],
        default="json",
        help="Output format (default: json)",
    )
    p.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Export only the last N entries",
    )
    p.set_defaults(func=cmd_audit_export)
