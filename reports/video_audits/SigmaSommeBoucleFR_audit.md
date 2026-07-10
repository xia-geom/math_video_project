# Video Audit: SigmaSommeBoucleFR

Generated: 2026-05-16 20:51:04

## Executive Summary

- Scene: `scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py`
- Video: `dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.mp4`
- Frame artifacts: `reports/video_audits/SigmaSommeBoucleFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 0 warning, 0 polish, 9 info.

## Blocking Issues

None.

## Warnings

None.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] No audio stream**
   - Category: `audio`
   - Location: `dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.mp4`
   - Detail: The MP4 has no audio stream.
   - Fix: This is expected for silent previews; render with Azure credentials for final narration.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.srt`
   - Detail: Parsed 5 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.mp4`
   - Detail: Duration 90.8s, resolution 854x480, frame rate 15.00 fps.
   - Fix: No action needed.

4. **[RenderMetadataAgent] Preview-resolution render**
   - Category: `format`
   - Location: `dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.mp4`
   - Detail: Resolution is 854x480.
   - Fix: Expected for low-quality silent previews; use `qh` or `-r 1920,1080` for final review.

5. **[SourceScriptAgent] External audio workflow detected**
   - Category: `voiceover`
   - Location: `scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py`
   - Detail: The scene uses optional local audio files and Manim subcaptions rather than Azure TTS.
   - Fix: No action needed unless this scene should be migrated to the shared TTS workflow.

6. **[SourceScriptAgent] Fixed-timing caption workflow detected**
   - Category: `sync`
   - Location: `scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py`
   - Detail: The scene uses timed Manim captions instead of SSML bookmarks.
   - Fix: No action needed unless tight word-level animation sync is required.

7. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

8. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py:8`
   - Detail: `SigmaSommeBoucleFR` is defined.
   - Fix: No action needed.

9. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/SigmaSommeBoucleFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py SigmaSommeBoucleFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py --class SigmaSommeBoucleFR --video dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.mp4 --out reports/video_audits/SigmaSommeBoucleFR_audit.md --silent-preview
```
