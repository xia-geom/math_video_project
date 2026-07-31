# Video Audit: RepetitionsDenombrementFR

Generated: 2026-07-31 00:11:54

## Executive Summary

- Scene: `scenes/probabilites_fr/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr_scene.py`
- Video: `dist/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr.mp4`
- Frame artifacts: `reports/video_audits/RepetitionsDenombrementFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 0 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] Bookmarks without waits**
   - Category: `sync`
   - Location: `scenes/probabilites_fr/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr_scene.py`
   - Detail: 32 bookmark(s) are never waited for: banana_calculation, central_question, choose_first_zero, closing_left, closing_question, closing_right, combine_duplicates, end_banana_formula.
   - Fix: Either add `wait_until_bookmark(...)` calls or remove unused bookmarks.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr.mp4`
   - Detail: Audio duration 189.9s, average -25.4 dBFS, peak -7.1 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr.srt`
   - Detail: Parsed 37 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr.mp4`
   - Detail: Duration 191.1s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/probabilites_fr/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr_scene.py:185`
   - Detail: `RepetitionsDenombrementFR` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/RepetitionsDenombrementFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/probabilites_fr/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/probabilites_fr/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr_scene.py RepetitionsDenombrementFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/probabilites_fr/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr_scene.py --class RepetitionsDenombrementFR --video dist/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr.mp4 --out reports/video_audits/RepetitionsDenombrementFR_audit.md --silent-preview
```
