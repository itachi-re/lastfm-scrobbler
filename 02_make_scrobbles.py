#!/usr/bin/env python3
"""
Step 2 - turn your play list into music-scrobble-<date>-<n>.csv

Input is plays.txt (from 01b_pick_plays.py, or typed by hand) or the filled-in
plays-template.csv from 01b_pick_plays.py --template. In a txt file, one song per
line, any of these styles:

    boa - duvet x5
    mr. kitty - 0 angel x10
    alumina by nightmare x7        # "title by artist"
    #57 x3                         # library id from library.csv / step 1
    kalafina - magia               # no count = 1 play

Matching ignores case, accents and punctuation, and allows partial names.
If a line is ambiguous or not found, nothing is written and you get candidates.

Timestamps: plays are laid back-to-back using each track's real duration.
  default        the last play ends right now
  --end   "2026-11-17 18:30"   last play ends then
  --start "2026-11-17 14:00"   first play starts then

    python3 02_make_scrobbles.py plays.txt
    python3 02_make_scrobbles.py plays.txt --shuffle --seed 1
"""
import argparse
import csv
import random
import re
import sys
import unicodedata
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path

MAX_AGE_DAYS = 14  # Last.fm rejects older scrobbles


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s.casefold())
    return re.sub(r"\s+", " ", s).strip()


def compact(s):
    return norm(s).replace(" ", "")


def sim(q, target):
    q, target = compact(q), compact(target)
    if not q or not target:
        return 0.0
    if q == target:
        return 1.0
    if len(q) >= 3 and q in target:
        return 0.92
    return SequenceMatcher(None, q, target).ratio()


def load_library(path):
    try:
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        sys.exit(f"{path} not found - run 01_scan_library.py first.")
    for r in rows:
        r["id"] = int(r["id"])
        r["durationMs"] = int(r["durationMs"])
    return rows


def parse_line(line):
    """-> (artist, title, library_id, count)"""
    count = 1
    m = re.search(r"\s*[x×*]\s*(\d+)\s*$", line, flags=re.I)
    if m:
        count = int(m.group(1))
        line = line[: m.start()]
    line = line.strip()
    m = re.fullmatch(r"#(\d+)", line)
    if m:
        return "", "", int(m.group(1)), count
    if " - " in line:
        artist, title = line.split(" - ", 1)
    elif re.search(r"\s+by\s+", line, flags=re.I):
        title, artist = re.split(r"\s+by\s+", line, maxsplit=1, flags=re.I)
    else:
        artist, title = "", line
    return artist.strip(), title.strip(), None, count


def score(row, qa, qt):
    ts = sim(qt, row["title"])
    if not qa:
        return ts
    asim = max(sim(qa, row["artist"]), sim(qa, row["albumArtist"]))
    if asim < 0.6:
        return 0.0
    return ts * 0.7 + asim * 0.3


def resolve(lib, artist, title, lib_id):
    if lib_id is not None:
        for r in lib:
            if r["id"] == lib_id:
                return r, None
        return None, f"no track with id #{lib_id}"
    ranked = sorted(((score(r, artist, title), r) for r in lib), key=lambda x: -x[0])
    ranked = [x for x in ranked if x[0] > 0]
    show = lambda rs: "\n".join(f'      #{r["id"]}  {r["artist"]} - {r["title"]}  [{r["album"]}]' for _, r in rs[:5])
    if not ranked or ranked[0][0] < 0.8:
        hint = ("\n    closest:\n" + show(ranked)) if ranked else ""
        return None, "not found (if the tag is in Japanese etc., use #id or the tagged title)" + hint
    best = ranked[0]
    rivals = [
        x for x in ranked[1:]
        if x[0] >= best[0] - 0.03
        and (norm(x[1]["artist"]), norm(x[1]["title"])) != (norm(best[1]["artist"]), norm(best[1]["title"]))
    ]
    if rivals:
        return None, "ambiguous, use a more specific name or #id:\n" + show([best] + rivals)
    return best[1], None


