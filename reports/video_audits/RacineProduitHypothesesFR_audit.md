# Video Audit: RacineProduitHypothesesFR

Generated: 2026-07-17 16:30:16

## Executive Summary

- Scene: `scenes/erreurs_frequentes_fr/03_racine_d_un_produit_fr/03_racine_d_un_produit_fr_scene.py`
- Video: `dist/RacineProduitHypothesesFR/RacineProduitHypothesesFR.mp4`
- Frame artifacts: `reports/video_audits/RacineProduitHypothesesFR_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 0 warning, 0 polish, 7 info.

## Blocking Issues

None.

## Warnings

None.

## Polish Items

None.

## Informational Notes

1. **[AudioCaptionAgent] No SRT beside MP4**
   - Category: `captions`
   - Location: `dist/RacineProduitHypothesesFR/RacineProduitHypothesesFR.srt`
   - Detail: `dist/RacineProduitHypothesesFR/RacineProduitHypothesesFR.srt` does not exist.
   - Fix: Expected for silent previews; render with voiceover/subcaptions for final caption QA.

2. **[AudioCaptionAgent] No audio stream**
   - Category: `audio`
   - Location: `dist/RacineProduitHypothesesFR/RacineProduitHypothesesFR.mp4`
   - Detail: The MP4 has no audio stream.
   - Fix: This is expected for silent previews; render with Azure credentials for final narration.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/RacineProduitHypothesesFR/RacineProduitHypothesesFR.mp4`
   - Detail: Duration 63.3s, resolution 854x480, frame rate 15.00 fps.
   - Fix: No action needed.

4. **[RenderMetadataAgent] Preview-resolution render**
   - Category: `format`
   - Location: `dist/RacineProduitHypothesesFR/RacineProduitHypothesesFR.mp4`
   - Detail: Resolution is 854x480.
   - Fix: Expected for low-quality silent previews; use `qh` or `-r 1920,1080` for final review.

5. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

6. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/erreurs_frequentes_fr/03_racine_d_un_produit_fr/03_racine_d_un_produit_fr_scene.py:53`
   - Detail: `RacineProduitHypothesesFR` is defined.
   - Fix: No action needed.

7. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/RacineProduitHypothesesFR_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/erreurs_frequentes_fr/03_racine_d_un_produit_fr/03_racine_d_un_produit_fr_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/erreurs_frequentes_fr/03_racine_d_un_produit_fr/03_racine_d_un_produit_fr_scene.py RacineProduitHypothesesFR ql
./.venv/bin/python scripts/audit_video.py --scene scenes/erreurs_frequentes_fr/03_racine_d_un_produit_fr/03_racine_d_un_produit_fr_scene.py --class RacineProduitHypothesesFR --video dist/RacineProduitHypothesesFR/RacineProduitHypothesesFR.mp4 --out reports/video_audits/RacineProduitHypothesesFR_audit.md --silent-preview
```
