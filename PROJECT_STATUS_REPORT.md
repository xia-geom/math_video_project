# Project Status Report

Generated: 2026-05-14

Scope: repository condition and file structure only. No source code was changed.

## Sources Inspected

Read carefully:

- `AGENT.md`
- `README.md`
- `pyproject.toml`
- `.gitignore`
- `.github/workflows/smoke.yml`
- `tools/tts.py`
- `scripts/render.sh`
- `scenes/pythagore_whiteboard_fr/README.md`
- `scenes/sigma_sum_whiteboard_fr/README.md`

Also inspected the live tree with `find`, tracked files with `git ls-files`, ignored files with `git status --short --ignored`, scene classes with `rg '^class '`, and the requested Python health commands.

## Executive Summary

The repository is usable but the documentation is only partially synchronized with the live tree.

The working tree was clean before this report was created, on branch `main`. The local virtual environment works, dependencies are internally consistent, Python compilation passes, and the existing pytest suite passes. The local venv does not currently have `ruff` installed, so the requested local Ruff check cannot run through `python -m ruff`.

The largest project risk is not broken code, but stale operational documentation. `AGENT.md` is intended to be authoritative, yet it references production files and workflows that do not exist in the repository, omits several live scene directories, and disagrees with both `README.md` and CI about scene classes. Several generated media files are tracked even though the ignore policy says they should normally be excluded.

## Current Command Results

| Check | Result |
|---|---|
| `pwd` | `/Users/xiaxiao/Desktop/Projects/math_video_project` |
| `git branch --show-current` | `main` |
| `git status --short` before report | clean |
| `python -V` | failed: `python` command not found |
| `./.venv/bin/python -V` | `Python 3.13.13` |
| `./.venv/bin/python -m pip --version` | `pip 25.3` in `.venv` |
| `./.venv/bin/python -m pip check` | passed, with a pip cache ownership warning |
| `./.venv/bin/python -m pytest -q` | passed: `42 passed in 0.70s` |
| `./.venv/bin/python -m ruff check .` | failed: `No module named ruff` |
| Python compile check over `scenes experiments tools archive` | passed |

## What The Documentation Says

### `AGENT.md`

`AGENT.md` defines the project as a French Manim math-video series with whiteboard styling, optional French TTS narration, and reference-quality scenes in `pythagore_whiteboard_fr` and `function_intuitive_fr`.

It documents this intended top-level structure:

- `scenes/` for production-ready videos, one directory per topic.
- `experiments/` for exploratory or in-progress work.
- `tools/` for development utilities, explicitly mentioning `ssml_sync_check.py`.
- `scripts/render.sh` and `scripts/grade_audit.py`.
- `data/raw/` for upstream data.
- `assets/branding/uqam_logo.png`.
- `archive/` as safe trash.
- `media/` as global Manim output cache, gitignored.

It lists these main scene entry points as complete:

- `FunctionIntuitive` in `scenes/function_intuitive_fr/function_intuitive_scene.py`
- `SigmaSommeBoucleFR` in `scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py`
- `PythagoreAireFR` in `scenes/pythagore_whiteboard_fr/pythagore_scene.py`
- `VariablesEtPolynomesFR` in `scenes/variables_et_polynomes/variables_et_polynomes_scene.py`
- `HyperbolicConeToCusp` in `scenes/hyperbolic_cone_to_cusp/hyperbolic_cone_to_cusp.py`

It also documents a newer script-first voiceover standard using `VoiceoverScene`, `AzureService`, SSML bookmarks, and plain captions. It says `add_voiceover_ssml()` is not implemented in `manim-voiceover` v0.3.7 and recommends embedding SSML tags in `text=...`.

### `README.md`

`README.md` documents setup for Python >= 3.11, LaTeX, FFmpeg, Cairo/Pango, and `pip install -e .` or `pip install -e ".[dev]"`.

It lists these production scenes:

- `PythagoreAireFR`
- `SigmaSommeBoucleFR`
- `FunctionIntuitive`
- `VariablesEtPolynomesFR`
- `GraphProperties`
- `CompleteTheSquare`
- `Logarithme`

It says experiments live under `experiments/` and names `fourier_series/`, `legendre_transform/`, `lorenz/`, `linear_transform/`, and `law_of_cosines/`.

It also says voiceover configuration is centralized in `tools/tts.py`, with `fr-CA-SylvieNeural` as the default voice and `MANIM_VOICE` as the render-time override.

### `pyproject.toml`

The project is named `math-video-project`, version `0.1.0`, requires Python >= 3.11, and depends on:

- `manim>=0.18`
- `manim-voiceover[azure]>=0.3.7`
- `numpy`
- `pandas`
- `xlrd`
- `pyyaml>=6.0`

