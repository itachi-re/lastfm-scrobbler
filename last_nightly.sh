#!/usr/bin/env bash
# Nightly: build yesterday's scrobble CSV from plays-template.csv, then send it.
# Works from wherever the folder lives and uses the venv's python directly
# (no `source activate`), so moving the folder can't break it.
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

PY=.venv/bin/python
TEMPLATE=plays-template.csv
LOG=nightly.log
DAYS_AGO=1

exec >>"$LOG" 2>&1
echo "=== $(date '+%F %T') ==="

[ -x "$PY" ] || { echo "ERROR: .venv/bin/python missing - recreate the venv"; exit 1; }
[ -f "$TEMPLATE" ] || { echo "ERROR: $TEMPLATE not found"; exit 1; }

# 0) wait for the network (the timer can fire right after boot/resume, before DNS is up)
for i in $(seq 1 60); do
    getent hosts ws.audioscrobbler.com >/dev/null 2>&1 && break
    [ "$i" -eq 1 ] && echo "waiting for network..."
    sleep 10
done

# 1) nothing to do if every plays cell is 0/empty
if ! "$PY" - "$TEMPLATE" <<'EOF'
import csv, sys
rows = csv.DictReader(open(sys.argv[1], encoding="utf-8-sig", newline=""))
sys.exit(0 if any((r.get("plays") or "").strip() not in ("", "0") for r in rows) else 1)
EOF
then
    echo "no plays set in $TEMPLATE, nothing to do"
    exit 0
fi

# 2) step 2: make the CSV (last line of its output ends with "-> <filename>")
OUT=$("$PY" 02_make_scrobbles.py "$TEMPLATE" --days-ago "$DAYS_AGO" | tee /dev/stderr | tail -n1 | sed 's/.* -> //')
[ -f "$OUT" ] || { echo "ERROR: step 2 produced no file"; exit 1; }
echo "built $OUT"

# 3) step 3: send; if Last.fm rate-limits, wait 15 min and resume where it stopped
SKIP=0
MAX_ATTEMPTS=5
for attempt in $(seq 1 $MAX_ATTEMPTS); do
    set +e
    "$PY" 03_submit_scrobbles.py "$OUT" --send --skip "$SKIP" 2>&1 | tee .submit.out
    rc=${PIPESTATUS[0]}
    set -e
    if [ "$rc" -eq 0 ]; then
        echo "done"
        exit 0
    fi
    NEXT=$(grep -oP '(?<=--send --skip )\d+' .submit.out | tail -n1 || true)
    if [ -n "$NEXT" ]; then
        SKIP=$NEXT
        echo "rate limited, resuming from $SKIP in 15 min (attempt $attempt/$MAX_ATTEMPTS)"
        sleep 900
    elif grep -q "Authentication failed: NetworkError" .submit.out; then
        echo "network error, login failed, nothing sent yet; retrying in 2 min (attempt $attempt/$MAX_ATTEMPTS)"
        sleep 120
    else
        echo "send failed (rc=$rc), not retrying"
        exit "$rc"
    fi
done
echo "gave up after $MAX_ATTEMPTS attempts; resume by hand: --send --skip $SKIP"
exit 2
