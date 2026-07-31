# Video Audit: FonctionsDomaineImageFR

Generated: 2026-07-31 00:11:15

## Executive Summary

- Scene: `scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py`
- Video: `dist/04_domaine_et_image_fr/04_domaine_et_image_fr.mp4`
- Frame artifacts: `reports/video_audits/FonctionsDomaineImageFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 1 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] Long captions detected**
   - Category: `captions`
   - Location: `scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py`
   - Detail: 2 caption(s) exceed the 55-character guideline. line 109: 'Une formule seule conduit à chercher son domaine naturel.'; line 120: 'Sous une racine carrée, le contenu doit être positif ou nul.'
   - Fix: Shorten captions or split the narration into smaller voiceover blocks.

## Polish Items

1. **[PedagogyAccessibilityAgent] Color-coded meaning should be double encoded**
   - Category: `accessibility`
   - Location: `scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py`
   - Detail: The scene uses several semantic colors.
   - Fix: Ensure every color distinction is also labeled with text, shape, position, or stroke style.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/04_domaine_et_image_fr/04_domaine_et_image_fr.mp4`
   - Detail: Audio duration 228.8s, average -25.8 dBFS, peak -7.8 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/04_domaine_et_image_fr/04_domaine_et_image_fr.srt`
   - Detail: Parsed 10 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/04_domaine_et_image_fr/04_domaine_et_image_fr.mp4`
   - Detail: Duration 228.8s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py:174`
   - Detail: `FonctionsDomaineImageFR` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/FonctionsDomaineImageFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py FonctionsDomaineImageFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py --class FonctionsDomaineImageFR --video dist/04_domaine_et_image_fr/04_domaine_et_image_fr.mp4 --out reports/video_audits/FonctionsDomaineImageFR_audit.md --silent-preview
```
