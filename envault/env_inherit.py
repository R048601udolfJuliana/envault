"""env_inherit.py – merge a parent .env into a child, letting child values win."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple


class InheritError(Exception):
    """Raised when env inheritance fails."""


def _parse_env(text: str) -> Dict[str, str]:
    """Return an ordered dict of key→value from env text."""
    result: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, val = stripped.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            result[key] = val
    return result


def _parse_blocks(text: str) -> List[str]:
    """Split env text into logical blocks (comment + key line pairs)."""
    blocks: List[str] = []
    pending: List[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            pending.append(line)
        else:
            pending.append(line)
            blocks.append("".join(pending))
            pending = []
    if pending:
        blocks.append("".join(pending))
    return blocks


def inherit_env(
    parent: Path,
    child: Path,
    dest: Path | None = None,
    *,
    show_source: bool = False,
) -> Tuple[Path, List[str]]:
    """Merge *parent* into *child*, child keys take precedence.

    Returns (dest_path, list_of_inherited_keys).
    """
    if not parent.exists():
        raise InheritError(f"Parent file not found: {parent}")
    if not child.exists():
        raise InheritError(f"Child file not found: {child}")

    parent_vars = _parse_env(parent.read_text(encoding="utf-8"))
    child_vars = _parse_env(child.read_text(encoding="utf-8"))

    child_text = child.read_text(encoding="utf-8")

    # Keys in parent but absent from child are inherited
    inherited: List[str] = [k for k in parent_vars if k not in child_vars]

    lines: List[str] = [child_text.rstrip()]
    if inherited:
        lines.append("")
        if show_source:
            lines.append(f"# inherited from {parent}")
        for key in inherited:
            lines.append(f"{key}={parent_vars[key]}")

    output = "\n".join(lines) + "\n"
    out_path = dest if dest is not None else child
    out_path.write_text(output, encoding="utf-8")
    return out_path, inherited