Dev extras include `ruff`, `mypy`, and `pytest`. Ruff is configured with `target-version = "py311"`, line length 100, and lint families `E`, `F`, `W`, `I`, ignoring `E501`.

### `.github/workflows/smoke.yml`

CI has three jobs:

- `lint`: installs `ruff` and runs `ruff check .`.
- `compile`: compile-checks every Python file under `scenes experiments tools archive`, excluding `__pycache__`.
- `render`: installs system rendering dependencies, installs the project, and smoke-renders selected scenes at low quality with `manim -ql --disable_caching`.

The CI render matrix includes:

- `PythagoreAireFR`
- `FunctionIntuitive`
- `SigmaSommeBoucleFR`
- `VariablesEtPolynomes`
- `Logarithme`
- `LogarithmeProprietes`
- `CompleteTheSquare`
- `GraphProperties`
- `CircleAreaFR`

CI does not run pytest.

### Topic READMEs

Only two topic-level READMEs were found under `scenes/` and `experiments/`:

- `scenes/pythagore_whiteboard_fr/README.md`
- `scenes/sigma_sum_whiteboard_fr/README.md`

The Pythagore README describes a short French whiteboard animation and refers to `pythagore_scene.py`, `subtitles_fr.srt`, optional `.env`, and a `render_voice_ssml.sh` workflow.

The Sigma README describes a roughly 90-second sigma notation video and refers to `sigma_sum_scene.py`, `narration_fr.txt`, `subtitles_fr.srt`, voiceover assets, and a `generate_voiceover.sh` workflow.

## What The Repository Actually Contains

### Top Level

Tracked top-level project files include:

- `AGENT.md`
- `README.md`
- `LICENSE`
- `pyproject.toml`
- `.gitignore`
- `.pre-commit-config.yaml`
- `.github/workflows/smoke.yml`
- `.vscode/launch.json`

The live tree also contains ignored local material:

- `.venv/`
- `.env`
- `.env.example`
- `.claude/`
- `.pytest_cache/`
- `.DS_Store`
- global `media/`

There is no `data/` directory and no top-level `tests/` directory. Tests exist under `tools/ssml/tests/`.

### `scenes/`

Current scene directories at depth 2:

- `scenes/circle_area/`
- `scenes/complete_the_square_fr/`
- `scenes/function_intuitive_fr/`
- `scenes/graph_properties_fr/`
- `scenes/logarithme_fr/`
- `scenes/pythagore_whiteboard_fr/`
- `scenes/sigma_sum_whiteboard_fr/`
- `scenes/trigonometry_fr/`
- `scenes/uqam_bumper/`
- `scenes/variables_et_polynomes/`

Scene classes found:

- `CircleAreaFR` in `scenes/circle_area/circle_area_scenes.py`
- `CompleteTheSquare` in `scenes/complete_the_square_fr/complete_the_square_scene.py`
- `FunctionIntuitive` in `scenes/function_intuitive_fr/function_intuitive_scene.py`
- `GraphProperties` in `scenes/graph_properties_fr/graph_properties_scene.py`
- `Logarithme` in `scenes/logarithme_fr/logarithme_scene.py`
- `LogarithmeProprietes` in `scenes/logarithme_fr/logarithme_proprietes_scene.py`
- `PythagoreAireFR` in `scenes/pythagore_whiteboard_fr/pythagore_scene.py`
- `SigmaSommeBoucleFR` in `scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py`
- `SineCurveUnitCircle` in both `scenes/trigonometry_fr/trigonometry_scene.py` and `scenes/trigonometry_fr/trigonometry_play.py`
- `UQAMLogoBumper` and `UQAMCornerBug` in `scenes/uqam_bumper/uqam_bumper_scene.py`
- `VariablesEtPolynomes` in `scenes/variables_et_polynomes/variables_et_polynomes_scene.py`

Tracked rendered or generated assets under `scenes/` include:

- `scenes/function_intuitive_fr/FunctionIntuitive.mp4`
- `scenes/function_intuitive_fr/FunctionIntuitive_low.mp4`
- `scenes/pythagore_whiteboard_fr/PythagoreAireFR.mp4`
- `scenes/pythagore_whiteboard_fr/_dragon_test.wav`
- `scenes/sigma_sum_whiteboard_fr/assets/voix_off_fr.wav`

Ignored local scene artifacts include multiple `.env` files, `__pycache__/` directories, `scenes/circle_area/media/`, `scenes/pythagore_whiteboard_fr/PythagoreAireFR_uncompressed.wav`, and `scenes/sigma_sum_whiteboard_fr/assets/voix_off_fr.aiff`.

### `experiments/`

Current experiment directories are nested by status/category, not directly by topic:

