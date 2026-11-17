# Last.fm Manual Scrobbler

Backfill plays your scrobbler missed: scan your library, mark what you played, send it to Last.fm.

[![Stars](https://img.shields.io/github/stars/itachi-re/lastfm-scrobbler?style=social)](https://github.com/itachi-re/lastfm-scrobbler/stargazers)
[![Forks](https://img.shields.io/github/forks/itachi-re/lastfm-scrobbler?style=social)](https://github.com/itachi-re/lastfm-scrobbler/network/members)
[![Watchers](https://img.shields.io/github/watchers/itachi-re/lastfm-scrobbler?style=social)](https://github.com/itachi-re/lastfm-scrobbler/watchers)

[![Issues](https://img.shields.io/github/issues/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/issues)
[![Pull requests](https://img.shields.io/github/issues-pr/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/pulls)
[![Last commit](https://img.shields.io/github/last-commit/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/commits/main)
[![Commit activity](https://img.shields.io/github/commit-activity/m/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/commits/main)
[![Repo size](https://img.shields.io/github/repo-size/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler)
[![Top language](https://img.shields.io/github/languages/top/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler)
[![License](https://img.shields.io/github/license/itachi-re/lastfm-scrobbler)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/itachi-re/lastfm-scrobbler/pulls)

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-compatible-DE5FE9?logo=uv&logoColor=white)](https://docs.astral.sh/uv/)
[![pylast](https://img.shields.io/badge/pylast-wrapper-informational)](https://github.com/pylast/pylast)
[![mutagen](https://img.shields.io/badge/mutagen-tag%20reader-informational)](https://mutagen.readthedocs.io/)
[![Last.fm API](https://img.shields.io/badge/Last.fm-API-D51007?logo=lastdotfm&logoColor=white)](https://www.last.fm/api)
[![Pano Scrobbler](https://img.shields.io/badge/Pano%20Scrobbler-CSV%20compatible-8A2BE2)](https://panoscrobbler.com/)

[![Linux](https://img.shields.io/badge/Linux-supported-FCC624?logo=linux&logoColor=black)](#setup)
[![Windows](https://img.shields.io/badge/Windows-supported-0078D6?logo=windows&logoColor=white)](#setup)
[![macOS](https://img.shields.io/badge/macOS-supported-000000?logo=apple&logoColor=white)](#setup)
[![Android (Termux)](https://img.shields.io/badge/Android-Termux-3DDC84?logo=android&logoColor=white)](#android-termux)

## Contents

- [How it works](#how-it-works)
- [Responsible use](#responsible-use)
- [Setup](#setup)
- [Quick start](#quick-start)
- [Android (Termux)](#android-termux)
- [Usage](#usage)
- [Limits to know](#limits-to-know)
- [Options](#options)
- [Scrobble CSV format](#scrobble-csv-format)
- [Troubleshooting](#troubleshooting)
- [Project layout](#project-layout)
- [License](#license)

## How it works

Four small scripts, run in order. Each reads the previous one's output, so you can re-run any step without redoing the earlier ones. Artist, title, album and duration come from the tags in your own files; you never type them.

```
~/Music --> 01_scan_library.py --> library.csv
                                       |
                 01b_pick_plays.py <---+
                       |   (you enter how many times you played each song)
                       v
             plays-template.csv  (or plays.txt)
                       |
                       v
           02_make_scrobbles.py --> music-scrobble-<date>-<n>.csv
                                              |
                                              v
                                  03_submit_scrobbles.py --> Last.fm
```

| Step | Script | Reads | Writes |
|---|---|---|---|
| 1 | `01_scan_library.py` | audio files in your music folder | `library.csv` |
| 1b | `01b_pick_plays.py` | `library.csv` | `plays-template.csv` or `plays.txt` |
| 2 | `02_make_scrobbles.py` | `library.csv` and your plays file | `music-scrobble-<date>-<n>.csv` |
| 3 | `03_submit_scrobbles.py` | the scrobble CSV and `LASTFM_*` variables | `<file>.sent` after a full send |

## Responsible use

Use this for plays you actually listened to and your scrobbler missed (offline player, crashed app, broken sync). Submitting plays you didn't make misrepresents your history and goes against [Last.fm's terms](https://www.last.fm/legal/terms).

Step 3 only previews by default. Nothing is sent, and nothing logs in, unless you pass `--send`.

## Setup

You need a [Last.fm account](https://www.last.fm/join), [Python 3.8+](https://www.python.org/downloads/), [Git](https://git-scm.com/downloads), and a music library with artist and title tags. Linux, macOS and Windows are covered below; Android is covered in [its own section](#android-termux).

### 1. Get API credentials

Open the [Last.fm API account page](https://www.last.fm/api/account), choose **Create API account**, fill in any app name, and copy the **API key** and **API secret**.

### 2. Install

**Linux and macOS**

```bash
git clone https://github.com/itachi-re/lastfm-scrobbler.git
cd lastfm-scrobbler
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/itachi-re/lastfm-scrobbler.git
cd lastfm-scrobbler
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS, if `python3 --version` shows less than 3.8, install a newer Python with `brew install python` or from [python.org](https://www.python.org/downloads/). Apple Music keeps its files under `~/Music/Music/Media`, so point step 1 at the folder that actually holds your audio files.

With [uv](https://docs.astral.sh/uv/), `uv venv` followed by `uv pip install -r requirements.txt` does the same. On Windows and in Termux, use `python` wherever this README says `python3`.

### 3. Set your credentials

Last.fm wants your password as an MD5 hash. Either set `LASTFM_PASSWORD` (the script hashes it for you) or set `LASTFM_PASSWORD_HASH` to a hash you made yourself:

```
python3 -c "import getpass,hashlib; print(hashlib.md5(getpass.getpass().encode()).hexdigest())"
```

It asks for the password without showing it, so nothing lands in your shell history. Treat the hash like a password: with your API key and secret it is enough to log in through the API.

**Linux and macOS, this terminal only**

```bash
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"
export LASTFM_USERNAME="your_username"
export LASTFM_PASSWORD_HASH="your_password_hash"
```

For something permanent, put the same lines in a file such as `~/.config/local/lastfm.env`, run `chmod 600` on it, and add `[ -f ~/.config/local/lastfm.env ] && source ~/.config/local/lastfm.env` to your shell config (`~/.bashrc` on most Linux, `~/.zshrc` on macOS). That keeps secrets out of a public dotfiles repo.

**Windows, this PowerShell window only**

```powershell
$env:LASTFM_API_KEY = "your_api_key"
$env:LASTFM_API_SECRET = "your_api_secret"
$env:LASTFM_USERNAME = "your_username"
$env:LASTFM_PASSWORD_HASH = "your_password_hash"
```

To keep them, run `setx LASTFM_API_KEY "your_api_key"` (and the same for the others), then open a new window.

Check with `echo $LASTFM_USERNAME` (Linux, macOS) or `echo $env:LASTFM_USERNAME` (Windows).

## Quick start

```bash
python3 01_scan_library.py ~/Music                  # 1.  read your library
python3 01b_pick_plays.py --template                # 1b. write plays-template.csv
# open plays-template.csv, fill the "plays" column, save as CSV (UTF-8)
python3 02_make_scrobbles.py plays-template.csv     # 2.  build the scrobble file (shuffled)
python3 03_submit_scrobbles.py <file it printed>           # 3.  preview
python3 03_submit_scrobbles.py <file it printed> --send    #     send for real
```

Use the exact filename step 2 prints. On Windows, scan with the path to your music, for example `python 01_scan_library.py $HOME\Music`.

## Android (Termux)

The scripts are plain Python, so they run in [Termux](https://termux.dev/) without root. Install Termux from F-Droid or its GitHub releases; the Play Store build is outdated.

```bash
pkg update && pkg upgrade
pkg install python git

git clone https://github.com/itachi-re/lastfm-scrobbler.git
cd lastfm-scrobbler
pip install -r requirements.txt

termux-setup-storage                          # once, to reach shared storage
python 01_scan_library.py ~/storage/music
```

Put the `LASTFM_*` exports in `~/.bashrc` so you don't retype them (see [Setup, step 3](#3-set-your-credentials)). Everything after that works as on Linux, with `python` instead of `python3`.

On a phone the interactive picker (`python 01b_pick_plays.py`) or a hand-written `plays.txt` is easier than the spreadsheet. If you do use the template, edit it in a spreadsheet app and save it as CSV with UTF-8 encoding.

## Usage

### Step 1: scan your library

```bash
python3 01_scan_library.py ~/Music
python3 01_scan_library.py --filter kalafina      # print only matching rows
```

Walks the folder recursively, reads the tags, drops exact duplicates, sorts by artist and title, and numbers every track. The numbers are the `id` column in `library.csv`. It supports mp3, flac, m4a, ogg, opus, wav, wma, aac, ape and wv. It warns about tracks with no artist tag; fix those in your tagger first, because Last.fm needs an artist.

### Step 1b: say what you played

There are three ways. All of them leave unlisted songs at 0.

**A. Spreadsheet (best for big libraries)**

```bash
python3 01b_pick_plays.py --template
```

Open `plays-template.csv` in LibreOffice or Excel (on macOS, Numbers works too). Every song is there with a `plays` column of zeros; type a number next to each song you played. Sorting and filtering are fine, because each row carries its own `id`.

When you save, choose **CSV UTF-8** (in LibreOffice: Text CSV, UTF-8, comma-separated; in Numbers: File, Export To, CSV, with the text encoding set to Unicode UTF-8). Do not save as `.ods` or `.xlsx`, and do not use plain "CSV", or Japanese titles get mangled and step 2 can't read the file. If the `id` column shows `###`, the column is too narrow: widen it (this is display only).

**B. Interactive**

```bash
python3 01b_pick_plays.py
```

```
search> duvet          # shows matches with their #id
search> 47 5           # set #47 to 5 plays   (0 removes it)
search> list           # everything picked so far
search> done           # writes plays.txt
```

Running it again loads your existing `plays.txt`; `--fresh` ignores it.

**C. Write `plays.txt` by hand**, one song per line:

```
boa - duvet x5
mr. kitty - 0angel x10
alumina by nightmare x7      # "title by artist" also works
#57 x3                       # exact, by library id
kalafina - magia             # no count means 1 play
# lines starting with "# " are comments
```

Matching ignores case, accents and punctuation, and allows partial names. If a title is tagged in another script (say a Japanese title) the romanized name won't match; the error lists the closest candidates with their ids, so use `#id x7` instead.

### Step 2: build the scrobble file

```bash
python3 02_make_scrobbles.py plays-template.csv
```

Every line is resolved against `library.csv`. If anything is ambiguous or not found, nothing is written and you get the candidates to fix.

**Order.** Plays are shuffled on every build, so your history doesn't show one song repeated in a long block. Use `--seed N` for a repeatable shuffle, or `--no-shuffle` to keep each song's plays together.

**When the plays happened.** Plays are laid out back-to-back using each track's real duration, as one continuous block. By default the last play ends now. Otherwise pick one (times are local):

| Option | Meaning |
|---|---|
| `--end "2026-11-16 22:00"` | the last play ends then |
| `--start "2026-11-16 18:30"` | the first play starts then |
| `--days-ago 3` | the last play ends at this time of day, 3 days back |
| `--date 2026-11-14` | the last play ends at this time of day, on that date |

Use only one of them. The block is as long as the total listening time (about 4 minutes per play), so 1000 plays is roughly 2.8 days. The whole block must fit inside Last.fm's window; see [Limits to know](#limits-to-know). The summary shows the first and last time, so check it before moving on.

The output is `music-scrobble-<date>-<n>.csv`. `<date>` is the day the last play ends, and `<n>` counts up (0, 1, 2) so files never overwrite each other. Delete files you don't intend to send, so you don't pick the wrong one.

### Step 3: submit

```bash
python3 03_submit_scrobbles.py music-scrobble-2026-11-17-0.csv           # preview only
python3 03_submit_scrobbles.py music-scrobble-2026-11-17-0.csv --send    # really send
```

The preview validates and de-duplicates the file but never logs in. With `--send` the script logs in from your `LASTFM_*` variables and sends 50 scrobbles per request, pausing `--delay` seconds (default 5) between requests, so about 5 minutes for 2800 plays. After a fully successful run it writes `<file>.sent`; running the same file again is refused unless you add `--force`.

If Last.fm answers with a rate limit, the script waits and retries the same batch. If it still fails, it stops and prints the exact value to resume from:

```bash
python3 03_submit_scrobbles.py music-scrobble-2026-11-17-0.csv --send --skip 100
```

`--skip N` skips the first N scrobbles (oldest first). Use the number the script prints, and don't restart from the beginning, or the plays that already went through are sent twice.

After sending, check your Last.fm profile. The script can only tell what Last.fm accepted, not what it later ignored.

## Limits to know

- **14-day window.** Last.fm rejects scrobbles older than about 14 days or more than 2 hours in the future. Step 2 warns when the first play is too old, and step 3 skips such rows. For a long list, move the block later with `--end` or `--days-ago`, or use fewer plays.
- **Daily cap.** Last.fm limits how many scrobbles you can send per day. It doesn't publish the number; around 2800 is commonly reported. Stay well under it, and check your profile after a big send.
- **One block per file.** All plays in a run share one continuous time range. For plays on different days, make a separate plays file and run step 2 for each day.
- **Don't send overlapping files twice.** Each build gets new timestamps, so sending two builds of the same plays gives you duplicates on your profile. Last.fm has no bulk undo that this tool can call.

## Options

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
                     [--start T | --end T | --days-ago N | --date D]
                     [--no-shuffle] [--seed N]
    plays_file         plays.txt or a filled-in plays-template.csv
    --start, --end     "YYYY-MM-DD HH:MM", local time
    --days-ago N       last play ends at this time of day, N days back
    --date D           last play ends at this time of day on D (YYYY-MM-DD)
    --no-shuffle       keep each song's plays together (default is shuffled)
    --seed N           make the shuffle repeatable

03_submit_scrobbles.py file_path [--send] [--force] [--skip N] [--delay SEC]
    --send             actually submit (default is preview only)
    --force            submit even if a .sent marker exists
    --skip N           skip the first N scrobbles, to resume an interrupted send
    --delay SEC        pause between batches (default 5)

Exit codes (step 3): 0 success, 1 fatal error or nothing valid to send,
2 finished with failed batches or stopped early.

Environment (step 3 with --send):
    LASTFM_API_KEY  LASTFM_API_SECRET  LASTFM_USERNAME
    LASTFM_PASSWORD_HASH  (or LASTFM_PASSWORD)
```

## Scrobble CSV format

Step 2 writes this and step 3 reads it:

```csv
timeHuman,timeMs,artist,track,album,albumArtist,durationMs
2026-11-17 14:02:10 +0600,1794902530000,bôa,Duvet,Twilight,bôa,204306
```

Required: `artist`, `track`, `timeMs` (Unix milliseconds). Optional: `album`, `albumArtist`, `durationMs`. Other columns are ignored, so Pano Scrobbler exports work too.

## Troubleshooting

| Problem | Fix |
|---|---|
| `library.csv not found` | Run `01_scan_library.py` first |
| `WARNING: N track(s) have no artist tag` | Fix the tags in your tagger, then scan again |
| `not found` or `ambiguous` in step 2 | Use a more specific name, or `#id` from `library.csv`. The error lists candidates |
| Japanese titles show as `????` in the spreadsheet | Reopen the file as UTF-8 and save as **CSV UTF-8**, not `.ods` or `.xlsx` |
| `###` in the spreadsheet | The column is too narrow. Widen it; the data is fine |
| `unrecognized arguments: --days-ago` (or `--no-shuffle`) | Your copy of `02_make_scrobbles.py` is old. Update it |
| `WARNING: first play is older than 14 days` | Last.fm will reject it. Use a later `--end` or `--days-ago`, or fewer plays. Don't send that file |
| `No valid scrobbles to send` | Every row was outside the 14-day window, or the file is empty or malformed |
| `... exists - this file was already sent` | The `.sent` marker is working. Use `--force` only if you're sure |
| `Rate Limit Exceeded` | The script retries by itself. If it stops, wait a few minutes and rerun with the `--skip` value it prints. Raise `--delay` if it keeps happening |
| `Authentication failed` | Check username, API key and secret, and the password hash |
| `Missing environment variable(s)` | Set the `LASTFM_*` variables in this window |
| `externally-managed-environment` | Use a virtual environment (Setup, step 2) |
| `ModuleNotFoundError: mutagen` or `pylast` | Activate the virtual environment and run `pip install -r requirements.txt` |

## Project layout

```
lastfm-scrobbler/
|-- 01_scan_library.py        scan music folder -> library.csv
|-- 01b_pick_plays.py         plays-template.csv, or interactive picker -> plays.txt
|-- 02_make_scrobbles.py      plays file -> music-scrobble-<date>-<n>.csv
|-- 03_submit_scrobbles.py    preview / send to Last.fm
|-- requirements.txt
|-- CHANGELOG.md
`-- LICENSE
```

Generated files (`library.csv`, `plays.txt`, `plays-template.csv`, `music-scrobble-*.csv`, `*.sent`) and `.venv/` are git-ignored, because they describe your listening.

## License

[MIT](LICENSE). Built with [pylast](https://github.com/pylast/pylast) and [mutagen](https://mutagen.readthedocs.io/). The scrobble CSV stays compatible with [Pano Scrobbler](https://panoscrobbler.com/) exports.
