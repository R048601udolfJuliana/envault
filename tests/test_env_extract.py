"""Tests for envault.env_extract."""
from pathlib import Path

import pytest

from envault.env_extract import ExtractError, extract_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text)
    return p


def test_extract_basic(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DB=postgres\nAPI_KEY=secret\nDEBUG=true\n")
    dest = extract_env(src, ["DB", "DEBUG"])
    content = dest.read_text()
    assert "DB=postgres" in content
    assert "DEBUG=true" in content
    assert "API_KEY" not in content


def test_extract_default_dest_name(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=bar\nBAZ=qux\n")
    dest = extract_env(src, ["FOO"])
    assert dest.name == ".extracted.env"


def test_extract_custom_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=bar\nBAZ=qux\n")
    custom = tmp_dir / "subset.env"
    dest = extract_env(src, ["BAZ"], dest=custom)
    assert dest == custom.resolve()
    assert "BAZ=qux" in dest.read_text()


def test_extract_preserves_comments(tmp_dir: Path) -> None:
    src = _write(
        tmp_dir / ".env",
        "# database\nDB=postgres\n# api\nAPI_KEY=secret\n",
    )
    dest = extract_env(src, ["DB"])
    content = dest.read_text()
    assert "# database" in content
    assert "DB=postgres" in content


def test_extract_missing_key_raises(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=bar\n")
    with pytest.raises(ExtractError, match="NOPE"):
        extract_env(src, ["NOPE"])


def test_extract_missing_key_ok_when_flag_set(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=bar\n")
    dest = extract_env(src, ["NOPE"], missing_ok=True)
    # File is written even if empty
    assert dest.exists()


def test_extract_missing_source_raises(tmp_dir: Path) -> None:
    with pytest.raises(ExtractError, match="not found"):
        extract_env(tmp_dir / "ghost.env", ["FOO"])


def test_extract_no_keys_raises(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "FOO=bar\n")
    with pytest.raises(ExtractError, match="No keys"):
        extract_env(src, [])


def test_extract_returns_resolved_path(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "X=1\n")
    dest = extract_env(src, ["X"])
    assert dest.is_absolute()
