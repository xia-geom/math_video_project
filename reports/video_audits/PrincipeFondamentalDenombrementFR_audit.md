# Video Audit: PrincipeFondamentalDenombrementFR

Generated: 2026-07-31 00:11:47

## Executive Summary

- Scene: `scenes/probabilites_fr/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr_scene.py`
- Video: `dist/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr.mp4`
- Frame artifacts: `reports/video_audits/PrincipeFondamentalDenombrementFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 0 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] Long captions detected**
   - Category: `captions`
   - Location: `scenes/probabilites_fr/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr_scene.py`
   - Detail: 5 caption(s) exceed the 55-character guideline. line 118: 'Chaque feuille de l’arbre est un résultat complet distinct.'; line 146: 'Avec plusieurs étapes régulières, on multiplie tous les nombres de cho'; line 159: 'L’opération dépend de la structure des résultats, pas d’un mot isolé.'; line 174: 'Branches inégales : séparer les cas, puis additionner leurs totaux.'
   - Fix: Shorten captions or split the narration into smaller voiceover blocks.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr.mp4`
   - Detail: Audio duration 275.8s, average -25.7 dBFS, peak -7.4 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr.srt`
   - Detail: Parsed 9 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr.mp4`
   - Detail: Duration 275.8s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/probabilites_fr/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr_scene.py:212`
   - Detail: `PrincipeFondamentalDenombrementFR` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/PrincipeFondamentalDenombrementFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/probabilites_fr/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/probabilites_fr/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr_scene.py PrincipeFondamentalDenombrementFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/probabilites_fr/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr_scene.py --class PrincipeFondamentalDenombrementFR --video dist/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr.mp4 --out reports/video_audits/PrincipeFondamentalDenombrementFR_audit.md --silent-preview
```
