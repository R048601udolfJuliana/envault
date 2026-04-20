"""Split a .env file into N roughly equal chunks."""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


class ChunkError(Exception):
    """Raised when chunking fails."""


def _parse_blocks(text: str) -> List[str]:
    """Return non-blank, non-comment lines (key=value entries)."""
    blocks = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            blocks.append(line)
    return blocks


def chunk_env(
    source: Path,
    n: int,
    dest_dir: Path,
    prefix: str = "chunk",
) -> List[Path]:
    """Split *source* into *n* chunk files written to *dest_dir*.

    Each chunk file is named ``<prefix>_01.env``, ``<prefix>_02.env``, …
    Comments and blank lines from the original file are dropped.

    Returns the list of created file paths.
    """
    if n < 1:
        raise ChunkError("n must be >= 1")

    if not source.exists():
        raise ChunkError(f"Source file not found: {source}")

    entries = _parse_blocks(source.read_text(encoding="utf-8"))

    if not entries:
        raise ChunkError(f"No key=value entries found in {source}")

    dest_dir.mkdir(parents=True, exist_ok=True)

    # Distribute entries as evenly as possible
    chunk_size = max(1, -(-len(entries) // n))  # ceiling division
    chunks: List[List[str]] = [
        entries[i : i + chunk_size] for i in range(0, len(entries), chunk_size)
    ]

    created: List[Path] = []
    for idx, chunk in enumerate(chunks, start=1):
        out = dest_dir / f"{prefix}_{idx:02d}.env"
        out.write_text("\n".join(chunk) + "\n", encoding="utf-8")
        created.append(out)

    return created
