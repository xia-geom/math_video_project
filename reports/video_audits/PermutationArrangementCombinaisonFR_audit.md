# Video Audit: PermutationArrangementCombinaisonFR

Generated: 2026-07-31 00:11:51

## Executive Summary

- Scene: `scenes/probabilites_fr/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr_scene.py`
- Video: `dist/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr.mp4`
- Frame artifacts: `reports/video_audits/PermutationArrangementCombinaisonFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 0 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] Long captions detected**
   - Category: `captions`
   - Location: `scenes/probabilites_fr/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr_scene.py`
   - Detail: 7 caption(s) exceed the 55-character guideline. line 90: "Trois personnes parmi cinq : 60 ou 10 selon le rôle de l'ordre."; line 105: 'Arrangement : on choisit r éléments parmi n et leurs positions compten'; line 124: 'Combinaison : les mêmes r éléments forment un seul groupe, quel que so'; line 142: "Permutation : tous les n éléments sont utilisés et l'ordre compte."
   - Fix: Shorten captions or split the narration into smaller voiceover blocks.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr.mp4`
   - Detail: Audio duration 359.6s, average -25.7 dBFS, peak -6.9 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr.srt`
   - Detail: Parsed 11 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr.mp4`
   - Detail: Duration 360.7s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/probabilites_fr/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr_scene.py:224`
   - Detail: `PermutationArrangementCombinaisonFR` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/PermutationArrangementCombinaisonFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/probabilites_fr/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/probabilites_fr/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr_scene.py PermutationArrangementCombinaisonFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/probabilites_fr/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr_scene.py --class PermutationArrangementCombinaisonFR --video dist/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr.mp4 --out reports/video_audits/PermutationArrangementCombinaisonFR_audit.md --silent-preview
```
