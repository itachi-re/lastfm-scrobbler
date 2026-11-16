#!/usr/bin/env python3
"""
Step 1 - scan your music folder and write library.csv

Reads the real tags (artist, title, album, duration) from your audio files
with mutagen, so the data is exactly what your player has.

    python3 01_scan_library.py                    # scans ~/Music
    python3 01_scan_library.py ~/Music/anime      # scan another folder
    python3 01_scan_library.py --filter kalafina  # only print matching rows

Output: library.csv  (id, artist, title, album, albumArtist, durationMs, path)
"""
import argparse
import csv
import sys
from pathlib import Path

import mutagen

EXTS = {".mp3", ".flac", ".m4a", ".ogg", ".opus", ".wav", ".wma", ".aac", ".ape", ".wv"}
FIELDS = ["id", "artist", "title", "album", "albumArtist", "durationMs", "path"]


ID3_FALLBACK = {"artist": "TPE1", "title": "TIT2", "album": "TALB", "albumartist": "TPE2"}


def tag(tags, key):
    if not tags:
        return ""
    v = None
    for k in (key, ID3_FALLBACK.get(key)):  # easy key first, raw ID3 frame (e.g. WAV) second
        try:
            v = tags.get(k) if k else None
        except Exception:
            v = None
        if v:
            break
    if not v:
        return ""
    v = getattr(v, "text", v)
    if isinstance(v, str):
        v = [v]
    return ", ".join(str(x).strip() for x in v if str(x).strip())


def read_track(path):
    try:
        f = mutagen.File(path, easy=True)
    except Exception:
        return None
    if f is None or f.info is None:
        return None
    t = f.tags
    album_artist = tag(t, "albumartist")
    artist = tag(t, "artist") or album_artist
    return {
        "artist": artist,
        "title": tag(t, "title") or path.stem,
        "album": tag(t, "album"),
        "albumArtist": album_artist or artist,
        "durationMs": int(round(f.info.length * 1000)),
        "path": str(path),
    }


def fmt_dur(ms):
    s = ms // 1000
    return f"{s // 60}:{s % 60:02d}"


def main():
    ap = argparse.ArgumentParser(description="Scan a music folder into library.csv")
    ap.add_argument("music_dir", nargs="?", default="~/Music")
    ap.add_argument("-o", "--output", default="library.csv")
    ap.add_argument("--filter", help="only print rows containing this text (file is still complete)")
    args = ap.parse_args()

    root = Path(args.music_dir).expanduser()
    if not root.is_dir():
        sys.exit(f"Not a directory: {root}")

    tracks, seen, dupes, unreadable, no_artist = [], set(), 0, 0, 0
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() not in EXTS or not p.is_file():
            continue
        tr = read_track(p)
        if tr is None:
            unreadable += 1
            continue
        if not tr["artist"]:
            no_artist += 1
        key = (tr["artist"].casefold(), tr["title"].casefold(), tr["album"].casefold())
        if key in seen:
            dupes += 1
            continue
        seen.add(key)
        tracks.append(tr)

    tracks.sort(key=lambda r: (r["artist"].casefold(), r["title"].casefold()))
    for i, tr in enumerate(tracks, start=1):
        tr["id"] = i

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(tracks)

    needle = args.filter.casefold() if args.filter else None
    for tr in tracks:
        line = f'{tr["id"]:>4}  {tr["artist"]} - {tr["title"]}  [{tr["album"]}]  {fmt_dur(tr["durationMs"])}'
        if needle is None or needle in line.casefold():
            print(line)

    print(f"\n{len(tracks)} tracks -> {args.output}", file=sys.stderr)
    if dupes:
        print(f"  skipped {dupes} duplicate(s) (same artist/title/album)", file=sys.stderr)
    if unreadable:
        print(f"  {unreadable} file(s) could not be read", file=sys.stderr)
    if no_artist:
        print(f"  WARNING: {no_artist} track(s) have no artist tag - fix them in your tagger", file=sys.stderr)


if __name__ == "__main__":
    main()
