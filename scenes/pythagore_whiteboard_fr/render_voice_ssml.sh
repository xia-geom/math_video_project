#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCENE_DIR="$ROOT_DIR/pythagore_whiteboard_fr"
SCENE_FILE="$SCENE_DIR/pythagore_scene.py"
SCENE_NAME="PythagoreAireFR"

"$ROOT_DIR/.venv/bin/manim" -ql --disable_caching "$SCENE_FILE" "$SCENE_NAME"

MP4_SRC="$ROOT_DIR/media/videos/pythagore_scene/480p15/PythagoreAireFR.mp4"
SRT_SRC="$ROOT_DIR/media/videos/pythagore_scene/480p15/PythagoreAireFR.srt"
MP4_OUT="$SCENE_DIR/PythagoreAireFR.mp4"
WAV_OUT="$SCENE_DIR/PythagoreAireFR_uncompressed.wav"
SRT_OUT="$SCENE_DIR/subtitles_fr.srt"

cp "$MP4_SRC" "$MP4_OUT"
cp "$SRT_SRC" "$SRT_OUT"

ffmpeg -y -i "$MP4_OUT" -vn -acodec pcm_s16le -ar 48000 -ac 1 "$WAV_OUT" >/dev/null 2>&1

echo "MP4: $MP4_OUT"
echo "WAV: $WAV_OUT"
echo "SRT: $SRT_OUT"
