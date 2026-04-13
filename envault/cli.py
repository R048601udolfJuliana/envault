"""Command-line interface for envault."""

import sys
import argparse

from envault.config import EnvaultConfig, ConfigError
from envault.sync import push, pull, SyncError

CONFIG_FILE = ".envault.json"


def _load_config() -> EnvaultConfig:
    try:
        return EnvaultConfig.load(CONFIG_FILE)
    except (ConfigError, FileNotFoundError) as exc:
        print(f"[envault] Config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_push(args: argparse.Namespace) -> None:
    config = _load_config()
    try:
        dest = push(config, env_file=args.env_file, force=args.force)
        print(f"[envault] Pushed encrypted file to: {dest}")
    except SyncError as exc:
        print(f"[envault] Push failed: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_pull(args: argparse.Namespace) -> None:
    config = _load_config()
    try:
        local = pull(config, env_file=args.env_file, force=args.force)
        print(f"[envault] Pulled and decrypted to: {local}")
    except SyncError as exc:
        print(f"[envault] Pull failed: {exc}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envault",
        description="Encrypt and sync .env files using GPG keys.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    push_p = sub.add_parser("push", help="Encrypt and push .env to the sync destination.")
    push_p.add_argument("--env-file", default=".env", help="Path to the .env file (default: .env)")
    push_p.add_argument("--force", action="store_true", help="Overwrite existing destination file.")
    push_p.set_defaults(func=cmd_push)

    pull_p = sub.add_parser("pull", help="Pull and decrypt .env from the sync destination.")
    pull_p.add_argument("--env-file", default=".env", help="Path to write the decrypted file (default: .env)")
    pull_p.add_argument("--force", action="store_true", help="Overwrite existing local .env file.")
    pull_p.set_defaults(func=cmd_pull)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
