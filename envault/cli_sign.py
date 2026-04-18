"""CLI subcommands for signing and verifying vault files."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envault.config import ConfigError, EnvaultConfig
from envault.sign import SignError, sign_file, verify_signature


def _load_config(args: argparse.Namespace) -> EnvaultConfig:
    try:
        return EnvaultConfig.load(Path(args.config))
    except ConfigError as exc:
        print(f"[envault] config error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_sign(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    enc_file = Path(cfg.encrypted_file)
    try:
        sig = sign_file(enc_file, args.key_id)
        print(f"Signed: {enc_file}")
        print(f"Signature: {sig}")
    except SignError as exc:
        print(f"[envault] sign error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_verify_sig(args: argparse.Namespace) -> None:
    cfg = _load_config(args)
    enc_file = Path(cfg.encrypted_file)
    sig_path = Path(args.sig) if args.sig else None
    try:
        signer = verify_signature(enc_file, sig_path)
        print(f"Signature valid. Signed by key: {signer}")
    except SignError as exc:
        print(f"[envault] verify error: {exc}", file=sys.stderr)
        sys.exit(1)


def register_subcommands(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_sign = sub.add_parser("sign", help="Sign the encrypted vault file")
    p_sign.add_argument("--config", default=".envault.json")
    p_sign.add_argument("--key-id", required=True, help="GPG key ID to sign with")
    p_sign.set_defaults(func=cmd_sign)

    p_verify = sub.add_parser("verify-sig", help="Verify the vault file signature")
    p_verify.add_argument("--config", default=".envault.json")
    p_verify.add_argument("--sig", default=None, help="Path to .sig file (optional)")
    p_verify.set_defaults(func=cmd_verify_sig)
