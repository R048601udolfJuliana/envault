"""Tests for envault.env_encode."""
from __future__ import annotations

import base64
from pathlib import Path

import pytest

from envault.env_encode import EncodeError, decode_env, encode_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, text: str) -> Path:
    p.write_text(text)
    return p


def test_encode_basic(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'API_KEY=secret\nDEBUG=true\n')
    encode_env(f)
    lines = f.read_text().splitlines()
    assert lines[0] == f"API_KEY={base64.b64encode(b'secret').decode()}"
    assert lines[1] == f"DEBUG={base64.b64encode(b'true').decode()}"


def test_encode_preserves_comments(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', '# comment\nKEY=val\n')
    encode_env(f)
    text = f.read_text()
    assert text.startswith('# comment')
    assert 'KEY=' in text


def test_encode_only_selected_keys(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'A=hello\nB=world\n')
    encode_env(f, keys=['A'])
    lines = f.read_text().splitlines()
    assert lines[0] == f"A={base64.b64encode(b'hello').decode()}"
    assert lines[1] == 'B=world'


def test_encode_to_separate_dest(tmp_dir: Path) -> None:
    src = _write(tmp_dir / '.env', 'X=foo\n')
    dest = tmp_dir / '.env.encoded'
    encode_env(src, dest)
    assert dest.exists()
    assert src.read_text() == 'X=foo\n'  # original unchanged


def test_encode_strips_quotes_before_encoding(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'KEY="myvalue"\n')
    encode_env(f)
    expected = base64.b64encode(b'myvalue').decode()
    assert f.read_text().strip() == f'KEY={expected}'


def test_encode_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(EncodeError, match='not found'):
        encode_env(tmp_dir / 'missing.env')


def test_decode_basic(tmp_dir: Path) -> None:
    encoded = base64.b64encode(b'topsecret').decode()
    f = _write(tmp_dir / '.env', f'TOKEN={encoded}\n')
    decode_env(f)
    assert f.read_text().strip() == 'TOKEN=topsecret'


def test_decode_invalid_base64_raises(tmp_dir: Path) -> None:
    f = _write(tmp_dir / '.env', 'BAD=not@@valid_base64!!!\n')
    with pytest.raises(EncodeError, match="Cannot base64-decode"):
        decode_env(f)


def test_decode_only_selected_keys(tmp_dir: Path) -> None:
    a_enc = base64.b64encode(b'alpha').decode()
    b_enc = base64.b64encode(b'beta').decode()
    f = _write(tmp_dir / '.env', f'A={a_enc}\nB={b_enc}\n')
    decode_env(f, keys=['A'])
    lines = f.read_text().splitlines()
    assert lines[0] == 'A=alpha'
    assert lines[1] == f'B={b_enc}'


def test_roundtrip(tmp_dir: Path) -> None:
    original = 'SECRET=hunter2\nPORT=5432\n'
    f = _write(tmp_dir / '.env', original)
    encode_env(f)
    decode_env(f)
    assert f.read_text() == original
