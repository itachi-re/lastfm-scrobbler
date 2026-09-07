# Last.fm Manual Scrobbler

[![GitHub Repo stars](https://img.shields.io/github/stars/itachi-re/lastfm-scrobbler?style=social)](https://github.com/itachi-re/lastfm-scrobbler/stars)
[![GitHub issues](https://img.shields.io/github/issues/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/issues)
[![GitHub license](https://img.shields.io/github/license/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/blob/main/LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)

A simple Python script to manually upload missing listening data to Last.fm from a CSV file. Perfect for filling data gaps when your scrobbler fails!

## ✨ Features

- **Batch upload**: submits in batches of 50 (Last.fm's API limit per `scrobble_many` call), with automatic retry on transient network errors
- **Pano Scrobbler compatible**: works with `timeMs` (milliseconds) or plain `timestamp` (seconds) export columns
- **Timestamp validation**: rows older than 14 days or more than 2 hours in the future are rejected up front — Last.fm won't accept them anyway, so they're filtered before upload with a clear warning instead of failing a whole batch
- **De-duplication**: identical artist/title/timestamp rows are automatically skipped
- **Dry-run mode**: validate and preview your CSV without submitting anything
- **Credentials via environment variables**: keep your API key and password hash out of shell history
- **Progress + error logging**: per-batch status via Python's `logging` module, with distinct exit codes for scripting/cron use

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

```python
import hashlib
password = "your_actual_password"
password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
print(password_hash)  # Copy this 32-character string
```

**💡 Pro tip**: export your credentials as environment variables instead of passing them as flags — they won't leak into your shell history or `ps` output:

```bash
export LASTFM_API_KEY="your_api_key"
export LASTFM_API_SECRET="your_api_secret"
export LASTFM_USERNAME="your_username"
export LASTFM_PASSWORD_HASH="your_password_hash"
```

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

# 4. Run the scrobbler (using env vars set above)
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

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| **`externally-managed-environment`** | Use a virtual environment: `python3 -m venv venv` |
| **`Missing required credential(s)`** | Pass all four credentials as flags, or set the matching `LASTFM_*` env var |
| **`"Invalid API key"`** | Double-check your API key/secret from Last.fm |
| **`"User not authorized"`** | Verify your username & password hash are correct |
| **Rows skipped as "out of range"** | Last.fm only accepts scrobbles from the last 14 days — older listens can't be backfilled this way |
| **Upload fails mid-way** | Check your CSV formatting and internet connection; failed batches are logged with the batch number so you can isolate the issue |

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

⭐ **Star this repo if it helped fill your Last.fm gaps!**

**Made with ❤️ for music lovers** 🎵

---

<div align="center">
  <sub>Built by <a href="https://github.com/itachi-re">@itachi-re</a> | Questions? Open an <a href="https://github.com/itachi-re/lastfm-scrobbler/issues/new">issue</a></sub>
</div>