def iter_plays(path):
    """Yield (label, artist, title, lib_id, count). count is None if unparseable."""
    p = Path(path)
    if p.suffix.lower() == ".csv":  # spreadsheet from 01b_pick_plays.py --template
        with open(p, encoding="utf-8-sig", newline="") as f:
            for n, row in enumerate(csv.DictReader(f), start=2):
                raw = (row.get("plays") or "").strip()
                if raw in ("", "0"):
                    continue
                label = f"row {n} ({row.get('artist', '')} - {row.get('title', '')})"
                try:
                    yield label, "", "", int(row["id"]), int(float(raw))
                except (KeyError, ValueError):
                    yield label, "", "", None, None
        return
    for n, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line or (line.startswith("#") and not re.match(r"#\d", line)):
            continue  # blank line or "# comment"
        line = re.sub(r"\s+#(?!\d).*$", "", line)  # trailing "  # comment"
        artist, title, lib_id, count = parse_line(line)
        yield f"line {n}: '{raw.strip()}'", artist, title, lib_id, count


def parse_time(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M").astimezone()


def next_filename(out_dir, today):
    n = 0
    while True:
        p = out_dir / f"music-scrobble-{today}-{n}.csv"
        if not p.exists():
            return p
        n += 1


def main():
    ap = argparse.ArgumentParser(description="Build a scrobble CSV from plays.txt")
    ap.add_argument("plays_file")
    ap.add_argument("--library", default="library.csv")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--start", type=parse_time, help='first play starts at "YYYY-MM-DD HH:MM" (local time)')
    ap.add_argument("--end", type=parse_time, help='last play ends at "YYYY-MM-DD HH:MM" (local time)')
    ap.add_argument("--shuffle", action="store_true", help="shuffle the expanded play order")
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()
    if args.start and args.end:
        sys.exit("Use --start or --end, not both.")

    lib = load_library(args.library)
    playlist, problems = [], []
    for label, artist, title, lib_id, count in iter_plays(args.plays_file):
        if count is None:
            problems.append(f"{label}: could not read id/plays")
            continue
        if count == 0:
            continue
        row, err = resolve(lib, artist, title, lib_id)
        if err:
            problems.append(f"{label}: {err}")
            continue
        print(f'  {count:>3} x  {row["artist"]} - {row["title"]}')
        playlist.extend([row] * count)

    if problems:
        print("\nFix these and run again (nothing written):", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        sys.exit(1)
    if not playlist:
        sys.exit("plays file is empty.")

    if args.shuffle:
        random.Random(args.seed).shuffle(playlist)

    total = timedelta(milliseconds=sum(r["durationMs"] for r in playlist))
    now = datetime.now().astimezone()
    start = args.start or ((args.end or now) - total)
    end = start + total

    if start < now - timedelta(days=MAX_AGE_DAYS):
        print(f"\nWARNING: first play is older than {MAX_AGE_DAYS} days; Last.fm will reject it.", file=sys.stderr)
    if end > now + timedelta(hours=2):
        print("\nWARNING: plays end more than 2h in the future; Last.fm will reject them.", file=sys.stderr)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = next_filename(out_dir, now.strftime("%Y-%m-%d"))

    fields = ["timeHuman", "timeMs", "artist", "track", "album", "albumArtist", "durationMs"]
    t = start
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in playlist:
            w.writerow({
                "timeHuman": t.strftime("%Y-%m-%d %H:%M:%S %z"),
                "timeMs": int(t.timestamp() * 1000),
                "artist": r["artist"],
                "track": r["title"],
                "album": r["album"],
                "albumArtist": r["albumArtist"],
                "durationMs": r["durationMs"],
            })
            t += timedelta(milliseconds=r["durationMs"])

    print(f"\n{len(playlist)} plays, {start:%Y-%m-%d %H:%M} -> {end:%Y-%m-%d %H:%M} -> {out}")


if __name__ == "__main__":
    main()
