#!/usr/bin/env python3
"""
Step 3 - send a music-scrobble-*.csv to Last.fm

Dry-run by default. Nothing is sent (and nothing logs in) unless you pass --send.
Only submit plays you actually listened to.

Credentials come from environment variables so they stay out of shell history:
    LASTFM_API_KEY, LASTFM_API_SECRET, LASTFM_USERNAME
    and either LASTFM_PASSWORD_HASH (md5) or LASTFM_PASSWORD (hashed for you)

    python3 03_submit_scrobbles.py music-scrobble-2026-11-17-0.csv           # preview
    python3 03_submit_scrobbles.py music-scrobble-2026-11-17-0.csv --send    # really send

After a fully successful send a "<file>.sent" marker is written so the same
file can't be submitted twice by accident (override with --force).

Last.fm throttles bursts, so batches are sent --delay seconds apart (default 5).
If Last.fm still says "rate limit", the script waits and retries the same batch,
and if that keeps failing it stops and tells you the --skip value to resume with:

    python3 03_submit_scrobbles.py music-scrobble-2026-11-15-0.csv --send --skip 100
"""
import argparse
import csv
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BATCH_SIZE = 50  # Last.fm accepts at most 50 per request
MAX_RETRIES = 3
RETRY_BACKOFF_SEC = 5
DEFAULT_DELAY_SEC = 5  # pause between batches so Last.fm doesn't throttle us
RATE_LIMIT_RETRIES = 4  # waits 60s, 120s, 180s, 240s before giving up
RATE_LIMIT_WAIT_SEC = 60
MAX_AGE_DAYS = 14
MAX_FUTURE_HOURS = 2

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("scrobbler")


def load(path):
    now = int(time.time())
    lo, hi = now - MAX_AGE_DAYS * 86400, now + MAX_FUTURE_HOURS * 3600
    out, seen = [], set()
    bad = old = dup = 0
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                artist, title = row["artist"].strip(), row["track"].strip()
                if not artist or not title:
                    raise ValueError
                ts = int(int(row["timeMs"]) / 1000)
            except (KeyError, ValueError, AttributeError):
                bad += 1
                continue
            if not lo <= ts <= hi:
                old += 1
                continue
            key = (artist.casefold(), title.casefold(), ts)
            if key in seen:
                dup += 1
                continue
            seen.add(key)
            item = {"artist": artist, "title": title, "timestamp": ts}
            if row.get("album", "").strip():
                item["album"] = row["album"].strip()
            if row.get("albumArtist", "").strip():
                item["album_artist"] = row["albumArtist"].strip()
            if row.get("durationMs", "").isdigit():
                item["duration"] = int(row["durationMs"]) // 1000
            out.append(item)
    if bad:
        log.warning("Skipped %d invalid row(s)", bad)
    if old:
        log.warning("Skipped %d row(s) outside Last.fm's window (older than %d days / >%dh ahead)", old, MAX_AGE_DAYS, MAX_FUTURE_HOURS)
    if dup:
        log.warning("Skipped %d duplicate row(s)", dup)
    out.sort(key=lambda x: x["timestamp"])
    return out


def is_rate_limit(err):
    return str(getattr(err, "status", "")) == "29" or "rate limit" in str(err).lower()


def send(network, scrobbles, pylast, delay=DEFAULT_DELAY_SEC):
    """Returns (sent, failed, stopped_at). stopped_at is the row offset to resume from, or None."""
    batches = [scrobbles[i:i + BATCH_SIZE] for i in range(0, len(scrobbles), BATCH_SIZE)]
    sent = failed = 0
    for i, batch in enumerate(batches, start=1):
        net_tries = rl_tries = 0
        while True:
            try:
                network.scrobble_many(batch)
                sent += len(batch)
                log.info("Batch %d/%d ok (%d/%d)", i, len(batches), sent, len(scrobbles))
                break
            except pylast.WSError as e:
                if is_rate_limit(e):
                    rl_tries += 1
                    if rl_tries > RATE_LIMIT_RETRIES:
                        log.error("Batch %d still rate limited after %d waits, stopping.", i, RATE_LIMIT_RETRIES)
                        return sent, failed, (i - 1) * BATCH_SIZE
                    wait = RATE_LIMIT_WAIT_SEC * rl_tries
                    log.warning("Batch %d rate limited, waiting %ds (retry %d/%d)", i, wait, rl_tries, RATE_LIMIT_RETRIES)
                    time.sleep(wait)
                    continue
                log.error("Batch %d rejected by Last.fm: %s", i, e)
                failed += 1
                break
            except (pylast.NetworkError, pylast.MalformedResponseError) as e:
                net_tries += 1
                log.warning("Batch %d attempt %d/%d failed: %s", i, net_tries, MAX_RETRIES, e)
                if net_tries < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SEC * net_tries)
                    continue
                failed += 1
                break
        if delay and i < len(batches):
            time.sleep(delay)
    return sent, failed, None


