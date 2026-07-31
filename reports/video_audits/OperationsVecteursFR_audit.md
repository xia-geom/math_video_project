# Video Audit: OperationsVecteursFR

Generated: 2026-07-31 00:12:01

## Executive Summary

- Scene: `scenes/vecteurs_fr/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr_scene.py`
- Video: `dist/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr.mp4`
- Frame artifacts: `reports/video_audits/OperationsVecteursFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 2 warning, 0 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] Bookmarks without waits**
   - Category: `sync`
   - Location: `scenes/vecteurs_fr/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr_scene.py`
   - Detail: 26 bookmark(s) are never waited for: ab_arrow, ab_warning, ba_arrow, direct_sum, double, horizontal_sum, negative_half, opposite.
   - Fix: Either add `wait_until_bookmark(...)` calls or remove unused bookmarks.

2. **[SourceScriptAgent] Long captions detected**
   - Category: `captions`
   - Location: `scenes/vecteurs_fr/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr_scene.py`
   - Detail: 2 caption(s) exceed the 55-character guideline. line 91: 'Comment les coordonnées décrivent-elles un déplacement ?'; line 163: 'Mouvement, composantes, formule : trois vues d’une même opération.'
   - Fix: Shorten captions or split the narration into smaller voiceover blocks.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr.mp4`
   - Detail: Audio duration 181.3s, average -25.6 dBFS, peak -8.0 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr.srt`
   - Detail: Parsed 8 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr.mp4`
   - Detail: Duration 182.3s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/vecteurs_fr/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr_scene.py:184`
   - Detail: `OperationsVecteursFR` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/OperationsVecteursFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/vecteurs_fr/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/vecteurs_fr/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr_scene.py OperationsVecteursFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/vecteurs_fr/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr_scene.py --class OperationsVecteursFR --video dist/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr.mp4 --out reports/video_audits/OperationsVecteursFR_audit.md --silent-preview
```
