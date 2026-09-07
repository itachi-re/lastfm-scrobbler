<div align="center">

# 🎵 Last.fm Manual Scrobbler

**Bulk-upload missing listening history to Last.fm from a CSV file — for when your scrobbler fails you.**

[![GitHub Repo stars](https://img.shields.io/github/stars/itachi-re/lastfm-scrobbler?style=social)](https://github.com/itachi-re/lastfm-scrobbler/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/issues)
[![GitHub license](https://img.shields.io/github/license/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/blob/main/LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/itachi-re/lastfm-scrobbler/pulls)
[![Maintained](https://img.shields.io/badge/maintained-yes-success.svg)](https://github.com/itachi-re/lastfm-scrobbler/commits/main)

**Runs anywhere Python does:**

[![Linux](https://img.shields.io/badge/Linux-supported-FCC624?logo=linux&logoColor=black)](#-prerequisites)
[![Windows](https://img.shields.io/badge/Windows-supported-0078D6?logo=windows&logoColor=white)](#-prerequisites)
[![macOS](https://img.shields.io/badge/macOS-supported-000000?logo=apple&logoColor=white)](#-prerequisites)
[![Android (Termux)](https://img.shields.io/badge/Android-Termux-3DDC84?logo=android&logoColor=white)](#-android--termux)

</div>

---

## 📚 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Setup](#-setup)
  - [1. Get Your Last.fm API Credentials](#1-get-your-lastfm-api-credentials)
  - [2. Generate Your Password Hash](#2-generate-your-password-hash)
  - [3. Store Your Credentials Securely](#3-store-your-credentials-securely)
  - [4. Set Up a Virtual Environment](#4-set-up-a-virtual-environment)
- [Quick Start](#-quick-start)
- [CSV Format](#-csv-format)
- [Command-Line Options](#️-command-line-options)
- [Rate & Batch Handling](#️-rate--batch-handling)
- [Example Output](#-example-output)
- [Android / Termux](#-android--termux)
- [Troubleshooting](#-troubleshooting)
- [Advanced Usage](#-advanced-usage)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## ✨ Features

| | |
|---|---|
| 📦 **Batch upload** | Submits in batches of 50 (Last.fm's `scrobble_many` API limit), with automatic retry on transient network errors |
| 🔄 **Pano Scrobbler compatible** | Works with `timeMs` (milliseconds) or plain `timestamp` (seconds) export columns |
| ✅ **Timestamp validation** | Rows older than 14 days or more than 2 hours in the future are rejected up front, with a clear warning instead of failing a whole batch |
| 🧹 **De-duplication** | Identical artist/title/timestamp rows are automatically skipped |
| 🧪 **Dry-run mode** | Validate and preview your CSV without submitting anything |
| 🔐 **Env-var credentials** | Keep your API key and password hash out of shell history |
| 📊 **Progress + error logging** | Per-batch status via Python's `logging` module, with distinct exit codes for scripting/cron use |
| 🖥️ **Cross-platform** | Linux, Windows, macOS, and Android via Termux — anywhere Python 3.6+ runs |

## 📝 Prerequisites

- [x] A [Last.fm account](https://www.last.fm/join)
- [x] **Python 3.6** or later ([Download here](https://www.python.org/downloads/))
- [x] **Git** ([Download here](https://git-scm.com/downloads))
- [x] A CSV file with your listening history (works with [Pano Scrobbler](https://panoscrobbler.com/) exports)

## 🔑 Setup

### 1. Get Your Last.fm API Credentials

1. Visit the [Last.fm API Account page](https://www.last.fm/api/account)
2. Log in with your Last.fm credentials
3. Click **"Create a new API account"**
4. Fill in any details (app name can be anything)
5. **Copy your API Key and API Secret** 📋

### 2. Generate Your Password Hash

Last.fm's API expects your password as an **MD5 hash**, never in plaintext.

> ⚠️ **Don't paste Python code directly into your shell.** Your shell (bash/zsh) doesn't understand Python syntax and will throw a parse error. Either drop into a Python interpreter first, or — better — use a throwaway script file. This also avoids escaping headaches if your password contains shell-special characters like `$`, `` ` ``, or `!`.

```bash
cat > hash.py << 'EOF'
import hashlib
password = "your_actual_password"
print(hashlib.md5(password.encode('utf-8')).hexdigest())
EOF

python3 hash.py
rm hash.py
```

Copy the 32-character string it prints — that's your `LASTFM_PASSWORD_HASH`.

*(The `rm hash.py` at the end matters: this keeps your plaintext password from lingering in a file on disk.)*

### 3. Store Your Credentials Securely

You now have four secrets: **API key**, **API secret**, **username**, and **password hash**. How you store them depends on your setup — pick the option that fits:

<details>
<summary><strong>Option A — Quick & temporary (this terminal session only)</strong></summary>

```bash
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"
export LASTFM_USERNAME="your_username"
export LASTFM_PASSWORD_HASH="your_password_hash"
```
These vanish the moment you close the terminal — fine for a one-off run, not for repeated use.
</details>

<details>
<summary><strong>Option B — Permanent, simple dotfiles (not using a public dotfiles repo)</strong></summary>

Append to your shell config (`~/.zshrc` for zsh, `~/.bashrc` for bash) so they load automatically every new session:

```bash
cat >> ~/.zshrc << 'EOF'
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"
export LASTFM_USERNAME="your_username"
export LASTFM_PASSWORD_HASH="your_password_hash"
EOF

source ~/.zshrc
```
</details>

<details open>
<summary><strong>Option C — Recommended if your dotfiles are managed with GNU Stow and backed up on GitHub ⭐</strong></summary>

If your `.zshrc` (or any file `stow` symlinks) is tracked in a public repo, **never** put real secrets directly in it. Instead, keep secrets in a separate, untracked, locked-down file, and only reference it from your tracked config:

```bash
# 1. Create a local-only secrets file, outside version control
mkdir -p ~/.config/local
cat > ~/.config/local/lastfm.env << 'EOF'
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"
export LASTFM_USERNAME="your_username"
export LASTFM_PASSWORD_HASH="your_password_hash"
EOF

# 2. Lock it down to your user only
chmod 600 ~/.config/local/lastfm.env

# 3. Gitignore it, so a stow re-sync or `git add .` never picks it up
echo ".config/local/" >> ~/dotfiles/.gitignore   # adjust path to your repo root
```

Then add **one safe, secret-free line** to your tracked `.zshrc`:

```bash
[ -f ~/.config/local/lastfm.env ] && source ~/.config/local/lastfm.env
```

Reload your shell to pick it up:

```bash
source ~/.zshrc
```

**Result:** your public repo only ever contains the harmless `source` line — the real secrets live in a local, untracked, `chmod 600` file that never leaves your machine. This same pattern works for any other secrets you pick up later (GitHub tokens, AWS keys, etc.) — just add more conditional `source` lines.
</details>

**Verify it worked** (any option):
```bash
echo $LASTFM_API_KEY
```
If that prints your key, you're good.

### 4. Set Up a Virtual Environment

```bash
cd lastfm-scrobbler
python3 -m venv venv
source venv/bin/activate
```

> 💡 `python3 -m venv venv` isn't creating "two environments" — `-m venv` tells Python to run its built-in **venv module**; the second `venv` is just the **folder name** you're choosing for the environment (convention, not a requirement). `python3 -m venv myenv` would work identically, just naming the folder `myenv` instead.

The `venv/` folder is created fresh inside the repo and doesn't need backing up — if it ever breaks, just delete it and re-run the command. Deactivate anytime with `deactivate`.

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/itachi-re/lastfm-scrobbler.git
cd lastfm-scrobbler

# 2. Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Dry-run first — validate your CSV without submitting anything
python3 manual_scrobbler.py --dry-run your_file.csv

# 5. Run for real (using env vars set up in Setup step 3)
python3 manual_scrobbler.py your_file.csv
```

### Example (flags instead of env vars)
```bash
python3 manual_scrobbler.py \
  --api-key c2ec6ca444b023c8b62c970a4f1bbc2e \
  --api-secret 0f2ca7559ec8f03f2e5bb3f2dc8e84d0 \
  --username itachi-re \
  --password-hash 767322d66b74474cff0eb25ce5fa31fe \
  generated_scrobbles_log_full.csv
```

Flags always take priority over environment variables if both are set.

## 📊 CSV Format

The script accepts either `timeMs` (Pano Scrobbler's native millisecond format) or a plain `timestamp` column in seconds:

```csv
artist,track,timeMs,album
The Beatles,Hey Jude,1699123456000,The Beatles 1967-1970
Radiohead,Karma Police,1699123512000,OK Computer
```

or

```csv
artist,track,timestamp,album
The Beatles,Hey Jude,1699123456,The Beatles 1967-1970
```

**Required columns**: `artist`, `track`, and one of `timeMs`/`timestamp`. **Optional**: `album`.

> ⚠️ Last.fm rejects scrobbles older than ~14 days. If your export includes older listens, they'll be counted and skipped rather than causing the whole run to fail — see the summary output.

## ⚙️ Command-Line Options

```
usage: manual_scrobbler.py [-h] [--api-key API_KEY] [--api-secret API_SECRET]
                            [--username USERNAME] [--password-hash PASSWORD_HASH]
                            [--dry-run]
                            file_path

positional arguments:
  file_path             Path to the CSV file of scrobbles

options:
  -h, --help            show this help message and exit
  --api-key API_KEY             (or set LASTFM_API_KEY)
  --api-secret API_SECRET       (or set LASTFM_API_SECRET)
  --username USERNAME           (or set LASTFM_USERNAME)
  --password-hash PASSWORD_HASH (or set LASTFM_PASSWORD_HASH)
  --dry-run             Parse and validate the CSV but do not submit anything
```

## 🛡️ Rate & Batch Handling

- Scrobbles are submitted in fixed batches of **50** — the maximum Last.fm's `track.scrobble` API accepts per call.
- Each batch retries up to 3 times with backoff on transient network errors before being marked failed.
- API-level rejections (e.g. invalid timestamp) are logged and skipped rather than retried, since retrying won't fix a bad request.

## 📈 Example Output

```
14:02:10 [INFO] Found 1247 valid scrobble(s) spanning 2024-11-01 08:00 to 2024-11-04 22:15 (UTC)
14:02:10 [WARNING] Skipped 12 row(s) with missing/invalid data
14:02:10 [WARNING] Skipped 8 duplicate row(s)
14:02:11 [INFO] Batch 1/25 submitted (50/1247 scrobbles total)
14:02:13 [INFO] Batch 2/25 submitted (100/1247 scrobbles total)
...
14:04:44 [INFO] Done! 1247 scrobble(s) submitted successfully.
```

## 📱 Android / Termux

The script runs fine under [Termux](https://termux.dev/) on Android — no root required:

```bash
# Inside Termux
pkg update && pkg upgrade
pkg install python git

git clone https://github.com/itachi-re/lastfm-scrobbler.git
cd lastfm-scrobbler

pip install -r requirements.txt
python manual_scrobbler.py your_file.csv
```

Notes for Termux:
- Skip the `venv` step if storage is tight — Termux's Python install is already isolated per-app.
- Use `termux-setup-storage` first if your CSV lives in shared storage (e.g. `~/storage/downloads/`).
- Set credentials as environment variables in `~/.bashrc` so you don't retype them each session (see [Setup step 3](#3-store-your-credentials-securely) for the secure-storage pattern).

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| **`externally-managed-environment`** | Use a virtual environment: `python3 -m venv venv` |
| **`zsh: parse error near ...`** | You pasted Python code straight into your shell. Run `python3` first to enter the interpreter, or use the script-file method in [Setup step 2](#2-generate-your-password-hash) |
| **`Missing required credential(s)`** | Pass all four credentials as flags, or set the matching `LASTFM_*` env var |
| **`"Invalid API key"`** | Double-check your API key/secret from Last.fm |
| **`"User not authorized"`** | Verify your username & password hash are correct |
| **Rows skipped as "out of range"** | Last.fm only accepts scrobbles from the last 14 days — older listens can't be backfilled this way |
| **Upload fails mid-way** | Check your CSV formatting and internet connection; failed batches are logged with the batch number so you can isolate the issue |
| **`ModuleNotFoundError: pylast` (Termux)** | Run `pkg install python-pip` first, then `pip install -r requirements.txt` |

## 🔧 Advanced Usage

```bash
# Dry run — validate and preview without uploading
python3 manual_scrobbler.py --dry-run file.csv

# Use env-var credentials, just point at the file
python3 manual_scrobbler.py file.csv

# Full help
python3 manual_scrobbler.py --help
```

## 🤝 Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request!

## 📄 License

[MIT License](LICENSE) - Free to use, modify, and distribute!

## 🙏 Acknowledgments

- [Last.fm API](https://www.last.fm/api) - Amazing music data platform
- [Pylast](https://github.com/pylast/pylast) - Python wrapper for Last.fm
- [Pano Scrobbler](https://panoscrobbler.com/) - Great CSV export tool

---

<div align="center">

⭐ **Star this repo if it helped fill your Last.fm gaps!**

**Made with ❤️ for music lovers** 🎵

<sub>Built by <a href="https://github.com/itachi-re">@itachi-re</a> | Questions? Open an <a href="https://github.com/itachi-re/lastfm-scrobbler/issues/new">issue</a></sub>

</div>
