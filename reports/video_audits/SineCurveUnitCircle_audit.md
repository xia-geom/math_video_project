# Video Audit: SineCurveUnitCircle

Generated: 2026-07-31 00:11:32

## Executive Summary

- Scene: `scenes/trigonometrie_fr/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr_scene.py`
- Video: `dist/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr.mp4`
- Frame artifacts: `reports/video_audits/SineCurveUnitCircle_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 0 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] No SSML bookmarks detected**
   - Category: `sync`
   - Location: `scenes/trigonometrie_fr/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr_scene.py`
   - Detail: The narration has no explicit sync points.
   - Fix: Add `<bookmark mark='...'>` markers and wait for them around key animations.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr.mp4`
   - Detail: Audio duration 184.8s, average -25.5 dBFS, peak -6.7 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr.srt`
   - Detail: Parsed 36 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr.mp4`
   - Detail: Duration 185.7s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/trigonometrie_fr/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr_scene.py:105`
   - Detail: `SineCurveUnitCircle` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/SineCurveUnitCircle_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/trigonometrie_fr/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/trigonometrie_fr/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr_scene.py SineCurveUnitCircle ql
./.venv/bin/python scripts/audit_video.py --scene scenes/trigonometrie_fr/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr_scene.py --class SineCurveUnitCircle --video dist/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr.mp4 --out reports/video_audits/SineCurveUnitCircle_audit.md --silent-preview
```