def main():
    ap = argparse.ArgumentParser(description="Submit a scrobble CSV to Last.fm (dry-run unless --send)")
    ap.add_argument("file_path")
    ap.add_argument("--send", action="store_true", help="actually submit (default is preview only)")
    ap.add_argument("--skip", type=int, default=0, metavar="N",
                    help="skip the first N scrobbles (oldest first), e.g. to resume an interrupted send")
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY_SEC, metavar="SEC",
                    help="seconds to pause between batches (default %(default)s)")
    ap.add_argument("--force", action="store_true", help="submit even if a .sent marker exists")
    args = ap.parse_args()

    marker = Path(args.file_path + ".sent")
    if args.send and marker.exists() and not args.force:
        sys.exit(f"{marker} exists - this file was already sent. Use --force to override.")

    try:
        scrobbles = load(args.file_path)
    except FileNotFoundError:
        sys.exit(f"File not found: {args.file_path}")
    if args.skip:
        log.info("Skipping the first %d scrobble(s) as requested", args.skip)
        scrobbles = scrobbles[args.skip:]
    if not scrobbles:
        sys.exit("No valid scrobbles to send.")

    first = datetime.fromtimestamp(scrobbles[0]["timestamp"], tz=timezone.utc)
    last = datetime.fromtimestamp(scrobbles[-1]["timestamp"], tz=timezone.utc)
    log.info("%d valid scrobble(s), %s -> %s UTC", len(scrobbles), first.strftime("%Y-%m-%d %H:%M"), last.strftime("%Y-%m-%d %H:%M"))

    if not args.send:
        log.info("Preview only (no --send). First 5:")
        for s in scrobbles[:5]:
            log.info("  %s - %s @ %d", s["artist"], s["title"], s["timestamp"])
        return

    import pylast  # imported late so preview works without it

    env = os.environ
    key, secret, user = env.get("LASTFM_API_KEY"), env.get("LASTFM_API_SECRET"), env.get("LASTFM_USERNAME")
    pw_hash = env.get("LASTFM_PASSWORD_HASH") or (pylast.md5(env["LASTFM_PASSWORD"]) if env.get("LASTFM_PASSWORD") else None)
    missing = [n for n, v in [("LASTFM_API_KEY", key), ("LASTFM_API_SECRET", secret), ("LASTFM_USERNAME", user), ("LASTFM_PASSWORD_HASH or LASTFM_PASSWORD", pw_hash)] if not v]
    if missing:
        sys.exit("Missing environment variable(s): " + ", ".join(missing))

    try:
        network = pylast.LastFMNetwork(api_key=key, api_secret=secret, username=user, password_hash=pw_hash)
    except (pylast.NetworkError, pylast.WSError) as e:
        sys.exit(f"Authentication failed: {e}")

    sent, failed, stopped_at = send(network, scrobbles, pylast, args.delay)
    if stopped_at is not None:
        log.error("Stopped early: %d sent this run. Wait a while, then resume with: --send --skip %d",
                  sent, args.skip + stopped_at)
        sys.exit(2)
    if failed:
        log.warning("Finished with errors: %d sent, %d batch(es) failed.", sent, failed)
        sys.exit(2)
    marker.write_text(f"sent {sent} scrobbles (skipped first {args.skip}) at {datetime.now().isoformat()}\n")
    log.info("Done, %d scrobble(s) submitted.", sent)


if __name__ == "__main__":
    main()
