"""env_annotate.py – attach inline annotations (type hints / descriptions) to .env keys."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class AnnotateError(Exception):
    """Raised when annotation operations fail."""


# Annotation comment format:  # @type:<type>  @desc:<description>
_ANNOTATION_RE = re.compile(
    r"#\s*@type:(?P<type>\S+)?(?:\s+@desc:(?P<desc>.+))?"
)


def _parse_lines(text: str) -> List[Tuple[str, str]]:
    """Return list of (raw_line, stripped_line) tuples."""
    return [(ln, ln.rstrip()) for ln in text.splitlines(keepends=True)]


def _build_annotation(ann_type: Optional[str], desc: Optional[str]) -> str:
    parts = []
    if ann_type:
        parts.append(f"@type:{ann_type}")
    if desc:
        parts.append(f"@desc:{desc}")
    return "# " + "  ".join(parts) if parts else ""


def annotate_key(
    path: Path,
    key: str,
    ann_type: Optional[str] = None,
    desc: Optional[str] = None,
    dest: Optional[Path] = None,
) -> Path:
    """Add or replace an annotation comment above *key* in *path*."""
    if not path.exists():
        raise AnnotateError(f"File not found: {path}")
    if not ann_type and not desc:
        raise AnnotateError("At least one of ann_type or desc must be provided.")

    lines = path.read_text().splitlines(keepends=True)
    annotation = _build_annotation(ann_type, desc) + "\n"
    output: List[str] = []
    i = 0
    found = False
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"{key} ="):
            # Remove preceding annotation line if present
            if output and _ANNOTATION_RE.search(output[-1]):
                output.pop()
            output.append(annotation)
            output.append(lines[i])
            found = True
            i += 1
            continue
        output.append(lines[i])
        i += 1

    if not found:
        raise AnnotateError(f"Key '{key}' not found in {path}")

    out_path = dest or path
    out_path.write_text("".join(output))
    return out_path


def read_annotations(path: Path) -> Dict[str, Dict[str, str]]:
    """Return a mapping of key -> {type, desc} for all annotated keys."""
    if not path.exists():
        raise AnnotateError(f"File not found: {path}")
    lines = path.read_text().splitlines()
    result: Dict[str, Dict[str, str]] = {}
    pending: Optional[Dict[str, str]] = None
    for line in lines:
        stripped = line.strip()
        m = _ANNOTATION_RE.search(stripped)
        if m:
            pending = {k: v for k, v in m.groupdict().items() if v is not None}
            continue
        if pending is not None and "=" in stripped and not stripped.startswith("#"):
            key = stripped.split("=", 1)[0].strip()
            result[key] = pending
        pending = None
    return result
