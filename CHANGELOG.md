# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions are dates in
`YYMMDD` form (for example `261117` is 2026-11-17).

## [Unreleased]

## [261117] - 2026-11-17

A rewrite around a four-step workflow: **scan your library, choose what you played,
build a scrobble file, submit it.** The old single-script usage and the synthetic
data generators are gone, so this release is not backward compatible.

### Added
- `01_scan_library.py`: scans a music folder recursively with `mutagen` and writes `library.csv` (`id`, `artist`, `title`, `album`, `albumArtist`, `durationMs`, `path`). Supports mp3, flac, m4a, ogg, opus, wav, wma, aac, ape and wv. Results are sorted, numbered and de-duplicated, with a warning for tracks that have no artist tag. `--filter` prints only matching rows.
- `01b_pick_plays.py`: two ways to say which songs you played and how many times, with everything else staying at 0.
  - `--template` writes `plays-template.csv`, every song with a `plays` column of zeros, to fill in with a spreadsheet editor.
  - An interactive picker with search, `<id> <count>` entry, `list` and `done`, which writes `plays.txt` and resumes from an existing one (`--fresh` to ignore it).
- `02_make_scrobbles.py`: turns a plays file (`plays.txt` or the filled-in template CSV) into `music-scrobble-<date>-<n>.csv`, with the counter increasing so files never overwrite each other.
  - Free-form `plays.txt` lines: `artist - title xN`, `title by artist xN`, `#id xN`, and `# comments`.
  - Name matching that ignores case, accents and punctuation and allows partial names. Ambiguous or unknown names abort the run, write nothing, and list the closest candidates with their ids.
  - Timestamps laid back-to-back using each track's real duration. By default the last play ends now; `--start` / `--end` place them elsewhere, and `--shuffle` / `--seed` control the order.
  - Warnings when plays fall outside Last.fm's accepted window.
- `03_submit_scrobbles.py`: the submission step, merging and replacing the old `manual_scrobbler.py`.
  - **Preview by default.** Nothing is sent and nothing logs in unless `--send` is passed.
  - A `<file>.sent` marker written after a fully successful send, so the same file isn't submitted twice by accident (`--force` overrides it).
  - Credentials read from `LASTFM_API_KEY`, `LASTFM_API_SECRET`, `LASTFM_USERNAME`, and either `LASTFM_PASSWORD_HASH` or `LASTFM_PASSWORD` (hashed for you).
  - Album artist and track duration are now submitted along with artist, title, album and timestamp.
  - Authentication failures (`NetworkError` and `WSError`) are caught and reported cleanly instead of producing a traceback.
- Batching into groups of 50 (Last.fm's per-call limit) with per-batch progress logging, up to 3 retries with backoff for transient network errors, pre-submission timestamp validation (older than 14 days or more than 2 hours ahead), de-duplication of identical artist/title/timestamp rows, and distinct exit codes (`0` success, `1` fatal error or no valid data, `2` finished with failed batches).
- `.gitignore` entries for generated, personal data: `library.csv`, `plays.txt`, `plays-template.csv`, `music-scrobble-*.csv`, `*.sent`.

### Changed
- `README.md` rewritten for the new workflow, with a pipeline diagram, per-step instructions, an options reference, a refreshed troubleshooting table, and a responsible-use note. Minimum Python raised to 3.8 to match current `mutagen`, and the virtual environment folder is now `.venv`.
- `requirements.txt` now lists `mutagen` and `pylast`.
- Scrobble CSVs are read with `utf-8-sig`, so BOM-prefixed exports from Windows tools still work. Pano Scrobbler CSVs remain compatible (`artist`, `track`, `timeMs`, optional `album`).
- Empty artist or track fields are rejected instead of producing malformed scrobbles.

### Removed
- `manual_scrobbler.py`, replaced by `03_submit_scrobbles.py`. Positional credential arguments are gone, so use environment variables.
- `generate.py` and `generate_test_fixture.py`, replaced by building scrobble files from your real library. The hardcoded song lists are no longer needed.
- `music-metadata.sh`, replaced by `01_scan_library.py`, which is recursive, handles missing tags without inventing an artist, escapes all text safely, and outputs the CSV the later steps read.
- Support for a plain `timestamp` (seconds) column. Scrobble files now use `timeMs`.
- Hardcoded example credentials from the README.

### Fixed
- Oversized single `scrobble_many()` calls that could fail or partially submit on large inputs are chunked to the API limit.
- `WSError` rejections (for example invalid timestamps) are distinguished from transient `NetworkError`s, so retries aren't wasted on requests that can never succeed.
- Overlapping or colliding timestamps from the old generators can no longer occur, because every play is laid out sequentially after the previous one.

## [250904] - 2025-09-04 - Initial release

### Added
- `manual_scrobbler.py`: submit scrobbles to Last.fm in bulk from a Pano Scrobbler-style CSV export, using `pylast`.
- Basic CSV parsing keyed on `timeMs`, with `artist`, `track`, and optional `album` columns.
- Single-batch submission via `network.scrobble_many()`.
- Baseline error handling for `pylast.NetworkError` and `pylast.WSError`, including a specific message for invalid-timestamp rejections.

[Unreleased]: https://github.com/itachi-re/lastfm-scrobbler/compare/v261117...HEAD
[261117]: https://github.com/itachi-re/lastfm-scrobbler/compare/v250904...v261117
[250904]: https://github.com/itachi-re/lastfm-scrobbler/releases/tag/v250904
