# Video Audit: VariablesEtPolynomes

Generated: 2026-07-31 00:11:25

## Executive Summary

- Scene: `scenes/algebre_et_polynomes_fr/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr_scene.py`
- Video: `dist/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr.mp4`
- Frame artifacts: `reports/video_audits/VariablesEtPolynomes_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 2 warning, 0 polish, 7 info.

## Blocking Issues

None.

## Warnings

1. **[VisualFrameAgent] Blank or near-flat sampled frames**
   - Category: `visual`
   - Detail: Frame sample(s) [5, 8] look blank or nearly flat.
   - Fix: Inspect the contact sheet and adjust scene timing or object visibility.

2. **[VisualFrameAgent] Low average contrast**
   - Category: `visual`
   - Detail: Sampled frames have low grayscale contrast.
   - Fix: Use stronger black strokes/text or reduce pale fills.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr.mp4`
   - Detail: Audio duration 109.8s, average -25.8 dBFS, peak -7.5 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr.srt`
   - Detail: Parsed 11 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr.mp4`
   - Detail: Duration 116.7s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker passed**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` returned success.
   - Fix: No action needed.

5. **[SourceScriptAgent] Manual narration pacing detected**
   - Category: `sync`
   - Location: `scenes/algebre_et_polynomes_fr/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr_scene.py`
   - Detail: The scene uses paced narration helpers instead of SSML bookmarks.
   - Fix: No action needed unless tight word-level animation sync is required.

6. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/algebre_et_polynomes_fr/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr_scene.py:192`
   - Detail: `VariablesEtPolynomes` is defined.
   - Fix: No action needed.

7. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/VariablesEtPolynomes_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/algebre_et_polynomes_fr/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/algebre_et_polynomes_fr/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr_scene.py VariablesEtPolynomes ql
./.venv/bin/python scripts/audit_video.py --scene scenes/algebre_et_polynomes_fr/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr_scene.py --class VariablesEtPolynomes --video dist/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr.mp4 --out reports/video_audits/VariablesEtPolynomes_audit.md --silent-preview
```
