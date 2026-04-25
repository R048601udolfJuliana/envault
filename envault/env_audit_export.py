"""Export audit log entries to various formats (json, csv, text)."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import List, Literal

from envault.audit import AuditLog, AuditEntry

ExportFormat = Literal["json", "csv", "text"]


class AuditExportError(Exception):
    pass


def _load_entries(log_path: Path) -> List[AuditEntry]:
    log = AuditLog(log_path)
    return log.read()


def export_audit(
    log_path: Path,
    dest: Path,
    fmt: ExportFormat = "json",
    limit: int | None = None,
) -> int:
    """Export audit log to *dest* in the given format.

    Returns the number of entries written.
    """
    entries = _load_entries(log_path)
    if not entries:
        raise AuditExportError(f"No audit entries found in {log_path}")

    if limit is not None and limit > 0:
        entries = entries[-limit:]

    if fmt == "json":
        data = [e.to_dict() for e in entries]
        dest.write_text(json.dumps(data, indent=2), encoding="utf-8")
    elif fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["timestamp", "action", "actor", "detail"])
        writer.writeheader()
        for e in entries:
            writer.writerow(e.to_dict())
        dest.write_text(buf.getvalue(), encoding="utf-8")
    elif fmt == "text":
        lines = []
        for e in entries:
            d = e.to_dict()
            lines.append(f"[{d['timestamp']}] {d['action']} by {d['actor']}: {d['detail']}")
        dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        raise AuditExportError(f"Unknown format: {fmt!r}")

    return len(entries)
