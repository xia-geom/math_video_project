# Math Video Project

Collection of Manim Community scenes for a French math-education video series, built with Manim Community and optional Azure TTS narration (whiteboard style, minimalist visuals). A self-driven project to produce rigorous, visually clean math explanations for French-speaking students.

## Quickstart

```bash
# 1. Clone and enter the repo
git clone <repo-url> && cd math_video_project

# 2. Create and activate the virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -e .

# 4. Low-quality preview (auto-opens the video)
./scripts/render.sh scenes/pythagore_whiteboard_fr/pythagore_scene.py PythagoreAireFR
```

For Azure TTS narration set `SPEECH_KEY` and `SPEECH_REGION` in your environment
(or copy `scenes/<topic>/.env.example` to `scenes/<topic>/.env`).

## Production Scenes

| Scene class | Directory | Description |
|-------------|-----------|-------------|
| `PythagoreAireFR` | `scenes/pythagore_whiteboard_fr/` | Pythagorean theorem — area proof, FR narration |
| `SigmaSommeBoucleFR` | `scenes/sigma_sum_whiteboard_fr/` | Sigma notation with worked example |
| `FunctionIntuitive` | `scenes/function_intuitive_fr/` | Intuitive intro to one-variable functions |
| `VariablesEtPolynomesFR` | `scenes/variables_et_polynomes/` | Variables and polynomials |

## Experiments

Early-stage or exploratory work lives under `experiments/`:
`fourier_series/`, `legendre_transform/`, `lorenz/`, `linear_transform/`, `law_of_cosines/`.

## High-Quality Export

```bash
manim -pqh scenes/<topic>/<topic>_scene.py <SceneClass> -r 1920,1080
```

## Voiceover (Azure)
(voice="fr-CA-SylvieNeural", global_speed=0.80)
Voice and speed are set per-scene via `self.set_speech_service(AzureService(...))` in each scene's `construct()` method (e.g. `scenes/pythagore_whiteboard_fr/pythagore_scene.py`).
```bash
export SPEECH_KEY=...
export SPEECH_REGION=...
# Pythagore scene (MP4 + SRT + uncompressed WAV)
./scenes/pythagore_whiteboard_fr/render_voice_ssml.sh
```
