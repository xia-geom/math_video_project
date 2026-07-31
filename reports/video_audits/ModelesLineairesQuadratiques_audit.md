# Video Audit: ModelesLineairesQuadratiques

Generated: 2026-07-31 00:11:19

## Executive Summary

- Scene: `scenes/fonctions_et_graphiques_fr/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr_scene.py`
- Video: `dist/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr.mp4`
- Frame artifacts: `reports/video_audits/ModelesLineairesQuadratiques_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 1 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] Long captions detected**
   - Category: `captions`
   - Location: `scenes/fonctions_et_graphiques_fr/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr_scene.py`
   - Detail: 2 caption(s) exceed the 55-character guideline. line 84: 'Quadratique : les premiers écarts changent régulièrement.'; line 111: "Affine ou quadratique : quel niveau d'écart est constant ?"
   - Fix: Shorten captions or split the narration into smaller voiceover blocks.

## Polish Items

1. **[PedagogyAccessibilityAgent] Color-coded meaning should be double encoded**
   - Category: `accessibility`
   - Location: `scenes/fonctions_et_graphiques_fr/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr_scene.py`
   - Detail: The scene uses several semantic colors.
   - Fix: Ensure every color distinction is also labeled with text, shape, position, or stroke style.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr.mp4`
   - Detail: Audio duration 296.1s, average -25.6 dBFS, peak -7.3 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr.srt`
   - Detail: Parsed 7 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr.mp4`
   - Detail: Duration 296.1s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/fonctions_et_graphiques_fr/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr_scene.py:158`
   - Detail: `ModelesLineairesQuadratiques` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/ModelesLineairesQuadratiques_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/fonctions_et_graphiques_fr/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/fonctions_et_graphiques_fr/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr_scene.py ModelesLineairesQuadratiques ql
./.venv/bin/python scripts/audit_video.py --scene scenes/fonctions_et_graphiques_fr/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr_scene.py --class ModelesLineairesQuadratiques --video dist/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr.mp4 --out reports/video_audits/ModelesLineairesQuadratiques_audit.md --silent-preview
```
