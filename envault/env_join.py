"""env_join.py – merge multiple .env files into one."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


class JoinError(Exception):
    """Raised when joining .env files fails."""


def _parse_env(text: str) -> list[tuple[str, str]]:
    """Return (raw_line, key) pairs preserving comments and blanks."""
    result: list[tuple[str, str]] = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append((line, ""))
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            result.append((line, key))
        else:
            result.append((line, ""))
    return result


def join_env(
    sources: Iterable[Path | str],
    dest: Path | str,
    *,
    strategy: str = "last",
    skip_missing: bool = False,
) -> Path:
    """Merge *sources* into *dest*.

    Parameters
    ----------
    sources:
        Ordered list of .env file paths to merge.
    dest:
        Output file path.
    strategy:
        ``'last'`` – last file wins on duplicate keys (default).
        ``'first'`` – first file wins on duplicate keys.
    skip_missing:
        When ``True``, silently skip source files that do not exist.
        When ``False`` (default), raise :class:`JoinError`.
    """
    if strategy not in ("last", "first"):
        raise JoinError(f"Unknown strategy {strategy!r}; expected 'first' or 'last'")

    source_paths = [Path(s) for s in sources]
    dest_path = Path(dest)

    # Collect all (line, key) blocks per file
    blocks: list[list[tuple[str, str]]] = []
    for src in source_paths:
        if not src.exists():
            if skip_missing:
                continue
            raise JoinError(f"Source file not found: {src}")
        blocks.append(_parse_env(src.read_text()))

    if not blocks:
        dest_path.write_text("")
        return dest_path.resolve()

    # Build key -> line mapping according to strategy
    key_to_line: dict[str, str] = {}
    order: list[str] = []  # insertion order for keys

    for block in blocks:
        for line, key in block:
            if not key:
                continue  # comments / blanks handled separately
            if key not in key_to_line:
                order.append(key)
                key_to_line[key] = line
            elif strategy == "last":
                key_to_line[key] = line

    # Write output: emit keys in order, then a trailing newline
    lines = [key_to_line[k] for k in order]
    text = "".join(lines)
    if text and not text.endswith("\n"):
        text += "\n"

    dest_path.write_text(text)
    return dest_path.resolve()
