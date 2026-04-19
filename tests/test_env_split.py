"""Tests for envault.env_split"""
from pathlib import Path

import pytest

from envault.env_split import SplitError, split_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def test_split_basic(tmp_dir: Path) -> None:
    src = _write(
        tmp_dir / ".env",
        "DB_HOST=localhost\nDB_PORT=5432\nAWS_KEY=abc\nAPP_NAME=myapp\n",
    )
    written = split_env(src, tmp_dir / "out", ["DB", "AWS"])
    assert ".env.db" in written
    assert ".env.aws" in written
    db_content = written[".env.db"].read_text()
    assert "DB_HOST" in db_content
    assert "DB_PORT" in db_content
    assert "AWS_KEY" not in db_content


def test_split_unmatched_goes_to_default(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DB_HOST=localhost\nUNKNOWN=foo\n")
    written = split_env(src, tmp_dir / "out", ["DB"])
    assert ".env.other" in written
    assert "UNKNOWN" in written[".env.other"].read_text()


def test_split_custom_default_file(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "X=1\nY=2\n")
    written = split_env(src, tmp_dir / "out", ["DB"], default_file=".env.misc")
    assert ".env.misc" in written


def test_split_missing_source_raises(tmp_dir: Path) -> None:
    with pytest.raises(SplitError, match="not found"):
        split_env(tmp_dir / "missing.env", tmp_dir / "out", ["DB"])


def test_split_ignores_comments_and_blanks(tmp_dir: Path) -> None:
    src = _write(
        tmp_dir / ".env",
        "# comment\n\nDB_HOST=localhost\n",
    )
    written = split_env(src, tmp_dir / "out", ["DB"])
    assert ".env.db" in written
    assert "# comment" not in written[".env.db"].read_text()


def test_split_creates_dest_dir(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "APP_KEY=secret\n")
    dest = tmp_dir / "nested" / "output"
    split_env(src, dest, ["APP"])
    assert dest.exists()


def test_split_empty_prefix_bucket_not_written(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DB_HOST=localhost\n")
    written = split_env(src, tmp_dir / "out", ["DB", "AWS"])
    assert ".env.aws" not in written
