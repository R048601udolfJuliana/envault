"""Tests for envault.lint."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.lint import LintError, LintIssue, LintResult, lint_env


@pytest.fixture()
def tmp_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(tmp_dir: Path, content: str) -> Path:
    p = tmp_dir / ".env"
    p.write_text(content, encoding="utf-8")
    return p


def test_lint_clean_file(tmp_dir: Path) -> None:
    p = _write(tmp_dir, "FOO=bar\nBAZ=qux\n")
    result = lint_env(p)
    assert result.ok
    assert result.summary() == "No issues found."


def test_lint_missing_file_raises(tmp_dir: Path) -> None:
    with pytest.raises(LintError, match="File not found"):
        lint_env(tmp_dir / "nonexistent.env")


def test_lint_detects_no_equals(tmp_dir: Path) -> None:
    p = _write(tmp_dir, "BADLINE\n")
    result = lint_env(p)
    assert not result.ok
    assert any(i.code == "E001" for i in result.issues)


def test_lint_detects_invalid_key(tmp_dir: Path) -> None:
    p = _write(tmp_dir, "123BAD=value\n")
    result = lint_env(p)
    assert any(i.code == "E002" for i in result.issues)


def test_lint_detects_duplicate_key(tmp_dir: Path) -> None:
    p = _write(tmp_dir, "FOO=one\nFOO=two\n")
    result = lint_env(p)
    assert any(i.code == "W001" for i in result.issues)


def test_lint_detects_empty_value(tmp_dir: Path) -> None:
    p = _write(tmp_dir, "EMPTY=\n")
    result = lint_env(p)
    assert any(i.code == "W002" for i in result.issues)


def test_lint_ignores_comments_and_blanks(tmp_dir: Path) -> None:
    p = _write(tmp_dir, "# comment\n\nFOO=bar\n")
    result = lint_env(p)
    assert result.ok


def test_lint_issue_str() -> None:
    issue = LintIssue(line_no=3, code="W002", message="empty value")
    assert str(issue) == "Line 3 [W002]: empty value"


def test_lint_result_summary_with_issues(tmp_dir: Path) -> None:
    p = _write(tmp_dir, "EMPTY=\nDUP=x\nDUP=y\n")
    result = lint_env(p)
    summary = result.summary()
    assert "issue(s) found" in summary
