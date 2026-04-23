"""env_shuffle.py — Randomly shuffle the order of key-value pairs in a .env file."""

from __future__ import annotations

import random
from pathlib import Path
from typing import List, Tuple


class ShuffleError(Exception):
    """Raised when shuffling fails."""


def _parse_blocks(text: str) -> List[List[str]]:
    """Group lines into blocks: each key=value line with its preceding comments."""
    blocks: List[List[str]] = []
    pending: List[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped:
            if pending:
                blocks.append(pending)
                pending = []
            blocks.append([line])
        elif stripped.startswith("#"):
            pending.append(line)
        elif "=" in stripped:
            pending.append(line)
            blocks.append(pending)
            pending = []
        else:
            pending.append(line)
    if pending:
        blocks.append(pending)
    return blocks


def shuffle_env(
    src: Path,
    dest: Path | None = None,
    *,
    seed: int | None = None,
    in_place: bool = False,
) -> Path:
    """Shuffle the key blocks in *src* and write the result.

    Args:
        src:      Source .env file.
        dest:     Destination path. Defaults to ``<stem>.shuffled.env``.
        seed:     Optional RNG seed for reproducible shuffles.
        in_place: If *True*, overwrite *src* (ignores *dest*).

    Returns:
        The path of the written file.
    """
    src = Path(src)
    if not src.exists():
        raise ShuffleError(f"Source file not found: {src}")

    text = src.read_text(encoding="utf-8")
    blocks = _parse_blocks(text)

    # Separate key blocks (contain "=") from pure blank/comment blocks
    key_blocks = [b for b in blocks if any("=" in l for l in b)]
    other_blocks = [b for b in blocks if not any("=" in l for l in b)]

    rng = random.Random(seed)
    rng.shuffle(key_blocks)

    # Reassemble: key blocks first, then trailing blanks/comments
    shuffled_lines: List[str] = []
    for block in key_blocks:
        shuffled_lines.extend(block)
    for block in other_blocks:
        shuffled_lines.extend(block)

    output = "".join(shuffled_lines)
    if not output.endswith("\n") and output:
        output += "\n"

    if in_place:
        target = src
    elif dest is not None:
        target = Path(dest)
    else:
        target = src.with_name(src.stem + ".shuffled" + src.suffix)

    target.write_text(output, encoding="utf-8")
    return target.resolve()
