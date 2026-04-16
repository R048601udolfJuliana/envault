"""Tests for envault.pin."""
import json
from pathlib import Path

import pytest

from envault.pin import (
    PinError,
    check_pin,
    load_pin,
    pin_file,
    remove_pin,
)


@pytest.fixture()
def tmp_dir(tmp_path: Path):
    return tmp_path


@pytest.fixture()
def enc_file(tmp_dir: Path) -> Path:
    p = tmp_dir / "secrets.env.gpg"
    p.write_bytes(b"encrypted-content")
    return p


def test_pin_file_creates_pin(enc_file, tmp_dir):
    pin_path = tmp_dir / ".envault-pin"
    digest = pin_file(enc_file, pin_path=pin_path)
    assert pin_path.exists()
    assert len(digest) == 64  # sha256 hex


def test_pin_file_stores_correct_hash(enc_file, tmp_dir):
    pin_path = tmp_dir / ".envault-pin"
    digest = pin_file(enc_file, pin_path=pin_path)
    data = json.loads(pin_path.read_text())
    assert data["sha256"] == digest
    assert data["file"] == str(enc_file)


def test_pin_file_missing_raises(tmp_dir):
    with pytest.raises(PinError, match="not found"):
        pin_file(tmp_dir / "missing.gpg", pin_path=tmp_dir / ".pin")


def test_check_pin_returns_true_when_matching(enc_file, tmp_dir):
    pin_path = tmp_dir / ".envault-pin"
    pin_file(enc_file, pin_path=pin_path)
    assert check_pin(enc_file, pin_path=pin_path) is True


def test_check_pin_returns_false_after_modification(enc_file, tmp_dir):
    pin_path = tmp_dir / ".envault-pin"
    pin_file(enc_file, pin_path=pin_path)
    enc_file.write_bytes(b"tampered")
    assert check_pin(enc_file, pin_path=pin_path) is False


def test_check_pin_raises_when_no_pin_file(enc_file, tmp_dir):
    with pytest.raises(PinError, match="Pin file not found"):
        check_pin(enc_file, pin_path=tmp_dir / "nonexistent")


def test_check_pin_raises_on_corrupt_pin(enc_file, tmp_dir):
    pin_path = tmp_dir / ".envault-pin"
    pin_path.write_text("not json")
    with pytest.raises(PinError, match="Corrupt"):
        check_pin(enc_file, pin_path=pin_path)


def test_load_pin_returns_none_when_missing(tmp_dir):
    assert load_pin(pin_path=tmp_dir / "nope") is None


def test_load_pin_returns_dict(enc_file, tmp_dir):
    pin_path = tmp_dir / ".envault-pin"
    pin_file(enc_file, pin_path=pin_path)
    data = load_pin(pin_path=pin_path)
    assert isinstance(data, dict)
    assert "sha256" in data


def test_remove_pin_deletes_file(enc_file, tmp_dir):
    pin_path = tmp_dir / ".envault-pin"
    pin_file(enc_file, pin_path=pin_path)
    assert remove_pin(pin_path=pin_path) is True
    assert not pin_path.exists()


def test_remove_pin_returns_false_when_missing(tmp_dir):
    assert remove_pin(pin_path=tmp_dir / "nope") is False
