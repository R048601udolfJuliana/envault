"""Export decrypted .env contents to shell-sourceable or JSON formats."""

from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Dict, Literal

ExportFormat = Literal["shell", "json", "dotenv"]


class ExportError(Exception):
    """Raised when an export operation fails."""


def _parse_env(text: str) -> Dict[str, str]:
    """Parse key=value pairs from env file text, skipping comments and blanks."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes if present
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        if key:
            result[key] = value
    return result


def export_env(
    source: Path,
    fmt: ExportFormat = "dotenv",
    output: Path | None = None,
) -> str:
    """Read a plaintext .env file and render it in the requested format.

    Args:
        source: Path to the plaintext .env file.
        fmt: One of ``shell``, ``json``, or ``dotenv``.
        output: Optional path to write the result; if omitted the result is
                only returned as a string.

    Returns:
        The formatted string.

    Raises:
        ExportError: If the source file is missing or the format is unknown.
    """
    if not source.exists():
        raise ExportError(f"Source file not found: {source}")

    text = source.read_text(encoding="utf-8")
    pairs = _parse_env(text)

    if fmt == "dotenv":
        rendered = "\n".join(f"{k}={v}" for k, v in pairs.items())
    elif fmt == "shell":
        lines = [f"export {k}={shlex.quote(v)}" for k, v in pairs.items()]
        rendered = "\n".join(lines)
    elif fmt == "json":
        rendered = json.dumps(pairs, indent=2)
    else:
        raise ExportError(f"Unknown export format: {fmt!r}")

    if output is not None:
        output.write_text(rendered, encoding="utf-8")

    return rendered
