# Video Audit: CircleAreaFR

Generated: 2026-05-16 20:53:07

## Executive Summary

- Scene: `scenes/circle_area/circle_area_scenes.py`
- Video: `dist/CircleAreaFR/CircleAreaFR.mp4`
- Frame artifacts: `reports/video_audits/CircleAreaFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 1 polish, 7 info.

## Blocking Issues

None.

## Warnings

1. **[VisualFrameAgent] Low average contrast**
   - Category: `visual`
   - Detail: Sampled frames have low grayscale contrast.
   - Fix: Use stronger black strokes/text or reduce pale fills.

## Polish Items

1. **[PedagogyAccessibilityAgent] Color-coded meaning should be double encoded**
   - Category: `accessibility`
   - Location: `scenes/circle_area/circle_area_scenes.py`
   - Detail: The scene uses several semantic colors.
   - Fix: Ensure every color distinction is also labeled with text, shape, position, or stroke style.

## Informational Notes

1. **[AudioCaptionAgent] No SRT beside MP4**
   - Category: `captions`
   - Location: `dist/CircleAreaFR/CircleAreaFR.srt`
   - Detail: `dist/CircleAreaFR/CircleAreaFR.srt` does not exist.
   - Fix: Expected for silent previews; render with voiceover/subcaptions for final caption QA.

2. **[AudioCaptionAgent] No audio stream**
   - Category: `audio`
   - Location: `dist/CircleAreaFR/CircleAreaFR.mp4`
   - Detail: The MP4 has no audio stream.
   - Fix: This is expected for silent previews; render with Azure credentials for final narration.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/CircleAreaFR/CircleAreaFR.mp4`
   - Detail: Duration 28.4s, resolution 854x480, frame rate 15.00 fps.
   - Fix: No action needed.

4. **[RenderMetadataAgent] Preview-resolution render**
   - Category: `format`
   - Location: `dist/CircleAreaFR/CircleAreaFR.mp4`
   - Detail: Resolution is 854x480.
   - Fix: Expected for low-quality silent previews; use `qh` or `-r 1920,1080` for final review.

5. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

6. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/circle_area/circle_area_scenes.py:213`
   - Detail: `CircleAreaFR` is defined.
   - Fix: No action needed.

7. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/CircleAreaFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/circle_area/circle_area_scenes.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/circle_area/circle_area_scenes.py CircleAreaFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/circle_area/circle_area_scenes.py --class CircleAreaFR --video dist/CircleAreaFR/CircleAreaFR.mp4 --out reports/video_audits/CircleAreaFR_audit.md --silent-preview
```
