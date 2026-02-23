# AGENT.md — Math Video Production Manual

This file is the authoritative production manual for coding agents and human contributors
working in this repository. Follow every section to produce videos that are consistent
with the existing series.

---

## 1. Project Purpose

Manim scenes for a French math-education video series.
Style: whiteboard (white background, black ink), pedagogical pacing, optional French TTS narration.
Reference quality: `pythagore_whiteboard_fr` and `function_intuitive_fr`.

---

## 2. Project Structure

```
math_video_project/
├── AGENT.md                      # This file
├── README.md
├── run.sh                        # Quick preview helper
├── tools/                        # Shared utilities / helpers
├── venv/  (or .venv/)            # Python virtual environment
│
├── <topic_slug>/                 # One directory per video
│   ├── <TopicSlug>_scene.py      # Main Manim scene(s)
│   ├── README.md                 # Topic-level notes
│   ├── render_voice_ssml.sh      # (optional) TTS render script
│   ├── subtitles_fr.srt          # (optional) Generated subtitle file
│   └── media/                    # Rendered outputs (gitignored)
│
└── media/                        # Global Manim output cache (gitignored)
```

### Naming conventions

| Item | Convention | Example |
|------|-----------|---------|
| Directory (topic slug) | `snake_case_fr` | `fourier_series_fr` |
| Scene file | `<topic_slug>_scene.py` | `fourier_series_scene.py` |
| Scene class | `PascalCaseFR` | `FourierSeriesFR` |
| SRT file | `subtitles_fr.srt` | — |
| Rendered MP4 | `<SceneClass>.mp4` | `FourierSeriesFR.mp4` |
| Low-quality preview | `<SceneClass>_low.mp4` | `FourierSeriesFR_low.mp4` |

---

---
