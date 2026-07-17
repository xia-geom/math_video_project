# Video Audit: Logarithme

Generated: 2026-07-17 16:30:02

## Executive Summary

- Scene: `scenes/exponentielles_et_logarithmes_fr/11_logarithmes_fr/11_logarithmes_fr_scene.py`
- Video: `dist/Logarithme/Logarithme.mp4`
- Frame artifacts: `reports/video_audits/Logarithme_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 1 polish, 8 info.

## Blocking Issues

None.

## Warnings

1. **[VisualFrameAgent] Blank or near-flat sampled frames**
   - Category: `visual`
   - Detail: Frame sample(s) [2] look blank or nearly flat.
   - Fix: Inspect the contact sheet and adjust scene timing or object visibility.

## Polish Items

1. **[PedagogyAccessibilityAgent] Color-coded meaning should be double encoded**
   - Category: `accessibility`
   - Location: `scenes/exponentielles_et_logarithmes_fr/11_logarithmes_fr/11_logarithmes_fr_scene.py`
   - Detail: The scene uses several semantic colors.
   - Fix: Ensure every color distinction is also labeled with text, shape, position, or stroke style.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/Logarithme/Logarithme.mp4`
   - Detail: Audio duration 272.2s, average -25.7 dBFS, peak -6.5 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/Logarithme/Logarithme.srt`
   - Detail: Parsed 63 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/Logarithme/Logarithme.mp4`
   - Detail: Duration 272.7s, resolution 854x480, frame rate 15.00 fps.
   - Fix: No action needed.

4. **[RenderMetadataAgent] Preview-resolution render**
   - Category: `format`
   - Location: `dist/Logarithme/Logarithme.mp4`
   - Detail: Resolution is 854x480.
   - Fix: Expected for low-quality silent previews; use `qh` or `-r 1920,1080` for final review.

5. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

6. **[SourceScriptAgent] Manual narration pacing detected**
   - Category: `sync`
   - Location: `scenes/exponentielles_et_logarithmes_fr/11_logarithmes_fr/11_logarithmes_fr_scene.py`
   - Detail: The scene uses paced narration helpers instead of SSML bookmarks.
   - Fix: No action needed unless tight word-level animation sync is required.

7. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/exponentielles_et_logarithmes_fr/11_logarithmes_fr/11_logarithmes_fr_scene.py:36`
   - Detail: `Logarithme` is defined.
   - Fix: No action needed.

8. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/Logarithme_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/exponentielles_et_logarithmes_fr/11_logarithmes_fr/11_logarithmes_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/exponentielles_et_logarithmes_fr/11_logarithmes_fr/11_logarithmes_fr_scene.py Logarithme ql
./.venv/bin/python scripts/audit_video.py --scene scenes/exponentielles_et_logarithmes_fr/11_logarithmes_fr/11_logarithmes_fr_scene.py --class Logarithme --video dist/Logarithme/Logarithme.mp4 --out reports/video_audits/Logarithme_audit.md --silent-preview
```
