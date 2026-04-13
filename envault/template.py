"""Template generation for .env files from encrypted vault."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional


class TemplateError(Exception):
    """Raised when template generation fails."""


def _parse_env_keys(text: str) -> List[str]:
    """Extract variable names from .env file content, preserving order."""
    keys: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=', stripped)
        if match:
            keys.append(match.group(1))
    return keys


def generate_template(
    source_path: Path,
    output_path: Optional[Path] = None,
    placeholder: str = "",
    keep_comments: bool = True,
) -> str:
    """Generate a .env.template file from a decrypted .env file.

    Each variable's value is replaced with *placeholder* (default: empty).
    Comments and blank lines are preserved when *keep_comments* is True.

    Returns the template content as a string and optionally writes it to
    *output_path*.
    """
    if not source_path.exists():
        raise TemplateError(f"Source file not found: {source_path}")

    text = source_path.read_text(encoding="utf-8")
    lines: List[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if keep_comments:
                lines.append("")
            continue
        if stripped.startswith("#"):
            if keep_comments:
                lines.append(line)
            continue
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=', stripped)
        if match:
            lines.append(f"{match.group(1)}={placeholder}")
        # lines that don't match key=value are silently skipped

    content = "\n".join(lines) + "\n"

    if output_path is not None:
        output_path.write_text(content, encoding="utf-8")

    return content


def keys_from_template(template_path: Path) -> List[str]:
    """Return the list of variable names declared in a template file."""
    if not template_path.exists():
        raise TemplateError(f"Template file not found: {template_path}")
    return _parse_env_keys(template_path.read_text(encoding="utf-8"))
