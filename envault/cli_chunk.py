"""CLI sub-commands for env-chunk: split a .env file into N chunks."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_chunk import ChunkError, chunk_env


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    return EnvaultConfig.load(cfg_path)


def cmd_chunk(args: argparse.Namespace) -> None:
    """Split the project .env file into N chunk files."""
    try:
        cfg = _load_config(args)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)

    source = Path(cfg.env_file)
    dest_dir = Path(args.dest_dir) if args.dest_dir else source.parent / "chunks"
    prefix = args.prefix or "chunk"

    try:
        paths = chunk_env(source, n=args.n, dest_dir=dest_dir, prefix=prefix)
    except ChunkError as exc:
        print(f"[envault] chunk error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Created {len(paths)} chunk(s) in {dest_dir}:")
    for p in paths:
        print(f"  {p}")


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("chunk", help="Split .env into N chunk files")
    p.add_argument("n", type=int, metavar="N", help="Number of chunks")
    p.add_argument(
        "--dest-dir",
        metavar="DIR",
        default=None,
        help="Output directory (default: <env-dir>/chunks)",
    )
    p.add_argument(
        "--prefix",
        metavar="PREFIX",
        default="chunk",
        help="Filename prefix for chunks (default: chunk)",
    )
    p.set_defaults(func=cmd_chunk)
