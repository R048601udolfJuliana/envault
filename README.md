# envault

> A CLI tool for encrypting and syncing `.env` files across team members using GPG keys.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

**Initialize envault in your project:**
```bash
envault init
```

**Add a team member's GPG key:**
```bash
envault add-key teammate@example.com
```

**Encrypt and push your `.env` file:**
```bash
envault push .env
```

**Pull and decrypt the latest `.env`:**
```bash
envault pull
```

Your `.env` file is encrypted for all registered team members and stored as `.env.vault` — safe to commit to version control.

---

## How It Works

1. Each team member registers their GPG public key with `envault`
2. Secrets are encrypted using GPG for every registered key
3. The encrypted `.env.vault` file can be shared via Git or any file storage
4. Team members decrypt locally using their private GPG key

---

## Requirements

- Python 3.8+
- GPG installed on your system (`gpg --version`)

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Contributions welcome! Open an issue or submit a pull request.*