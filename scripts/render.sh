#!/usr/bin/env bash
# scripts/render.sh — shared Manim render entry point
#
# Usage:
#   scripts/render.sh <scene_file> <SceneClass> [quality]
#
#   quality: ql (480p15) | qm (720p30) | qh (1080p60, default)
#
# Environment:
#   SPEECH_KEY, SPEECH_REGION — required only if the scene uses Azure voiceover.
#   MANIM_VOICE               — optional fr-CA voice override; defaults to project default.
#
# Outputs:
#   Rendered MP4/SRT are copied to  dist/<SceneClass>/<SceneClass>.{mp4,srt}
#   A 48 kHz mono WAV is also produced for captioning / editing.

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <scene_file> <SceneClass> [ql|qm|qh]" >&2
    exit 2
fi

SCENE_FILE="$1"
SCENE_CLASS="$2"
QUALITY="${3:-qh}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MANIM="./.venv/bin/manim"
if [[ ! -x "$MANIM" ]]; then
    echo "ERROR: $MANIM not found. Activate venv or run 'pip install -e .' first." >&2
    exit 1
fi

case "$QUALITY" in
    ql) FLAG="-ql"; SUBDIR="480p15" ;;
    qm) FLAG="-qm"; SUBDIR="720p30" ;;
    qh) FLAG="-qh"; SUBDIR="1080p60" ;;
    *)  echo "ERROR: quality must be ql|qm|qh (got '$QUALITY')" >&2; exit 2 ;;
esac

if [[ ! -f "$SCENE_FILE" ]]; then
    echo "ERROR: scene file not found: $SCENE_FILE" >&2
    exit 1
fi

SCENE_STEM="$(basename "$SCENE_FILE" .py)"
DIST_DIR="$ROOT_DIR/dist/$SCENE_CLASS"
mkdir -p "$DIST_DIR"

echo "── Rendering $SCENE_CLASS ($QUALITY) ──"
if [[ "$QUALITY" == "qh" ]]; then
    "$MANIM" "$FLAG" "$SCENE_FILE" "$SCENE_CLASS" -r 1920,1080
else
    "$MANIM" "$FLAG" "$SCENE_FILE" "$SCENE_CLASS"
fi

MP4_SRC="$ROOT_DIR/media/videos/$SCENE_STEM/$SUBDIR/$SCENE_CLASS.mp4"
SRT_SRC="$ROOT_DIR/media/videos/$SCENE_STEM/$SUBDIR/$SCENE_CLASS.srt"

if [[ -f "$MP4_SRC" ]]; then
    cp "$MP4_SRC" "$DIST_DIR/$SCENE_CLASS.mp4"
    echo "MP4: $DIST_DIR/$SCENE_CLASS.mp4"
else
    echo "WARN: no MP4 at $MP4_SRC" >&2
fi

if [[ -f "$SRT_SRC" ]]; then
    cp "$SRT_SRC" "$DIST_DIR/$SCENE_CLASS.srt"
    echo "SRT: $DIST_DIR/$SCENE_CLASS.srt"
fi

if [[ -f "$DIST_DIR/$SCENE_CLASS.mp4" ]] && command -v ffmpeg >/dev/null 2>&1; then
    WAV_OUT="$DIST_DIR/${SCENE_CLASS}_uncompressed.wav"
    ffmpeg -y -i "$DIST_DIR/$SCENE_CLASS.mp4" -vn -acodec pcm_s16le -ar 48000 -ac 1 \
        "$WAV_OUT" >/dev/null 2>&1 || true
    [[ -f "$WAV_OUT" ]] && echo "WAV: $WAV_OUT"
fi
