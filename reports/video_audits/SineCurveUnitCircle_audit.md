# Video Audit: SineCurveUnitCircle

Generated: 2026-07-17 16:30:04

## Executive Summary

- Scene: `scenes/trigonometrie_fr/13_du_cercle_au_sinus_fr/13_du_cercle_au_sinus_fr_scene.py`
- Video: `dist/SineCurveUnitCircle/SineCurveUnitCircle.mp4`
- Frame artifacts: `reports/video_audits/SineCurveUnitCircle_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 2 warning, 1 polish, 7 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] No SSML bookmarks detected**
   - Category: `sync`
   - Location: `scenes/trigonometrie_fr/13_du_cercle_au_sinus_fr/13_du_cercle_au_sinus_fr_scene.py`
   - Detail: The narration has no explicit sync points.
   - Fix: Add `<bookmark mark='...'>` markers and wait for them around key animations.

2. **[VisualFrameAgent] Blank or near-flat sampled frames**
   - Category: `visual`
   - Detail: Frame sample(s) [1, 2, 3, 4, 5, 6] look blank or nearly flat.
   - Fix: Inspect the contact sheet and adjust scene timing or object visibility.

## Polish Items

1. **[PedagogyAccessibilityAgent] Color-coded meaning should be double encoded**
   - Category: `accessibility`
   - Location: `scenes/trigonometrie_fr/13_du_cercle_au_sinus_fr/13_du_cercle_au_sinus_fr_scene.py`
   - Detail: The scene uses several semantic colors.
   - Fix: Ensure every color distinction is also labeled with text, shape, position, or stroke style.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/SineCurveUnitCircle/SineCurveUnitCircle.mp4`
   - Detail: Audio duration 200.9s, average -25.6 dBFS, peak -7.2 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/SineCurveUnitCircle/SineCurveUnitCircle.srt`
   - Detail: Parsed 41 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/SineCurveUnitCircle/SineCurveUnitCircle.mp4`
   - Detail: Duration 202.9s, resolution 854x480, frame rate 15.00 fps.
   - Fix: No action needed.

4. **[RenderMetadataAgent] Preview-resolution render**
   - Category: `format`
   - Location: `dist/SineCurveUnitCircle/SineCurveUnitCircle.mp4`
   - Detail: Resolution is 854x480.
   - Fix: Expected for low-quality silent previews; use `qh` or `-r 1920,1080` for final review.

5. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

6. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/trigonometrie_fr/13_du_cercle_au_sinus_fr/13_du_cercle_au_sinus_fr_scene.py:110`
   - Detail: `SineCurveUnitCircle` is defined.
   - Fix: No action needed.

7. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/SineCurveUnitCircle_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/trigonometrie_fr/13_du_cercle_au_sinus_fr/13_du_cercle_au_sinus_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/trigonometrie_fr/13_du_cercle_au_sinus_fr/13_du_cercle_au_sinus_fr_scene.py SineCurveUnitCircle ql
./.venv/bin/python scripts/audit_video.py --scene scenes/trigonometrie_fr/13_du_cercle_au_sinus_fr/13_du_cercle_au_sinus_fr_scene.py --class SineCurveUnitCircle --video dist/SineCurveUnitCircle/SineCurveUnitCircle.mp4 --out reports/video_audits/SineCurveUnitCircle_audit.md --silent-preview
```
