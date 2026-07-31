# Video Audit: OperationsMatricesFR

Generated: 2026-07-31 00:12:11

## Executive Summary

- Scene: `scenes/matrices_fr/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr_scene.py`
- Video: `dist/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr.mp4`
- Frame artifacts: `reports/video_audits/OperationsMatricesFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 3 warning, 0 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] Bookmarks without waits**
   - Category: `sync`
   - Location: `scenes/matrices_fr/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr_scene.py`
   - Detail: 28 bookmark(s) are never waited for: bad_grid, composition_name, first_action, first_column, left_path, matching_grid, neq, output_grid.
   - Fix: Either add `wait_until_bookmark(...)` calls or remove unused bookmarks.

2. **[SourceScriptAgent] Long captions detected**
   - Category: `captions`
   - Location: `scenes/matrices_fr/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr_scene.py`
   - Detail: 3 caption(s) exceed the 55-character guideline. line 91: 'Pourquoi l’addition et le produit suivent-ils des règles différentes ?'; line 139: 'Le produit transforme les colonnes de la matrice de droite.'; line 168: 'Mêmes cases, même scalaire, ou composition de transformations.'
   - Fix: Shorten captions or split the narration into smaller voiceover blocks.

3. **[VisualFrameAgent] Blank or near-flat sampled frames**
   - Category: `visual`
   - Detail: Frame sample(s) [3] look blank or nearly flat.
   - Fix: Inspect the contact sheet and adjust scene timing or object visibility.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr.mp4`
   - Detail: Audio duration 214.4s, average -25.4 dBFS, peak -7.0 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr.srt`
   - Detail: Parsed 9 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr.mp4`
   - Detail: Duration 215.3s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/matrices_fr/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr_scene.py:187`
   - Detail: `OperationsMatricesFR` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/OperationsMatricesFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/matrices_fr/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/matrices_fr/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr_scene.py OperationsMatricesFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/matrices_fr/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr_scene.py --class OperationsMatricesFR --video dist/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr.mp4 --out reports/video_audits/OperationsMatricesFR_audit.md --silent-preview
```
