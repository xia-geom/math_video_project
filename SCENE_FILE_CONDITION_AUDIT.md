# Scene Python File Condition Audit

Generated: 2026-05-15

Scope: static audit of Python scene files under `scenes/` only. No source code was modified and no Manim renders were run.

## Method

This report combines:

- a primary local static scan of all `scenes/**/*.py` files;
- the Branding/Style reviewer findings;
- the Voiceover/Assets reviewer findings;
- the Docs/CI reviewer findings.

Validation commands run:

```bash
find scenes -maxdepth 2 -type f -name '*.py' | sort
rg --glob '*.py' "^class |play_uqam_intro|background_color|VoiceoverScene|AzureService|subcaption|add_subcaption|add_sound" scenes
rg -n "PythagoreAireFR|SigmaSommeBoucleFR|FunctionIntuitive|VariablesEtPolynomes|GraphProperties|CompleteTheSquare|Logarithme|LogarithmeProprietes|CircleAreaFR|SineCurveUnitCircle|UQAM|HyperbolicConeToCusp" README.md AGENT.md .github/workflows/smoke.yml
find scenes -maxdepth 4 -type f \( -name '*.mp4' -o -name '*.wav' -o -name '*.aiff' -o -name '*.srt' -o -name '*.png' \) | sort
```

AST sanity check passed for all 12 scene Python files.

Status legend:

- `PASS`: condition is present and consistent.
- `WARN`: usable but inconsistent, undocumented, partial, or not fully aligned with the production standard.
- `FAIL`: likely production blocker or clear standard violation.
- `N/A`: condition does not apply to the file.

## Executive Summary

- Total scene Python files checked: 12.
- Shared UQAM intro helper exists: `tools/branding.py::play_uqam_intro`, using `assets/branding/uqam_logo.png`.
- UQAM intro is present in every mathematical scene file under `scenes/`; the standalone UQAM bumper is a branding utility and does not call the helper.
- Strong production-condition files: `function_intuitive_scene.py`, `variables_et_polynomes_scene.py`, `logarithme_scene.py`, and `logarithme_proprietes_scene.py`, with only documentation drift on some.
- Clear condition failures:
  - `pythagore_scene.py`: duplicate/legacy UQAM logo usage plus unguarded voiceover/Azure dependency.
  - `circle_area_scenes.py`: unguarded voiceover/Azure dependency plus white-on-white risks.
  - both trigonometry files: dark-style visual assumptions and duplicate `SineCurveUnitCircle` class.
  - `uqam_bumper_scene.py`: likely asset-loader mismatch, using `SVGMobject` on a `.png`.
- Documentation/CI drift remains: docs list stale `VariablesEtPolynomesFR`, `AGENT.md` lists missing `HyperbolicConeToCusp`, and CI includes `CircleAreaFR`/`LogarithmeProprietes` that are not fully documented.

## Per-File Condition Table

