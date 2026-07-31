# Video Audit: VecteursR2R3FR

Generated: 2026-07-31 00:12:04

## Executive Summary

- Scene: `scenes/vecteurs_fr/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr_scene.py`
- Video: `dist/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr.mp4`
- Frame artifacts: `reports/video_audits/VecteursR2R3FR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 0 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[VisualFrameAgent] Blank or near-flat sampled frames**
   - Category: `visual`
   - Detail: Frame sample(s) [7] look blank or nearly flat.
   - Fix: Inspect the contact sheet and adjust scene timing or object visibility.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr.mp4`
   - Detail: Audio duration 190.5s, average -25.0 dBFS, peak -7.2 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr.srt`
   - Detail: Parsed 37 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr.mp4`
   - Detail: Duration 191.9s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/vecteurs_fr/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr_scene.py:156`
   - Detail: `VecteursR2R3FR` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/VecteursR2R3FR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/vecteurs_fr/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/vecteurs_fr/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr_scene.py VecteursR2R3FR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/vecteurs_fr/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr_scene.py --class VecteursR2R3FR --video dist/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr.mp4 --out reports/video_audits/VecteursR2R3FR_audit.md --silent-preview
```
