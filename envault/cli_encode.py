"""CLI subcommands: encode / decode .env values."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_encode import EncodeError, decode_env, encode_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, 'config', '.envault.json'))
    return EnvaultConfig.load(cfg_path)


def cmd_encode(args: argparse.Namespace) -> None:
    """Base64-encode values in the .env file."""
    try:
        cfg = _load_config(args)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    src = Path(cfg.env_file)
    dest = Path(args.dest) if args.dest else None
    keys = args.keys if args.keys else None

    try:
        out = encode_env(src, dest, keys=keys)
        print(f"[envault] encoded values written to {out}")
    except EncodeError as exc:
        print(f"[envault] encode error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_decode(args: argparse.Namespace) -> None:
    """Base64-decode values in the .env file."""
    try:
        cfg = _load_config(args)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    src = Path(cfg.env_file)
    dest = Path(args.dest) if args.dest else None
    keys = args.keys if args.keys else None

    try:
        out = decode_env(src, dest, keys=keys)
        print(f"[envault] decoded values written to {out}")
    except EncodeError as exc:
        print(f"[envault] decode error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    enc = sub.add_parser('encode', help='Base64-encode .env values')
    enc.add_argument('--dest', default=None, help='Output file (default: in-place)')
    enc.add_argument('--keys', nargs='+', metavar='KEY', help='Only encode these keys')
    enc.set_defaults(func=cmd_encode)

    dec = sub.add_parser('decode', help='Base64-decode .env values')
    dec.add_argument('--dest', default=None, help='Output file (default: in-place)')
    dec.add_argument('--keys', nargs='+', metavar='KEY', help='Only decode these keys')
    dec.set_defaults(func=cmd_decode)
