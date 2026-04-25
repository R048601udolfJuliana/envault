"""Tests for envault.env_checksum."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.env_checksum import (
    ChecksumError,
    compute_checksum,
    save_checksum,
    verify_checksum,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


# ---------------------------------------------------------------------------
# compute_checksum
# ---------------------------------------------------------------------------

def test_compute_checksum_returns_hex_string(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=value\n")
    digest = compute_checksum(f)
    assert isinstance(digest, str)
    assert len(digest) == 64


def test_compute_checksum_deterministic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "FOO=bar\n")
    assert compute_checksum(f) == compute_checksum(f)


def test_compute_checksum_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(ChecksumError, match="not found"):
        compute_checksum(tmp_dir / "missing.env")


# ---------------------------------------------------------------------------
# save_checksum
# ---------------------------------------------------------------------------

def test_save_checksum_creates_default_sidecar(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=val\n")
    dest = save_checksum(f)
    assert dest == f.with_suffix(".checksum.json")
    assert dest.exists()


def test_save_checksum_content_is_valid_json(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "A=1\n")
    dest = save_checksum(f)
    data = json.loads(dest.read_text())
    assert "sha256" in data
    assert data["file"] == ".env"


def test_save_checksum_custom_dest(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "X=y\n")
    custom = tmp_dir / "my.checksum.json"
    result = save_checksum(f, custom)
    assert result == custom
    assert custom.exists()


def test_save_checksum_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(ChecksumError, match="not found"):
        save_checksum(tmp_dir / "ghost.env")


# ---------------------------------------------------------------------------
# verify_checksum
# ---------------------------------------------------------------------------

def test_verify_checksum_passes_for_unchanged_file(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=value\n")
    save_checksum(f)
    assert verify_checksum(f) is True


def test_verify_checksum_fails_after_modification(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=original\n")
    save_checksum(f)
    f.write_text("KEY=modified\n")
    assert verify_checksum(f) is False


def test_verify_checksum_missing_env_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(ChecksumError, match="not found"):
        verify_checksum(tmp_dir / "missing.env")


def test_verify_checksum_missing_checksum_file_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "K=v\n")
    with pytest.raises(ChecksumError, match="Checksum file not found"):
        verify_checksum(f)


def test_verify_checksum_malformed_checksum_file_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "K=v\n")
    sidecar = f.with_suffix(".checksum.json")
    sidecar.write_text("not-json")
    with pytest.raises(ChecksumError, match="Malformed"):
        verify_checksum(f)
