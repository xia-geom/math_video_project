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
├── pyproject.toml                # Reproducible dependencies
│
├── scenes/                       # Production-ready videos (one dir per topic)
│   └── <topic_slug>/
│       ├── <topic_slug>_scene.py # Main Manim scene(s)
│       ├── README.md             # Topic-level notes (optional)
│       ├── render_voice_ssml.sh  # (optional) TTS render script
│       └── subtitles_fr.srt      # (optional) generated subtitle file
│
├── experiments/                  # Exploratory / in-progress work
│   └── <topic_slug>/
│       └── <topic_slug>_scene.py
│
├── tools/                        # Dev utilities (ssml_sync_check, etc.)
│   └── ssml_sync_check.py
│
├── scripts/
│   ├── render.sh                 # Quick preview helper (was run.sh)
│   └── grade_audit.py            # UQAM grade-sheet verifier (was web.py)
│
├── data/
│   └── raw/                      # Upstream data files, unmodified
│
├── assets/
│   └── branding/
│       └── uqam_logo.png
│
├── archive/                      # Safe trash — review before deleting
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

## 3. Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (first time or after pulling)
pip install -e .

# Quick preview (low quality, auto-open)
./scripts/render.sh scenes/<topic>/<topic>_scene.py SceneName

# High-quality export (1920×1080)
manim -pqh scenes/<topic>/<topic>_scene.py SceneName -r 1920,1080

# Medium quality (development iteration)
manim -pqm scenes/<topic>/<topic>_scene.py SceneName
```

---

## 4. Main Scene Entry Points

| Scene class | File | Status |
|-------------|------|--------|
| `FunctionIntuitive` | `scenes/function_intuitive_fr/function_intuitive_scene.py` | Complete |
| `SigmaSommeBoucleFR` | `scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py` | Complete |
| `PythagoreAireFR` | `scenes/pythagore_whiteboard_fr/pythagore_scene.py` | Complete |
| `VariablesEtPolynomesFR` | `scenes/variables_et_polynomes/variables_et_polynomes_scene.py` | Complete |
| `HyperbolicConeToCusp` | `scenes/hyperbolic_cone_to_cusp/hyperbolic_cone_to_cusp.py` | Complete |

---

## 5. Visual Style Guide

### 5.1 Canvas and colors

```python
config.background_color = WHITE   # always set at module level
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)
```

- Background: `WHITE`
- Primary ink: `BLACK` (stroke_width 2–4 for shapes, 3 for polygons)
- Accent: one color per video, typically `BLUE_D` or `BLUE`. Define once as `accent = BLUE_D`.
- Do **not** use gradients, drop shadows, or heavy fills. Fill opacity ≤ 0.15 unless the
  fill is the main pedagogical object.

### 5.2 Typography

| Element | Class | font_size |
|---------|-------|-----------|
| Video title | `Text` | 44–50 |
| Section heading / caption | `Text` | 28–34 |
| Body prose | `Text` | 28–34 |
| Math (inline) | `MathTex` | default (scaled ≈ 0.85–1.1×) |
| Math (featured) | `MathTex` | scaled 1.4–1.9× |
| Axis labels | `MathTex` | default |

Font: leave at Manim default (Latin Modern / DejaVu); do not specify `font=` unless
matching the whiteboard look requires it.

### 5.3 Layout

- Work in the default Manim frame (14.2 × 8 units, 16:9).
- Keep a margin of ≥ 0.5 units from all edges for text; ≥ 0.18 for caption boxes.
- Caption box: anchored to `DOWN` edge, buff 0.18. See the `_subtitle_box` helper below.
- Place the primary diagram slightly right of center when a text column appears on the left.
- Fade geometry and text out cleanly between scenes; do not let stale objects accumulate.

### 5.4 Pacing

The **voiceover track is the primary pacing driver**. Avoid “global pacing frameworks” (e.g. `play_paced()` wrappers or multiplying every `run_time`). They tend to make the code harder to read and they often slow *everything* uniformly, which is not what good teaching needs.

Preferred pacing strategy:

- **Audio first:** control speed and pauses with Azure `global_speed` plus SSML (`<prosody>`, `<break>`). This keeps speech natural and reduces the need to stretch animations.
- **Sync points:** use `<bookmark mark='...'>` in the narration text and `self.wait_until_bookmark("...")` to trigger key animations *exactly* when the voice reaches the concept (e.g., when a segment appears or a value changes).
- **Selective visuals:** only adjust `run_time` on the few animations that genuinely need more time (complex `Create`, long tracker sweeps, dense `TransformMatchingTex`).

Rule of thumb: if you want the viewer to slow down, first add a **spoken pause** (`<break>`) or a **bookmark**, not a new abstraction layer.
---

## 6. Voiceover + Captions Pipeline (NEW STANDARD)

The production standard is now **script-first narration with bookmarks**, as in `LawOfCos`:

- A `script` list holds the narration in order.
- Each narration item may contain SSML, especially `<bookmark .../>` markers.
- Animations are synchronized with `self.wait_until_bookmark("...")`.
- Captions/subtitles are **plain text** (no SSML tags).

### 6.1 Minimal baseline

Use `VoiceoverScene + AzureService` directly. Keep the scene code readable: **no pacing wrappers** (no `play_paced()`), and only small helpers (e.g., `uv(angle)` for geometry).

### 6.2 Script representation

Prefer **dict items** so captions stay clean while SSML stays expressive:

```python
script = [
  {
    "caption": "Considérons un triangle dont deux côtés mesurent A et B, et l’angle γ entre eux.",
    "ssml":    "Considérons un triangle dont deux côtés mesurent <say-as interpret-as='characters'>A</say-as> "
              "et <say-as interpret-as='characters'>B</say-as>, et l’angle <say-as interpret-as='characters'>γ</say-as> entre eux.",
  },
  {
    "caption": "La hauteur vaut B sin γ.",
    "ssml":    "La hauteur vaut <bookmark mark='triangle'/> <say-as interpret-as='characters'>B</say-as> sinus "
              "<say-as interpret-as='characters'>γ</say-as>. <bookmark mark='length'/>",
  },
]
```

- `caption`: what you want on screen / in SRT (plain French, concise).
- `ssml`: what Azure reads (may include bookmarks, breaks, phonemes, say-as, etc.).

If you really want a single source of truth, keep only `ssml` and generate the caption by stripping tags (see §6.5), but the dict style is usually simpler.

### 6.3 Bookmarks: the synchronization standard

Use bookmarks to prevent “voice says x=0 while screen shows x=1” issues:

```python
with self.voiceover(text=item["ssml"], subcaption=item["caption"]):
    self.play(...)
    self.wait_until_bookmark("triangle")
    self.play(...)  # highlight the right triangle exactly when spoken
    self.wait_until_bookmark("length")
    self.play(...)  # write the length exactly when spoken
