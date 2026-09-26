#!/usr/bin/env bash
# Render a scene with the four existing fr-CA comparison voices.
# Usage: scripts/render_all_voices.sh <scene_file> <SceneClass> [ql|qm|qh]
# Voice selections are unchanged; output identity comes from the course catalogue.

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
source "$ROOT_DIR/scripts/render_outputs.sh"

PYTHON="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
    echo "ERROR: project Python is unavailable: $PYTHON" >&2
    exit 1
fi
SCENE_FILE="$("$PYTHON" "$ROOT_DIR/tools/course_catalog.py" resolve-path "$SCENE_FILE")"
ARTIFACT_NAME="$("$PYTHON" "$ROOT_DIR/tools/course_catalog.py" artifact-name "$SCENE_FILE")"
DIST_DIR="$(resolve_render_dist_dir "$ROOT_DIR" "$ARTIFACT_NAME" "$QUALITY")"
OUTPUT_STEM="$(resolve_render_output_stem "$ARTIFACT_NAME" "$QUALITY")"

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
    RENDER_SKIP_DRIVE_COPY=1 MANIM_VOICE="$VOICE" \
        scripts/render.sh "$SCENE_FILE" "$SCENE_CLASS" "$QUALITY"

    if [[ ! -f "$DIST_DIR/$OUTPUT_STEM.mp4" ]]; then
        echo "ERROR: missing fresh voice render: $DIST_DIR/$OUTPUT_STEM.mp4" >&2
        exit 1
    fi
    mv "$DIST_DIR/$OUTPUT_STEM.mp4" "$DIST_DIR/${OUTPUT_STEM}_${VOICE}.mp4"
    if [[ "$QUALITY" == "qh" ]]; then
        copy_render_mp4_to_drive \
            "$DIST_DIR/${OUTPUT_STEM}_${VOICE}.mp4" "$SCENE_CLASS" "$SCENE_FILE"
    fi
    if [[ -f "$DIST_DIR/$OUTPUT_STEM.srt" ]]; then
        mv "$DIST_DIR/$OUTPUT_STEM.srt" "$DIST_DIR/${OUTPUT_STEM}_${VOICE}.srt"
    fi
    if [[ -f "$DIST_DIR/${OUTPUT_STEM}_uncompressed.wav" ]]; then
        mv "$DIST_DIR/${OUTPUT_STEM}_uncompressed.wav" \
           "$DIST_DIR/${OUTPUT_STEM}_${VOICE}.wav"
    fi
done

echo ""
echo "All voice comparisons rendered under: $DIST_DIR/"
