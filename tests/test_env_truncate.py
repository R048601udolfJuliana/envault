"""Tests for envault.env_truncate."""
from pathlib import Path
import pytest

from envault.env_truncate import TruncateError, truncate_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_truncate_keeps_first_n(tmp_dir):
    f = _write(tmp_dir / ".env", "A=1\nB=2\nC=3\nD=4\n")
    orig, kept = truncate_env(f, max_keys=2)
    assert orig == 4
    assert kept == 2
    lines = f.read_text().splitlines()
    assert "A=1" in lines
    assert "B=2" in lines
    assert "C=3" not in lines
    assert "D=4" not in lines


def test_truncate_from_end(tmp_dir):
    f = _write(tmp_dir / ".env", "A=1\nB=2\nC=3\nD=4\n")
    orig, kept = truncate_env(f, max_keys=2, from_end=True)
    assert orig == 4
    assert kept == 2
    lines = f.read_text().splitlines()
    assert "C=3" in lines
    assert "D=4" in lines
    assert "A=1" not in lines


def test_truncate_preserves_comments(tmp_dir):
    content = "# header\nA=1\n# mid\nB=2\nC=3\n"
    f = _write(tmp_dir / ".env", content)
    truncate_env(f, max_keys=2)
    text = f.read_text()
    assert "# header" in text
    assert "# mid" in text
    assert "A=1" in text
    assert "B=2" in text
    assert "C=3" not in text


def test_truncate_to_separate_dest(tmp_dir):
    src = _write(tmp_dir / ".env", "X=1\nY=2\nZ=3\n")
    dest = tmp_dir / ".env.truncated"
    truncate_env(src, dest=dest, max_keys=1)
    assert dest.exists()
    assert "X=1" in dest.read_text()
    # source unchanged
    assert "Z=3" in src.read_text()


def test_truncate_max_keys_larger_than_file(tmp_dir):
    f = _write(tmp_dir / ".env", "A=1\nB=2\n")
    orig, kept = truncate_env(f, max_keys=100)
    assert orig == 2
    assert kept == 2


def test_truncate_missing_file_raises(tmp_dir):
    with pytest.raises(TruncateError, match="not found"):
        truncate_env(tmp_dir / "missing.env", max_keys=5)


def test_truncate_zero_max_keys_raises(tmp_dir):
    f = _write(tmp_dir / ".env", "A=1\n")
    with pytest.raises(TruncateError, match="max_keys"):
        truncate_env(f, max_keys=0)
