"""Tests for envault.template."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.template import  keys_from_template, _parse_env_keys


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


# --- _parse_env_keys ---

def test_parse_env_keys_basic():
    text = "DB_HOST=localhost\nDB_PORT=5432\n"
    assert _parse_env_keys(text) == ["DB_HOST", "DB_PORT"]


def test_parse_env_keys_ignores_comments_and_blanks():
    text = "# comment\n\nSECRET=value\n"
    assert _parse_env_keys(text) == ["SECRET"]


def test_parse_env_keys_no_value_still_captured():
    text = "KEY=\n"
    assert _parse_env_keys(text) == ["KEY"]


# --- generate_template ---

def test_generate_template_replaces_values(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "API_KEY=supersecret\nDEBUG=true\n")
    result = generate_template(src)
    assert "API_KEY=" in result
    assert "supersecret" not in result
    assert "DEBUG=" in result
    assert "true" not in result


def test_generate_template_custom_placeholder(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "TOKEN=abc123\n")
    result = generate_template(src, placeholder="CHANGEME")
    assert "TOKEN=CHANGEME" in result


def test_generate_template_keeps_comments_by_default(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "# Database\nDB_URL=postgres://localhost/db\n")
    result = generate_template(src)
    assert "# Database" in result


def test_generate_template_strips_comments(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "# comment\nFOO=bar\n")
    result = generate_template(src, keep_comments=False)
    assert "# comment" not in result
    assert "FOO=" in result


def test_generate_template_writes_output_file(tmp_dir: Path):
    src = _write(tmp_dir / ".env", "X=1\n")
    out = tmp_dir / ".env.template"
    generate_template(src, output_path=out)
    assert out.exists()
    assert "X=" in out.read_text()


def test_generate_template_missing_source_raises(tmp_dir: Path):
    with pytest.raises(TemplateError, match="not found"):
        generate_template(tmp_dir / "nonexistent.env")


# --- keys_from_template ---

def test_keys_from_template_returns_names(tmp_dir: Path):
    tpl = _write(tmp_dir / ".env.template", "FOO=\nBAR=\n")
    assert keys_from_template(tpl) == ["FOO", "BAR"]


def test_keys_from_template_missing_file_raises(tmp_dir: Path):
    with pytest.raises(TemplateError, match="not found"):
        keys_from_template(tmp_dir / "missing.template")
