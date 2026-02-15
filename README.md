# Math Video Project

Collection of Manim Community scenes for French math videos (whiteboard style, minimalist visuals, optional voiceover).

## Quick Start

```bash
source .venv/bin/activate
./run.sh path/to/scene.py SceneName
```

`run.sh` renders a quick preview (`-pql`).

For high-quality render:

```bash
./.venv/bin/manim -pqh path/to/scene.py SceneName -r 1920,1080
```

## Main Scenes

- `function_intuitive_fr/function_intuitive_scene.py` -> `FunctionIntuitive`  
  Intuitive introduction to one-variable functions.

- `sigma_sum_whiteboard_fr/sigma_sum_scene.py` -> `SigmaSommeBoucleFR`  
  Sigma notation with a worked example.

- `pythagore_whiteboard_fr/pythagore_scene.py` -> `PythagoreAireFR`  
  Pythagorean theorem by area proof (FR captions + Azure voiceover).

## Voiceover (Azure)

Set credentials before rendering voice-enabled scenes:

```bash
export SPEECH_KEY=...
export SPEECH_REGION=...
```

For the Pythagore scene (MP4 + SRT + uncompressed WAV):

```bash
./pythagore_whiteboard_fr/render_voice_ssml.sh
```
