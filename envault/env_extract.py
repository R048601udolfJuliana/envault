"""Extract a subset of keys from a .env file into a new file."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable


class ExtractError(Exception):
    """Raised when extraction fails."""


def _parse_env(text: str) -> list[tuple[str, str]]:
    """Return list of (raw_line, key) pairs preserving comments/blanks."""
    result = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.append((line, ""))
            continue
        if "=" not in stripped:
            result.append((line, ""))
            continue
        key = stripped.split("=", 1)[0].strip()
        result.append((line, key))
    return result


def extract_env(
    src: Path,
    keys: Iterable[str],
    dest: Path | None = None,
    *,
    missing_ok: bool = False,
) -> Path:
    """Extract *keys* from *src* and write them to *dest*.

    Parameters
    ----------
    src:
        Source .env file.
    keys:
        Keys to extract.
    dest:
        Destination path. Defaults to ``<src stem>.extracted.env``.
    missing_ok:
        When *True*, silently skip keys not present in *src*.
        When *False* (default), raise :class:`ExtractError` if any key
        is absent.

    Returns
    -------
    Path
        Resolved path of the written file.
    """
    src = Path(src).resolve()
    if not src.exists():
        raise ExtractError(f"Source file not found: {src}")

    wanted = set(keys)
    if not wanted:
        raise ExtractError("No keys specified for extraction.")

    pairs = _parse_env(src.read_text())
    found_keys = {k for _, k in pairs if k}

    if not missing_ok:
        missing = wanted - found_keys
        if missing:
            raise ExtractError(
                "Keys not found in source: " + ", ".join(sorted(missing))
            )

    lines = [
        line
        for line, key in pairs
        if key in wanted or not key
    ]

    # Strip leading/trailing blank lines for a clean output.
    content = "".join(lines).strip()
    if content:
        content += "\n"

    if dest is None:
        dest = src.with_name(src.stem + ".extracted.env")
    dest = Path(dest).resolve()
    dest.write_text(content)
    return dest
