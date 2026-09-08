#!/bin/bash
# metadata extractor – verbose with -v/--verbose, otherwise silent
# Usage: ./music-metadata.sh [-v] > library.json

MUSIC_DIR="/data/itachi/Music"
VERBOSE=false

# Parse command line
for arg in "$@"; do
    case $arg in
        -v|--verbose)
            VERBOSE=true
            ;;
        *)
            echo "Usage: $0 [-v|--verbose]" >&2
            exit 1
            ;;
    esac
done

cd "$MUSIC_DIR" || { echo "ERROR: Cannot cd to $MUSIC_DIR" >&2; exit 1; }

log() {
    if [ "$VERBOSE" = true ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
    fi
}

# Safe string truncation (no bash‑isms)
truncate_string() {
    local str="$1"
    local maxlen=40
    if [ ${#str} -le $maxlen ]; then
        echo "$str"
    else
        echo "${str:0:$maxlen}…"
    fi
}

log "Starting metadata extraction from $MUSIC_DIR"

# Build list of files (avoid subshell)
files=()
while IFS= read -r -d '' file; do
    files+=("$file")
done < <(find . -maxdepth 1 -type f \( -iname "*.flac" -o -iname "*.m4a" -o -iname "*.mp3" -o -iname "*.wav" \) -print0)

TOTAL_FILES=${#files[@]}
log "Found $TOTAL_FILES audio files to process."

echo "["
FIRST=true
COUNT=0

for FILE in "${files[@]}"; do
    COUNT=$((COUNT+1))
    DISPLAY_NAME="${FILE#./}"
    log "Processing [$COUNT/$TOTAL_FILES]: $DISPLAY_NAME"

    JSON=$(ffprobe -v quiet -print_format json -show_format -show_streams "$FILE" 2>/dev/null)
    if [ $? -ne 0 ] || [ -z "$JSON" ]; then
        log "WARNING: ffprobe failed for $DISPLAY_NAME – skipping"
        continue
    fi

    TITLE=$(echo "$JSON" | jq -r '.streams[0].tags.title // .format.tags.TITLE // .format.tags.title // "Unknown"')
    ARTIST=$(echo "$JSON" | jq -r '.streams[0].tags.artist // .format.tags.ARTIST // .format.tags.artist // "Unknown"')
    ALBUM=$(echo "$JSON" | jq -r '.streams[0].tags.album // .format.tags.ALBUM // .format.tags.album // "Unknown"')
    DURATION=$(echo "$JSON" | jq -r '.format.duration // 0')
    DURATION_MS=$(echo "$DURATION * 1000 / 1" | bc 2>/dev/null || echo "0")

    log "  → Title: $(truncate_string "$TITLE")"
    log "  → Artist: $(truncate_string "$ARTIST")"
    log "  → Album: $(truncate_string "$ALBUM")"
    log "  → Duration: ${DURATION_MS} ms"

    [ "$TITLE" = "Unknown" ] && log "  ⚠️ Title missing"
    [ "$ARTIST" = "Unknown" ] && log "  ⚠️ Artist missing"
    [ "$ALBUM" = "Unknown" ] && log "  ⚠️ Album missing"

    TITLE_ESC=$(echo "$TITLE" | sed 's/\\/\\\\/g; s/"/\\"/g')
    ARTIST_ESC=$(echo "$ARTIST" | sed 's/\\/\\\\/g; s/"/\\"/g')
    ALBUM_ESC=$(echo "$ALBUM" | sed 's/\\/\\\\/g; s/"/\\"/g')

    if [ "$FIRST" = true ]; then
        FIRST=false
    else
        echo ","
    fi
    printf '  {"track": "%s", "artist": "%s", "album": "%s", "durationMs": %s}' \
        "$TITLE_ESC" "$ARTIST_ESC" "$ALBUM_ESC" "$DURATION_MS"

    log "  ✅ Done with $DISPLAY_NAME"
done

echo
echo "]"
log "Extraction complete. Total files processed: $COUNT"
