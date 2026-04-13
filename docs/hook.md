# Git Hook Integration

envault can install a Git `pre-commit` hook that prevents you from accidentally
committing plaintext `.env` files to your repository.

## Install

```bash
envault hook install
```

This writes a `pre-commit` script to `.git/hooks/pre-commit` and makes it
executable. If a hook already exists the command will exit with an error.
Use `--force` to overwrite:

```bash
envault hook install --force
```

## Uninstall

```bash
envault hook uninstall
```

Removes the hook file. Raises an error if no hook is present.

## Status

```bash
envault hook status
```

Outputs whether a hook is installed and whether it is managed by envault:

```
Hook path     : /project/.git/hooks/pre-commit
Installed     : True
Envault hook  : True
```

## How It Works

The installed hook checks whether any staged files match the pattern
`.env` or `.env.*`. If a match is found the commit is aborted with a
helpful message:

```
[envault] ERROR: Attempting to commit a plaintext .env file.
[envault] Run 'envault push' to encrypt it first, then unstage the .env file.
```

## Options

| Flag | Description |
|------|-------------|
| `--force` | Overwrite an existing hook (install only) |
| `--repo PATH` | Path to the git repository root (defaults to cwd) |
