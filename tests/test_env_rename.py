"""Tests for envault.env_rename."""
from pathlib import Path

import pytest

from envault.env_rename import RenameError, rename_key


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content)
    return p


def test_rename_basic(tmp_dir):
    f = _write(tmp_dir / ".env", "FOO=bar\nBAZ=qux\n")
    changed = rename_key(f, "FOO", "NEW_FOO")
    assert changed == 1
    text = f.read_text()
    assert "NEW_FOO=bar" in text
    assert "FOO=" not in text


def test_rename_preserves_value_and_comments(tmp_dir):
    content = "# comment\nDB_HOST=localhost\nDB_PORT=5432\n"
    f = _write(tmp_dir / ".env", content)
    rename_key(f, "DB_HOST", "DATABASE_HOST")
    text = f.read_text()
    assert "# comment" in text
    assert "DATABASE_HOST=localhost" in text
    assert "DB_PORT=5432" in text


def test_rename_missing_file_raises(tmp_dir):
    with pytest.raises(RenameError, match="not found"):
        rename_key(tmp_dir / "no.env", "A", "B")


def test_rename_key_not_found_raises(tmp_dir):
    f = _write(tmp_dir / ".env", "FOO=1\n")
    with pytest.raises(RenameError, match="not found"):
        rename_key(f, "MISSING", "NEW")


def test_rename_duplicate_key_raises(tmp_dir):
    f = _write(tmp_dir / ".env", "FOO=1\nBAR=2\n")
    with pytest.raises(RenameError, match="already exists"):
        rename_key(f, "FOO", "BAR")


def test_rename_invalid_new_key_raises(tmp_dir):
    f = _write(tmp_dir / ".env", "FOO=1\n")
    with pytest.raises(RenameError, match="Invalid key"):
        rename_key(f, "FOO", "123INVALID")


def test_rename_same_key_is_noop(tmp_dir):
    f = _write(tmp_dir / ".env", "FOO=bar\n")
    changed = rename_key(f, "FOO", "FOO")
    assert changed == 1
    assert f.read_text() == "FOO=bar\n"
