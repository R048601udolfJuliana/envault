"""Tests for envault.export."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.export import ExportError, export_env, _parse_env


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        "# comment\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "SECRET_KEY=\"my secret\"\n"
        "EMPTY_LINE_BELOW=1\n"
        "\n",
        encoding="utf-8",
    )
    return p


# ---------------------------------------------------------------------------
# _parse_env
# ---------------------------------------------------------------------------

def test_parse_env_basic(env_file: Path) -> None:
    pairs = _parse_env(env_file.read_text())
    assert pairs["DB_HOST"] == "localhost"
    assert pairs["DB_PORT"] == "5432"


def test_parse_env_strips_double_quotes(env_file: Path) -> None:
    pairs = _parse_env(env_file.read_text())
    assert pairs["SECRET_KEY"] == "my secret"


def test_parse_env_ignores_comments(env_file: Path) -> None:
    pairs = _parse_env(env_file.read_text())
    assert all(not k.startswith("#") for k in pairs)


def test_parse_env_empty_text() -> None:
    assert _parse_env("") == {}


# ---------------------------------------------------------------------------
# export_env — dotenv format
# ---------------------------------------------------------------------------

def test_export_dotenv_format(env_file: Path) -> None:
    result = export_env(env_file, fmt="dotenv")
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result


# ---------------------------------------------------------------------------
# export_env — shell format
# ---------------------------------------------------------------------------

def test_export_shell_format(env_file: Path) -> None:
    result = export_env(env_file, fmt="shell")
    assert "export DB_HOST=localhost" in result
    assert "export SECRET_KEY=" in result


# ---------------------------------------------------------------------------
# export_env — json format
# ---------------------------------------------------------------------------

def test_export_json_format(env_file: Path) -> None:
    result = export_env(env_file, fmt="json")
    data = json.loads(result)
    assert data["DB_HOST"] == "localhost"
    assert data["DB_PORT"] == "5432"


# ---------------------------------------------------------------------------
# export_env — output file
# ---------------------------------------------------------------------------

def test_export_writes_output_file(env_file: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.json"
    export_env(env_file, fmt="json", output=out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert "DB_HOST" in data


# ---------------------------------------------------------------------------
# export_env — error cases
# ---------------------------------------------------------------------------

def test_export_missing_source_raises(tmp_path: Path) -> None:
    with pytest.raises(ExportError, match="not found"):
        export_env(tmp_path / "nonexistent.env")


def test_export_unknown_format_raises(env_file: Path) -> None:
    with pytest.raises(ExportError, match="Unknown export format"):
        export_env(env_file, fmt="xml")  # type: ignore[arg-type]