```

Bookmarks are lightweight, local, and keep pacing logic out of animation wrappers.

### 6.4 SSML rules (French math narration)

SSML is **good** when it is used to control *speech* (pauses, clarity, pronunciation), not to create a second codebase.

Recommended primitives:

- **Language + pace**
  ```xml
  <lang xml:lang='fr-CA'><prosody rate='-8%'> ... </prosody></lang>
  ```
- **Pauses for reading**
  ```xml
  <break time='120ms'/>   <!-- short -->
  <break time='180ms'/>   <!-- medium -->
  <break time='250ms'/>   <!-- long (new slide / dense formula) -->
  ```
- **Letters/variables**
  ```xml
  <say-as interpret-as='characters'>a</say-as>
  ```
  Use for single-letter variables. For products like “ab”, prefer two tokens:
  ```xml
  <say-as interpret-as='characters'>a</say-as> <say-as interpret-as='characters'>b</say-as>
  ```
- **Force “plus” in math**
  Azure often drops the final *s* in “plus”. For **addition**, force /plys/:
  ```xml
  <phoneme alphabet='ipa' ph='plys'>plus</phoneme>
  ```
  (Or rephrase to “somme” if that reads better.)

### 6.5 Keep captions clean (strip SSML tags)

If you generate captions from SSML, strip tags for `subcaption=`:

```python
import re

SSML_TAG_RE = re.compile(r"<[^>]+>")

def strip_ssml_tags(s: str) -> str:
    return SSML_TAG_RE.sub("", s).replace("  ", " ").strip()
```

Then:

```python
ssml = script[i]
cap = strip_ssml_tags(ssml)
with self.voiceover(text=ssml, subcaption=cap):
    ...
