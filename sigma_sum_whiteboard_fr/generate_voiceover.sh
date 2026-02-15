#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SCRIPT_FILE="$ROOT_DIR/assets/tts_script_fr.txt"
AIFF_FILE="$ROOT_DIR/assets/voix_off_fr.aiff"
WAV_FILE="$ROOT_DIR/assets/voix_off_fr.wav"
TMP_WAV_FILE="$ROOT_DIR/assets/voix_off_fr_padded.wav"

if ! command -v say >/dev/null 2>&1; then
  echo "Error: 'say' command is required (macOS)."
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Error: 'ffmpeg' command is required."
  exit 1
fi

say -v Thomas -r 100 -f "$SCRIPT_FILE" -o "$AIFF_FILE"

ffmpeg -y -i "$AIFF_FILE" -af apad=pad_dur=3 -t 88.9 "$TMP_WAV_FILE" >/dev/null 2>&1
mv "$TMP_WAV_FILE" "$WAV_FILE"

printf "Voiceover generated: %s\n" "$WAV_FILE"
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$WAV_FILE"
