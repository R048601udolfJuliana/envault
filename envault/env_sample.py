"""Generate a .env.sample file from a .env file (keys only, values stripped)."""

from __future__ import annotations

from pathlib import Path


class SampleError(Exception):
    pass


def _parse_lines(text: str) -> list[tuple[str, str]]:
    """Return list of (kind, content) where kind is 'comment', 'blank', or 'key'."""
    result = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            result.append(("blank", ""))
        elif stripped.startswith("#"):
            result.append(("comment", line))
        elif "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            result.append(("key", key))
        else:
            result.append(("blank", ""))
    return result


def generate_sample(src: Path, dest: Path | None = None) -> Path:
    """Write a .env.sample next to *src* (or to *dest*) with values blanked out."""
    src = Path(src)
    if not src.exists():
        raise SampleError(f"Source file not found: {src}")

    if dest is None:
        dest = src.parent / (src.name + ".sample")
    else:
        dest = Path(dest)

    lines = _parse_lines(src.read_text())
    out: list[str] = []
    for kind, content in lines:
        if kind == "key":
            out.append(f"{content}=")
        elif kind == "comment":
            out.append(content)
        else:
            out.append("")

    dest.write_text("\n".join(out) + "\n")
    return dest