- `experiments/sketches/fourier_series/`
- `experiments/sketches/hyperbolic_cone_to_cusp/`
- `experiments/sketches/linear_transform/`
- `experiments/sketches/lorenz/`
- `experiments/wip/hairy_ball/`
- `experiments/wip/law_of_cosines/`
- `experiments/wip/legendre_transform/`

Notable classes include:

- `FourierSquareWave`
- `ConeAngleNegativeCurvature`
- `EigenvectorTransformation`
- `LorenzAttractor`
- `LawOfCos`
- `LawOfCosTh`
- `LegendreTangentIntercept`
- many `hairy_ball.py` exploratory classes based on `InteractiveScene`

### `tools/`

Current tools include:

- `tools/tts.py`
- `tools/branding.py`
- `tools/ssml_sync_check.py`
- `tools/ssml/` package
- `tools/ssml/config/fr_ca_lexicon.yaml`
- `tools/ssml/config/fr_ca_math.yaml`
- `tools/ssml/tests/`

`tools/tts.py` is present and does act as the central current TTS helper. It defines `VOICE_CONFIGS`, `DEFAULT_VOICE`, `VOICE_ID`, `VOICE_RATE`, `ssml`, `char`, `chars`, `strip_ssml`, `PLUS`, `ET`, and common variable tokens. Most current voiceover scenes import `tools.tts as tts`.

`tools/ssml_sync_check.py` still has its own list of voices. `tools/tts.py` explicitly says this is planned to migrate, so this duplication is known but unresolved.

### `scripts/`

Current scripts are:

- `scripts/render.sh`
- `scripts/render_all_voices.sh`

`scripts/render.sh` uses `./.venv/bin/manim`, renders a scene, and copies MP4/SRT output into `dist/<SceneClass>/`. If `ffmpeg` is available, it also extracts a 48 kHz mono WAV.

`scripts/render_all_voices.sh` wraps `scripts/render.sh` for the four configured fr-CA voices and renames outputs by voice.

There is no `scripts/grade_audit.py`.

### `archive/`

Tracked archive files include older or parked scripts:

- `archive/hyperbolic_cone_to_cusp_zsurface.py`
- `archive/hyperbolic_cone_to_cuspcopy.py`
- `archive/tools_PDF.py`
- `archive/tools_implementation_plan.md`
- `archive/tools_set.py`
- `archive/tools_webfiller.py`
- `archive/variables_et_polynomes_v2_simplified.py`

The only `HyperbolicConeToCusp` class found is in `archive/hyperbolic_cone_to_cuspcopy.py`, not under `scenes/`.

## Inconsistencies, Stale Items, Missing Pieces

1. `AGENT.md` lists `scenes/hyperbolic_cone_to_cusp/hyperbolic_cone_to_cusp.py` as a complete production entry point, but that path does not exist. Related hyperbolic files are under `experiments/sketches/` and `archive/`, and the live experiment class is `ConeAngleNegativeCurvature`, not `HyperbolicConeToCusp`.

2. `AGENT.md` and `README.md` refer to `./scenes/pythagore_whiteboard_fr/render_voice_ssml.sh`, but no such file exists. `find scenes ... -name '*.sh'` found no scene-local shell scripts.

3. `AGENT.md` and the Sigma README refer to `./scenes/sigma_sum_whiteboard_fr/generate_voiceover.sh`, but no such file exists.

4. `AGENT.md` documents `scripts/grade_audit.py` and `data/raw/`, but neither exists. `pyproject.toml` also comments that `xlrd` is for `grade_audit`, which appears stale unless that script is intentionally omitted.

5. The documented production scene lists disagree:
   - `AGENT.md` omits `GraphProperties`, `CompleteTheSquare`, `Logarithme`, `LogarithmeProprietes`, `CircleAreaFR`, `SineCurveUnitCircle`, and UQAM bumper scenes.
   - `README.md` omits `CircleAreaFR`, `LogarithmeProprietes`, `SineCurveUnitCircle`, and UQAM bumper scenes.
   - CI includes `CircleAreaFR` and `LogarithmeProprietes`.
   - CI does not include `SineCurveUnitCircle` or the UQAM bumper scenes.

6. `AGENT.md` and `README.md` both name `VariablesEtPolynomesFR`, but the actual live class is `VariablesEtPolynomes`. CI uses the actual class name.

7. `AGENT.md` says the standard scene file convention is `<topic_slug>_scene.py`. Several current files do not follow that exactly, including `circle_area_scenes.py`, `trigonometry_play.py`, and experiment files such as `Lawofcosinus.py` and `Legendre.py`.

8. `README.md` says experiment topic directories live directly under `experiments/`, but the actual tree uses `experiments/sketches/` and `experiments/wip/`.

9. Topic README render commands for Pythagore and Sigma use paths like `pythagore_whiteboard_fr/pythagore_scene.py` and `sigma_sum_whiteboard_fr/sigma_sum_scene.py`. From the repository root, the valid paths are under `scenes/`. The current README commands are ambiguous about expected working directory.