| File | Class(es) | UQAM | Whiteboard style | Voiceover/captions | Docs/CI | Assets | Overall | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `scenes/function_intuitive_fr/function_intuitive_scene.py` | `FunctionIntuitive` | PASS | PASS | PASS | PASS | N/A | PASS | Imports/calls `play_uqam_intro`; sets white background and black defaults; guarded Azure fallback; uses `subcaption=`. Listed in README, AGENT, and CI. |
| `scenes/variables_et_polynomes/variables_et_polynomes_scene.py` | `VariablesEtPolynomes` | PASS | PASS | PASS | WARN | PASS | WARN | Production condition is strong, but README/AGENT list stale class `VariablesEtPolynomesFR`; CI uses actual class. Scene-local `ssml/*.ssml` files exist but are not loaded by the scene. |
| `scenes/complete_the_square_fr/complete_the_square_scene.py` | `CompleteTheSquare` | PASS | PASS | WARN | WARN | N/A | WARN | Guarded Azure fallback, but narrated voiceover call does not pass `subcaption=`. Listed in README and CI, omitted from AGENT main table. |
| `scenes/graph_properties_fr/graph_properties_scene.py` | `GraphProperties` | PASS | PASS | WARN | WARN | N/A | WARN | Uses `_logo_intro()` wrapper around shared intro. Has visual caption boxes, but narrator helper uses `self.voiceover(text=text)` without `subcaption=`, so no Manim subcaption track from voiceover. Listed in README and CI, omitted from AGENT main table. |
| `scenes/logarithme_fr/logarithme_scene.py` | `Logarithme` | PASS | PASS | PASS | WARN | N/A | WARN | Guarded Azure fallback and `subcaption=`. Listed in README and CI, omitted from AGENT main table. |
| `scenes/logarithme_fr/logarithme_proprietes_scene.py` | `LogarithmeProprietes` | PASS | PASS | PASS | WARN | N/A | WARN | Guarded Azure fallback and `subcaption=`. Included in CI but missing as its own entry from README production table and AGENT main table. |
| `scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py` | `SigmaSommeBoucleFR` | PASS | WARN | PASS | PASS | PASS | WARN | White background and shared intro are present. No module-level black defaults, though visible text/math is mostly explicitly black. Uses prerecorded `assets/voix_off_fr.wav`, `add_subcaption`, and existing SRT. Listed in README, AGENT, and CI. |
| `scenes/pythagore_whiteboard_fr/pythagore_scene.py` | `PythagoreAireFR` | FAIL | WARN | FAIL | PASS | PASS | FAIL | Calls shared intro and also loads local `LOGO_UQAM.png`, creating duplicate branding. Direct `VoiceoverScene` subclass and unguarded Azure setup make missing voiceover dependency/credentials render-blocking. White background is set but global black defaults are absent. |
| `scenes/circle_area/circle_area_scenes.py` | `CircleAreaFR`, helper `RigidMove` | PASS | FAIL | FAIL | WARN | N/A | FAIL | Calls shared intro and sets white background, but has white foreground objects on white background. Direct `VoiceoverScene` subclass and unguarded Azure setup are render-blocking without voiceover dependencies/credentials. Included in CI but missing from README/AGENT inventories. |
| `scenes/trigonometry_fr/trigonometry_scene.py` | `SineCurveUnitCircle` | PASS | FAIL | PASS | FAIL | N/A | FAIL | Calls shared intro and has guarded voiceover fallback, but no white background/black defaults and explicit white title/geometry indicate dark-style design. Duplicate class name also appears in `trigonometry_play.py`; neither is documented or CI-rendered. |
| `scenes/trigonometry_fr/trigonometry_play.py` | `SineCurveUnitCircle` | PASS | FAIL | PASS | FAIL | N/A | FAIL | Alternate sine implementation with the same class name as `trigonometry_scene.py`. Calls shared intro and has guarded voiceover fallback, but dark-style white visuals and no docs/CI listing. |
| `scenes/uqam_bumper/uqam_bumper_scene.py` | `UQAMLogoBumper`, `UQAMCornerBug` | N/A | WARN | N/A | WARN | FAIL | WARN | Branding utility, not a mathematical scene. Uses canonical logo path but loads `.png` with `SVGMobject`, which is suspicious and likely a render issue. Absent from README, AGENT, and CI; this may be acceptable if classified as utility. |

## Reviewer Reconciliation Notes

No reviewer conflicts required a `Needs manual verification` marker. The reviewers agreed on the main risks:

- `tools/branding.py` is the canonical UQAM intro helper.
- all mathematical `scenes/` files call the shared UQAM intro.
- Pythagore has duplicate branding because it also loads `scenes/pythagore_whiteboard_fr/LOGO_UQAM.png`.
- Circle area and Pythagore have unguarded voiceover/Azure dependencies.
- trigonometry files are structurally present but visually not aligned with the whiteboard standard and duplicate the same scene class.
- docs/CI do not match the live scene tree.

## Detailed Findings

### UQAM Branding

`tools/branding.py` defines the shared intro:

- `UQAM_LOGO_PATH` points to `assets/branding/uqam_logo.png`.
- `play_uqam_intro(scene)` fades the logo in, waits, fades it out, and waits briefly.

Condition by category:

- `PASS`: all mathematical scene files import and call `play_uqam_intro`.
- `FAIL`: `pythagore_scene.py` calls `play_uqam_intro(self)` and also loads `scenes/pythagore_whiteboard_fr/LOGO_UQAM.png` manually in the first voiceover block.
- `WARN`: `uqam_bumper_scene.py` is a standalone branding utility. It does not call `play_uqam_intro`, which is reasonable, but it uses `SVGMobject(LOGO_PATH)` where `LOGO_PATH` points to a `.png` file.

### Whiteboard Style

Strongly aligned files:

- `function_intuitive_scene.py`
- `variables_et_polynomes_scene.py`
- `complete_the_square_scene.py`
- `graph_properties_scene.py`
- `logarithme_scene.py`
- `logarithme_proprietes_scene.py`

Partial alignment:

- `sigma_sum_scene.py`: white background and mostly explicit black text/math, but no module-level `Text/Tex/MathTex.set_default(color=BLACK)`.
- `pythagore_scene.py`: white background and mostly black explicit objects, but no module-level black defaults.

