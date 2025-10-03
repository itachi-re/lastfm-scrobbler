import csv
import datetime

# This is your full, corrected song list, sorted alphabetically by track title.
songs = [
    {"track": "0% Angel", "artist": "Mr. Kitty", "album": "A.I.", "durationMs": 203413},
    {"track": "Akuma no Ko", "artist": "Ai Higuchi", "album": "Akuma no Ko", "durationMs": 227284},
    {"track": "Blue Bird", "artist": "Ikimonogakari", "album": "My song Your song", "durationMs": 218200},
    {"track": "Bury Me Deep Inside Your Heart", "artist": "HIM", "album": "Razorblade Romance", "durationMs": 256266},
    {"track": "Calling (NEO Mix)", "artist": "Leah", "album": "THE WORLD ENDS WITH YOU -NEO MIX-", "durationMs": 159840},
    {"track": "Can You Feel My Heart", "artist": "Bring Me the Horizon", "album": "Sempiternal", "durationMs": 227586},
    {"track": "Careless Whisper", "artist": "George Michael", "album": "Make It Big", "durationMs": 391573},
    {"track": "Duvet", "artist": "bôa", "album": "Twilight", "durationMs": 204306},
    {"track": "Fly with me", "artist": "ꉈꀧ꒒꒒ꁄꍈꍈꀧ꒦ꉈ ꉣꅔꎡꅔꁕꁄ", "album": "THE MILLENNIUM PARADE", "durationMs": 276250},
    {"track": "Gone With The Sin", "artist": "HIM", "album": "Razorblade Romance", "durationMs": 262066},
    {"track": "Hacking to the Gate", "artist": "Itou Kanako", "album": "Hacking to the Gate", "durationMs": 256053},
    {"track": "Houseki", "artist": "Inoue Marina", "album": "Houseki", "durationMs": 279533},
    {"track": "Hyouriittai", "artist": "Yuzu", "album": "Shin Sekai", "durationMs": 335266},
    {"track": "Ignite", "artist": "Alan Walker, Julie Bergen, K-391, SEI", "album": "Ignite", "durationMs": 210103},
    {"track": "Just the Two of Us", "artist": "Grover Washington, Jr.", "album": "Winelight", "durationMs": 443706},
    {"track": "Katayoku no Tori", "artist": "Shikata Akiko", "album": "Umineko no Naku Koro ni", "durationMs": 278693},
    {"track": "KOMM, SUSSER TOD (M-10 Director's Edit Version)", "artist": "Arianne", "album": "THE END OF EVANGELION", "durationMs": 470653},
    {"track": "LITERALLY ME | VØJ x Narvent - Memory reboot", "artist": "Idlealliance", "album": "VA-PE", "durationMs": 236263},
    {"track": "Little Dark Age", "artist": "MGMT", "album": "Little Dark Age", "durationMs": 299413},
    {"track": "Magia", "artist": "Kalafina", "album": "After Eden", "durationMs": 309733},
    {"track": "Many Nights", "artist": "Yasuharu Takanashi", "album": "FAIRY TAIL Original Soundtrack Vol.4", "durationMs": 176453},
    {"track": "Mary On A Cross", "artist": "Ghost", "album": "Seven Inches of Satanic Panic", "durationMs": 244586},
    {"track": "Memory Reboot", "artist": "VØJ, Narvent", "album": "Memory Reboot", "durationMs": 204687},
    {"track": "Mortals", "artist": "Warriyo", "album": "Mortals", "durationMs": 230513},
    {"track": "Mozaiku Kakera", "artist": "Sunset Swish", "album": "Sunset Swish", "durationMs": 265000},
    {"track": "My Ordinary Life", "artist": "The Living Tombstone", "album": "My Ordinary Life", "durationMs": 230769},
    {"track": "No Time to Cast Anchor", "artist": "ꉈꀧ꒒꒒ꁄꍈꍈꀧ꒦ꉈ ꉣꅔꎡꅔꁕꁄ", "album": "No Time to Cast Anchor", "durationMs": 192713},
    {"track": "oblivious", "artist": "Kalafina", "album": "Seventh Heaven", "durationMs": 262266},
    {"track": "Obsession", "artist": "See-Saw", "album": ".hack//SIGN Original Sound & Song Track 1", "durationMs": 267333},
    {"track": "RED", "artist": "Survive Said The Prophet", "album": "Red", "durationMs": 253900},
    {"track": "Red Swan", "artist": "YOSHIKI feat. HYDE", "album": "Red Swan", "durationMs": 262653},
    {"track": "Shinzou wo Sasageyo!", "artist": "Linked Horizon", "album": "Shingeki no Kiseki", "durationMs": 341333},
    {"track": "Snow Falling", "artist": "Kalafina", "album": "After Eden", "durationMs": 278573},
    {"track": "Somewhere Only We Know", "artist": "Keane", "album": "Hopes and Fears", "durationMs": 237240},
    {"track": "STORY", "artist": "Mayu Maeshima", "album": "STORY", "durationMs": 259546},
    {"track": "STYX HELIX", "artist": "MYTH & ROID", "album": "eYe's", "durationMs": 291133},
    {"track": "Super scription of data", "artist": "Eiko Shimamiya", "album": "Super scription of data", "durationMs": 273640},
    {"track": "sustain++;", "artist": "Mili", "album": "Millennium Mother", "durationMs": 273613},
    {"track": "Thanatos", "artist": "Shiro SAGISU", "album": "NEON GENESIS EVANGELION II", "durationMs": 215333},
    {"track": "the WORLD", "artist": "ナイトメア (Nightmare)", "album": "the WORLD Ruler", "durationMs": 229200},
    {"track": "Throne", "artist": "Bring Me The Horizon", "album": "That's The Spirit", "durationMs": 191333},
    {"track": "to the beginning", "artist": "Kalafina", "album": "Consolation", "durationMs": 256786},
    {"track": "Treachery", "artist": "Shiro Sagisu", "album": "Bleach Original Soundtrack 3", "durationMs": 192800},
    {"track": "Unravel", "artist": "TK from Ling tosite sigure", "album": "Fantastic Magic", "durationMs": 238733},
    {"track": "Uso", "artist": "SID", "album": "hikari", "durationMs": 204733},
    {"track": "Why We Lose", "artist": "Cartoon", "album": "Why We Lose", "durationMs": 197486},
    {"track": "Yasashii yoake", "artist": "See-Saw", "album": ".hack//SIGN Original Sound & Song Track 1", "durationMs": 311200},
    {"track": "Zankoku na Tenshi no These [<Director's Edit. Version>]", "artist": "Yoko Takahashi", "album": "NEON GENESIS EVANGELION", "durationMs": 245333},
    {"track": "アルミナ", "artist": "ナイトメア (Nightmare)", "album": "DEATH NOTE｜the WORLD ・ アルミナ", "durationMs": 304107},
    {"track": "インフェルノ", "artist": "9mm Parabellum Bullet", "album": "BABEL", "durationMs": 155306},
    {"track": "また風が強くなった", "artist": "Kalafina", "album": "Consolation", "durationMs": 306506},
    {"track": "ライトのテーマ", "artist": "タニウチヒデキ", "album": "DEATH NOTE ORIGINAL SOUNDTRACK", "durationMs": 187426},
    {"track": "夏の林檎", "artist": "Kalafina", "album": "Seventh Heaven", "durationMs": 243226},
    {"track": "刻司ル十二ノ盟約", "artist": "FANTASMA (FES cv. 神原弥生)", "album": "STEINS;GATE SYMPHONIC REUNION", "durationMs": 270400},
    {"track": "光の旋律", "artist": "Kalafina", "album": "Red Moon", "durationMs": 373400},
    {"track": "紅蓮の弓矢", "artist": "Linked Horizon", "album": "Jiyuu e no Shingeki", "durationMs": 316546},
    {"track": "月と花束", "artist": "さユり", "album": "Me", "durationMs": 277026}
]

