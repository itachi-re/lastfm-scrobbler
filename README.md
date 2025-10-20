# Last.fm Manual Scrobbler

[![GitHub Repo stars](https://img.shields.io/github/stars/itachi-re/lastfm-scrobbler?style=social)](https://github.com/itachi-re/lastfm-scrobbler/stars)
[![GitHub issues](https://img.shields.io/github/issues/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/issues)
[![GitHub license](https://img.shields.io/github/license/itachi-re/lastfm-scrobbler)](https://github.com/itachi-re/lastfm-scrobbler/blob/main/LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)

A simple Python script to manually upload missing listening data to Last.fm from a CSV file. Perfect for filling data gaps when your scrobbler fails!

## ✨ Features

- **Batch Upload**: Submit thousands of scrobbles in a single batch
- **Pano Scrobbler Compatible**: Works seamlessly with files from Pano Scrobbler
- **Rate Limit Safe**: Built-in delays to respect Last.fm's API limits
- **Error Handling**: Robust error handling with detailed logs
- **Progress Tracking**: Real-time progress updates during upload

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

**💡 Pro Tip**: Save your credentials securely in a `.env` file or password manager!

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

# 4. Run the scrobbler
python3 manual_scrobbler.py YOUR_API_KEY YOUR_API_SECRET YOUR_USERNAME YOUR_PASSWORD_HASH your_file.csv
```

### Example Command
```bash
python3 manual_scrobbler.py \
  c2ec6ca444b023c8b62c970a4f1bbc2e \
  0f2ca7559ec8f03f2e5bb3f2dc8e84d0 \
  itachi-re \
  767322d66b74474cff0eb25ce5fa31fe \
  generated_scrobbles_log_full.csv
```

## 📊 CSV Format

The script expects CSV files in **Pano Scrobbler format**:

```csv
timestamp,artist,title,album
1699123456,The Beatles,Hey Jude,The Beatles 1967-1970
1699123512,Radiohead,Karma Police,OK Computer
```

**Supported columns**: `timestamp`, `artist`, `title`, `album` (optional)

## ⚙️ Configuration Options

Create a `config.json` file for easier usage:

```json
{
  "api_key": "your_api_key",
  "api_secret": "your_api_secret", 
  "username": "your_username",
  "password_hash": "your_password_hash",
  "csv_file": "path/to/your/file.csv",
  "batch_size": 50,
  "delay_seconds": 1.2
}
```

Then run:
```bash
python3 manual_scrobbler.py --config config.json
```

## 🛡️ Rate Limiting

- **Default**: 50 scrobbles per batch, 1.2s delay between requests
- **Customizable**: Adjust via command line flags or config file
- **Safe**: Respects Last.fm's [API guidelines](https://www.last.fm/api/guidelines)

## 📈 Example Output

```
🚀 Starting Last.fm Manual Scrobbler
📁 Reading CSV file: generated_scrobbles_log_full.csv
✅ Loaded 1,247 scrobbles
📤 Uploading batch 1/25 (50 scrobbles)...
✅ Batch 1 uploaded successfully!
⏳ Waiting 1.2s before next batch...
📤 Uploading batch 2/25 (50 scrobbles)...
...
🎉 All 1,247 scrobbles uploaded successfully!
⏱️ Total time: 2m 34s
📊 Success rate: 100%
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| **`externally-managed-environment`** | Use virtual environment: `python3 -m venv venv` |
| **`TypeError: _Network.scrobble()`** | This script uses `scrobble_many()` - works correctly! |
| **`"Invalid API key"`** | Double-check your API key/secret from Last.fm |
| **`"User not authorized"`** | Verify username & password hash are correct |
| **Upload fails mid-way** | Check CSV format & internet connection |

## 🔧 Advanced Usage

```bash
# Custom batch size & delay
python3 manual_scrobbler.py [credentials] file.csv --batch-size 25 --delay 2.0

# Dry run (test without uploading)
python3 manual_scrobbler.py [credentials] file.csv --dry-run

# Verbose logging
python3 manual_scrobbler.py [credentials] file.csv --verbose

# Help
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
