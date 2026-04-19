"""Tests for envault.env_mask."""
from pathlib import Path

import pytest

from envault.env_mask import MaskError, mask_env


@pytest.fixture()
def tmp_dir(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def test_mask_auto_detects_sensitive_keys(tmp_dir):
    src = _write(tmp_dir / ".env", "API_KEY=supersecret\nNAME=alice\n")
    masked = mask_env(src, auto_detect=True)
    assert "API_KEY" in masked
    assert masked["API_KEY"] == "supersecret"
    assert "NAME" not in masked


def test_mask_explicit_key(tmp_dir):
    src = _write(tmp_dir / ".env", "CUSTOM=value\nOTHER=ok\n")
    masked = mask_env(src, keys=["CUSTOM"], auto_detect=False)
    assert masked == {"CUSTOM": "value"}


def test_mask_writes_dest_file(tmp_dir):
    src = _write(tmp_dir / ".env", "SECRET_TOKEN=abc123\nFOO=bar\n")
    dest = tmp_dir / "masked.env"
    mask_env(src, dest)
    content = dest.read_text()
    assert "abc123" not in content
    assert "***" in content
    assert "FOO=bar" in content


def test_mask_custom_placeholder(tmp_dir):
    src = _write(tmp_dir / ".env", "PASSWORD=hunter2\n")
    dest = tmp_dir / "out.env"
    mask_env(src, dest, placeholder="REDACTED")
    assert "REDACTED" in dest.read_text()


def test_mask_preserves_comments_and_blanks(tmp_dir):
    src = _write(tmp_dir / ".env", "# comment\n\nFOO=bar\n")
    dest = tmp_dir / "out.env"
    mask_env(src, dest)
    content = dest.read_text()
    assert "# comment" in content
    assert "FOO=bar" in content


def test_mask_missing_file_raises(tmp_dir):
    with pytest.raises(MaskError):
        mask_env(tmp_dir / "nonexistent.env")


def test_mask_no_auto_skips_sensitive(tmp_dir):
    src = _write(tmp_dir / ".env", "API_KEY=secret\n")
    masked = mask_env(src, auto_detect=False)
    assert masked == {}


def test_mask_empty_value_not_masked(tmp_dir):
    src = _write(tmp_dir / ".env", "SECRET=\n")
    masked = mask_env(src)
    assert "SECRET" not in masked
