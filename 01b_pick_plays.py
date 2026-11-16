#!/usr/bin/env python3
"""
Step 1b - say which songs you played and how many times. Everything else stays 0.

Two ways, same result:

A) Interactive (default): search, then set a count. Writes plays.txt
       python3 01b_pick_plays.py

   search>  duvet                 -> shows matches with their #id
   search>  57 7                  -> sets #57 to 7 plays   (0 removes it)
   search>  #57                   -> sets #57 to 1 play
   search>  list                  -> show everything picked so far
   search>  done                  -> save plays.txt and quit      (quit = discard)

B) Spreadsheet: all songs with a plays column pre-filled with 0.
       python3 01b_pick_plays.py --template        # writes plays-template.csv
   Open it (LibreOffice / VS Code / vim), type numbers in the "plays" column,
   leave the rest at 0, save, then run step 2 on that CSV.
"""
import argparse
import csv
import re
import sys
import unicodedata
from pathlib import Path


def compact(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", "", s.casefold())


def fmt_dur(ms):
    s = int(ms) // 1000
    return f"{s // 60}:{s % 60:02d}"


def load_library(path):
    try:
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        sys.exit(f"{path} not found - run 01_scan_library.py first.")
    for r in rows:
        r["id"] = int(r["id"])
    return rows


def write_template(lib, out):
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["plays", "id", "artist", "title", "album", "duration"])
        for r in lib:
            w.writerow([0, r["id"], r["artist"], r["title"], r["album"], fmt_dur(r["durationMs"])])
    print(f"Wrote {out} ({len(lib)} songs). Fill the 'plays' column, save, then:")
    print(f"  python3 02_make_scrobbles.py {out}")


def load_existing(path):
    counts = {}
    p = Path(path)
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*#(\d+)\s+x(\d+)", line)
            if m:
                counts[int(m.group(1))] = int(m.group(2))
    return counts


def save(counts, by_id, path):
    lines = []
    for i in sorted(counts, key=lambda i: (by_id[i]["artist"].casefold(), by_id[i]["title"].casefold())):
        r = by_id[i]
        lines.append(f'#{i} x{counts[i]}  # {r["artist"]} - {r["title"]}')
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    total = sum(counts.values())
    print(f"Saved {len(counts)} songs / {total} plays -> {path}")
    print(f"Next: python3 02_make_scrobbles.py {path}")


def show(rows, counts):
    for r in rows:
        n = counts.get(r["id"], 0)
        mark = f"   <- {n} play(s)" if n else ""
        print(f'  #{r["id"]:<4} {r["artist"]} - {r["title"]}  [{r["album"]}]  {fmt_dur(r["durationMs"])}{mark}')


def main():
    ap = argparse.ArgumentParser(description="Pick songs and play counts")
    ap.add_argument("--library", default="library.csv")
    ap.add_argument("-o", "--output", default="plays.txt")
    ap.add_argument("--template", action="store_true", help="write plays-template.csv instead of going interactive")
    ap.add_argument("--fresh", action="store_true", help="ignore an existing plays file")
    args = ap.parse_args()

    lib = load_library(args.library)
    if args.template:
        write_template(lib, "plays-template.csv")
        return

    by_id = {r["id"]: r for r in lib}
    index = {r["id"]: compact(f'{r["artist"]} {r["title"]} {r["album"]}') for r in lib}
    counts = {} if args.fresh else {i: n for i, n in load_existing(args.output).items() if i in by_id}
    if counts:
        print(f"Loaded {len(counts)} song(s) from existing {args.output} (use --fresh to ignore).")
    print(f"{len(lib)} songs. Type part of a name to search, '57 7' to set #57 to 7 plays, 'list', 'done'.\n")

    while True:
        try:
            cmd = input("search> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit("Aborted, nothing saved.")
        if not cmd:
            continue
        low = cmd.casefold()
        if low in ("done", "d", "save"):
            if not counts:
                print("Nothing picked yet.")
                continue
            save(counts, by_id, args.output)
            return
        if low in ("quit", "q", "exit"):
            sys.exit("Quit, nothing saved.")
        if low in ("list", "l"):
            show([by_id[i] for i in sorted(counts)], counts) if counts else print("  (nothing picked yet)")
            print(f"  total: {sum(counts.values())} plays")
            continue

        m = re.fullmatch(r"#?(\d+)\s+x?(\d+)", cmd) or re.fullmatch(r"#(\d+)()", cmd)
        if m:
            i, n = int(m.group(1)), int(m.group(2) or 1)
            if i not in by_id:
                print(f"  no song with id {i}")
            elif n == 0:
                counts.pop(i, None)
                print(f'  removed: {by_id[i]["artist"]} - {by_id[i]["title"]}')
            else:
                counts[i] = n
                print(f'  {n} x {by_id[i]["artist"]} - {by_id[i]["title"]}')
            continue

        q = compact(cmd)
        hits = [r for r in lib if q and q in index[r["id"]]][:25]
        if hits:
            show(hits, counts)
        else:
            print("  no matches")


if __name__ == "__main__":
    main()
