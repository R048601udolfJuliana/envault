"""Tests for envault.hook."""
from __future__ import annotations

import stat
from pathlib import Path

import pytest

from envault.hook import (
    HOOK_NAME,
    HOOK_SCRIPT,
    HookError,
    install_hook,
    uninstall_hook,
    hook_status,
)


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    return tmp_path


def test_install_hook_creates_file(git_repo: Path) -> None:
    path = install_hook(git_repo)
    assert path.exists()
    assert "envault" in path.read_text()


def test_install_hook_is_executable(git_repo: Path) -> None:
    path = install_hook(git_repo)
    assert path.stat().st_mode & stat.S_IEXEC


def test_install_hook_raises_if_exists_no_force(git_repo: Path) -> None:
    install_hook(git_repo)
    with pytest.raises(HookError, match="already exists"):
        install_hook(git_repo, force=False)


def test_install_hook_force_overwrites(git_repo: Path) -> None:
    install_hook(git_repo)
    path = install_hook(git_repo, force=True)
    assert path.exists()


def test_install_hook_no_git_dir_raises(tmp_path: Path) -> None:
    with pytest.raises(HookError, match="No .git/hooks"):
        install_hook(tmp_path)


def test_uninstall_hook_removes_file(git_repo: Path) -> None:
    install_hook(git_repo)
    uninstall_hook(git_repo)
    assert not (git_repo / ".git" / "hooks" / HOOK_NAME).exists()


def test_uninstall_hook_raises_if_missing(git_repo: Path) -> None:
    with pytest.raises(HookError, match="No hook found"):
        uninstall_hook(git_repo)


def test_hook_status_not_installed(git_repo: Path) -> None:
    status = hook_status(git_repo)
    assert status["installed"] is False
    assert status["envault_managed"] is False


def test_hook_status_installed_envault(git_repo: Path) -> None:
    install_hook(git_repo)
    status = hook_status(git_repo)
    assert status["installed"] is True
    assert status["envault_managed"] is True


def test_hook_status_installed_foreign(git_repo: Path) -> None:
    hook_path = git_repo / ".git" / "hooks" / HOOK_NAME
    hook_path.write_text("#!/bin/sh\necho hello\n")
    status = hook_status(git_repo)
    assert status["installed"] is True
    assert status["envault_managed"] is False
