"""Tests for envault/env_status.py."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from envault.env_status import VaultStatus, get_status


@pytest.fixture()
def config(tmp_path):
    cfg = MagicMock()
    cfg.env_file = str(tmp_path / ".env")
    cfg.encrypted_file = str(tmp_path / ".env.gpg")
    return cfg


def test_get_status_all_missing(config, tmp_path):
    status = get_status(config)
    assert not status.env_exists
    assert not status.encrypted_exists
    assert not status.manifest_exists
    assert status.manifest_ok is None
    assert status.encrypted_sha256 is None


def test_get_status_env_exists(config, tmp_path):
    Path(config.env_file).write_text("KEY=value\n")
    status = get_status(config)
    assert status.env_exists
    assert not status.encrypted_exists


def test_get_status_encrypted_exists(config, tmp_path):
    enc = Path(config.encrypted_file)
    enc.write_bytes(b"fake-gpg-data")
    status = get_status(config)
    assert status.encrypted_exists
    assert status.encrypted_sha256 is not None
    assert len(status.encrypted_sha256) == 64


def test_get_status_manifest_ok(config, tmp_path):
    import hashlib
    enc = Path(config.encrypted_file)
    enc.write_bytes(b"data")
    sha = hashlib.sha256(b"data").hexdigest()
    manifest = enc.with_suffix(".manifest")
    manifest.write_text(json.dumps({"sha256": sha}))
    status = get_status(config)
    assert status.manifest_exists
    assert status.manifest_ok is True


def test_get_status_manifest_bad_hash(config, tmp_path):
    enc = Path(config.encrypted_file)
    enc.write_bytes(b"data")
    manifest = enc.with_suffix(".manifest")
    manifest.write_text(json.dumps({"sha256": "deadbeef"}))
    status = get_status(config)
    assert status.manifest_ok is False


def test_get_status_manifest_invalid_json(config, tmp_path):
    enc = Path(config.encrypted_file)
    enc.write_bytes(b"data")
    manifest = enc.with_suffix(".manifest")
    manifest.write_text("not-json")
    status = get_status(config)
    assert status.manifest_ok is False


def test_vault_status_summary_lines_includes_recipients(config, tmp_path):
    status = VaultStatus(
        env_file=config.env_file,
        env_exists=False,
        encrypted_file=config.encrypted_file,
        encrypted_exists=False,
        manifest_file=".env.manifest",
        manifest_exists=False,
        manifest_ok=None,
        recipients=["alice@example.com", "bob@example.com"],
    )
    lines = status.summary_lines()
    combined = "\n".join(lines)
    assert "alice@example.com" in combined
    assert "bob@example.com" in combined
    assert "recipients (2)" in combined


def test_vault_status_summary_no_recipients(config):
    status = VaultStatus(
        env_file=config.env_file,
        env_exists=True,
        encrypted_file=config.encrypted_file,
        encrypted_exists=False,
        manifest_file=".env.manifest",
        manifest_exists=False,
        manifest_ok=None,
        recipients=[],
    )
    lines = "\n".join(status.summary_lines())
    assert "(none)" in lines
