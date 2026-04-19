"""Tag management for envault encrypted files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

TAGS_FILENAME = ".envault_tags.json"


class TagError(Exception):
    """Raised when a tag operation fails."""


def _tags_path(directory: Path) -> Path:
    return directory / TAGS_FILENAME


def load_tags(directory: Path) -> Dict[str, List[str]]:
    """Load tags mapping from *directory*. Returns empty dict if file missing."""
    path = _tags_path(directory)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TagError(f"Invalid JSON in tags file: {exc}") from exc
    if not isinstance(data, dict):
        raise TagError("Tags file must contain a JSON object.")
    return {k: list(v) for k, v in data.items()}


def save_tags(directory: Path, tags: Dict[str, List[str]]) -> None:
    """Persist *tags* mapping to *directory*."""
    directory.mkdir(parents=True, exist_ok=True)
    _tags_path(directory).write_text(
        json.dumps(tags, indent=2, sort_keys=True), encoding="utf-8"
    )


def add_tag(directory: Path, tag: str, filename: str) -> None:
    """Associate *filename* with *tag* inside *directory*."""
    tag = tag.strip()
    if not tag:
        raise TagError("Tag name must not be empty.")
    tags = load_tags(directory)
    entries = tags.setdefault(tag, [])
    if filename not in entries:
        entries.append(filename)
    save_tags(directory, tags)


def remove_tag(directory: Path, tag: str, filename: str) -> None:
    """Remove association of *filename* from *tag*. Raises if not found."""
    tags = load_tags(directory)
    if tag not in tags or filename not in tags[tag]:
        raise TagError(f"File '{filename}' is not tagged with '{tag}'.")
    tags[tag].remove(filename)
    if not tags[tag]:
        del tags[tag]
    save_tags(directory, tags)


def list_tags(directory: Path) -> Dict[str, List[str]]:
    """Return all tags and their associated files."""
    return load_tags(directory)


def files_for_tag(directory: Path, tag: str) -> List[str]:
    """Return files associated with *tag*, or empty list if tag unknown."""
    return load_tags(directory).get(tag, [])


def tags_for_file(directory: Path, filename: str) -> List[str]:
    """Return all tags associated with *filename*, or empty list if none."""
    return [
        tag
        for tag, files in load_tags(directory).items()
        if filename in files
    ]
