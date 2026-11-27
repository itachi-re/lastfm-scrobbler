# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions are dates in
`YYMMDD` form (for example `261117` is 2026-11-17).

## [Unreleased]

## [261125] - 2026-11-25

Scheduling and reliability. Nothing here breaks the 261117 workflow: every new
option is optional, and the only behaviour change is the default shuffle.

### Added
- `last_nightly.sh`: automates steps 2 and 3 for a nightly timer. It builds yesterday's file with `02_make_scrobbles.py plays-template.csv --days-ago 1`, then sends it with `03_submit_scrobbles.py --send`. Steps 1 and 1b stay manual.
  - Skips the run when every `plays` count in the template is 0.
  - Sends the template every night, whether or not it changed since the last run.
  - On a rate limit, waits 15 minutes and resumes from the `--skip` value the submit step prints, up to 3 attempts.
  - Runs from its own folder and calls `.venv/bin/python` directly, so it does not depend on `activate` or on where the project lives.
  - Logs to `nightly.log`. Needs Linux (GNU `grep -P`).
- `02_make_scrobbles.py`: `--days-ago N` and `--date YYYY-MM-DD` place the plays so the last one ends at the current time of day, N days back or on that date. Only one of `--start`, `--end`, `--days-ago`, `--date` may be used at a time.
- `03_submit_scrobbles.py`:
  - `--skip N` skips the first N scrobbles (oldest first) to resume an interrupted send.
  - `--delay SEC` pauses between batches (default 5) so Last.fm does not throttle bursts.
  - Rate-limit handling: on `Rate Limit Exceeded` the same batch is retried after 60, 120, 180 and 240 seconds. If it still fails, the script stops and prints the exact `--skip` value to resume with.
- README sections for the nightly run (systemd user timer, env file for the timer, cron alternative), Limits to know, Windows and macOS install and credentials, and Android (Termux).
- `.gitignore` entries for the nightly run's generated files: `nightly.log`, `.submit.out`.

### Changed
- `02_make_scrobbles.py`: plays are shuffled on every build by default. Use `--no-shuffle` to keep each song's plays together and `--seed N` for a repeatable shuffle. The old `--shuffle` flag is still accepted (hidden from help) and has no effect.
- `02_make_scrobbles.py`: the `<date>` in `music-scrobble-<date>-<n>.csv` is now the day the last play ends, not the day the script was run, so files built with `--days-ago` or `--date` are named for the day the plays belong to.
- `03_submit_scrobbles.py`: exit code `2` now also covers a send that stopped early because of rate limiting (previously it meant only that some batches failed).
- `README.md` rewritten: new header with platform badges, nightly automation, command-line reference for every current option and exit code, a `getpass`-based password hash command that keeps the password out of shell history, and a longer troubleshooting table.
- README no longer states a fixed daily scrobble cap. Last.fm does not publish one, and large single sends are throttled well before any daily limit.

### Fixed
- A rate-limit response no longer fails the whole batch: it is waited out and retried, and a send that cannot finish can be resumed without re-sending what already went through.
- Documented why a project folder cannot simply be moved: the virtual environment stores absolute paths, so `activate` breaks and `pylast` appears to be missing. The README troubleshooting table now says to delete `.venv` and recreate it.

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

[Unreleased]: https://github.com/itachi-re/lastfm-scrobbler/compare/v261125...HEAD
[261125]: https://github.com/itachi-re/lastfm-scrobbler/compare/v261117...v261125
[261117]: https://github.com/itachi-re/lastfm-scrobbler/compare/v250904...v261117
[250904]: https://github.com/itachi-re/lastfm-scrobbler/releases/tag/v250904
