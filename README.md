<div align="center">

# 🎵 Last.fm Manual Scrobbler

**Backfill plays your scrobbler missed: scan your library, mark what you played, send it to Last.fm.**

[![Stars](https://img.shields.io/github/stars/itachi-re/lastfm-scrobbler?style=social)](https://github.com/itachi-re/lastfm-scrobbler/stargazers)
[![Forks](https://img.shields.io/github/forks/itachi-re/lastfm-scrobbler?style=social)](https://github.com/itachi-re/lastfm-scrobbler/network/members)
[![Watchers](https://img.shields.io/github/watchers/itachi-re/lastfm-scrobbler?style=social)](https://github.com/itachi-re/lastfm-scrobbler/watchers)

[![Issues](https://img.shields.io/github/issues/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/issues)
[![Pull requests](https://img.shields.io/github/issues-pr/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/pulls)
[![Last commit](https://img.shields.io/github/last-commit/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/commits/main)
[![Commit activity](https://img.shields.io/github/commit-activity/m/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/commits/main)
[![Contributors](https://img.shields.io/github/contributors/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/graphs/contributors)
[![Repo size](https://img.shields.io/github/repo-size/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler)
[![Code size](https://img.shields.io/github/languages/code-size/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler)
[![Top language](https://img.shields.io/github/languages/top/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler)
[![License](https://img.shields.io/github/license/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/blob/main/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/itachi-re/lastfm-scrobbler/pulls)
[![Maintained](https://img.shields.io/badge/maintained-yes-success.svg)](https://github.com/itachi-re/lastfm-scrobbler/commits/main)

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-compatible-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![pylast](https://img.shields.io/badge/pylast-wrapper-informational)](https://github.com/pylast/pylast)
[![mutagen](https://img.shields.io/badge/mutagen-tag%20reader-informational)](https://mutagen.readthedocs.io/)
[![Last.fm API](https://img.shields.io/badge/Last.fm-API-D51007?logo=lastdotfm&logoColor=white)](https://www.last.fm/api)
[![Pano Scrobbler](https://img.shields.io/badge/Pano%20Scrobbler-CSV%20compatible-8A2BE2)](https://panoscrobbler.com/)

[![Linux](https://img.shields.io/badge/Linux-supported-FCC624?logo=linux&logoColor=black)](#-prerequisites)
[![Windows](https://img.shields.io/badge/Windows-supported-0078D6?logo=windows&logoColor=white)](#-prerequisites)
[![macOS](https://img.shields.io/badge/macOS-supported-000000?logo=apple&logoColor=white)](#-prerequisites)
[![Android (Termux)](https://img.shields.io/badge/Android-Termux-3DDC84?logo=android&logoColor=white)](#-android--termux)

</div>

---

## 📚 Table of Contents

- [What it does](#-what-it-does)
- [Responsible use](#️-responsible-use)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Setup](#-setup)
- [Quick start](#-quick-start)
- [The workflow in detail](#-the-workflow-in-detail)
- [Command-line options](#️-command-line-options)
- [Example output](#-example-output)
- [Android / Termux](#-android--termux)
- [Troubleshooting](#-troubleshooting)
- [Project layout](#-project-layout)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🧭 What it does

Four small scripts, run in order. Each one reads the previous one's output, so you can re-run any step without redoing the earlier ones.

```
~/Music ──► 01_scan_library.py ──► library.csv
                                        │
                  01b_pick_plays.py ◄───┘
                        │   (you type play counts in a spreadsheet)
                        ▼
              plays-template.csv  (or plays.txt)
                        │
                        ▼
            02_make_scrobbles.py ──► music-scrobble-<date>-<n>.csv
                                                │
                                                ▼
                                    03_submit_scrobbles.py ──► Last.fm
```

| Step | Script | Reads | Writes |
|---|---|---|---|
| 1 | `01_scan_library.py` | audio files in your music folder | `library.csv` |
| 2 | `01b_pick_plays.py` | `library.csv` | `plays-template.csv` or `plays.txt` |
| 3 | `02_make_scrobbles.py` | `library.csv` + your plays file | `music-scrobble-<date>-<n>.csv` |
| 4 | `03_submit_scrobbles.py` | the scrobble CSV + `LASTFM_*` env vars | `<file>.sent` after a successful send |

You never type artist names, titles or durations by hand. They come from the tags in your own files.

## ⚖️ Responsible use

This tool is for **plays you actually listened to** that your scrobbler missed (offline player, crashed app, broken sync). Submitting plays you didn't make misrepresents your history and goes against [Last.fm's terms](https://www.last.fm/legal/terms).

Step 4 is a **preview by default**. Nothing is sent, and nothing logs in, unless you pass `--send`.

## ✨ Features

| | |
|---|---|
| 🏷️ **Metadata from your files** | Reads artist, title, album, album artist and exact duration with [mutagen](https://mutagen.readthedocs.io/) (mp3, flac, m4a, ogg, opus, wav, wma, aac, ape, wv) |
| 📋 **Spreadsheet picking** | Get every song in a CSV with a `plays` column of zeros. Fill in only the ones you played |
| 🔎 **Or interactive picking** | Search by name in the terminal and set counts with `57 7` |
| 🎯 **Forgiving name matching** | Case, accents and punctuation are ignored (`boa - duvet` finds `bôa - Duvet`, `0angel` finds `0% Angel`). Ambiguous or missing names stop the run and list candidates |
| ⏱️ **Realistic timestamps** | Plays are laid back-to-back using each track's real duration, ending now by default or at the time you choose |
| ✅ **Timestamp validation** | Rows outside Last.fm's window (older than 14 days or more than 2 hours ahead) are skipped with a clear warning |
| 🧹 **De-duplication** | Identical artist/title/timestamp rows are dropped |
| 📦 **Batching and retries** | 50 scrobbles per request (Last.fm's limit), up to 3 retries on network errors |
| 🔒 **Double-send protection** | A `.sent` marker stops you submitting the same file twice by accident |
| 🔐 **Env-var credentials** | Your API secret and password stay out of shell history |
| 🔁 **Pano Scrobbler CSVs still work** | Step 4 accepts any CSV with `artist`, `track`, `timeMs` (and optional `album`) columns |

## 📝 Prerequisites

- A [Last.fm account](https://www.last.fm/join)
- **Python 3.8+** ([download](https://www.python.org/downloads/))
- **Git** ([download](https://git-scm.com/downloads))
- A music library with proper tags (artist and title at minimum)

## 🔑 Setup

### 1. Get your Last.fm API credentials

1. Open the [Last.fm API account page](https://www.last.fm/api/account) and log in
2. Click **Create API account**
3. Fill in anything for the app name
4. Copy your **API key** and **API secret**

### 2. Choose how to authenticate

Last.fm's API wants your password as an **MD5 hash**. You have two options:

- **`LASTFM_PASSWORD`**: your plain password. The script hashes it for you. Simplest.
- **`LASTFM_PASSWORD_HASH`**: a hash you generated yourself, so the plain password never sits in an env var.

To generate a hash (use a script file so shell-special characters like `$` or `!` can't break it):

```bash
cat > hash.py << 'EOF'
import hashlib
password = "your_actual_password"
print(hashlib.md5(password.encode('utf-8')).hexdigest())
EOF

python3 hash.py
rm hash.py
```

> ⚠️ **Treat the hash like a password.** Together with your API key and secret it is enough to log in through the API. Never put it in the README, an issue, or a commit.

### 3. Store your credentials securely

<details>
<summary><strong>Option A: this terminal session only</strong></summary>

```bash
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"
export LASTFM_USERNAME="your_username"
export LASTFM_PASSWORD_HASH="your_password_hash"   # or LASTFM_PASSWORD="..."
```

They disappear when you close the terminal.
</details>

<details>
<summary><strong>Option B: permanent, simple shell config</strong></summary>

```bash
cat >> ~/.bashrc << 'EOF'
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"
export LASTFM_USERNAME="your_username"
export LASTFM_PASSWORD_HASH="your_password_hash"
EOF
source ~/.bashrc
```

Use `~/.zshrc` for zsh. Don't do this if that file is in a public dotfiles repo; use Option C.
</details>

<details open>
<summary><strong>Option C: recommended if your dotfiles are public (GNU Stow, etc.) ⭐</strong></summary>

Keep the secrets in an untracked, locked-down file and only `source` it from your tracked config:

```bash
mkdir -p ~/.config/local
cat > ~/.config/local/lastfm.env << 'EOF'
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"
export LASTFM_USERNAME="your_username"
export LASTFM_PASSWORD_HASH="your_password_hash"
EOF

chmod 600 ~/.config/local/lastfm.env
echo ".config/local/" >> ~/dotfiles/.gitignore   # adjust to your dotfiles repo root
```

Then add one secret-free line to your tracked shell config:

```bash
[ -f ~/.config/local/lastfm.env ] && source ~/.config/local/lastfm.env
```

Your public repo only ever contains the harmless `source` line.
</details>

Check it worked:

```bash
echo $LASTFM_USERNAME
```

### 4. Install dependencies

With [uv](https://docs.astral.sh/uv/):

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

Or with plain Python:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The environment lives in `.venv/`, is git-ignored, and can be deleted and recreated any time.

## 🚀 Quick start

```bash
git clone https://github.com/itachi-re/lastfm-scrobbler.git
cd lastfm-scrobbler
# (install dependencies as above)

python3 01_scan_library.py ~/Music                  # 1. read your library
python3 01b_pick_plays.py --template                # 2. write plays-template.csv
libreoffice --calc plays-template.csv               #    fill the "plays" column, save as CSV
python3 02_make_scrobbles.py plays-template.csv     # 3. build the scrobble file
python3 03_submit_scrobbles.py music-scrobble-2026-11-17-0.csv           # 4. preview
python3 03_submit_scrobbles.py music-scrobble-2026-11-17-0.csv --send    #    send for real
```

## 🔬 The workflow in detail

### Step 1: scan your library

```bash
python3 01_scan_library.py ~/Music
python3 01_scan_library.py --filter kalafina      # print only matching rows
```

Walks the folder recursively, reads the tags, drops exact duplicates, sorts by artist and title, and numbers every track. The numbers are the `id` column in `library.csv`. Re-run it whenever your library changes.

It warns about tracks with no artist tag. Fix those in your tagger first, because Last.fm needs an artist.

### Step 2: choose what you played

**Option B, spreadsheet (recommended for big libraries):**

```bash
python3 01b_pick_plays.py --template
libreoffice --calc plays-template.csv
```

You get every song with a `plays` column pre-filled with `0`. Type counts for the songs you played and leave the rest. When you save, keep the format as **Text CSV, UTF-8, comma-separated**, otherwise Japanese titles are mangled and step 3 can't read the file. Sorting and filtering the sheet is fine, because each row carries its own `id`.

**Option A, interactive:**

```bash
python3 01b_pick_plays.py
```

```
search> duvet          # shows matches with their #id
search> 1 5            # set #1 to 5 plays   (0 removes it)
search> list           # everything picked so far
search> done           # writes plays.txt
```

Running it again loads your existing `plays.txt`, so you can keep adding. `--fresh` ignores it.

**Or write `plays.txt` by hand**, one song per line:

```
boa - duvet x5
mr. kitty - 0angel x10
alumina by nightmare x7      # "title by artist" also works
#57 x3                       # exact, by library id
kalafina - magia             # no count means 1 play
# lines starting with "# " are comments
```

> 💡 If a title is tagged in another script (say `アルミナ`), the romanized name won't match. The error lists the closest candidates with their ids, so use `#id x7` instead.

### Step 3: build the scrobble file

```bash
python3 02_make_scrobbles.py plays-template.csv
```

It resolves every line against `library.csv`, then lays the plays out one after another using each track's real duration. If anything is ambiguous or not found, **nothing is written** and you get the candidates to fix.

By default the last play ends right now. If you listened earlier, say so:

```bash
python3 02_make_scrobbles.py plays.txt --end   "2026-11-16 22:00"   # last play ends then
python3 02_make_scrobbles.py plays.txt --start "2026-11-16 18:30"   # first play starts then
python3 02_make_scrobbles.py plays.txt --shuffle --seed 1           # mix the order
```

Times are your local time. The output is `music-scrobble-<today>-<n>.csv`, where `<n>` counts up (0, 1, 2…) so files never overwrite each other. Check the summary it prints against what you typed before moving on.

### Step 4: submit

```bash
python3 03_submit_scrobbles.py music-scrobble-2026-11-17-0.csv           # preview only
python3 03_submit_scrobbles.py music-scrobble-2026-11-17-0.csv --send    # really send
```

The preview validates and de-duplicates the file but never logs in. With `--send`, it authenticates from your `LASTFM_*` environment variables, submits in batches of 50, and writes `<file>.sent` after a fully successful run. Running it again on the same file refuses unless you add `--force`.

> ⚠️ **14-day limit.** Last.fm rejects scrobbles older than about 14 days or more than 2 hours in the future. Older plays can't be backfilled this way.

## 📊 Scrobble CSV format

`02_make_scrobbles.py` writes this, and `03_submit_scrobbles.py` reads it:

```csv
timeHuman,timeMs,artist,track,album,albumArtist,durationMs
2026-11-17 14:02:10 +0600,1794898930000,bôa,Duvet,Twilight,bôa,204306
```

**Required:** `artist`, `track`, `timeMs` (Unix milliseconds). **Optional:** `album`, `albumArtist`, `durationMs`. Other columns are ignored, so Pano Scrobbler exports work too.

## ⚙️ Command-line options

```
01_scan_library.py [music_dir] [-o OUTPUT] [--filter TEXT]
    music_dir          folder to scan (default ~/Music)
    -o, --output       output file (default library.csv)
    --filter           only print rows containing TEXT (the file is still complete)

01b_pick_plays.py [--library FILE] [-o OUTPUT] [--template] [--fresh]
    --library          library file (default library.csv)
    -o, --output       plays file for interactive mode (default plays.txt)
    --template         write plays-template.csv instead of going interactive
    --fresh            ignore an existing plays file

02_make_scrobbles.py plays_file [--library FILE] [--out-dir DIR]
                     [--start "YYYY-MM-DD HH:MM" | --end "YYYY-MM-DD HH:MM"]
                     [--shuffle] [--seed N]
    plays_file         plays.txt or a filled-in plays-template.csv

03_submit_scrobbles.py file_path [--send] [--force]
    --send             actually submit (default is preview only)
    --force            submit even if a .sent marker exists

Environment (step 4 with --send):
    LASTFM_API_KEY  LASTFM_API_SECRET  LASTFM_USERNAME
    LASTFM_PASSWORD_HASH  (or LASTFM_PASSWORD)
```

## 📈 Example output

```
$ python3 02_make_scrobbles.py plays.txt
    5 x  bôa - Duvet
    7 x  ナイトメア (Nightmare) - アルミナ
   10 x  Mr. Kitty - 0% Angel
    1 x  Kalafina - Magia

23 plays, 2026-11-17 12:32 -> 2026-11-17 14:04 -> music-scrobble-2026-11-17-0.csv

$ python3 03_submit_scrobbles.py music-scrobble-2026-11-17-0.csv --send
14:04:17 [INFO] 23 valid scrobble(s), 2026-11-17 06:32 -> 2026-11-17 07:59 UTC
14:04:18 [INFO] Batch 1/1 ok (23/23)
14:04:18 [INFO] Done, 23 scrobble(s) submitted.
```

## 📱 Android / Termux

Works under [Termux](https://termux.dev/) with no root:

```bash
pkg update && pkg upgrade
pkg install python git

git clone https://github.com/itachi-re/lastfm-scrobbler.git
cd lastfm-scrobbler
pip install -r requirements.txt

termux-setup-storage                                  # once, to reach shared storage
python 01_scan_library.py ~/storage/music
```

Set the `LASTFM_*` variables in `~/.bashrc` so you don't retype them (see [Setup step 3](#3-store-your-credentials-securely)).

## 🆘 Troubleshooting

| Problem | Fix |
|---|---|
| `library.csv not found` | Run `01_scan_library.py` first |
| `WARNING: N track(s) have no artist tag` | Fix the tags in your music tagger, then re-scan |
| `not found` / `ambiguous` in step 3 | Use a more specific name, or `#id` from `library.csv`. The error lists candidates |
| Romanized title doesn't match (`alumina` vs `アルミナ`) | Use `#id xN`, or type the title as it is tagged |
| Japanese titles show as `????` in the spreadsheet | Re-open the CSV and set the import encoding to **UTF-8**. Save as CSV, not `.ods`/`.xlsx` |
| `WARNING: first play is older than 14 days` | Last.fm will reject it. Use a later `--start` / `--end` |
| `No valid scrobbles to send` | Every row was outside the 14-day window, or the file is empty or malformed |
| `... exists - this file was already sent` | The `.sent` marker is working. Use `--force` only if you're sure |
| `Authentication failed` | Check username, API key/secret and password hash |
| `Missing environment variable(s)` | Export the `LASTFM_*` variables in this shell (`echo $LASTFM_USERNAME` to check) |
| `externally-managed-environment` | Use a virtual environment (Setup step 4) |
| `ModuleNotFoundError: mutagen` / `pylast` | Activate the venv and run `pip install -r requirements.txt` |

## 🗂️ Project layout

```
lastfm-scrobbler/
├── 01_scan_library.py        # scan music folder -> library.csv
├── 01b_pick_plays.py         # plays-template.csv, or interactive picker -> plays.txt
├── 02_make_scrobbles.py      # plays file -> music-scrobble-<date>-<n>.csv
├── 03_submit_scrobbles.py    # preview / send to Last.fm
├── requirements.txt
├── CHANGELOG.md
└── LICENSE
```

Generated files (`library.csv`, `plays.txt`, `plays-template.csv`, `music-scrobble-*.csv`, `*.sent`) are git-ignored because they describe your listening.

With `uv`, the same invocations work once the environment is activated (see [Install dependencies](#4-install-dependencies)), or in one shot via `uv run`:

```bash
uv run --with-requirements requirements.txt python3 01_scan_library.py --help
```

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

[MIT License](LICENSE). Free to use, modify, and distribute.

## 🙏 Acknowledgments

- [Last.fm API](https://www.last.fm/api)
- [pylast](https://github.com/pylast/pylast), the Python wrapper for Last.fm
- [mutagen](https://mutagen.readthedocs.io/), for reading audio tags
- [Pano Scrobbler](https://panoscrobbler.com/), whose CSV export format this stays compatible with

---

<div align="center">

⭐ **Star this repo if it helped fill your Last.fm gaps!**

<sub>Built by <a href="https://github.com/itachi-re">@itachi-re</a> | Questions? Open an <a href="https://github.com/itachi-re/lastfm-scrobbler/issues/new">issue</a></sub>

</div>
