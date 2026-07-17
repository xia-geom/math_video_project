# Video Audit: SigmaSommeBoucleFR

Generated: 2026-07-17 16:29:57

## Executive Summary

- Scene: `scenes/notations_fr/14_notation_sigma_fr/14_notation_sigma_fr_scene.py`
- Video: `dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.mp4`
- Frame artifacts: `reports/video_audits/SigmaSommeBoucleFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 0 warning, 0 polish, 8 info.

## Blocking Issues

None.

## Warnings

None.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.mp4`
   - Detail: Audio duration 90.4s, average -19.3 dBFS, peak -2.8 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.srt`
   - Detail: Parsed 5 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.mp4`
   - Detail: Duration 90.8s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] External audio workflow detected**
   - Category: `voiceover`
   - Location: `scenes/notations_fr/14_notation_sigma_fr/14_notation_sigma_fr_scene.py`
   - Detail: The scene uses optional local audio files and Manim subcaptions rather than Azure TTS.
   - Fix: No action needed unless this scene should be migrated to the shared TTS workflow.

5. **[SourceScriptAgent] Fixed-timing caption workflow detected**
   - Category: `sync`
   - Location: `scenes/notations_fr/14_notation_sigma_fr/14_notation_sigma_fr_scene.py`
   - Detail: The scene uses timed Manim captions instead of SSML bookmarks.
   - Fix: No action needed unless tight word-level animation sync is required.

6. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

7. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/notations_fr/14_notation_sigma_fr/14_notation_sigma_fr_scene.py:8`
   - Detail: `SigmaSommeBoucleFR` is defined.
   - Fix: No action needed.

8. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/SigmaSommeBoucleFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/notations_fr/14_notation_sigma_fr/14_notation_sigma_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/notations_fr/14_notation_sigma_fr/14_notation_sigma_fr_scene.py SigmaSommeBoucleFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/notations_fr/14_notation_sigma_fr/14_notation_sigma_fr_scene.py --class SigmaSommeBoucleFR --video dist/SigmaSommeBoucleFR/SigmaSommeBoucleFR.mp4 --out reports/video_audits/SigmaSommeBoucleFR_audit.md --silent-preview
```
