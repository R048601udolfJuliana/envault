"""Tests for envault.note."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.note import NoteError, add_note, clear_notes, list_notes, load_notes, save_notes


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def test_load_notes_missing_returns_empty(tmp_dir):
    assert load_notes(tmp_dir) == []


def test_load_notes_invalid_json_raises(tmp_dir):
    (tmp_dir / ".envault_notes.json").write_text("not json")
    with pytest.raises(NoteError, match="Corrupt"):
        load_notes(tmp_dir)


def test_load_notes_non_array_raises(tmp_dir):
    (tmp_dir / ".envault_notes.json").write_text(json.dumps({"a": 1}))
    with pytest.raises(NoteError, match="array"):
        load_notes(tmp_dir)


def test_add_note_creates_entry(tmp_dir):
    entry = add_note(tmp_dir, "production", "Initial deploy", "alice")
    assert entry["profile"] == "production"
    assert entry["text"] == "Initial deploy"
    assert entry["author"] == "alice"
    assert "created_at" in entry


def test_add_note_persists(tmp_dir):
    add_note(tmp_dir, "staging", "Test note")
    notes = load_notes(tmp_dir)
    assert len(notes) == 1
    assert notes[0]["text"] == "Test note"


def test_list_notes_no_filter(tmp_dir):
    add_note(tmp_dir, "prod", "note1")
    add_note(tmp_dir, "staging", "note2")
    assert len(list_notes(tmp_dir)) == 2


def test_list_notes_with_profile_filter(tmp_dir):
    add_note(tmp_dir, "prod", "note1")
    add_note(tmp_dir, "staging", "note2")
    result = list_notes(tmp_dir, profile="prod")
    assert len(result) == 1
    assert result[0]["text"] == "note1"


def test_clear_notes_all(tmp_dir):
    add_note(tmp_dir, "prod", "a")
    add_note(tmp_dir, "staging", "b")
    removed = clear_notes(tmp_dir)
    assert removed == 2
    assert load_notes(tmp_dir) == []


def test_clear_notes_by_profile(tmp_dir):
    add_note(tmp_dir, "prod", "a")
    add_note(tmp_dir, "staging", "b")
    removed = clear_notes(tmp_dir, profile="prod")
    assert removed == 1
    remaining = load_notes(tmp_dir)
    assert len(remaining) == 1
    assert remaining[0]["profile"] == "staging"
