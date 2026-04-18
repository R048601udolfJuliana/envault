"""CLI subcommands for vault notes."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.note import NoteError, add_note, clear_notes, list_notes


def cmd_note_add(args: argparse.Namespace) -> None:
    config_dir = Path(args.config_dir)
    try:
        entry = add_note(config_dir, args.profile, args.text, args.author or None)
    except NoteError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Note added for profile '{entry['profile']}' at {entry['created_at']}")


def cmd_note_list(args: argparse.Namespace) -> None:
    config_dir = Path(args.config_dir)
    try:
        notes = list_notes(config_dir, args.profile or None)
    except NoteError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    if not notes:
        print("No notes found.")
        return
    for n in notes:
        author = f" [{n['author']}]" if n.get("author") else ""
        print(f"[{n['created_at']}] ({n['profile']}){author}: {n['text']}")


def cmd_note_clear(args: argparse.Namespace) -> None:
    config_dir = Path(args.config_dir)
    try:
        removed = clear_notes(config_dir, args.profile or None)
    except NoteError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"Cleared {removed} note(s).")


def register_subcommands(sub: argparse._SubParsersAction) -> None:
    p_add = sub.add_parser("note-add", help="Add a note to a profile vault")
    p_add.add_argument("profile", help="Profile name")
    p_add.add_argument("text", help="Note text")
    p_add.add_argument("--author", default="", help="Author name")
    p_add.add_argument("--config-dir", default=".", help="Config directory")
    p_add.set_defaults(func=cmd_note_add)

    p_list = sub.add_parser("note-list", help="List notes")
    p_list.add_argument("--profile", default="", help="Filter by profile")
    p_list.add_argument("--config-dir", default=".", help="Config directory")
    p_list.set_defaults(func=cmd_note_list)

    p_clear = sub.add_parser("note-clear", help="Clear notes")
    p_clear.add_argument("--profile", default="", help="Clear only this profile")
    p_clear.add_argument("--config-dir", default=".", help="Config directory")
    p_clear.set_defaults(func=cmd_note_clear)