```

### 6.6 Voice configuration

Use `global_speed` as a coarse control (typical math: **0.75–0.90**).

```python
self.set_speech_service(AzureService(
    voice="fr-CA-ThierryNeural",
    global_speed=0.8,
))
```

Prefer SSML pauses (`<break>`) and bookmarks for fine timing rather than slowing every animation.

### 6.7 Note on `add_voiceover_ssml`

In manim-voiceover v0.3.7, `add_voiceover_ssml()` is not implemented. Do **not** rely on `voiceover(ssml=...)` APIs. Instead, embed SSML tags directly in `text=...` as shown above and keep `subcaption=` plain.
---

## 7. New-Video Checklist & Skeleton

### 7.1 Checklist

- [ ] Create `<topic_slug>/` directory.
- [ ] Copy the skeleton below into `<topic_slug>/<topic_slug>_scene.py`.
- [ ] Define scene acts in comments before writing code.
- [ ] Set `accent` color and write `construct()`.
- [ ] Run silent low-quality preview: `./run.sh ...` — no errors.
- [ ] Write `script` entries (`caption` + `ssml`) and insert bookmarks for sync.
- [ ] Run narrated preview with Azure credentials.
- [ ] Listen to audio; adjust `<break>` tags and `rate` as needed.
- [ ] Generate final SRT (if applicable): verify timestamps align with animations/bookmarks.
- [ ] Run high-quality export at 1920×1080.
- [ ] Watch the exported MP4 end-to-end.
- [ ] Commit scene file, SRT, and render scripts. **Do not commit MP4 or WAV.**

### 7.2 Scene skeleton (script + bookmarks)

```python
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService
from numpy import sin, cos, sqrt, array, arctan2 as atan2

# -------------------------------------------------------------------------
# Abbreviations (keep code short and consistent)
# abs = absolute, ang = angle, bg = background, dest = destination,
# eq = equation, hl = highlight, len = length, rect = rectangle,
# sq = squared, tri = triangle, uv = unit vector, vt = value tracker
# -------------------------------------------------------------------------

def uv(angle):
    return array([cos(angle), sin(angle), 0])

SSML_RATE = "-8%"  # typical math narration pace

def fr_ca(body: str, rate: str = SSML_RATE) -> str:
    # Wrap a narration snippet with locale + prosody.
    return f"<lang xml:lang='fr-CA'><prosody rate='{rate}'>{body}</prosody></lang>"

# Script standard: captions are plain text; ssml carries bookmarks + pronunciation control.
script = [
    {
        "caption": "Considérons un triangle avec deux côtés A et B, et l’angle γ entre eux.",
        "ssml": fr_ca(
            "Considérons un triangle avec deux côtés "
            "<say-as interpret-as='characters'>A</say-as> et "
            "<say-as interpret-as='characters'>B</say-as>, "
            "et l’angle <say-as interpret-as='characters'>γ</say-as> entre eux."
        ),
    },
    {
        "caption": "La hauteur vaut B sin γ.",
        "ssml": fr_ca(
            "La hauteur est dans <bookmark mark='triangle'/>ce triangle rectangle. "
            "<bookmark mark='length'/>Sa longueur vaut "
            "<say-as interpret-as='characters'>B</say-as> sinus "
            "<say-as interpret-as='characters'>γ</say-as>."
        ),
    },
]

class MyTopicFR(VoiceoverScene):
    def construct(self):
        self.camera.background_color = WHITE

        # Voice: pick one voice per video; global_speed is coarse pace (0.75–0.90 typical).
        self.set_speech_service(AzureService(
            voice="fr-CA-SylvieNeural",
            global_speed=0.8,
        ))

        C_HL = YELLOW  # highlight

        # Example act (bookmarks drive sync)
        with self.voiceover(text=script[0]["ssml"], subcaption=script[0]["caption"]):
            tri = Polygon([-2, -1, 0], [2, -1, 0], [1, 1, 0], color=BLACK)
            self.play(Create(tri))

        with self.voiceover(text=script[1]["ssml"], subcaption=script[1]["caption"]):
            height = DashedLine(RIGHT + UP, RIGHT + DOWN)
            self.play(Create(height))
            self.wait_until_bookmark("triangle")
            self.play(tri.animate.set_stroke(width=6, color=C_HL), rate_func=there_and_back)
            self.wait_until_bookmark("length")
            self.play(Write(MathTex(r"b\sin\gamma").next_to(height, RIGHT)))
