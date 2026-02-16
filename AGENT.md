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

## 3. Environment

```bash
# Activate virtual environment
source venv/bin/activate        # or: source .venv/bin/activate

# Quick preview (low quality, auto-open)
./run.sh path/to/scene.py SceneName

# High-quality export (1920×1080)
./.venv/bin/manim -pqh path/to/scene.py SceneName -r 1920,1080

# Medium quality (development iteration)
./.venv/bin/manim -pqm path/to/scene.py SceneName
```

---

## 4. Main Scene Entry Points

| Scene class | File | Status |
|-------------|------|--------|
| `FunctionIntuitive` | `function_intuitive_fr/function_intuitive_scene.py` | Complete |
| `SigmaSommeBoucleFR` | `sigma_sum_whiteboard_fr/sigma_sum_scene.py` | Complete |
| `PythagoreAireFR` | `pythagore_whiteboard_fr/pythagore_scene.py` | Complete |

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

- Minimum `self.wait()` between animation steps: 0.6 s.
- Caption display time: caption text should remain visible for the full narration segment
  plus ≈ 0.4 s lead-out before `_hide_caption`.
- `run_time` guidelines:
  - Simple `FadeIn` / `FadeOut`: 0.6–1.0 s
  - `Create` on a complex shape: 1.2–2.0 s
  - `Write` on a short equation: 1.0–1.6 s
  - `TransformMatchingTex`: 1.4–1.8 s
  - `LaggedStart` with 4+ items: 1.8–2.8 s, `lag_ratio` 0.05–0.15

---

## 6. Voiceover + Captions Pipeline

### 6.1 Supported modes

Every scene must render correctly in **two modes**:

1. **Silent mode** — no Azure credentials, no `manim-voiceover` installed.
2. **Narrated mode** — Azure credentials present, `manim-voiceover` installed.

### 6.2 Boilerplate imports (copy into every new scene)

```python
import os
from contextlib import contextmanager
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.azure import AzureService
except ImportError:
    VoiceoverScene = None
    AzureService = None


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0
```

### 6.3 Scene class declaration

```python
class MySceneFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    ...
```

### 6.4 Voiceover setup helper

```python
def _setup_voiceover(self, voice: str = "fr-FR-DeniseNeural", prosody: dict | None = None):
    self._voiceover_enabled = False
    if load_dotenv is not None:
        load_dotenv()
        load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)

    if VoiceoverScene is None or AzureService is None:
        print("[voiceover] manim-voiceover not installed. Rendering without narration.")
        return

    azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
    azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
    if not azure_key or not azure_region:
        print(
            "[voiceover] Missing Azure credentials. Set AZURE_SUBSCRIPTION_KEY/"
            "AZURE_SERVICE_REGION or SPEECH_KEY/SPEECH_REGION."
        )
        return

    os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
    os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
    os.environ.setdefault("SPEECH_KEY", azure_key)
    os.environ.setdefault("SPEECH_REGION", azure_region)

    kwargs = {"voice": voice}
    if prosody:
        kwargs["prosody"] = prosody
    self.set_speech_service(AzureService(**kwargs))
    self._voiceover_enabled = True
```

### 6.5 `narrated()` context manager

```python
@contextmanager
def narrated(self, caption: str, ssml: str | None = None):
    """
    caption — plain text shown as subtitle and used as fallback TTS text.
    ssml    — optional SSML override for the Azure request.
    """
    if self._voiceover_enabled:
        voice_text = ssml if ssml is not None else caption
        with self.voiceover(text=voice_text, subcaption=caption) as tracker:
            yield tracker
    else:
        yield _NoVoiceTracker()
```

### 6.6 Caption box helpers

