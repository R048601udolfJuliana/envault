"""Tests for envault.env_sample."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_sample import SampleError, generate_sample


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text)
    return p


def test_generate_sample_strips_values(tmp_dir):
    src = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PASS=secret\n")
    out = generate_sample(src)
    lines = out.read_text().splitlines()
    assert "DB_HOST=" in lines
    assert "DB_PASS=" in lines
    assert not any("localhost" in l or "secret" in l for l in lines)


def test_generate_sample_default_dest_name(tmp_dir):
    src = _write(tmp_dir / ".env", "KEY=val\n")
    out = generate_sample(src)
    assert out == tmp_dir / ".env.sample"


def test_generate_sample_custom_dest(tmp_dir):
    src = _write(tmp_dir / ".env", "KEY=val\n")
    dest = tmp_dir / "custom.sample"
    out = generate_sample(src, dest)
    assert out == dest
    assert dest.exists()


def test_generate_sample_preserves_comments(tmp_dir):
    src = _write(tmp_dir / ".env", "# database\nDB_HOST=localhost\n")
    out = generate_sample(src)
    content = out.read_text()
    assert "# database" in content


def test_generate_sample_preserves_blank_lines(tmp_dir):
    src = _write(tmp_dir / ".env", "A=1\n\nB=2\n")
    out = generate_sample(src)
    lines = out.read_text().splitlines()
    assert "" in lines


def test_generate_sample_missing_file_raises(tmp_dir):
    with pytest.raises(SampleError, match="not found"):
        generate_sample(tmp_dir / "nonexistent.env")


def test_generate_sample_empty_file(tmp_dir):
    src = _write(tmp_dir / ".env", "")
    out = generate_sample(src)
    assert out.exists()
