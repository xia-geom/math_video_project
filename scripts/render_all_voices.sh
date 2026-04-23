#!/usr/bin/env bash
# scripts/render_all_voices.sh — render a scene with every fr-CA voice
#
# Usage:
#   scripts/render_all_voices.sh <scene_file> <SceneClass> [quality]
#
# Re-runs scripts/render.sh four times, once per voice, and tags the
# output files with the voice name so they can be A/B compared.

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

VOICES=(
    "fr-CA-SylvieNeural"
    "fr-CA-JeanNeural"
    "fr-CA-AntoineNeural"
    "fr-CA-ThierryNeural"
)

if [[ -z "${SPEECH_KEY:-}" || -z "${SPEECH_REGION:-}" ]]; then
    echo "ERROR: Set SPEECH_KEY and SPEECH_REGION before running." >&2
    exit 1
fi

for VOICE in "${VOICES[@]}"; do
    echo ""
    echo "══ $VOICE ══"
    MANIM_VOICE="$VOICE" scripts/render.sh "$SCENE_FILE" "$SCENE_CLASS" "$QUALITY"

    DIST_DIR="$ROOT_DIR/dist/$SCENE_CLASS"
    if [[ -f "$DIST_DIR/$SCENE_CLASS.mp4" ]]; then
        mv "$DIST_DIR/$SCENE_CLASS.mp4" "$DIST_DIR/${SCENE_CLASS}_${VOICE}.mp4"
    fi
    if [[ -f "$DIST_DIR/$SCENE_CLASS.srt" ]]; then
        mv "$DIST_DIR/$SCENE_CLASS.srt" "$DIST_DIR/${SCENE_CLASS}_${VOICE}.srt"
    fi
    if [[ -f "$DIST_DIR/${SCENE_CLASS}_uncompressed.wav" ]]; then
        mv "$DIST_DIR/${SCENE_CLASS}_uncompressed.wav" \
           "$DIST_DIR/${SCENE_CLASS}_${VOICE}.wav"
    fi
done

echo ""
echo "All voices rendered under: dist/$SCENE_CLASS/"