```python
def _subtitle_box(self, text: str) -> VGroup:
    caption = Text(text, color=BLACK, font_size=30)
    max_width = config.frame_width - 1.0
    if caption.width > max_width:
        caption.scale_to_fit_width(max_width)
    panel = RoundedRectangle(
        corner_radius=0.08,
        width=caption.width + 0.45,
        height=caption.height + 0.28,
        stroke_color=GRAY_B,
        stroke_width=1,
    )
    panel.set_fill(WHITE, opacity=0.96)
    caption.move_to(panel.get_center())
    box = VGroup(panel, caption)
    box.to_edge(DOWN, buff=0.18)
    return box

def _show_caption(self, text: str) -> VGroup:
    box = self._subtitle_box(text)
    self.play(FadeIn(box), run_time=0.2)
    return box

def _hide_caption(self, box: VGroup) -> None:
    self.play(FadeOut(box), run_time=0.2)
```

### 6.7 Azure voice catalogue (French)

| Voice ID | Accent | Style |
|----------|--------|-------|
| `fr-FR-DeniseNeural` | Standard French | Clear, neutral |
| `fr-CA-ThierryNeural` | Canadian French | Slightly slower |
| `fr-FR-HenriNeural` | Standard French | Male, formal |

Set `prosody={"rate": "-10%"}` to `-18%"` for denser mathematical exposition.

### 6.8 SSML template

Wrap each narration block in:
```xml
<lang xml:lang='fr-FR'>
  <prosody rate='-10%'>
    ...text with <break time='150ms'/> pauses...
    ...<say-as interpret-as='characters'>a</say-as> for single letters...
  </prosody>
</lang>
```

Rules:
- Always wrap in `<lang>` matching the chosen voice locale.
- Use `<say-as interpret-as='characters'>` for single variable names (a, b, c, x, y).
- Add `<break time='100ms'/>` to `<break time='200ms'/>` around displayed equations
  to give viewers time to read.
- Keep each `narrated` block to one logical sentence or clause.

### 6.9 SRT alignment rules

- One subtitle entry per `narrated` block.
- Timestamps come from the generated `.wav` durations; do not hand-edit timestamps.
- Line length: ≤ 60 characters per line, ≤ 2 lines per entry.
- Run `generate_voiceover.sh` (or `render_voice_ssml.sh`) to regenerate `.srt` after
  any script change.

---

## 7. New-Video Checklist & Skeleton

### 7.1 Checklist

- [ ] Create `<topic_slug>/` directory.
- [ ] Copy the skeleton below into `<topic_slug>/<topic_slug>_scene.py`.
- [ ] Define scene acts in comments before writing code.
- [ ] Set `accent` color and write `construct()`.
- [ ] Run silent low-quality preview: `./run.sh ...` — no errors.
- [ ] Write SSML for each `narrated` block.
- [ ] Run narrated preview with Azure credentials.
- [ ] Listen to audio; adjust `<break>` tags and `rate` as needed.
- [ ] Generate final SRT: verify timestamps align with animations.
- [ ] Run high-quality export at 1920×1080.
- [ ] Watch the exported MP4 end-to-end.
- [ ] Commit scene file, SRT, and render scripts. **Do not commit MP4 or WAV.**

### 7.2 Scene skeleton

