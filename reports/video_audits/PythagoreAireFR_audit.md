# Video Audit: PythagoreAireFR

Generated: 2026-05-16 20:49:41

## Executive Summary

- Scene: `scenes/pythagore_whiteboard_fr/pythagore_scene.py`
- Video: `dist/PythagoreAireFR/PythagoreAireFR.mp4`
- Frame artifacts: `reports/video_audits/PythagoreAireFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 0 polish, 7 info.

## Blocking Issues

None.

## Warnings

1. **[VisualFrameAgent] Blank or near-flat sampled frames**
   - Category: `visual`
   - Detail: Frame sample(s) [2, 3, 7] look blank or nearly flat.
   - Fix: Inspect the contact sheet and adjust scene timing or object visibility.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] No SRT beside MP4**
   - Category: `captions`
   - Location: `dist/PythagoreAireFR/PythagoreAireFR.srt`
   - Detail: `dist/PythagoreAireFR/PythagoreAireFR.srt` does not exist.
   - Fix: Expected for silent previews; render with voiceover/subcaptions for final caption QA.

2. **[AudioCaptionAgent] No audio stream**
   - Category: `audio`
   - Location: `dist/PythagoreAireFR/PythagoreAireFR.mp4`
   - Detail: The MP4 has no audio stream.
   - Fix: This is expected for silent previews; render with Azure credentials for final narration.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/PythagoreAireFR/PythagoreAireFR.mp4`
   - Detail: Duration 34.9s, resolution 854x480, frame rate 15.00 fps.
   - Fix: No action needed.

4. **[RenderMetadataAgent] Preview-resolution render**
   - Category: `format`
   - Location: `dist/PythagoreAireFR/PythagoreAireFR.mp4`
   - Detail: Resolution is 854x480.
   - Fix: Expected for low-quality silent previews; use `qh` or `-r 1920,1080` for final review.

5. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

6. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/pythagore_whiteboard_fr/pythagore_scene.py:64`
   - Detail: `PythagoreAireFR` is defined.
   - Fix: No action needed.

7. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/PythagoreAireFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/pythagore_whiteboard_fr/pythagore_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/pythagore_whiteboard_fr/pythagore_scene.py PythagoreAireFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/pythagore_whiteboard_fr/pythagore_scene.py --class PythagoreAireFR --video dist/PythagoreAireFR/PythagoreAireFR.mp4 --out reports/video_audits/PythagoreAireFR_audit.md --silent-preview
```
