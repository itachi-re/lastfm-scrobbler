import pylast
import csv
import sys
from datetime import datetime

# Get API key, secret, and file path from command line arguments
if len(sys.argv) < 6:
    print("Usage: python manual_scrobbler.py <api_key> <api_secret> <username> <password_hash> <file_path>")
    sys.exit(1)

API_KEY = sys.argv[1]
API_SECRET = sys.argv[2]
USERNAME = sys.argv[3]
PASSWORD_HASH = sys.argv[4]
FILE_PATH = sys.argv[5]

try:
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                   username=USERNAME, password_hash=PASSWORD_HASH)
except pylast.NetworkError as e:
    print(f"Authentication failed: {e}")
    sys.exit(1)

scrobbles = []
with open(FILE_PATH, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        try:
            # Use 'timeMs' for a more accurate timestamp
            timestamp_ms = int(row['timeMs'])
            timestamp_sec = int(timestamp_ms / 1000)

            # Append the scrobble to a list
            scrobbles.append({
                "artist": row['artist'],
                "title": row['track'],
                "timestamp": timestamp_sec,
                "album": row.get('album', ''),
            })
        except (ValueError, KeyError) as e:
            print(f"Skipping row due to missing or invalid data: {row}")
            continue

# Sort scrobbles by timestamp to ensure they are sent in correct order
scrobbles.sort(key=lambda x: x['timestamp'])

if not scrobbles:
    print("No valid scrobbles found in the file.")
    sys.exit(0)

print(f"Found {len(scrobbles)} valid scrobbles. Submitting to Last.fm...")

# Submit scrobbles in a single batch
try:
    network.scrobble_many(scrobbles)
    print("Batch scrobble successful! Your scrobbles should now appear on your profile.")
except pylast.NetworkError as e:
    print(f"An error occurred during scrobbling: {e}")
except pylast.WSError as e:
    print(f"Last.fm API error: {e}")
    if "Invalid timestamp" in str(e):
         print("This is likely due to the scrobbles being too old. They will not be accepted with their original date.")
