"""Tests for envault.env_redact."""
from pathlib import Path

import pytest

from envault.env_redact import RedactError, redact_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_redact_sensitive_key_auto_detect(tmp_dir):
    f = _write(tmp_dir / ".env", "API_KEY=supersecret\nAPP_NAME=myapp\n")
    lines = redact_env(f)
    assert lines[0] == "API_KEY=***"
    assert lines[1] == "APP_NAME=myapp"


def test_redact_explicit_key(tmp_dir):
    f = _write(tmp_dir / ".env", "APP_NAME=myapp\nDB_HOST=localhost\n")
    lines = redact_env(f, keys=["DB_HOST"], auto_detect=False)
    assert lines[0] == "APP_NAME=myapp"
    assert lines[1] == "DB_HOST=***"


def test_redact_custom_placeholder(tmp_dir):
    f = _write(tmp_dir / ".env", "SECRET_TOKEN=abc123\n")
    lines = redact_env(f, placeholder="<hidden>")
    assert lines[0] == "SECRET_TOKEN=<hidden>"


def test_redact_preserves_comments_and_blanks(tmp_dir):
    content = "# comment\n\nPORT=8080\n"
    f = _write(tmp_dir / ".env", content)
    lines = redact_env(f)
    assert lines[0] == "# comment"
    assert lines[1] == ""
    assert lines[2] == "PORT=8080"


def test_redact_missing_file_raises(tmp_dir):
    with pytest.raises(RedactError, match="not found"):
        redact_env(tmp_dir / "missing.env")


def test_redact_auto_detect_false_skips_pattern(tmp_dir):
    f = _write(tmp_dir / ".env", "PASSWORD=hunter2\n")
    lines = redact_env(f, auto_detect=False)
    assert lines[0] == "PASSWORD=hunter2"


def test_redact_key_case_insensitive_explicit(tmp_dir):
    f = _write(tmp_dir / ".env", "db_password=secret\n")
    lines = redact_env(f, keys=["DB_PASSWORD"], auto_detect=False)
    assert lines[0] == "db_password=***"


def test_redact_value_with_equals_sign(tmp_dir):
    f = _write(tmp_dir / ".env", "PRIVATE_KEY=abc=def=ghi\n")
    lines = redact_env(f)
    assert lines[0] == "PRIVATE_KEY=***"
