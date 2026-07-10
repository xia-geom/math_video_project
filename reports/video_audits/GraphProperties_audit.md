# Video Audit: GraphProperties

Generated: 2026-05-16 20:53:02

## Executive Summary

- Scene: `scenes/graph_properties_fr/graph_properties_scene.py`
- Video: `dist/GraphProperties/GraphProperties.mp4`
- Frame artifacts: `reports/video_audits/GraphProperties_audit_frames`
- Silent preview mode: `True`
- Findings: 0 blocker, 1 warning, 1 polish, 8 info.

## Blocking Issues

None.

## Warnings

1. **[VisualFrameAgent] Blank or near-flat sampled frames**
   - Category: `visual`
   - Detail: Frame sample(s) [5] look blank or nearly flat.
   - Fix: Inspect the contact sheet and adjust scene timing or object visibility.

## Polish Items

1. **[PedagogyAccessibilityAgent] Color-coded meaning should be double encoded**
   - Category: `accessibility`
   - Location: `scenes/graph_properties_fr/graph_properties_scene.py`
   - Detail: The scene uses several semantic colors.
   - Fix: Ensure every color distinction is also labeled with text, shape, position, or stroke style.

## Informational Notes

1. **[AudioCaptionAgent] No SRT beside MP4**
   - Category: `captions`
   - Location: `dist/GraphProperties/GraphProperties.srt`
   - Detail: `dist/GraphProperties/GraphProperties.srt` does not exist.
   - Fix: Expected for silent previews; render with voiceover/subcaptions for final caption QA.

2. **[AudioCaptionAgent] No audio stream**
   - Category: `audio`
   - Location: `dist/GraphProperties/GraphProperties.mp4`
   - Detail: The MP4 has no audio stream.
   - Fix: This is expected for silent previews; render with Azure credentials for final narration.

3. **[RenderMetadataAgent] Metadata summary**
   - Category: `render`
   - Location: `dist/GraphProperties/GraphProperties.mp4`
   - Detail: Duration 132.0s, resolution 854x480, frame rate 15.00 fps.
   - Fix: No action needed.

4. **[RenderMetadataAgent] Preview-resolution render**
   - Category: `format`
   - Location: `dist/GraphProperties/GraphProperties.mp4`
   - Detail: Resolution is 854x480.
   - Fix: Expected for low-quality silent previews; use `qh` or `-r 1920,1080` for final review.

5. **[SourceScriptAgent] Legacy SSML checker not applicable**
   - Category: `sync`
   - Detail: The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.
   - Fix: No action needed unless this scene is intended to use the legacy constants.

6. **[SourceScriptAgent] Manual narration pacing detected**
   - Category: `sync`
   - Location: `scenes/graph_properties_fr/graph_properties_scene.py`
   - Detail: The scene uses paced narration helpers instead of SSML bookmarks.
   - Fix: No action needed unless tight word-level animation sync is required.

7. **[SourceScriptAgent] Scene class found**
   - Category: `source`
   - Location: `scenes/graph_properties_fr/graph_properties_scene.py:167`
   - Detail: `GraphProperties` is defined.
   - Fix: No action needed.

8. **[VisualFrameAgent] Contact sheet generated**
   - Category: `visual`
   - Location: `reports/video_audits/GraphProperties_audit_frames/contact_sheet.png`
   - Detail: Sampled frames were written for visual review.
   - Fix: Open the contact sheet when reviewing visual layout.

## Recommended Commands

```bash
./.venv/bin/python -m py_compile scenes/graph_properties_fr/graph_properties_scene.py
MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh scenes/graph_properties_fr/graph_properties_scene.py GraphProperties ql
./.venv/bin/python scripts/audit_video.py --scene scenes/graph_properties_fr/graph_properties_scene.py --class GraphProperties --video dist/GraphProperties/GraphProperties.mp4 --out reports/video_audits/GraphProperties_audit.md --silent-preview
```
