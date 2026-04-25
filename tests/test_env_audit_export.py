"""Tests for envault.env_audit_export."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from envault.audit import AuditLog
from envault.env_audit_export import AuditExportError, export_audit


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def log_file(tmp_dir: Path) -> Path:
    log = AuditLog(tmp_dir / "audit.jsonl")
    log.record(action="push", actor="alice", detail="pushed .env")
    log.record(action="pull", actor="bob", detail="pulled .env")
    log.record(action="rotate", actor="alice", detail="rotated keys")
    return tmp_dir / "audit.jsonl"


def test_export_json_creates_file(tmp_dir: Path, log_file: Path) -> None:
    dest = tmp_dir / "out.json"
    count = export_audit(log_file, dest, fmt="json")
    assert dest.exists()
    assert count == 3


def test_export_json_content(tmp_dir: Path, log_file: Path) -> None:
    dest = tmp_dir / "out.json"
    export_audit(log_file, dest, fmt="json")
    data = json.loads(dest.read_text())
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["action"] == "push"
    assert data[0]["actor"] == "alice"


def test_export_csv_creates_file(tmp_dir: Path, log_file: Path) -> None:
    dest = tmp_dir / "out.csv"
    count = export_audit(log_file, dest, fmt="csv")
    assert dest.exists()
    assert count == 3


def test_export_csv_has_header(tmp_dir: Path, log_file: Path) -> None:
    dest = tmp_dir / "out.csv"
    export_audit(log_file, dest, fmt="csv")
    rows = list(csv.DictReader(dest.read_text().splitlines()))
    assert len(rows) == 3
    assert "action" in rows[0]
    assert "actor" in rows[0]


def test_export_text_creates_file(tmp_dir: Path, log_file: Path) -> None:
    dest = tmp_dir / "out.txt"
    count = export_audit(log_file, dest, fmt="text")
    assert dest.exists()
    assert count == 3


def test_export_text_contains_action(tmp_dir: Path, log_file: Path) -> None:
    dest = tmp_dir / "out.txt"
    export_audit(log_file, dest, fmt="text")
    content = dest.read_text()
    assert "push" in content
    assert "alice" in content


def test_export_limit(tmp_dir: Path, log_file: Path) -> None:
    dest = tmp_dir / "out.json"
    count = export_audit(log_file, dest, fmt="json", limit=2)
    data = json.loads(dest.read_text())
    assert count == 2
    assert len(data) == 2
    assert data[-1]["action"] == "rotate"


def test_export_empty_log_raises(tmp_dir: Path) -> None:
    empty_log = tmp_dir / "empty.jsonl"
    empty_log.write_text("")
    dest = tmp_dir / "out.json"
    with pytest.raises(AuditExportError, match="No audit entries"):
        export_audit(empty_log, dest)


def test_export_unknown_format_raises(tmp_dir: Path, log_file: Path) -> None:
    dest = tmp_dir / "out.xml"
    with pytest.raises(AuditExportError, match="Unknown format"):
        export_audit(log_file, dest, fmt="xml")  # type: ignore[arg-type]
