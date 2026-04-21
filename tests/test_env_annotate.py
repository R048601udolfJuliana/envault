"""Tests for envault.env_annotate."""
from __future__ import annotations

from pathlib import Path

import pytest

from envault.env_annotate import AnnotateError, annotate_key, read_annotations


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text)
    return p


def test_annotate_key_adds_comment(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    annotate_key(f, "DB_HOST", ann_type="string", desc="Database hostname")
    content = f.read_text()
    assert "@type:string" in content
    assert "@desc:Database hostname" in content
    assert content.index("@type:string") < content.index("DB_HOST=")


def test_annotate_key_replaces_existing_annotation(tmp_dir: Path) -> None:
    f = _write(
        tmp_dir / ".env",
        "# @type:int  @desc:old desc\nDB_PORT=5432\n",
    )
    annotate_key(f, "DB_PORT", ann_type="integer", desc="new desc")
    content = f.read_text()
    assert "old desc" not in content
    assert "@type:integer" in content
    assert "@desc:new desc" in content
    assert content.count("@type") == 1


def test_annotate_key_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(AnnotateError, match="not found"):
        annotate_key(tmp_dir / "missing.env", "KEY", ann_type="string")


def test_annotate_key_missing_key_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "EXISTING=1\n")
    with pytest.raises(AnnotateError, match="GHOST"):
        annotate_key(f, "GHOST", ann_type="string")


def test_annotate_key_no_annotation_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=val\n")
    with pytest.raises(AnnotateError, match="At least one"):
        annotate_key(f, "KEY")


def test_annotate_key_writes_to_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / ".env", "TOKEN=abc\n")
    dest = tmp_dir / "annotated.env"
    result = annotate_key(src, "TOKEN", desc="API token", dest=dest)
    assert result == dest
    assert dest.exists()
    assert "@desc:API token" in dest.read_text()
    assert "@desc:API token" not in src.read_text()


def test_read_annotations_basic(tmp_dir: Path) -> None:
    f = _write(
        tmp_dir / ".env",
        "# @type:string  @desc:The host\nDB_HOST=localhost\n"
        "# @type:int\nDB_PORT=5432\n",
    )
    result = read_annotations(f)
    assert result["DB_HOST"] == {"type": "string", "desc": "The host"}
    assert result["DB_PORT"] == {"type": "int"}


def test_read_annotations_empty_file(tmp_dir: Path) -> None:
    f = _write(tmp_dir / ".env", "KEY=value\n")
    assert read_annotations(f) == {}


def test_read_annotations_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(AnnotateError, match="not found"):
        read_annotations(tmp_dir / "ghost.env")
