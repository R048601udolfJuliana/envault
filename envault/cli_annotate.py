"""cli_annotate.py – CLI subcommands for env-key annotation."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.env_annotate import AnnotateError, annotate_key, read_annotations


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    cfg_path = Path(getattr(args, "config", ".envault.json"))
    try:
        return EnvaultConfig.load(cfg_path)
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_annotate_set(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    env_path = Path(cfg.env_file)
    dest = Path(args.dest) if getattr(args, "dest", None) else None
    try:
        out = annotate_key(
            env_path,
            args.key,
            ann_type=getattr(args, "type", None) or None,
            desc=getattr(args, "desc", None) or None,
            dest=dest,
        )
        print(f"[envault] annotation written to {out}")
    except AnnotateError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_annotate_list(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    env_path = Path(cfg.env_file)
    try:
        annotations = read_annotations(env_path)
    except AnnotateError as exc:
        print(f"[envault] error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not annotations:
        print("No annotations found.")
        return
    for key, meta in annotations.items():
        parts = [f"{key}:"]
        if "type" in meta:
            parts.append(f"  type={meta['type']}")
        if "desc" in meta:
            parts.append(f"  desc={meta['desc']}")
        print(" ".join(parts))


def register_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # annotate set
    p_set = sub.add_parser("annotate-set", help="Add/replace annotation for a key")
    p_set.add_argument("key", help=".env key to annotate")
    p_set.add_argument("--type", dest="type", default="", help="Type hint (e.g. string, int)")
    p_set.add_argument("--desc", dest="desc", default="", help="Human-readable description")
    p_set.add_argument("--dest", default=None, help="Output file (default: in-place)")
    p_set.add_argument("--config", default=".envault.json")
    p_set.set_defaults(func=cmd_annotate_set)

    # annotate list
    p_list = sub.add_parser("annotate-list", help="List all annotations in the .env file")
    p_list.add_argument("--config", default=".envault.json")
    p_list.set_defaults(func=cmd_annotate_list)
