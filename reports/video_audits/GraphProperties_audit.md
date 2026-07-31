# Video Audit: GraphProperties

Generated: 2026-07-31 00:11:39

## Executive Summary

- Scene: `scenes/fonctions_et_graphiques_fr/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr_scene.py`
- Video: `dist/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr.mp4`
- Frame artifacts: `reports/video_audits/GraphProperties_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 2 warning, 1 polish, 6 info.

## Blocking Issues

None.

## Warnings

1. **[SourceScriptAgent] Bookmarks without waits**
   - Category: `sync`
   - Location: `scenes/fonctions_et_graphiques_fr/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr_scene.py`
   - Detail: 24 bookmark(s) are never waited for: compress_formula, compress_graph, compress_point, compress_reason, h_formula, h_graph, h_reason, parabola_reflect.
   - Fix: Either add `wait_until_bookmark(...)` calls or remove unused bookmarks.

2. **[VisualFrameAgent] Blank or near-flat sampled frames**
   - Category: `visual`
   - Detail: Frame sample(s) [5] look blank or nearly flat.
   - Fix: Inspect the contact sheet and adjust scene timing or object visibility.

## Polish Items

1. **[PedagogyAccessibilityAgent] Color-coded meaning should be double encoded**
   - Category: `accessibility`
   - Location: `scenes/fonctions_et_graphiques_fr/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr_scene.py`
   - Detail: The scene uses several semantic colors.
   - Fix: Ensure every color distinction is also labeled with text, shape, position, or stroke style.

## Informational Notes

1. **[AudioCaptionAgent] Audio summary**
   - Category: `audio`
   - Location: `dist/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr.mp4`
   - Detail: Audio duration 402.7s, average -25.7 dBFS, peak -7.5 dBFS.
   - Fix: No action needed.

2. **[AudioCaptionAgent] SRT timing parsed**
   - Category: `captions`
   - Location: `dist/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr.srt`
   - Detail: Parsed 82 subtitle entries.
   - Fix: No action needed.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr.mp4`
   - Detail: Duration 403.6s, resolution 1920x1080, frame rate 60.00 fps.
   - Fix: No action needed.

4. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

5. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/fonctions_et_graphiques_fr/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr_scene.py:243`
   - Detail: `GraphProperties` is defined.
   - Fix: No action needed.

6. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/GraphProperties_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/fonctions_et_graphiques_fr/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/fonctions_et_graphiques_fr/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr_scene.py GraphProperties ql
./.venv/bin/python scripts/audit_video.py --scene scenes/fonctions_et_graphiques_fr/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr_scene.py --class GraphProperties --video dist/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr.mp4 --out reports/video_audits/GraphProperties_audit.md --silent-preview
```
