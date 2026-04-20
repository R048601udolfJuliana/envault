"""Detect and remove duplicate keys across multiple .env files."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple


class DedupKeysError(Exception):
    """Raised when dedup_keys encounters an unrecoverable error."""


def _parse_env(text: str) -> List[Tuple[int, str, str]]:
    """Return list of (lineno, key, raw_line) for assignment lines."""
    results: List[Tuple[int, str, str]] = []
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        if key:
            results.append((i, key, line))
    return results


def find_cross_file_duplicates(
    paths: List[Path],
) -> Dict[str, List[Tuple[Path, int]]]:
    """Return mapping of key -> [(file, lineno), ...] for keys found in >1 file."""
    key_locations: Dict[str, List[Tuple[Path, int]]] = {}
    for path in paths:
        if not path.exists():
            raise DedupKeysError(f"File not found: {path}")
        text = path.read_text(encoding="utf-8")
        for lineno, key, _ in _parse_env(text):
            key_locations.setdefault(key, []).append((path, lineno))
    return {k: v for k, v in key_locations.items() if len(v) > 1}


def dedup_keys(
    source: Path,
    reference: Path,
    dest: Path | None = None,
    keep: str = "source",
) -> Path:
    """Remove keys from *source* that already exist in *reference*.

    Parameters
    ----------
    source:
        The .env file to prune.
    reference:
        The .env file whose keys take precedence.
    dest:
        Output path.  Defaults to overwriting *source*.
    keep:
        ``"source"`` keeps source keys (removes nothing) — for dry-run info only.
        ``"reference"`` removes keys from source that exist in reference.
    """
    if not source.exists():
        raise DedupKeysError(f"Source file not found: {source}")
    if not reference.exists():
        raise DedupKeysError(f"Reference file not found: {reference}")
    if keep not in ("source", "reference"):
        raise DedupKeysError("keep must be 'source' or 'reference'")

    ref_text = reference.read_text(encoding="utf-8")
    ref_keys = {key for _, key, _ in _parse_env(ref_text)}

    src_lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
    output_lines: List[str] = []

    if keep == "reference":
        skip_next_blank = False
        for line in src_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                if key in ref_keys:
                    skip_next_blank = True
                    continue
            output_lines.append(line)
            skip_next_blank = False
    else:
        output_lines = src_lines  # type: ignore[assignment]

    out_path = dest or source
    out_path.write_text("".join(output_lines), encoding="utf-8")
    return out_path.resolve()
