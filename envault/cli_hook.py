"""CLI subcommands for managing git hook integration."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.hook import HookError, install_hook, uninstall_hook, hook_status


def _repo_root(ns: argparse.Namespace) -> Path:
    return Path(getattr(ns, "repo", None) or Path.cwd())


def cmd_hook_install(ns: argparse.Namespace) -> None:
    root = _repo_root(ns)
    try:
        path = install_hook(root, force=ns.force)
        print(f"[envault] Hook installed at {path}")
    except HookError as exc:
        print(f"[envault] Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_hook_uninstall(ns: argparse.Namespace) -> None:
    root = _repo_root(ns)
    try:
        uninstall_hook(root)
        print("[envault] Hook removed.")
    except HookError as exc:
        print(f"[envault] Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_hook_status(ns: argparse.Namespace) -> None:
    root = _repo_root(ns)
    status = hook_status(root)
    print(f"Hook path     : {status['path']}")
    print(f"Installed     : {status['installed']}")
    print(f"Envault hook  : {status['envault_managed']}")


def register_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_hook = sub.add_parser("hook", help="Manage git hook integration")
    hook_sub = p_hook.add_subparsers(dest="hook_cmd", required=True)

    p_install = hook_sub.add_parser("install", help="Install pre-commit hook")
    p_install.add_argument("--force", action="store_true", help="Overwrite existing hook")
    p_install.add_argument("--repo", default=None, help="Path to git repo root")
    p_install.set_defaults(func=cmd_hook_install)

    p_uninstall = hook_sub.add_parser("uninstall", help="Remove pre-commit hook")
    p_uninstall.add_argument("--repo", default=None, help="Path to git repo root")
    p_uninstall.set_defaults(func=cmd_hook_uninstall)

    p_status = hook_sub.add_parser("status", help="Show hook status")
    p_status.add_argument("--repo", default=None, help="Path to git repo root")
    p_status.set_defaults(func=cmd_hook_status)
