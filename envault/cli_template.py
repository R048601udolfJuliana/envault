"""CLI subcommands for .env template generation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.cli import _load_config
from envault.template import TemplateError, generate_template, keys_from_template


def cmd_template_generate(args: argparse.Namespace) -> None:
    """Generate a .env.template from the current .env file."""
    config = _load_config(args)
    source = Path(config.env_file)
    output = Path(args.output) if args.output else source.with_suffix(".template")

    try:
        content = generate_template(
            source_path=source,
            output_path=output,
            placeholder=args.placeholder,
            keep_comments=not args.strip_comments,
        )
    except TemplateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.print:
        print(content, end="")
    else:
        print(f"Template written to {output}")


def cmd_template_keys(args: argparse.Namespace) -> None:
    """List variable names declared in a template file."""
    template_path = Path(args.template_file)
    try:
        keys = keys_from_template(template_path)
    except TemplateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not keys:
        print("No keys found in template.")
    else:
        for key in keys:
            print(key)


def register_subcommands(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # --- generate ---
    p_gen = subparsers.add_parser("template-generate", help="Generate a .env.template file")
    p_gen.add_argument("--output", "-o", default=None, help="Output path (default: <env_file>.template)")
    p_gen.add_argument("--placeholder", default="", help="Value placeholder (default: empty string)")
    p_gen.add_argument("--strip-comments", action="store_true", help="Omit comments from template")
    p_gen.add_argument("--print", action="store_true", help="Print template to stdout instead of writing")
    p_gen.set_defaults(func=cmd_template_generate)

    # --- keys ---
    p_keys = subparsers.add_parser("template-keys", help="List keys in a template file")
    p_keys.add_argument("template_file", help="Path to .env.template file")
    p_keys.set_defaults(func=cmd_template_keys)
