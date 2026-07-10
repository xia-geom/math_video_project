# Video Audit: CompleteTheSquare

Generated: 2026-05-16 20:52:22

## Executive Summary

- Scene: `scenes/complete_the_square_fr/complete_the_square_scene.py`
- Video: `dist/CompleteTheSquare/CompleteTheSquare.mp4`
- Frame artifacts: `reports/video_audits/CompleteTheSquare_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 2 warning, 0 polish, 8 info.

## Blocking Issues

None.

## Warnings

1. **[VisualFrameAgent] Blank or near-flat sampled frames**
   - Category: `visual`
   - Detail: Frame sample(s) [6, 7] look blank or nearly flat.
   - Fix: Inspect the contact sheet and adjust scene timing or object visibility.

2. **[VisualFrameAgent] Low average contrast**
   - Category: `visual`
   - Detail: Sampled frames have low grayscale contrast.
   - Fix: Use stronger black strokes/text or reduce pale fills.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] No SRT beside MP4**
   - Category: `captions`
   - Location: `dist/CompleteTheSquare/CompleteTheSquare.srt`
   - Detail: `dist/CompleteTheSquare/CompleteTheSquare.srt` does not exist.
   - Fix: Expected for silent previews; render with voiceover/subcaptions for final caption QA.

2. **[AudioCaptionAgent] No audio stream**
   - Category: `audio`
   - Location: `dist/CompleteTheSquare/CompleteTheSquare.mp4`
   - Detail: The MP4 has no audio stream.
   - Fix: This is expected for silent previews; render with Azure credentials for final narration.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/CompleteTheSquare/CompleteTheSquare.mp4`
   - Detail: Duration 91.9s, resolution 854x480, frame rate 15.00 fps.
   - Fix: No action needed.

4. **[RenderMetadataAgent] Preview-resolution render**
   - Category: `format`
   - Location: `dist/CompleteTheSquare/CompleteTheSquare.mp4`
   - Detail: Resolution is 854x480.
   - Fix: Expected for low-quality silent previews; use `qh` or `-r 1920,1080` for final review.

5. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

6. **[SourceScriptAgent] Manual narration pacing detected**
   - Category: `sync`
   - Location: `scenes/complete_the_square_fr/complete_the_square_scene.py`
   - Detail: The scene uses paced narration helpers instead of SSML bookmarks.
   - Fix: No action needed unless tight word-level animation sync is required.

7. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/complete_the_square_fr/complete_the_square_scene.py:41`
   - Detail: `CompleteTheSquare` is defined.
   - Fix: No action needed.

8. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/CompleteTheSquare_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/complete_the_square_fr/complete_the_square_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/complete_the_square_fr/complete_the_square_scene.py CompleteTheSquare ql
./.venv/bin/python scripts/audit_video.py --scene scenes/complete_the_square_fr/complete_the_square_scene.py --class CompleteTheSquare --video dist/CompleteTheSquare/CompleteTheSquare.mp4 --out reports/video_audits/CompleteTheSquare_audit.md --silent-preview
```