```python
from manim import *
import numpy as np
import os
from contextlib import contextmanager
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.azure import AzureService
except ImportError:
    VoiceoverScene = None
    AzureService = None

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class MyTopicFR(VoiceoverScene if VoiceoverScene is not None else Scene):

    # ── voiceover helpers ─────────────────────────────────────────────────
    def _setup_voiceover(self, voice="fr-FR-DeniseNeural", prosody=None):
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
            load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)
        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] not installed — silent render")
            return
        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print("[voiceover] missing credentials — silent render")
            return
        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)
        kw = {"voice": voice}
        if prosody:
            kw["prosody"] = prosody
        self.set_speech_service(AzureService(**kw))
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, caption: str, ssml: str = None):
        if self._voiceover_enabled:
            with self.voiceover(text=ssml or caption, subcaption=caption) as tr:
                yield tr
        else:
            yield _NoVoiceTracker()

    def _subtitle_box(self, text: str) -> VGroup:
        cap = Text(text, color=BLACK, font_size=30)
        if cap.width > config.frame_width - 1.0:
            cap.scale_to_fit_width(config.frame_width - 1.0)
        panel = RoundedRectangle(
            corner_radius=0.08,
            width=cap.width + 0.45,
            height=cap.height + 0.28,
            stroke_color=GRAY_B,
            stroke_width=1,
        ).set_fill(WHITE, opacity=0.96)
        cap.move_to(panel)
        box = VGroup(panel, cap).to_edge(DOWN, buff=0.18)
        return box

    def _show_caption(self, text: str) -> VGroup:
        box = self._subtitle_box(text)
        self.play(FadeIn(box), run_time=0.2)
        return box

    def _hide_caption(self, box: VGroup) -> None:
        self.play(FadeOut(box), run_time=0.2)

    # ── main scene ────────────────────────────────────────────────────────
    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        accent = BLUE_D

        # ------------------------------------------------------------------
        # Act 1 — Title
        # ------------------------------------------------------------------
        title = Text("Titre de la vidéo", font_size=48)
        with self.narrated(
            "Texte de narration ici.",
            ssml="<lang xml:lang='fr-FR'>Texte SSML ici.</lang>",
        ) as _:
            cap = self._show_caption("Texte du sous-titre ici.")
            self.play(FadeIn(title), run_time=1.5)
            self.wait(2.0)
            self._hide_caption(cap)
            self.play(FadeOut(title), run_time=0.8)

        # ------------------------------------------------------------------
        # Act 2 — ...
        # ------------------------------------------------------------------
```

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
- If a caption is > 55 characters, either shorten it or split across two `narrated`
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
./run.sh <topic>/<topic>_scene.py <SceneClass>

# 3. Medium quality (development)
manim -pqm <topic>/<topic>_scene.py <SceneClass>

# 4. High quality (1080p, for release)
manim -pqh <topic>/<topic>_scene.py <SceneClass> -r 1920,1080

# 5. Narrated render (Azure credentials in .env)
SPEECH_KEY=<key> SPEECH_REGION=<region> \
  manim -pqh <topic>/<topic>_scene.py <SceneClass> -r 1920,1080

# 6. Pythagore narrated render (uses render_voice_ssml.sh)
./pythagore_whiteboard_fr/render_voice_ssml.sh

# 7. Sigma narrated render
./sigma_sum_whiteboard_fr/generate_voiceover.sh
```

---

## 10. Voiceover Workflows (Existing Scenes)

- **Pythagore:**
  - Set `SPEECH_KEY` / `SPEECH_REGION` (or `AZURE_SUBSCRIPTION_KEY` / `AZURE_SERVICE_REGION`).
  - Optionally place credentials in `pythagore_whiteboard_fr/.env`.
  - Run: `./pythagore_whiteboard_fr/render_voice_ssml.sh`

- **Sigma:**
  - Run: `./sigma_sum_whiteboard_fr/generate_voiceover.sh`

---

## 11. Editing Rules

- Preserve existing scene class names unless a rename is explicitly requested.
- Keep visuals minimalist and consistent with the whiteboard style defined in §5.
- Prefer small, focused edits over broad rewrites.
- Do not delete generated media or asset files unless asked.
- Avoid introducing new dependencies unless required.
- After any edit, run the validation checklist in §8 before considering the task done.
- **After every render, automatically run `git add -A && git commit`** with a concise message describing what was rendered. Do not wait to be asked.

---

## 12. Validation Checklist After Changes

1. Run a low-quality render of the edited scene — no Python errors, no visual glitches.
2. Confirm there are no Python syntax errors (`python -m py_compile <scene>.py`).
3. Verify math: check every formula that was added or modified.
4. If narration timing changed, regenerate the audio and SRT for that scene.
5. Watch the full rendered preview at 1× speed.

---

## 13. Agent Skills Context

If a task explicitly asks for skills, the available skills are:
- `skill-creator`
- `skill-installer`

Use only when directly requested or when the task clearly matches those skill descriptions.
