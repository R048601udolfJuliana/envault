"""envault.env_interpolate — expand variable references inside .env files.

Supports ``${VAR}`` and ``$VAR`` syntax.  References are resolved in
declaration order; a variable may reference an earlier variable in the
same file, an externally supplied mapping, or the process environment
(when *use_os_env* is True).
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


class InterpolateError(Exception):
    """Raised when interpolation fails."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_lines(text: str) -> List[Tuple[str, Optional[str], str]]:
    """Return a list of ``(key, value, raw_line)`` tuples.

    *value* is ``None`` for comment / blank lines; *key* is ``""`` in that
    case and *raw_line* preserves the original text (including newline).
    """
    result: List[Tuple[str, Optional[str], str]] = []
    for raw in text.splitlines(keepends=True):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            result.append(("", None, raw))
            continue
        if "=" not in stripped:
            result.append(("", None, raw))
            continue
        key, _, val = stripped.partition("=")
        key = key.strip()
        val = val.strip()
        # Strip surrounding quotes
        if len(val) >= 2 and val[0] in ('"', "'") and val[-1] == val[0]:
            val = val[1:-1]
        result.append((key, val, raw))
    return result


def _resolve(value: str, env: Dict[str, str]) -> str:
    """Replace all ``${VAR}`` / ``$VAR`` references using *env*."""

    def _sub(match: re.Match) -> str:  # type: ignore[type-arg]
        name = match.group(1) or match.group(2)
        return env.get(name, match.group(0))  # leave unresolved refs as-is

    return _REF_RE.sub(_sub, value)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def interpolate_env(
    src: Path,
    dest: Optional[Path] = None,
    *,
    extra: Optional[Dict[str, str]] = None,
    use_os_env: bool = False,
    fail_on_missing: bool = False,
) -> Path:
    """Expand variable references in *src* and write the result to *dest*.

    Parameters
    ----------
    src:
        Source ``.env`` file.
    dest:
        Output path.  Defaults to *src* (in-place).
    extra:
        Additional key→value pairs consulted *before* the file itself.
    use_os_env:
        When ``True``, ``os.environ`` is used as a fallback for unresolved
        references.
    fail_on_missing:
        When ``True``, raise :class:`InterpolateError` if a reference cannot
        be resolved.  Otherwise the reference token is left unchanged.

    Returns
    -------
    Path
        Resolved path of the written output file.
    """
    if not src.exists():
        raise InterpolateError(f"Source file not found: {src}")

    text = src.read_text(encoding="utf-8")
    parsed = _parse_lines(text)

    # Build the resolution environment incrementally
    env: Dict[str, str] = {}
    if use_os_env:
        env.update(os.environ)
    if extra:
        env.update(extra)

    out_lines: List[str] = []
    for key, value, raw in parsed:
        if value is None:
            # Comment or blank — pass through unchanged
            out_lines.append(raw)
            continue

        resolved = _resolve(value, env)

        if fail_on_missing:
            unresolved = _REF_RE.findall(resolved)
            if unresolved:
                names = [g1 or g2 for g1, g2 in unresolved]
                raise InterpolateError(
                    f"Unresolved reference(s) for key '{key}': {names}"
                )

        # Register the resolved value so later vars can reference it
        env[key] = resolved

        # Preserve quoting style: always write double-quoted values
        out_lines.append(f"{key}=\"{resolved}\"\n")

    dest = dest or src
    dest.write_text("".join(out_lines), encoding="utf-8")
    return dest.resolve()
