# Math Video Project

Collection of Manim Community scenes for a French math-education video series
(whiteboard style, minimalist visuals, optional Azure TTS narration).

# /Users/xiaxiao/Desktop/math_video_project/assets/branding/uqam_logo.png
        logo = ImageMobject("/Users/xiaxiao/Desktop/math_video_project/assets/branding/uqam_logo.png")

        self.play(FadeIn(logo, shift=0.2*UP), run_time=0.6)
        self.play(logo.animate.scale(0.5), run_time=1.0)
        self.play(logo.animate.scale(1.0), run_time=1.0)
        self.play(FadeOut(logo, shift=0.2*UP), run_time=0.6)
add this to the beginning of the scene to show the UQAM logo as an intro 
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
(voice="fr-CA-SylvieNeural", global_speed=0.80)
```bash
export SPEECH_KEY=...
export SPEECH_REGION=...
# Pythagore scene (MP4 + SRT + uncompressed WAV)
./scenes/pythagore_whiteboard_fr/render_voice_ssml.sh
```
