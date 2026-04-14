"""Compare two encrypted .env files by decrypting and diffing their contents."""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

from envault.crypto import decrypt_file, GPGError


class CompareError(Exception):
    """Raised when a comparison operation fails."""


@dataclass
class CompareResult:
    only_in_a: List[str] = field(default_factory=list)
    only_in_b: List[str] = field(default_factory=list)
    changed: List[Tuple[str, str, str]] = field(default_factory=list)  # (key, val_a, val_b)

    @property
    def has_differences(self) -> bool:
        return bool(self.only_in_a or self.only_in_b or self.changed)

    def summary_lines(self) -> List[str]:
        lines: List[str] = []
        for key in sorted(self.only_in_a):
            lines.append(f"  - {key}  (only in A)")
        for key in sorted(self.only_in_b):
            lines.append(f"  + {key}  (only in B)")
        for key, va, vb in sorted(self.changed, key=lambda t: t[0]):
            lines.append(f"  ~ {key}  A={va!r}  B={vb!r}")
        return lines


def _parse_env(text: str) -> dict:
    result: dict = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            result[key] = value
    return result


def compare_encrypted(
    file_a: Path,
    file_b: Path,
    passphrase: str | None = None,
) -> CompareResult:
    """Decrypt both files and return a CompareResult describing the differences."""
    for path, label in ((file_a, "A"), (file_b, "B")):
        if not path.exists():
            raise CompareError(f"File {label} not found: {path}")

    with tempfile.TemporaryDirectory() as tmp:
        out_a = Path(tmp) / "a.env"
        out_b = Path(tmp) / "b.env"
        try:
            decrypt_file(file_a, out_a, passphrase=passphrase)
            decrypt_file(file_b, out_b, passphrase=passphrase)
        except GPGError as exc:
            raise CompareError(f"Decryption failed: {exc}") from exc

        env_a = _parse_env(out_a.read_text())
        env_b = _parse_env(out_b.read_text())

    keys_a = set(env_a)
    keys_b = set(env_b)

    result = CompareResult(
        only_in_a=sorted(keys_a - keys_b),
        only_in_b=sorted(keys_b - keys_a),
        changed=[
            (k, env_a[k], env_b[k])
            for k in keys_a & keys_b
            if env_a[k] != env_b[k]
        ],
    )
    return result