10. `.gitignore` ignores `.env` and `.env.*`. The root `.env.example` exists locally but is ignored and not tracked, even though `README.md` instructs users to copy `.env.example` to `.env`. A fresh clone may not contain that example file.

11. `.gitignore` ignores `.vscode/` and `*.mp4`, but these ignored-pattern files are already tracked:
    - `.vscode/launch.json`
    - `scenes/function_intuitive_fr/FunctionIntuitive.mp4`
    - `scenes/function_intuitive_fr/FunctionIntuitive_low.mp4`
    - `scenes/pythagore_whiteboard_fr/PythagoreAireFR.mp4`

12. The project policy in `AGENT.md` says not to commit MP4 or WAV files, yet multiple rendered media files are tracked. `scenes/sigma_sum_whiteboard_fr/assets/voix_off_fr.wav` and `scenes/pythagore_whiteboard_fr/_dragon_test.wav` are tracked WAV files; the ignore policy only ignores `*_uncompressed.wav` and `*.aiff`, not all WAV files.

13. `scripts/render.sh` writes to `dist/`, but `dist/` is not in `.gitignore`, is not described in `AGENT.md` or `README.md`, and does not currently exist. If this script is the new standard, the docs and ignore policy should say so.

14. The local venv uses Python 3.13.13, while CI uses Python 3.11 and Ruff targets `py311`. This is not currently failing, but it means local and CI interpreter behavior are not identical.

15. The local venv appears to have runtime/test dependencies but not dev lint dependencies. `pytest` is installed and passes; `ruff` is not installed even though it is in the `dev` extra and CI depends on it.

16. `AGENT.md` still includes some older workflow language, including a checklist item that says `./run.sh ...`, while the actual helper is `scripts/render.sh`.

17. `AGENT.md`'s voiceover section recommends direct local helpers such as `fr_ca(...)` in the scene skeleton, while `README.md` and most live scenes use `tools.tts` as the centralized voice/SSML helper. The live repository is closer to the README standard than the AGENT skeleton here.

18. `tools/ssml_sync_check.py` and `tools/tts.py` duplicate voice configuration. `tools/tts.py` calls this a planned migration, so this is an acknowledged unresolved cleanup.

19. The live tree contains a very large ignored `media/` directory and many ignored `__pycache__/`, `.DS_Store`, and local `.env` files. They do not affect git status, but they make raw tree inspection noisy and can hide what is actually tracked.

20. The project has tests under `tools/ssml/tests/`, but the GitHub smoke workflow does not run them. Local pytest passes today, but CI would not catch future regressions in these tests unless the workflow is extended.

## Current Structure Summary

The live repository is best understood as:

```text
math_video_project/
  AGENT.md
  README.md
  pyproject.toml
  .github/workflows/smoke.yml
  scripts/
    render.sh
    render_all_voices.sh
  tools/
    tts.py
    branding.py
    ssml_sync_check.py
    ssml/
      config/
      tests/
      *.py
  scenes/
    circle_area/
    complete_the_square_fr/
    function_intuitive_fr/
    graph_properties_fr/
    logarithme_fr/
    pythagore_whiteboard_fr/
    sigma_sum_whiteboard_fr/
    trigonometry_fr/
    uqam_bumper/
    variables_et_polynomes/
  experiments/
    sketches/
    wip/
  archive/
  assets/branding/
  media/                 # ignored generated output, present locally
```

Missing from the documented structure:

- `data/raw/`
- `scripts/grade_audit.py`
- `scenes/hyperbolic_cone_to_cusp/`
- scene-local `render_voice_ssml.sh`
- scene-local `generate_voiceover.sh`
- top-level `tests/`

## Suggested Next Cleanup Order

1. Update `AGENT.md` first, since it claims to be authoritative. Align its production scene table with the live classes and decide whether `CircleAreaFR`, trigonometry, and UQAM bumper are production, experimental, or utility scenes.

2. Decide whether scene-local render scripts are deprecated. If yes, remove references to `render_voice_ssml.sh` and `generate_voiceover.sh` and document `scripts/render.sh` / `scripts/render_all_voices.sh` instead.

3. Fix the `VariablesEtPolynomesFR` versus `VariablesEtPolynomes` naming mismatch in docs, or rename the class deliberately.

4. Decide the media policy. Either keep selected MP4/WAV outputs tracked and document that exception, or remove tracked generated media in a separate cleanup commit.

5. Unignore or rename `.env.example` if new clones are supposed to get a usable environment template.

6. Add `dist/` to `.gitignore` if `scripts/render.sh` remains the standard export path.

7. Add pytest to CI if `tools/ssml/tests/` are meant to be part of the project quality gate.

