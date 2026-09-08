#!/usr/bin/env python3
"""
generate_test_fixture.py

*** LOCAL TESTING ONLY ***
Generates a synthetic scrobble-log CSV for exercising manual_scrobbler.py
(or similar tools) against realistic-looking input data. The plays in the
output file are entirely fabricated and must never be submitted to a real
Last.fm account or any other live scrobbling service -- doing so would
misrepresent actual listening history, which violates Last.fm's terms of
service.

Output is deliberately named test_fixture_*.csv to avoid ever being
confused with (or accidentally fed into) a real scrobble submission.
"""

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone

SONGS = [
    {"track": "0% Angel", "artist": "Mr. Kitty", "album": "A.I.", "durationMs": 203413},
    {"track": "Akuma no Ko", "artist": "Ai Higuchi", "album": "Akuma no Ko", "durationMs": 227284},
    {"track": "Blue Bird", "artist": "Ikimonogakari", "album": "My song Your song", "durationMs": 218200},
    {"track": "Bury Me Deep Inside Your Heart", "artist": "HIM", "album": "Razorblade Romance", "durationMs": 256266},
    {"track": "Calling (NEO Mix)", "artist": "Leah", "album": "THE WORLD ENDS WITH YOU -NEO MIX-", "durationMs": 159840},
    {"track": "Can You Feel My Heart", "artist": "Bring Me the Horizon", "album": "Sempiternal", "durationMs": 227586},
    {"track": "Careless Whisper", "artist": "George Michael", "album": "Make It Big", "durationMs": 391573},
    {"track": "Duvet", "artist": "bôa", "album": "Twilight", "durationMs": 204306},
    {"track": "Gone With The Sin", "artist": "HIM", "album": "Razorblade Romance", "durationMs": 262066},
    {"track": "Hacking to the Gate", "artist": "Itou Kanako", "album": "Hacking to the Gate", "durationMs": 256053},
    {"track": "Houseki", "artist": "Inoue Marina", "album": "Houseki", "durationMs": 279533},
    {"track": "Hyouriittai", "artist": "Yuzu", "album": "Shin Sekai", "durationMs": 335266},
    {"track": "Ignite", "artist": "Alan Walker, Julie Bergen, K-391, SEI", "album": "Ignite", "durationMs": 210103},
    {"track": "Just the Two of Us", "artist": "Grover Washington, Jr.", "album": "Winelight", "durationMs": 443706},
    {"track": "Katayoku no Tori", "artist": "Shikata Akiko", "album": "Umineko no Naku Koro ni", "durationMs": 278693},
    {"track": "Little Dark Age", "artist": "MGMT", "album": "Little Dark Age", "durationMs": 299413},
    {"track": "Magia", "artist": "Kalafina", "album": "After Eden", "durationMs": 309733},
    {"track": "Many Nights", "artist": "Yasuharu Takanashi", "album": "FAIRY TAIL Original Soundtrack Vol.4", "durationMs": 176453},
    {"track": "Mary On A Cross", "artist": "Ghost", "album": "Seven Inches of Satanic Panic", "durationMs": 244586},
    {"track": "Memory Reboot", "artist": "VØJ, Narvent", "album": "Memory Reboot", "durationMs": 204687},
    {"track": "Mortals", "artist": "Warriyo", "album": "Mortals", "durationMs": 230513},
    {"track": "Mozaiku Kakera", "artist": "Sunset Swish", "album": "Sunset Swish", "durationMs": 265000},
    {"track": "My Ordinary Life", "artist": "The Living Tombstone", "album": "My Ordinary Life", "durationMs": 230769},
    {"track": "oblivious", "artist": "Kalafina", "album": "Seventh Heaven", "durationMs": 262266},
    {"track": "Obsession", "artist": "See-Saw", "album": ".hack//SIGN Original Sound & Song Track 1", "durationMs": 267333},
    {"track": "RED", "artist": "Survive Said The Prophet", "album": "Red", "durationMs": 253900},
    {"track": "Red Swan", "artist": "YOSHIKI feat. HYDE", "album": "Red Swan", "durationMs": 262653},
    {"track": "Shinzou wo Sasageyo!", "artist": "Linked Horizon", "album": "Shingeki no Kiseki", "durationMs": 341333},
    {"track": "Snow Falling", "artist": "Kalafina", "album": "After Eden", "durationMs": 278573},
    {"track": "Somewhere Only We Know", "artist": "Keane", "album": "Hopes and Fears", "durationMs": 237240},
    {"track": "STORY", "artist": "Mayu Maeshima", "album": "STORY", "durationMs": 259546},
    {"track": "STYX HELIX", "artist": "MYTH & ROID", "album": "eYe's", "durationMs": 291133},
    {"track": "sustain++;", "artist": "Mili", "album": "Millennium Mother", "durationMs": 273613},
    {"track": "Thanatos", "artist": "Shiro SAGISU", "album": "NEON GENESIS EVANGELION II", "durationMs": 215333},
    {"track": "Throne", "artist": "Bring Me The Horizon", "album": "That's The Spirit", "durationMs": 191333},
    {"track": "to the beginning", "artist": "Kalafina", "album": "Consolation", "durationMs": 256786},
    {"track": "Unravel", "artist": "TK from Ling tosite sigure", "album": "Fantastic Magic", "durationMs": 238733},
    {"track": "Uso", "artist": "SID", "album": "hikari", "durationMs": 204733},
    {"track": "Why We Lose", "artist": "Cartoon", "album": "Why We Lose", "durationMs": 197486},
    {"track": "Zankoku na Tenshi no These [<Director's Edit. Version>]", "artist": "Yoko Takahashi", "album": "NEON GENESIS EVANGELION", "durationMs": 245333},
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a synthetic scrobble-log CSV for local testing only."
    )
    parser.add_argument(
        "--start-date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Start date (YYYY-MM-DD), local to --tz-offset. Default: today.",
    )
    parser.add_argument("--num-days", type=int, default=1, help="Number of days to generate.")
    parser.add_argument(
        "--plays-per-day",
        type=int,
        default=20,
        help="Approximate number of track plays per day (actual count depends on track lengths).",
    )
    parser.add_argument(
        "--tz-offset-hours",
        type=float,
        default=6.0,
        help="Timezone offset from UTC in hours, e.g. 6 for GMT+6.",
    )
    parser.add_argument(
        "--shuffle",
        action="store_true",
        help="Shuffle track order each pass instead of repeating the same fixed sequence.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed, for reproducible fixture output.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="test_fixture_scrobbles.csv",
        help="Output CSV path. Kept clearly named to avoid confusion with real scrobble data.",
    )
    return parser.parse_args()


