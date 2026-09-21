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
#   MANIM_VOICE               — optional voice override; defaults to project default.
#
# Outputs use the catalogue's global number and semantic delivery name:
#   qh: dist/<delivery_name>/<delivery_name>.{mp4,srt}
#   ql/qm: dist/_previews/<quality>/<delivery_name>/<delivery_name>__<quality>.{mp4,srt}
#   A 48 kHz mono WAV is also produced when the video contains audio.

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <scene_file> <SceneClass> [ql|qm|qh]" >&2
    exit 2
fi

SCENE_FILE="$1"
SCENE_CLASS="$2"
QUALITY="${3:-qh}"

# Resolve the unique global course number and semantic delivery name below.
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
source "$ROOT_DIR/scripts/render_outputs.sh"

PYTHON="./.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
    echo "ERROR: $PYTHON not found. Activate venv or run 'pip install -e .' first." >&2
    exit 1
fi

SCENE_FILE="$("$PYTHON" "$ROOT_DIR/tools/course_catalog.py" resolve-path "$SCENE_FILE")"
ARTIFACT_NAME="$("$PYTHON" "$ROOT_DIR/tools/course_catalog.py" artifact-name "$SCENE_FILE")"

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
MP4_SRC="$ROOT_DIR/media/videos/$SCENE_STEM/$SUBDIR/$SCENE_CLASS.mp4"
SRT_SRC="$ROOT_DIR/media/videos/$SCENE_STEM/$SUBDIR/$SCENE_CLASS.srt"
DIST_DIR="$(resolve_render_dist_dir "$ROOT_DIR" "$ARTIFACT_NAME" "$QUALITY")"
OUTPUT_STEM="$(resolve_render_output_stem "$ARTIFACT_NAME" "$QUALITY")"
mkdir -p "$DIST_DIR"

rm -f "$MP4_SRC" "$SRT_SRC"

echo "── Rendering $SCENE_CLASS ($QUALITY) ──"
if [[ "$QUALITY" == "qh" ]]; then
    "$PYTHON" -m manim "$FLAG" "$SCENE_FILE" "$SCENE_CLASS" -r 1920,1080
else
    "$PYTHON" -m manim "$FLAG" "$SCENE_FILE" "$SCENE_CLASS"
fi

if [[ -f "$MP4_SRC" ]]; then
    MP4_OUT="$DIST_DIR/$OUTPUT_STEM.mp4"
    if [[ "$QUALITY" == "qh" && -f "$MP4_OUT" ]]; then
        "$PYTHON" "$ROOT_DIR/scripts/archive_renders.py" register "$MP4_OUT" --quality qh
    fi
    MP4_TEMP="$DIST_DIR/.${OUTPUT_STEM}.mp4.new"
    cp "$MP4_SRC" "$MP4_TEMP"
    mv -f "$MP4_TEMP" "$MP4_OUT"
    echo "MP4: $MP4_OUT"
    if [[ "$QUALITY" == "qh" ]]; then
        "$PYTHON" "$ROOT_DIR/scripts/archive_renders.py" register "$MP4_OUT" --quality qh
        copy_render_mp4_to_drive "$MP4_OUT" "$SCENE_CLASS" "$SCENE_FILE"
    fi
else
    echo "ERROR: render produced no fresh MP4 at $MP4_SRC; existing deliverables were not reused." >&2
    exit 1
fi

if [[ -f "$SRT_SRC" ]]; then
    SRT_OUT="$DIST_DIR/$OUTPUT_STEM.srt"
    cp "$SRT_SRC" "$SRT_OUT"
    echo "SRT: $SRT_OUT"
else
    rm -f "$DIST_DIR/$OUTPUT_STEM.srt"
fi

if [[ -f "$DIST_DIR/$OUTPUT_STEM.mp4" ]] && command -v ffmpeg >/dev/null 2>&1; then
    WAV_OUT="$DIST_DIR/${OUTPUT_STEM}_uncompressed.wav"
    rm -f "$WAV_OUT"
    ffmpeg -y -i "$DIST_DIR/$OUTPUT_STEM.mp4" \
        -vn -acodec pcm_s16le -ar 48000 -ac 1 \
        "$WAV_OUT" >/dev/null 2>&1 || true
    if [[ -f "$WAV_OUT" ]]; then
        echo "WAV: $WAV_OUT"
    fi
fi
