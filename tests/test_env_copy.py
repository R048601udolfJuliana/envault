"""Tests for envault.env_copy."""
from pathlib import Path

import pytest

from envault.env_copy import CopyError, copy_vault


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def enc_file(tmp_dir: Path) -> Path:
    f = tmp_dir / "vault" / ".env.gpg"
    f.parent.mkdir(parents=True)
    f.write_bytes(b"ENCRYPTED")
    return f


def test_copy_vault_creates_destination(enc_file: Path, tmp_dir: Path) -> None:
    dest = tmp_dir / "backup" / ".env.gpg"
    result = copy_vault(enc_file, dest)
    assert result == dest
    assert dest.exists()
    assert dest.read_bytes() == b"ENCRYPTED"


def test_copy_vault_returns_resolved_destination(enc_file: Path, tmp_dir: Path) -> None:
    dest = tmp_dir / "out" / ".env.gpg"
    result = copy_vault(enc_file, dest)
    assert isinstance(result, Path)


def test_copy_vault_missing_source_raises(tmp_dir: Path) -> None:
    with pytest.raises(CopyError, match="Source file not found"):
        copy_vault(tmp_dir / "missing.gpg", tmp_dir / "dest.gpg")


def test_copy_vault_existing_dest_raises_without_force(enc_file: Path, tmp_dir: Path) -> None:
    dest = tmp_dir / "out.gpg"
    dest.write_bytes(b"OLD")
    with pytest.raises(CopyError, match="already exists"):
        copy_vault(enc_file, dest)


def test_copy_vault_force_overwrites(enc_file: Path, tmp_dir: Path) -> None:
    dest = tmp_dir / "out.gpg"
    dest.write_bytes(b"OLD")
    copy_vault(enc_file, dest, force=True)
    assert dest.read_bytes() == b"ENCRYPTED"


def test_copy_vault_copies_manifest_when_present(enc_file: Path, tmp_dir: Path) -> None:
    manifest = enc_file.with_suffix(".manifest")
    manifest.write_text('{"sha256": "abc"}')
    dest = tmp_dir / "copy" / ".env.gpg"
    copy_vault(enc_file, dest)
    dest_manifest = dest.with_suffix(".manifest")
    assert dest_manifest.exists()
    assert dest_manifest.read_text() == '{"sha256": "abc"}'


def test_copy_vault_skips_manifest_when_absent(enc_file: Path, tmp_dir: Path) -> None:
    dest = tmp_dir / "copy" / ".env.gpg"
    copy_vault(enc_file, dest)
    assert not dest.with_suffix(".manifest").exists()


def test_copy_vault_include_manifest_false_skips_it(enc_file: Path, tmp_dir: Path) -> None:
    manifest = enc_file.with_suffix(".manifest")
    manifest.write_text('{"sha256": "xyz"}')
    dest = tmp_dir / "copy2" / ".env.gpg"
    copy_vault(enc_file, dest, include_manifest=False)
    assert not dest.with_suffix(".manifest").exists()
