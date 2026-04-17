"""CLI subcommands for alias management."""
from __future__ import annotations

import sys
from pathlib import Path

from envault.alias import AliasError, add_alias, load_aliases, remove_alias, resolve_alias


def cmd_alias_add(args, config) -> None:
    force = getattr(args, "force", False)
    config_dir = Path(config.config_path).parent
    try:
        if force:
            from envault.alias import load_aliases, save_aliases
            aliases = load_aliases(config_dir)
            aliases[args.name] = args.target
            save_aliases(config_dir, aliases)
        else:
            add_alias(config_dir, args.name, args.target)
        print(f"Alias '{args.name}' -> '{args.target}' added.")
    except AliasError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_alias_remove(args, config) -> None:
    config_dir = Path(config.config_path).parent
    try:
        remove_alias(config_dir, args.name)
        print(f"Alias '{args.name}' removed.")
    except AliasError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_alias_list(args, config) -> None:
    config_dir = Path(config.config_path).parent
    try:
        aliases = load_aliases(config_dir)
    except AliasError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    if not aliases:
        print("No aliases defined.")
        return
    for name, target in sorted(aliases.items()):
        print(f"  {name} -> {target}")


def cmd_alias_resolve(args, config) -> None:
    config_dir = Path(config.config_path).parent
    try:
        target = resolve_alias(config_dir, args.name)
        print(target)
    except AliasError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(subparsers, config) -> None:
    p = subparsers.add_parser("alias", help="Manage profile aliases")
    sub = p.add_subparsers(dest="alias_cmd", required=True)

    p_add = sub.add_parser("add", help="Add an alias")
    p_add.add_argument("name")
    p_add.add_argument("target")
    p_add.add_argument("--force", action="store_true")
    p_add.set_defaults(func=lambda a: cmd_alias_add(a, config))

    p_rm = sub.add_parser("remove", help="Remove an alias")
    p_rm.add_argument("name")
    p_rm.set_defaults(func=lambda a: cmd_alias_remove(a, config))

    p_ls = sub.add_parser("list", help="List all aliases")
    p_ls.set_defaults(func=lambda a: cmd_alias_list(a, config))

    p_res = sub.add_parser("resolve", help="Resolve an alias to its target")
    p_res.add_argument("name")
    p_res.set_defaults(func=lambda a: cmd_alias_resolve(a, config))
