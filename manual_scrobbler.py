#!/usr/bin/env python3
"""
manual_scrobbler.py

Submit historical scrobbles to Last.fm from a CSV export (e.g. Spotify/YouTube
Music history) using pylast.

Usage:
    python manual_scrobbler.py --username USER --password-hash HASH FILE.csv
    python manual_scrobbler.py FILE.csv   (reads credentials from env vars)

Credentials can be supplied via flags or via environment variables so they
don't end up in your shell history / process list:
    LASTFM_API_KEY, LASTFM_API_SECRET, LASTFM_USERNAME, LASTFM_PASSWORD_HASH

CSV columns expected (case-sensitive):
    artist, track, timeMs (or timestamp, in seconds), album (optional)
"""

import argparse
import csv
import logging
import os
import sys
import time
from datetime import datetime, timezone

import pylast

BATCH_SIZE = 50  # Last.fm's track.scrobble API accepts at most 50 per batch
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 5

# Last.fm rejects scrobbles with a timestamp more than ~14 days in the past
# or more than 2 hours in the future.
MAX_AGE_DAYS = 14
MAX_FUTURE_HOURS = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scrobbler")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Bulk-submit scrobbles to Last.fm from a CSV file."
    )
    parser.add_argument("file_path", help="Path to the CSV file of scrobbles")
    parser.add_argument("--api-key", default=os.environ.get("LASTFM_API_KEY"))
    parser.add_argument("--api-secret", default=os.environ.get("LASTFM_API_SECRET"))
    parser.add_argument("--username", default=os.environ.get("LASTFM_USERNAME"))
    parser.add_argument(
        "--password-hash",
        default=os.environ.get("LASTFM_PASSWORD_HASH"),
        help="MD5 hash of your Last.fm password (pylast.md5('plaintext'))",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate the CSV but do not submit anything",
    )
    args = parser.parse_args()

    missing = [
        name
        for name, val in [
            ("api-key", args.api_key),
            ("api-secret", args.api_secret),
            ("username", args.username),
            ("password-hash", args.password_hash),
        ]
        if not val
    ]
    if missing:
        parser.error(
            f"Missing required credential(s): {', '.join(missing)}. "
            "Pass as flags or set the corresponding LASTFM_* environment variable."
        )
    return args

def load_scrobbles(file_path):
    """Read, validate, and de-duplicate scrobbles from the CSV file."""
    now = int(time.time())
    min_ts = now - MAX_AGE_DAYS * 86400
    max_ts = now + MAX_FUTURE_HOURS * 3600

    scrobbles = []
    seen = set()
    skipped_invalid = 0
    skipped_out_of_range = 0
    skipped_duplicate = 0

    try:
        with open(file_path, mode="r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    artist = row["artist"].strip()
                    title = row["track"].strip()
                    if not artist or not title:
                        raise ValueError("empty artist/track")

                    if row.get("timeMs"):
                        timestamp = int(int(row["timeMs"]) / 1000)
                    elif row.get("timestamp"):
                        timestamp = int(row["timestamp"])
                    else:
                        raise KeyError("timeMs/timestamp")

                except (ValueError, KeyError, AttributeError):
                    skipped_invalid += 1
                    log.debug("Skipping invalid row: %s", row)
                    continue

                if not (min_ts <= timestamp <= max_ts):
                    skipped_out_of_range += 1
                    continue

                key = (artist.lower(), title.lower(), timestamp)
                if key in seen:
                    skipped_duplicate += 1
                    continue
                seen.add(key)

                scrobbles.append(
                    {
                        "artist": artist,
                        "title": title,
                        "timestamp": timestamp,
                        "album": row.get("album", "").strip(),
                    }
                )
    except FileNotFoundError:
        log.error("File not found: %s", file_path)
        sys.exit(1)
    except UnicodeDecodeError as e:
        log.error("Could not decode file as UTF-8: %s", e)
        sys.exit(1)

    scrobbles.sort(key=lambda x: x["timestamp"])

    if skipped_invalid:
        log.warning("Skipped %d row(s) with missing/invalid data", skipped_invalid)
    if skipped_out_of_range:
        log.warning(
            "Skipped %d row(s) outside Last.fm's accepted timestamp window "
            "(older than %d days or more than %dh in the future)",
            skipped_out_of_range,
            MAX_AGE_DAYS,
            MAX_FUTURE_HOURS,
        )
    if skipped_duplicate:
        log.warning("Skipped %d duplicate row(s)", skipped_duplicate)

    return scrobbles

def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]

def submit_scrobbles(network, scrobbles):
    total = len(scrobbles)
    batches = list(chunked(scrobbles, BATCH_SIZE))
    submitted = 0
    failed_batches = 0

    for i, batch in enumerate(batches, start=1):
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                network.scrobble_many(batch)
                submitted += len(batch)
                log.info(
                    "Batch %d/%d submitted (%d/%d scrobbles total)",
                    i,
                    len(batches),
                    submitted,
                    total,
                )
                break
            except pylast.WSError as e:
                if "Invalid timestamp" in str(e):
                    log.error(
                        "Batch %d rejected: invalid timestamp(s). Last.fm only "
                        "accepts scrobbles from the last %d days.",
                        i,
                        MAX_AGE_DAYS,
                    )
                else:
                    log.error("Batch %d rejected by Last.fm API: %s", i, e)
                failed_batches += 1
                break  # WSError is not transient; retrying won't help
            except (pylast.NetworkError, pylast.MalformedResponseError) as e:
                log.warning(
                    "Batch %d failed (attempt %d/%d): %s",
                    i,
                    attempt,
                    MAX_RETRIES,
                    e,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SEC * attempt)
                else:
                    log.error("Batch %d failed after %d attempts, giving up.", i, MAX_RETRIES)
                    failed_batches += 1

    return submitted, failed_batches

def main():
    args = parse_args()

    scrobbles = load_scrobbles(args.file_path)
    if not scrobbles:
        log.error("No valid scrobbles found in the file.")
        sys.exit(1)

    first = datetime.fromtimestamp(scrobbles[0]["timestamp"], tz=timezone.utc)
    last = datetime.fromtimestamp(scrobbles[-1]["timestamp"], tz=timezone.utc)
    log.info(
        "Found %d valid scrobble(s) spanning %s to %s (UTC)",
        len(scrobbles),
        first.strftime("%Y-%m-%d %H:%M"),
        last.strftime("%Y-%m-%d %H:%M"),
    )

    if args.dry_run:
        log.info("Dry run requested, not submitting. Sample of first 5 rows:")
        for s in scrobbles[:5]:
            log.info("  %s - %s @ %d", s["artist"], s["title"], s["timestamp"])
        return

    try:
        network = pylast.LastFMNetwork(
            api_key=args.api_key,
            api_secret=args.api_secret,
            username=args.username,
            password_hash=args.password_hash,
        )
    except pylast.NetworkError as e:
        log.error("Authentication failed: %s", e)
        sys.exit(1)

    submitted, failed_batches = submit_scrobbles(network, scrobbles)

    if failed_batches:
        log.warning(
            "Finished with errors: %d scrobble(s) submitted, %d batch(es) failed.",
            submitted,
            failed_batches,
        )
        sys.exit(2)

    log.info("Done! %d scrobble(s) submitted successfully.", submitted)

if __name__ == "__main__":
    main()
