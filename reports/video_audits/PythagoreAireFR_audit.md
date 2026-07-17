# Video Audit: PythagoreAireFR

Generated: 2026-07-17 16:29:48

## Executive Summary

- Scene: `scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py`
- Video: `dist/PythagoreAireFR/PythagoreAireFR.mp4`
- Frame artifacts: `reports/video_audits/PythagoreAireFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 0 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[VisualFrameAgent] Blank or near-flat sampled frames**
   - Category: `visual`
   - Detail: Frame sample(s) [2] look blank or nearly flat.
   - Fix: Inspect the contact sheet and adjust scene timing or object visibility.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/PythagoreAireFR/PythagoreAireFR.mp4`
   - Detail: Audio duration 84.4s, average -25.9 dBFS, peak -6.5 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/PythagoreAireFR/PythagoreAireFR.srt`
   - Detail: Parsed 15 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/PythagoreAireFR/PythagoreAireFR.mp4`
   - Detail: Duration 87.7s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py:65`
   - Detail: `PythagoreAireFR` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/PythagoreAireFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py PythagoreAireFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py --class PythagoreAireFR --video dist/PythagoreAireFR/PythagoreAireFR.mp4 --out reports/video_audits/PythagoreAireFR_audit.md --silent-preview
```
