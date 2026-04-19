"""Tests for envault.env_filter."""
from pathlib import Path
import pytest
from envault.env_filter import FilterError, filter_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text)
    return p


def test_filter_by_prefix(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=test\n")
    dest = tmp_dir / "out.env"
    count = filter_env(src, dest, prefix="DB_")
    assert count == 2
    content = dest.read_text()
    assert "DB_HOST" in content
    assert "DB_PORT" in content
    assert "APP_NAME" not in content


def test_filter_by_pattern(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "SECRET_KEY=abc\nPUBLIC_URL=http://x\nSECRET_SALT=xyz\n")
    dest = tmp_dir / "out.env"
    count = filter_env(src, dest, pattern=r"^SECRET_")
    assert count == 2
    content = dest.read_text()
    assert "SECRET_KEY" in content
    assert "SECRET_SALT" in content
    assert "PUBLIC_URL" not in content


def test_filter_by_keys(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "A=1\nB=2\nC=3\n")
    dest = tmp_dir / "out.env"
    count = filter_env(src, dest, keys=["A", "C"])
    assert count == 2
    assert "B=" not in dest.read_text()


def test_filter_exclude(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DB_HOST=x\nAPP_NAME=y\nDB_PORT=z\n")
    dest = tmp_dir / "out.env"
    count = filter_env(src, dest, prefix="DB_", exclude=True)
    assert count == 1
    assert "APP_NAME" in dest.read_text()


def test_filter_preserves_comments(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "# comment\nDB_HOST=x\nAPP=y\n")
    dest = tmp_dir / "out.env"
    filter_env(src, dest, prefix="DB_")
    assert "# comment" in dest.read_text()


def test_filter_missing_source_raises(tmp_dir: Path) -> None:
    with pytest.raises(FilterError, match="not found"):
        filter_env(tmp_dir / "missing.env", tmp_dir / "out.env", prefix="X")


def test_filter_no_criteria_raises(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "A=1\n")
    with pytest.raises(FilterError, match="At least one"):
        filter_env(src, tmp_dir / "out.env")