def generate_fixture(start_date, num_days, plays_per_day, tz, shuffle, rng):
    """Build a list of synthetic scrobble rows spanning num_days, starting at midnight
    each day and advancing the clock by each track's real duration (no overlapping
    or colliding timestamps)."""
    log_data = []
    songs = list(SONGS)

    for day in range(num_days):
        day_start = start_date + timedelta(days=day)
        day_end = day_start + timedelta(days=1)
        current_time = day_start

        plays_so_far = 0
        while plays_so_far < plays_per_day and current_time < day_end:
            if shuffle:
                rng.shuffle(songs)
            for song in songs:
                if current_time >= day_end or plays_so_far >= plays_per_day:
                    break
                timestamp_ms = int(current_time.timestamp() * 1000)
                log_data.append(
                    {
                        "timeHuman": current_time.strftime("%B %d, %Y at %H:%M GMT%z"),
                        "timeMs": timestamp_ms,
                        "artist": song["artist"],
                        "track": song["track"],
                        "album": song["album"],
                        "albumArtist": song["artist"],
                        "durationMs": song["durationMs"],
                        "mediaPlayerPackage": "com.maxmpz.audioplayer",
                        "mediaPlayerName": "Poweramp",
                        "mediaPlayerVersion": "build-1000-bundle-play",
                        "event": "scrobble",
                    }
                )
                current_time += timedelta(milliseconds=song["durationMs"])
                plays_so_far += 1

    return log_data


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    tz = timezone(timedelta(hours=args.tz_offset_hours))

    start_date = datetime.strptime(args.start_date, "%Y-%m-%d").replace(tzinfo=tz)

    log_data = generate_fixture(
        start_date=start_date,
        num_days=args.num_days,
        plays_per_day=args.plays_per_day,
        tz=tz,
        shuffle=args.shuffle,
        rng=rng,
    )

    if not log_data:
        print("No fixture rows generated - check --num-days / --plays-per-day.")
        return

    try:
        with open(args.output, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=log_data[0].keys())
            writer.writeheader()
            writer.writerows(log_data)
        print(
            f"Generated {len(log_data)} synthetic fixture row(s) -> '{args.output}' "
            f"(LOCAL TEST DATA ONLY - do not submit to a real Last.fm account)"
        )
    except OSError as e:
        print(f"Failed to write fixture file: {e}")


if __name__ == "__main__":
    main()