Clear deviations:

- `circle_area_scenes.py`: sets white background but includes white foreground objects, including `question[0].set_color(WHITE)` and `Integer(... color=WHITE)`.
- `trigonometry_scene.py` and `trigonometry_play.py`: no white background/black defaults and explicit white title/geometry/summary, indicating a dark-background design.

### Voiceover And Captions

Strong condition:

- `function_intuitive_scene.py`
- `variables_et_polynomes_scene.py`
- `logarithme_scene.py`
- `logarithme_proprietes_scene.py`
- `trigonometry_scene.py`
- `trigonometry_play.py`

These use guarded `VoiceoverScene if available else Scene` patterns, credential checks, and `subcaption=` in narrator helpers.

Partial condition:

- `complete_the_square_scene.py`: guarded Azure fallback, but no `subcaption=` in the narrated voiceover call.
- `graph_properties_scene.py`: guarded Azure fallback and visual caption boxes, but no `subcaption=` in the narrated voiceover helper.
- `sigma_sum_scene.py`: not Azure-based; it uses prerecorded audio, on-screen captions, and `add_subcaption`. This is acceptable but different from the current Azure/SSML pattern.

Render-blocking voiceover condition:

- `pythagore_scene.py`: imports `VoiceoverScene`/`AzureService` unguarded and directly subclasses `VoiceoverScene`.
- `circle_area_scenes.py`: imports `VoiceoverScene`/`AzureService` unguarded and directly subclasses `VoiceoverScene`.

### Assets

Confirmed present:

- `assets/branding/uqam_logo.png`
- `scenes/pythagore_whiteboard_fr/LOGO_UQAM.png`
- `scenes/pythagore_whiteboard_fr/Pythagore.png`
- `scenes/sigma_sum_whiteboard_fr/assets/voix_off_fr.wav`
- `scenes/sigma_sum_whiteboard_fr/subtitles_fr.srt`

Scene-local media/artifact notes:

- `scenes/function_intuitive_fr/FunctionIntuitive.mp4`
- `scenes/function_intuitive_fr/FunctionIntuitive_low.mp4`
- `scenes/pythagore_whiteboard_fr/PythagoreAireFR.mp4`
- `scenes/pythagore_whiteboard_fr/PythagoreAireFR_uncompressed.wav`
- `scenes/pythagore_whiteboard_fr/_dragon_test.wav` is zero bytes and unreferenced.
- `scenes/sigma_sum_whiteboard_fr/assets/voix_off_fr.aiff` also exists locally.

### Documentation And CI Consistency

`PASS`:

- CI smoke matrix class names all match actual classes for listed entries.
- CI compile job covers Python files under `scenes/`.

`FAIL`:

- README and AGENT list `VariablesEtPolynomesFR`, but the actual class is `VariablesEtPolynomes`.
- AGENT lists `HyperbolicConeToCusp` under `scenes/hyperbolic_cone_to_cusp/hyperbolic_cone_to_cusp.py`, but no such path exists under `scenes/`.
- `SineCurveUnitCircle` appears in two files with the same class name and is absent from README, AGENT, and CI.

`WARN`:

- `CircleAreaFR` is included in CI but not listed in README or AGENT.
- `LogarithmeProprietes` is included in CI but not listed as its own README production scene or AGENT main entry.
- `UQAMLogoBumper` and `UQAMCornerBug` are real scene classes under `scenes/`, but are absent from README, AGENT, and CI. This is acceptable only if explicitly treated as utilities.

## Recommended Cleanup Order

1. Fix static render blockers first:
   - guard or fallback the voiceover setup in `pythagore_scene.py` and `circle_area_scenes.py`;
   - fix `uqam_bumper_scene.py` to load the PNG with an image loader or switch the asset to SVG.

2. Normalize UQAM branding:
   - remove duplicate local-logo intro logic from `pythagore_scene.py`;
   - rely on `tools.branding.play_uqam_intro()` for production scenes.

3. Restore whiteboard consistency:
   - fix white-on-white elements in `circle_area_scenes.py`;
   - decide whether trigonometry should be converted to whiteboard style or moved/marked as non-production.

4. Fix caption-track gaps:
   - add `subcaption=` behavior to `complete_the_square_scene.py` and `graph_properties_scene.py` narrator helpers if SRT/subcaption output is expected.

5. Resolve documentation/CI drift:
   - update docs for `VariablesEtPolynomes`;
   - remove or relocate stale `HyperbolicConeToCusp` entry;
   - document `CircleAreaFR` and `LogarithmeProprietes`;
   - classify UQAM bumper and trigonometry files as production, utility, or WIP.

