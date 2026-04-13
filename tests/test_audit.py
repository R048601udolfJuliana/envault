"""Tests for envault.audit module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.audit import AuditEntry, AuditLog


@pytest.fixture
def log_file(tmp_path: Path) -> Path:
    return tmp_path / "test_audit.log"


def test_audit_entry_to_dict():
    entry = AuditEntry(
        action="push",
        actor="ABCD1234",
        target="vault/.env.gpg",
        timestamp="2024-01-01T00:00:00+00:00",
        details="forced",
    )
    d = entry.to_dict()
    assert d["action"] == "push"
    assert d["actor"] == "ABCD1234"
    assert d["target"] == "vault/.env.gpg"
    assert d["details"] == "forced"


def test_audit_entry_from_dict_roundtrip():
    original = AuditEntry(action="pull", actor="FP123", target=".env", details=None)
    restored = AuditEntry.from_dict(original.to_dict())
    assert restored.action == original.action
    assert restored.actor == original.actor
    assert restored.target == original.target
    assert restored.details is None


def test_audit_log_record_and_read(log_file: Path):
    log = AuditLog(str(log_file))
    entry = AuditEntry(action="push", actor="KEY1", target="vault/.env.gpg")
    log.record(entry)

    entries = log.read_all()
    assert len(entries) == 1
    assert entries[0].action == "push"
    assert entries[0].actor == "KEY1"


def test_audit_log_multiple_entries(log_file: Path):
    log = AuditLog(str(log_file))
    for i in range(3):
        log.record(AuditEntry(action="pull", actor=f"KEY{i}", target=".env"))

    entries = log.read_all()
    assert len(entries) == 3
    assert [e.actor for e in entries] == ["KEY0", "KEY1", "KEY2"]


def test_audit_log_read_empty(log_file: Path):
    log = AuditLog(str(log_file))
    assert log.read_all() == []


def test_audit_log_clear(log_file: Path):
    log = AuditLog(str(log_file))
    log.record(AuditEntry(action="push", actor="K", target="f"))
    assert log_file.exists()
    log.clear()
    assert not log_file.exists()


def test_audit_log_skips_malformed_lines(log_file: Path):
    log_file.write_text("not-json\n{\"action\":\"push\",\"actor\":\"K\",\"target\":\"f\",\"timestamp\":\"t\",\"details\":null}\n")
    log = AuditLog(str(log_file))
    entries = log.read_all()
    assert len(entries) == 1
    assert entries[0].action == "push"
