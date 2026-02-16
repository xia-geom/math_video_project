#!/usr/bin/env bash
# render_all_voices.sh
# Renders VariablesEtPolynomes with each of the four fr-CA voices.
# Outputs go to media/videos/variables_et_polynomes_scene/<voice>/
#
# Usage:
#   export SPEECH_KEY=<key>
#   export SPEECH_REGION=canadaeast
#   ./variables_et_polynomes/render_all_voices.sh
#
# To render a single voice:
#   MANIM_VOICE=fr-CA-SylvieNeural ./variables_et_polynomes/render_all_voices.sh

set -euo pipefail

SCENE="variables_et_polynomes/variables_et_polynomes_scene.py"
CLASS="VariablesEtPolynomes"
MANIM="./.venv/bin/manim"

# Voices to render (set MANIM_VOICE env to restrict to one)
if [[ -n "${MANIM_VOICE:-}" ]]; then
    VOICES=("$MANIM_VOICE")
else
    VOICES=(
        "fr-CA-SylvieNeural"
        "fr-CA-JeanNeural"
        "fr-CA-AntoineNeural"
        "fr-CA-ThierryNeural"
    )
fi

# Require Azure credentials
if [[ -z "${SPEECH_KEY:-}" || -z "${SPEECH_REGION:-}" ]]; then
    echo "ERROR: Set SPEECH_KEY and SPEECH_REGION before running." >&2
    exit 1
fi

# Run sync check first
echo "── Running SSML sync check ────────────────────────────────────"
python tools/ssml_sync_check.py "$SCENE" || {
    echo "SYNC CHECK FAILED — fix errors before rendering." >&2
    exit 1
}
echo "Sync check passed."
echo ""

for VOICE in "${VOICES[@]}"; do
    echo "── Rendering: $VOICE ──────────────────────────────────────────"

    OUT_DIR="media/videos/variables_et_polynomes_scene/${VOICE}"
    mkdir -p "$OUT_DIR"

    MANIM_VOICE="$VOICE" \
    SPEECH_KEY="$SPEECH_KEY" \
    SPEECH_REGION="$SPEECH_REGION" \
    "$MANIM" -qh "$SCENE" "$CLASS" \
        -r 1920,1080 \
        --media_dir "media/videos/variables_et_polynomes_scene/${VOICE}" \
        2>&1 | tail -6

    # Copy outputs to the voice-named directory for easy comparison
    SRC="media/videos/variables_et_polynomes_scene/${VOICE}/videos/variables_et_polynomes_scene/1080p60"
    if [[ -d "$SRC" ]]; then
        cp "$SRC/${CLASS}.mp4"  "$OUT_DIR/${CLASS}_${VOICE}.mp4"  2>/dev/null || true
        cp "$SRC/${CLASS}.srt"  "$OUT_DIR/${CLASS}_${VOICE}.srt"  2>/dev/null || true
        echo "  → $OUT_DIR/${CLASS}_${VOICE}.mp4"
    fi
    echo ""
done

echo "All voices rendered."
echo "Compare outputs in: media/videos/variables_et_polynomes_scene/"