```

Notes:
- Put **all sync** into bookmarks + `wait_until_bookmark(...)`. Avoid `play_paced()`-style wrappers.
- For math “plus”, force /plys/ in SSML: `<phoneme alphabet='ipa' ph='plys'>plus</phoneme>`.
- Use `<say-as interpret-as='characters'>` for single-letter variables; for “ab”, use two tokens.

---

## 8. Quality Checks

### 8.1 Math correctness
- Verify every displayed formula against a reference (textbook, SymPy, or manual
  calculation) before committing.
- For inequality directions, limiting cases, and sign conventions: add a one-line
  comment in the source with the verification.

### 8.2 Animation timing
- Total video length: aim for 60–120 s per concept.
- No animation step should be shorter than 0.4 s `run_time`.
- Every `wait()` call must be intentional; remove accidental 0-second waits.
- After the final act, end with `self.wait(1.0)` minimum before the scene exits.

### 8.3 Audio clarity
- Listen to the generated audio at 1× speed before final export.
- Adjust `<break>` durations so spoken math aligns with the moment the formula
  appears on screen (± 0.3 s tolerance).
- Ensure no clipping: final WAV peak should be ≤ −1 dBFS.

### 8.4 Caption readability
- Caption box must not overlap the primary mathematical diagram.
- If a caption is > 55 characters, either shorten it or split across two voiceover/script
  blocks.
- Use plain French prose in caption text; reserve SSML for the `ssml=` argument only.

### 8.5 Export settings

| Setting | Value |
|---------|-------|
| Resolution | 1920 × 1080 |
| Frame rate | 60 fps (`-r 1920,1080 --fps 60`) or Manim default 30 fps |
| Quality flag | `-qh` (high quality) |
| Container | MP4 (H.264) |
| Audio | AAC, embedded in MP4 |

```bash
# Final export command
./.venv/bin/manim -pqh <topic>/<topic>_scene.py <SceneClass> -r 1920,1080
```

---

## 9. Render & Export Commands Reference

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Low-quality preview (fastest, ~480p)
./scripts/render.sh scenes/<topic>/<topic>_scene.py <SceneClass>

# 3. Medium quality (development)
manim -pqm scenes/<topic>/<topic>_scene.py <SceneClass>

# 4. High quality (1080p, for release)
manim -pqh scenes/<topic>/<topic>_scene.py <SceneClass> -r 1920,1080

# 5. Narrated render (Azure credentials in .env)
SPEECH_KEY=<key> SPEECH_REGION=<region> \
  manim -pqh scenes/<topic>/<topic>_scene.py <SceneClass> -r 1920,1080

# 6. Pythagore narrated render (uses render_voice_ssml.sh)
./scenes/pythagore_whiteboard_fr/render_voice_ssml.sh

# 7. Sigma narrated render
./scenes/sigma_sum_whiteboard_fr/generate_voiceover.sh
```

---

## 10. Voiceover Workflows (Existing Scenes)

- **Pythagore:**
  - Set `SPEECH_KEY` / `SPEECH_REGION` (or `AZURE_SUBSCRIPTION_KEY` / `AZURE_SERVICE_REGION`).
  - Optionally place credentials in `scenes/pythagore_whiteboard_fr/.env`.
  - Run: `./scenes/pythagore_whiteboard_fr/render_voice_ssml.sh`

- **Sigma:**
  - Run: `./scenes/sigma_sum_whiteboard_fr/generate_voiceover.sh`

---

## 11. Editing Rules

- Preserve existing scene class names unless a rename is explicitly requested.
- Keep visuals minimalist and consistent with the whiteboard style defined in §5.
- Prefer small, focused edits over broad rewrites.
- Do not delete generated media or asset files unless asked.
- Avoid introducing new dependencies unless required.
- After any edit, run the validation checklist in §8 before considering the task done.

---

## 12. Validation Checklist After Changes

1. Run a low-quality render of the edited scene — no Python errors, no visual glitches.
2. Confirm there are no Python syntax errors (`python -m py_compile <scene>.py`).
3. Verify math: check every formula that was added or modified.
4. If narration timing changed, regenerate the audio and SRT for that scene.
5. Watch the full rendered preview at 1× speed.

---
