"""Tests for envault.env_scope."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_scope import ScopeError, scope_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text, encoding="utf-8")
    return p


def test_scope_keeps_matching_keys(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DEV_DB=sqlite\nPROD_DB=postgres\nAPP_NAME=myapp\n")
    out = scope_env(src, "dev", dest=tmp_dir / "out.env", keep_unscoped=False)
    content = out.read_text()
    assert "DEV_DB=sqlite" in content
    assert "PROD_DB" not in content
    assert "APP_NAME" not in content


def test_scope_keep_unscoped_by_default(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DEV_DB=sqlite\nPROD_DB=postgres\nAPP_NAME=myapp\n")
    out = scope_env(src, "dev", dest=tmp_dir / "out.env")
    content = out.read_text()
    assert "DEV_DB=sqlite" in content
    assert "APP_NAME=myapp" in content
    assert "PROD_DB" not in content


def test_scope_strip_prefix(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DEV_DB=sqlite\nDEV_HOST=localhost\n")
    out = scope_env(src, "dev", dest=tmp_dir / "out.env", strip_prefix=True)
    content = out.read_text()
    assert "DB=sqlite" in content
    assert "HOST=localhost" in content
    assert "DEV_" not in content


def test_scope_default_dest_name(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "PROD_KEY=secret\n")
    out = scope_env(src, "prod")
    assert out.name == ".env.prod"


def test_scope_preserves_comments_and_blanks(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "# comment\n\nDEV_X=1\n")
    out = scope_env(src, "dev", dest=tmp_dir / "out.env")
    content = out.read_text()
    assert "# comment" in content


def test_scope_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(ScopeError, match="not found"):
        scope_env(tmp_dir / "missing.env", "dev")


def test_scope_empty_scope_raises(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "DEV_X=1\n")
    with pytest.raises(ScopeError, match="non-empty"):
        scope_env(src, "")


def test_scope_case_insensitive_match(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "dev_key=value\n")
    out = scope_env(src, "DEV", dest=tmp_dir / "out.env", keep_unscoped=False)
    assert "dev_key=value" in out.read_text()
