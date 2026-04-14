"""CLI subcommand: envault watch — auto-push on .env changes."""

import argparse
import sys
from pathlib import Path

from envault.config import EnvaultConfig, ConfigError
from envault.sync import push, SyncError
from envault.watch import watch, WatchError


def _load_config(config_path: str) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(config_path))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_watch(ns: argparse.Namespace) -> None:
    """Watch .env and push automatically on every save."""
    config = _load_config(ns.config)
    env_path = Path(config.env_file)

    print(f"[envault] Watching {env_path} (interval={ns.interval}s) — Ctrl-C to stop")

    def _on_change(path: Path) -> None:
        print(f"[envault] Change detected in {path.name}, pushing…")
        try:
            push(config, force=True)
            print("[envault] Push successful.")
        except SyncError as exc:
            print(f"[envault] Push failed: {exc}", file=sys.stderr)

    try:
        watch(env_path, on_change=_on_change, interval=ns.interval)
    except WatchError as exc:
        print(f"[envault] watch error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[envault] Stopped watching.")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("watch", help="Watch .env and auto-push on changes")
    p.add_argument(
        "--interval",
        type=float,
        default=1.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 1.0)",
    )
    p.add_argument(
        "--config",
        default=".envault.json",
        metavar="FILE",
        help="Path to envault config file",
    )
    p.set_defaults(func=cmd_watch)
