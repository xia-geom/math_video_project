# Math Video Project

Collection of Manim Community scenes for a French math-education video series
(whiteboard style, minimalist visuals, optional Azure TTS narration).

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
| `HyperbolicConeToCusp` | `scenes/hyperbolic_cone_to_cusp/` | 3-D hyperbolic cone to cusp morphing |

## Experiments

Early-stage or exploratory work lives under `experiments/`:
`fourier_series/`, `legendre_transform/`, `lorenz/`, `linear_transform/`, `law_of_cosines/`.

## High-Quality Export

```bash
manim -pqh scenes/<topic>/<topic>_scene.py <SceneClass> -r 1920,1080
```

## Voiceover (Azure)

```bash
export SPEECH_KEY=...
export SPEECH_REGION=...
# Pythagore scene (MP4 + SRT + uncompressed WAV)
./scenes/pythagore_whiteboard_fr/render_voice_ssml.sh
```

See [AGENT.md](AGENT.md) for the full production manual, style guide, and SSML narration standard.
