# Video Audit: CompleteTheSquare

Generated: 2026-07-31 00:11:35

## Executive Summary

- Scene: `scenes/algebre_et_polynomes_fr/13_completer_le_carre_fr/13_completer_le_carre_fr_scene.py`
- Video: `dist/13_completer_le_carre_fr/13_completer_le_carre_fr.mp4`
- Frame artifacts: `reports/video_audits/CompleteTheSquare_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 0 warning, 0 polish, 7 info.

## Blocking Issues

None.

## Warnings

None.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/13_completer_le_carre_fr/13_completer_le_carre_fr.mp4`
   - Detail: Audio duration 226.2s, average -26.0 dBFS, peak -7.0 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/13_completer_le_carre_fr/13_completer_le_carre_fr.srt`
   - Detail: Parsed 48 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/13_completer_le_carre_fr/13_completer_le_carre_fr.mp4`
   - Detail: Duration 226.2s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Manual narration pacing detected**
   - Category: `sync`
   - Location: `scenes/algebre_et_polynomes_fr/13_completer_le_carre_fr/13_completer_le_carre_fr_scene.py`
   - Detail: The scene uses paced narration helpers instead of SSML bookmarks.
   - Fix: No action needed unless tight word-level animation sync is required.

6. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/algebre_et_polynomes_fr/13_completer_le_carre_fr/13_completer_le_carre_fr_scene.py:41`
   - Detail: `CompleteTheSquare` is defined.
   - Fix: No action needed.

7. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/CompleteTheSquare_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/algebre_et_polynomes_fr/13_completer_le_carre_fr/13_completer_le_carre_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/algebre_et_polynomes_fr/13_completer_le_carre_fr/13_completer_le_carre_fr_scene.py CompleteTheSquare ql
./.venv/bin/python scripts/audit_video.py --scene scenes/algebre_et_polynomes_fr/13_completer_le_carre_fr/13_completer_le_carre_fr_scene.py --class CompleteTheSquare --video dist/13_completer_le_carre_fr/13_completer_le_carre_fr.mp4 --out reports/video_audits/CompleteTheSquare_audit.md --silent-preview
```
