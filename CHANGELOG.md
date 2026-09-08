# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `music-metadata.sh`: a standalone Bash script that scans a music directory (FLAC, M4A, MP3, WAV) and outputs a JSON array of track metadata (title, artist, album, duration in milliseconds). Supports reading tags from both `format.tags` and `streams[0].tags`, and falls back to "Unknown" when tags are missing. Includes a `-v` / `--verbose` flag for real‑time progress logging to stderr without polluting the JSON output. Useful for cataloguing a music library before filtering or feeding into the Last.fm scrobbler pipeline.
- `--dry-run` flag on `manual_scrobbler.py` to validate and preview a CSV without submitting anything.
- Support for reading Last.fm credentials from environment variables (`LASTFM_API_KEY`, `LASTFM_API_SECRET`, `LASTFM_USERNAME`, `LASTFM_PASSWORD_HASH`) as an alternative to command-line flags, so they no longer need to appear in shell history or `ps` output.
- Automatic batching of scrobble submissions into groups of 50 (Last.fm's `track.scrobble` API limit per call), with per-batch progress logging.
- Retry with exponential backoff (up to 3 attempts) for transient network errors during submission.
- Pre-submission timestamp validation: rows older than 14 days or more than 2 hours in the future are filtered out before hitting the API, with a summary count of how many were skipped and why.
- De-duplication of rows with identical artist/title/timestamp.
- Support for a plain `timestamp` (seconds) column as an alternative to `timeMs` (milliseconds).
- `generate_test_fixture.py`, a new local-only dev tool for generating synthetic scrobble CSVs to exercise `manual_scrobbler.py` against, with configurable start date, day count, plays-per-day, timezone offset, shuffling, and a random seed for reproducibility. Output is explicitly named and labeled as test fixture data, and is never intended for submission to a real Last.fm account.
- Distinct process exit codes: `0` (success), `1` (no valid data / fatal error), `2` (completed with one or more failed batches), for easier use in scripts/cron.

### Changed
- Replaced manual `sys.argv` parsing with `argparse`, adding `--help` output and named flags (`--api-key`, `--api-secret`, `--username`, `--password-hash`) in place of strictly ordered positional arguments.
- Replaced ad hoc `print()` statements with the standard `logging` module (timestamped, leveled output).
- CSV reading now uses `utf-8-sig` to correctly handle BOM-prefixed exports from Windows-based tools.
- Empty artist/track fields are now explicitly rejected instead of silently producing malformed scrobbles.

### Fixed
- Single oversized `scrobble_many()` calls (previously unbounded) that could silently fail or partially submit on large CSVs are now chunked to stay within the API's per-call limit.
- `WSError` API rejections (e.g. invalid timestamp) are now distinguished from transient `NetworkError`s so the script no longer wastes retries on requests that will never succeed.

### Fixture generator: bug notes (relative to the original ad hoc script)
- Fixed a day-wraparound bug where overflowing a day's worth of plays reset the clock to midnight and produced colliding/duplicate timestamps instead of continuing forward in time.
- Replaced the Linux/macOS-only `%-d` strftime directive with the portable `%d`.
- Made `num_days`, `plays_per_day`, `start_date`, and timezone offset actual CLI parameters instead of hardcoded constants.
- Renamed default output from `scrobble_log.csv` to `test_fixture_scrobbles.csv` to reduce the risk of it being confused with, or fed directly into, a real submission path.

## [1.0.0] - Initial release

### Added
- `manual_scrobbler.py`: submit scrobbles to Last.fm in bulk from a Pano Scrobbler-style CSV export, using `pylast`.
- Basic CSV parsing keyed on `timeMs`, with `artist`, `track`, and optional `album` columns.
- Single-batch submission via `network.scrobble_many()`.
- Baseline error handling for `pylast.NetworkError` and `pylast.WSError`, including a specific message for invalid-timestamp rejections.

[Unreleased]: https://github.com/itachi-re/lastfm-scrobbler/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/itachi-re/lastfm-scrobbler/releases/tag/v1.0.0
