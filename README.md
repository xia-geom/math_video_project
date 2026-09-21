# Math Video Project

Collection of Manim Community scenes for a French math-education video series, with optional Azure TTS narration. The project favors rigorous explanations, minimalist whiteboard visuals, progressive animation, and concise French captions.

## Project Status

The unified course contains **43 globally numbered teaching videos**: 37 main
lessons and six common-error supplements numbered 38–43. The 10 syllabus
additions are integrated into their chapters but remain productions under review.
There are 44 scene sources including the separate, unnumbered course-identity
animation. Promotional films are outside the course sequence.

[Complete course order](curriculum/NUMBERING.md) ·
[Historical numbering lookup](curriculum/LEGACY_NUMBERING.md) ·
[Production and audit status](reports/course_audit/2026-09-20/AUDIT.md).

`curriculum/programme_principal_fr.yaml` is the sole authority for global numbers,
source paths, packaging and Drive routing. Public scene classes are unchanged.
Generated catalogue indexes replace hand-maintained copies of the course list.

## Setup

### Prerequisites

Install these system-level tools before the Python steps:

| Tool | Purpose | Install |
|------|---------|---------|
| Python ≥ 3.11 | Runtime | [python.org](https://www.python.org/downloads/) or `brew install python` |
| LaTeX (TeX Live / MiKTeX) | Rendering math formulas | `brew install --cask mactex` (macOS) / `apt install texlive-full` (Linux) |
| FFmpeg | Video encoding | `brew install ffmpeg` / `apt install ffmpeg` |
| Cairo & Pango | Vector graphics | `brew install cairo pango` / `apt install libcairo2-dev libpango1.0-dev` |

### Install

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd math_video_project

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 3. Install all Python dependencies
pip install -e .

# For development tools (linter, type-checker):
pip install -e ".[dev]"
```

### Environment variables (voiceover only)

Scenes with Azure TTS narration need two credentials.  
Copy the example file and fill in your values:

```bash
cp .env.example .env
# then edit .env with your Azure Speech key and region
```

| Variable | Description |
|----------|-------------|
| `SPEECH_KEY` | Azure Cognitive Services Speech key |
| `SPEECH_REGION` | Azure region (e.g. `eastus`, `canadacentral`) |

Scenes without voiceover work fine without a `.env` file.

### Render a scene

```bash
# Low-quality preview copied to dist/36_pythagore_par_les_aires_fr/
./scripts/render.sh \
  scenes/geometrie_fr/36_pythagore_par_les_aires_fr/36_pythagore_par_les_aires_fr_scene.py \
  PythagoreAireFR ql

# High-quality export (1080p60)
./scripts/render.sh \
  scenes/geometrie_fr/36_pythagore_par_les_aires_fr/36_pythagore_par_les_aires_fr_scene.py \
  PythagoreAireFR qh
```

The quality argument is `ql` (480p15), `qm` (720p30), or `qh` (1080p60).
Production `qh` renders are written to `dist/<topic_slug>/`; `ql` and `qm`
previews are kept separately under `dist/_previews/<quality>/<topic_slug>/` so
they cannot replace a production video. The helper also writes SRT and
uncompressed WAV outputs when available. Manim still renders the class supplied
on the command line; only the deliverable names come from the scene's parent
folder.

### Keep render history

Successful `qh` renders are automatically registered in the local archive at
`dist/_render_archive/`. Each readable version name includes its timestamp, Git
commit, resolution, and frame rate. The JSON-lines index records the original
path, checksum, size, duration, audio presence, render quality, and repository
state. Identical MP4 content is stored only once, even when it also appears in a
curriculum package.

```bash
# Capture all current MP4 files before a merge or other major change.
python scripts/archive_renders.py snapshot --label pre-merge

# Inspect all versions, or versions of one output.
python scripts/archive_renders.py list
python scripts/archive_renders.py list --path dist/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr.mp4

# Restore a version without altering the archive.
python scripts/archive_renders.py restore <version-id> --output /tmp/restored.mp4
```

The archive is ignored by Git and is not copied to Google Drive. Curriculum
package rebuilds and UQAM release builds register their MP4 outputs through the
same archive. Re-registering an unchanged path and checksum is a no-op.

### Render the curriculum

```bash
# Silent 480p previews selected by GLOBAL course number
./.venv/bin/python scripts/render_curriculum.py \
  --track programme --quality ql --render --disable-voiceover \
  --order 15 --order 16 --order 17 \
  --order 18 --order 19 --order 20 --order 21 --order 22 --order 23

# Resumable narrated 1080p render; every course video must pass the same checks
./.venv/bin/python scripts/render_curriculum.py \
  --track programme --quality qh --render --resume

# Validate and build the 37-video programme plus globally numbered supplements
./.venv/bin/python scripts/render_curriculum.py \
  --track all --quality qh --validate --package --drive
```

Local packages are written to `dist/programme_principal_fr/` and
`dist/erreurs_frequentes_fr/`. Drive receives only MP4 files, under
`Math Video Project/1 - Programme principal/` and `2 - Erreurs fréquentes/`.
Unclassified scene renders remain local.

### Audit a rendered video

```bash
./.venv/bin/python scripts/audit_video.py \
  --scene scenes/<category>/<topic>/<topic>_scene.py \
  --class <SceneClass> \
  --video dist/<topic_slug>/<topic_slug>.mp4 \
  --out reports/video_audits/<SceneClass>_audit.md

# Render low-quality silent previews and audit all 43 course scenes.
./.venv/bin/python scripts/audit_all_scenes.py

# Re-audit existing videos without rendering.
./.venv/bin/python scripts/audit_all_scenes.py --no-render
```

The latest batch summary is stored in [`reports/video_audits/INDEX.md`](reports/video_audits/INDEX.md).

## Scene Organization

Sources use `scenes/<category>/<global-number>_<topic>/<global-number>_<topic>_scene.py`.
See [the generated course inventory](curriculum/NUMBERING.md) for every source.
Global numbers are unique across categories and tracks; the identity bumper
is not a numbered course video. Semantic IDs and public classes remain stable.

## Common Mathematical Errors

The `scenes/erreurs_frequentes_fr/` category contains lessons intentionally organized around a tempting but invalid mathematical step. It is not a catch-all folder for every scene that mentions a mistake. Each lesson exposes the misconception, gives a counterexample or failed argument, and finishes with a reliable replacement method.

The six supplements now use global numbers 38–43. Their sources and historical
aliases are listed in [the course inventory](curriculum/NUMBERING.md).

## Main Curriculum — Pedagogical Order

See [the generated course order](curriculum/NUMBERING.md) and
[the machine-readable playlist](curriculum/playlist.csv). Update the catalogue,
then run `python tools/course_catalog.py --write-indexes`; do not duplicate it here.

## Experiments

Early-stage work is kept outside production scenes:

- `experiments/sketches/`: Fourier series, sorting, hyperbolic cone-to-cusp, linear transformations, and the Lorenz system.
- `experiments/wip/`: hairy-ball theorem, Legendre transform, and law of cosines.
- `archive/`: superseded scenes and retired utilities kept for historical reference.

## Teaching production standard

See [docs/TEACHING_STANDARD.md](docs/TEACHING_STANDARD.md) for legible panels, sequential explanations, the MAI teaching profile, measured bookmark timing, and the single UQAM opening.

## Voiceover (Azure)

Teaching scenes now use the existing **`MAI-Voice-2`** profile at **`-3%`**, through `tools/teaching_voiceover.py`, as their standard voice. Voice configuration is centralised in `tools/tts.py`; individual scenes should not hardcode voice names or duplicate shared SSML helpers. The Sigma scene can also use its prerecorded local narration asset.

```bash
export SPEECH_KEY=...
export SPEECH_REGION=...
# Pythagore scene
./scripts/render.sh scenes/geometrie_fr/36_pythagore_par_les_aires_fr/36_pythagore_par_les_aires_fr_scene.py PythagoreAireFR qh
```

To switch voice at render time:

```bash
MANIM_VOICE=fr-CA-JeanNeural manim -pql scenes/.../my_scene.py MyScene
```

To explicitly select the shared MAI teaching profile, use the friendly
`MAI-Voice-2` selector. The project maps it to the published French voice
`fr-FR-Soleil:MAI-Voice-2` and requires the configured Speech resource to be
in `canadacentral`:

```bash
SPEECH_REGION=canadacentral MANIM_VOICE=MAI-Voice-2 \
  ./scripts/render.sh scenes/.../my_scene.py MyScene ql
```

MAI-Voice-2 uses Microsoft's Azure Speech SDK and SSML, just like the existing
neural voices. Its neutral profile uses a moderately paced `-3%` rate and the
existing punctuation/SSML pauses so the scene's measured narration timing and
video synchronization continue to drive the render. The published French MAI
voice has no calm or narration-specific style, so the neutral setting is
intentional and leaves varied intonation to MAI's native delivery. MAI-Voice-2
is currently in public preview and has no service-level agreement. See Microsoft's
[MAI-Voice documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/mai-voices)
and [Azure Speech region matrix](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/regions).

Available voices:

| Selector / voice ID | Rate | Character |
|---------------------|------|-----------|
| `fr-CA-SylvieNeural` | `-14%` | Legacy profile; explicit override |
| `fr-CA-JeanNeural` | `-14%` | Male, natural delivery |
| `fr-CA-AntoineNeural` | `-14%` | Male, expressive |
| `fr-CA-ThierryNeural` | `-14%` | Male, clear diction |
| `MAI-Voice-2` (`fr-FR-Soleil:MAI-Voice-2`) | `-3%` | Female, high-fidelity long-form narration |

## TTS / SSML utilities (`tools/tts.py`)

All pronunciation logic lives in a single module. Import what you need:

```python
from tools.tts import VOICE_ID, VOICE_RATE, ssml, char, chars, strip_ssml
from tools.tts import ET, PLUS, A, B, C, P, Q, T, X, Y
```

| Export | Purpose |
|--------|---------|
| `VOICE_CONFIGS` | Dict mapping voice IDs to prosody rates |
| `VOICE_ID` / `VOICE_RATE` | Resolved from `$MANIM_VOICE`; supports the `MAI-Voice-2` alias |
| `azure_service_kwargs()` | Bridges environment-only Azure settings and preserves the 48 kHz output profile |
| `ssml(text, rate)` | Wraps text in the selected voice locale and prosody rate |
| `char(c)` | `<say-as interpret-as='characters'>c</say-as>` |
| `chars(*letters)` | Space-joined `char()` tokens for multi-letter products |
| `strip_ssml(text)` | Strips all XML tags — use for `subcaption=` |
| `ET` | French liaison break: `<break time='150ms'/> et <break time='100ms'/>` |
| `PLUS` | Forces /plys/ IPA — prevents Azure dropping the final *s* |
| `A B C P Q T X Y` | Pre-built `char()` tokens for common math variables |
