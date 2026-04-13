"""CLI subcommands for tag management."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.tag import TagError, add_tag, files_for_tag, list_tags, remove_tag


def cmd_tag_add(args: argparse.Namespace) -> None:
    """envault tag add <tag> <file>"""
    try:
        add_tag(Path(args.directory), args.tag, args.file)
        print(f"Tagged '{args.file}' with '{args.tag}'.")
    except TagError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_remove(args: argparse.Namespace) -> None:
    """envault tag remove <tag> <file>"""
    try:
        remove_tag(Path(args.directory), args.tag, args.file)
        print(f"Removed tag '{args.tag}' from '{args.file}'.")
    except TagError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_tag_list(args: argparse.Namespace) -> None:
    """envault tag list [<tag>]"""
    try:
        if args.tag:
            files = files_for_tag(Path(args.directory), args.tag)
            if not files:
                print(f"No files tagged with '{args.tag}'.")
            else:
                for f in files:
                    print(f)
        else:
            tags = list_tags(Path(args.directory))
            if not tags:
                print("No tags defined.")
            else:
                for tag, files in sorted(tags.items()):
                    print(f"{tag}: {', '.join(files)}")
    except TagError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(sub: argparse.Action) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("tag", help="Manage tags for encrypted files")
    p.add_argument("--directory", default=".", help="Working directory")
    tag_sub = p.add_subparsers(dest="tag_cmd", required=True)

    p_add = tag_sub.add_parser("add", help="Tag a file")
    p_add.add_argument("tag")
    p_add.add_argument("file")
    p_add.set_defaults(func=cmd_tag_add)

    p_rm = tag_sub.add_parser("remove", help="Remove a tag from a file")
    p_rm.add_argument("tag")
    p_rm.add_argument("file")
    p_rm.set_defaults(func=cmd_tag_remove)

    p_ls = tag_sub.add_parser("list", help="List tags")
    p_ls.add_argument("tag", nargs="?", default=None)
    p_ls.set_defaults(func=cmd_tag_list)