log_data = []

# Correct timezone definition (GMT+6)
tz = datetime.timezone(datetime.timedelta(hours=6))

# Set the correct start date and number of days for Sep x
start_date = datetime.datetime(2025, 10, 2, 0, 0, 0, tzinfo=tz)
num_days = 1  # For october x only
plays_per_day = 50  # each song played 50 times per day

for day in range(num_days):
    # Midnight for the current day
    current_day_start = start_date + datetime.timedelta(days=day)
    timestamp_ms = int(current_day_start.timestamp() * 1000)

    for _ in range(plays_per_day):
        for song in songs:
            time_human_dt = datetime.datetime.fromtimestamp(timestamp_ms / 1000, tz=tz)
            time_human_str = time_human_dt.strftime('%B %-d, %Y at %H:%M GMT%z')
            time_human_formatted = time_human_str[:-2] + ":" + time_human_str[-2:]

            log_entry = {
                "timeHuman": time_human_formatted,
                "timeMs": timestamp_ms,
                "artist": song["artist"],
                "track": song["track"],
                "album": song["album"],
                "albumArtist": song["artist"],
                "durationMs": song["durationMs"],
                "mediaPlayerPackage": "com.maxmpz.audioplayer",
                "mediaPlayerName": "Poweramp",
                "mediaPlayerVersion": "build-1000-bundle-play",
                "event": "scrobble"
            }
            log_data.append(log_entry)

            # Move forward in time
            timestamp_ms += song["durationMs"]

            # Wrap around if we go past midnight of the same day
            day_end = int((current_day_start + datetime.timedelta(days=1)).timestamp() * 1000)
            if timestamp_ms >= day_end:
                timestamp_ms = int(current_day_start.timestamp() * 1000)

# --- Write CSV file ---
output_filename = "scrobble_log.csv"
header = log_data[0].keys()

try:
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)
        writer.writeheader()
        writer.writerows(log_data)

    print(f"✅ CSV log file '{output_filename}' created successfully for Oct x.")

except Exception as e:
    print(f"❌ An error occurred: {e}")
