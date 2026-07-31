# Video Audit: DeterminantEtMatriceInverseFR

Generated: 2026-07-31 00:12:14

## Executive Summary

- Scene: `scenes/matrices_fr/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr_scene.py`
- Video: `dist/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr.mp4`
- Frame artifacts: `reports/video_audits/DeterminantEtMatriceInverseFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 1 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] Long captions detected**
   - Category: `captions`
   - Location: `scenes/matrices_fr/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr_scene.py`
   - Detail: 4 caption(s) exceed the 55-character guideline. line 171: 'Déterminant zéro : une surface est écrasée sur une ligne.'; line 185: 'Une sortie commune ne permet pas de retrouver deux entrées.'; line 197: 'Une vraie inverse défait effectivement la transformation.'; line 221: 'La formule de l’inverse vient d’un produit qui se simplifie.'
   - Fix: Shorten captions or split the narration into smaller voiceover blocks.

## Polish Items

1. **[PedagogyAccessibilityAgent] Color-coded meaning should be double encoded**
   - Category: `accessibility`
   - Location: `scenes/matrices_fr/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr_scene.py`
   - Detail: The scene uses several semantic colors.
   - Fix: Ensure every color distinction is also labeled with text, shape, position, or stroke style.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr.mp4`
   - Detail: Audio duration 230.8s, average -25.0 dBFS, peak -7.1 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr.srt`
   - Detail: Parsed 9 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr.mp4`
   - Detail: Duration 231.7s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/matrices_fr/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr_scene.py:256`
   - Detail: `DeterminantEtMatriceInverseFR` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/DeterminantEtMatriceInverseFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/matrices_fr/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/matrices_fr/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr_scene.py DeterminantEtMatriceInverseFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/matrices_fr/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr_scene.py --class DeterminantEtMatriceInverseFR --video dist/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr.mp4 --out reports/video_audits/DeterminantEtMatriceInverseFR_audit.md --silent-preview
```
