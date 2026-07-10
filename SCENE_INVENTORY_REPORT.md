# Scene Inventory and Pedagogical Summary

Generated: 2026-05-15

Scope: inventory of existing Manim scene/video material under `scenes/` and `experiments/`, using the repository as the source of truth. No source code was modified.

## Method

Commands and inspections used:

- `find scenes experiments -maxdepth 3 -type f | sort`
- `rg "^class " scenes experiments`
- `rg "VoiceoverScene|Scene\\)" scenes experiments`
- `rg "script =|voiceover|subcaption|MathTex|Tex|Text" scenes experiments`
- focused reads of each Python scene file under `scenes/` and `experiments/`
- `git status --short`

Current git status while inspecting: only `PROJECT_STATUS_REPORT.md` was already untracked from the previous report task. This report is an additional report artifact.

No official MAT0339 syllabus or topic outline was found in the repository. The MAT0339 complement suggestions below are therefore inferred from the existing repository content and from the apparent algebra/functions/precalculus direction of the current videos.

## High-Level Inventory

The repository contains 12 Python files under `scenes/`:

- `scenes/circle_area/circle_area_scenes.py`
- `scenes/complete_the_square_fr/complete_the_square_scene.py`
- `scenes/function_intuitive_fr/function_intuitive_scene.py`
- `scenes/graph_properties_fr/graph_properties_scene.py`
- `scenes/logarithme_fr/logarithme_scene.py`
- `scenes/logarithme_fr/logarithme_proprietes_scene.py`
- `scenes/pythagore_whiteboard_fr/pythagore_scene.py`
- `scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py`
- `scenes/trigonometry_fr/trigonometry_scene.py`
- `scenes/trigonometry_fr/trigonometry_play.py`
- `scenes/uqam_bumper/uqam_bumper_scene.py`
- `scenes/variables_et_polynomes/variables_et_polynomes_scene.py`

It also contains experiment/WIP Python files under `experiments/`:

- `experiments/sketches/fourier_series/square_wave.py`
- `experiments/sketches/hyperbolic_cone_to_cusp/hyperbolic_cone_to_cusp.py`
- `experiments/sketches/linear_transform/linear_transform.py`
- `experiments/sketches/lorenz/lorenz.py`
- `experiments/sketches/sort.py`
- `experiments/wip/hairy_ball/hairy_ball.py`
- `experiments/wip/law_of_cosines/Lawofcosinus.py`
- `experiments/wip/legendre_transform/Legendre.py`

There is also a notebook:

- `experiments/sketches/lorenz/Untitled-1.ipynb`

## Production/Scene Directory Inventory

| Area | File | Scene class(es) | Pedagogical content | Narration/audio | Documentation status |
|---|---|---|---|---|---|
| Pythagorean theorem | `scenes/pythagore_whiteboard_fr/pythagore_scene.py` | `PythagoreAireFR` | Area proof of `c^2 = a^2 + b^2`: starts from a right triangle, recalls `(a+b)^2`, builds a large square of side `a+b`, inserts four congruent right triangles, counts areas, and cancels `2ab`. | `VoiceoverScene`, Azure via `tools.tts`, SSML bookmarks, subcaptions, UQAM intro. | Listed in both `README.md` and `AGENT.md`. |
| Sigma notation | `scenes/sigma_sum_whiteboard_fr/sigma_sum_scene.py` | `SigmaSommeBoucleFR` | Explains sigma as compact addition: `sum_{i=0}^n f(i)`, expands terms, works example `sum_{i=0}^4(2i+1)=25`, uses a table of `i`, `2i+1`, and total. | Plain `Scene`; loads prerecorded `assets/voix_off_fr.wav` if present; uses on-screen captions and `add_subcaption`. | Listed in both `README.md` and `AGENT.md`. |
| Functions, intuitive definition | `scenes/function_intuitive_fr/function_intuitive_scene.py` | `FunctionIntuitive` | Introduces a one-variable function as a machine/rule: input `x`, output `f(x)`, same input gives same output, mapping diagram, formal notation `f: R -> R`, graph example `y=2x+1`, vertical-line test, circle as non-function counterexample. | Optional `VoiceoverScene` with Azure fallback; uses `tools.tts`; UQAM intro. | Listed in both `README.md` and `AGENT.md`. |
| Variables and polynomials | `scenes/variables_et_polynomes/variables_et_polynomes_scene.py` | `VariablesEtPolynomes` | Explains variable vs constants, evaluates `2x+1` at `x=0,1,2`, builds a polynomial as a sum of terms, identifies coefficients, then graphs `P(x)=x^2+2x+3`. | Optional `VoiceoverScene`; SSML generated from shared constants to prevent narration/visual drift; UQAM intro. | README/AGENT list `VariablesEtPolynomesFR`, but actual class is `VariablesEtPolynomes`. CI uses the actual class. |
| Graph properties | `scenes/graph_properties_fr/graph_properties_scene.py` | `GraphProperties` | Covers restrictions/intersections with `y>0` and `x<3`; Venn diagram for logical AND; increasing functions; even, odd, periodic functions; application to `f(x)=x^2-2x-3` with roots, vertex/minimum, non-even/non-odd, non-periodic, decreasing/increasing intervals. | Optional `VoiceoverScene`; `tools.tts`; captions; UQAM intro. | Listed in `README.md`; omitted from `AGENT.md` main scene table; included in CI. |
| Completing the square | `scenes/complete_the_square_fr/complete_the_square_scene.py` | `CompleteTheSquare` | Explains geometric meaning of completing the square for `x^2+6x+2`, rewrites as `(x+3)^2-7`, connects to vertex form `a(x-h)^2+k`, graphs the shifted parabola, then derives the quadratic formula from `ax^2+bx+c=0`. | Optional `VoiceoverScene`; `tools.tts`; UQAM intro. Uses local pacing helper methods. | Listed in `README.md`; omitted from `AGENT.md` main scene table; included in CI. |
| Logarithm definition/inverse | `scenes/logarithme_fr/logarithme_scene.py` | `Logarithme` | Starts from bacteria doubling and `2^t=16`; builds table mapping `t` to `2^t` and inverse mapping population to `t`; shows exponential and logarithm graphs as reflections across `y=x`; states domain/image relation for `2^x` and `log_2 x`. | Optional `VoiceoverScene`; `tools.tts`; UQAM intro. | Listed in `README.md`; omitted from `AGENT.md` main scene table; included in CI. |
| Logarithm properties | `scenes/logarithme_fr/logarithme_proprietes_scene.py` | `LogarithmeProprietes` | Extends logarithms through bacterial growth, injectivity of the exponential, product property `log_a(bc)=log_a(b)+log_a(c)`, change-of-base/multiplicative chain `log_a(c)=log_a(b) log_b(c)`, and an estimate for `log_2(1,000,000)`. | Optional `VoiceoverScene`; `tools.tts`; UQAM intro. | Not named in README production table, though README says "definition and properties" for `Logarithme`; omitted from `AGENT.md`; included in CI. |
| Circle area | `scenes/circle_area/circle_area_scenes.py` | `CircleAreaFR` plus helper `RigidMove` | Derives `A = pi r^2` by cutting a circle into wedges, increasing wedge count, and rearranging wedges into a near-rectangle with base `pi r` and height `r`. | `VoiceoverScene`, Azure via `tools.tts`, SSML captions/bookmarks, UQAM intro. | Not listed in `README.md` or `AGENT.md`; included in CI. |
| Sine/unit circle | `scenes/trigonometry_fr/trigonometry_scene.py` | `SineCurveUnitCircle` | Explains sine as the vertical coordinate/height of a point on the unit circle, then records that height as a sine curve over angle, with landmarks `pi`, `2pi`, `3pi` and period `2pi`. | Optional `VoiceoverScene`; `tools.tts`; UQAM intro. Visual style uses white objects/text, apparently dark-background-oriented rather than the standard whiteboard style. | Not listed in `README.md`, `AGENT.md`, or CI. |
| Sine/unit circle alternate | `scenes/trigonometry_fr/trigonometry_play.py` | `SineCurveUnitCircle` | Alternate/iteration of the same sine-unit-circle concept. It has the same class name as `trigonometry_scene.py` but different implementation details. | Optional `VoiceoverScene`; `tools.tts`; UQAM intro. Also dark-background-oriented. | Not listed in `README.md`, `AGENT.md`, or CI. The duplicate class name is potentially confusing. |
| Branding utility | `scenes/uqam_bumper/uqam_bumper_scene.py` | `UQAMLogoBumper`, `UQAMCornerBug` | Branding bumper and corner watermark animation for the UQAM logo. Not mathematical pedagogy. | Plain `Scene`; no narration. | Not listed in `README.md`, `AGENT.md`, or CI. |

## Existing Rendered/Media Artifacts Under `scenes/`

Tracked or local media under `scenes/` includes:

- `scenes/function_intuitive_fr/FunctionIntuitive.mp4`
- `scenes/function_intuitive_fr/FunctionIntuitive_low.mp4`
- `scenes/pythagore_whiteboard_fr/PythagoreAireFR.mp4`
- `scenes/pythagore_whiteboard_fr/PythagoreAireFR_uncompressed.wav`
- `scenes/pythagore_whiteboard_fr/_dragon_test.wav` (0 bytes)
- `scenes/pythagore_whiteboard_fr/subtitles_fr.srt`
- `scenes/sigma_sum_whiteboard_fr/assets/voix_off_fr.wav`
- `scenes/sigma_sum_whiteboard_fr/assets/voix_off_fr.aiff`
- `scenes/sigma_sum_whiteboard_fr/assets/tts_script_fr.txt`
- `scenes/sigma_sum_whiteboard_fr/narration_fr.txt`
- `scenes/sigma_sum_whiteboard_fr/subtitles_fr.srt`
- `scenes/variables_et_polynomes/ssml/fr-CA-*.ssml`

Important distinction: several source scenes exist without a scene-local rendered MP4. The source files are the reliable inventory of available content; scene-local MP4s are only present for `FunctionIntuitive` and `PythagoreAireFR`.

## Experiment/WIP Inventory

| Area | File | Scene class(es) | Pedagogical/content summary | Production readiness notes |
|---|---|---|---|---|
| Fourier/square wave | `experiments/sketches/fourier_series/square_wave.py` | `FourierSquareWave` | Epicycle-style rotating vectors using odd harmonics to approximate/trace a square-wave idea. | No narration, no French captions, not whiteboard style, experimental code comments. |
| Hyperbolic/cone sketch | `experiments/sketches/hyperbolic_cone_to_cusp/hyperbolic_cone_to_cusp.py` | `ConeAngleNegativeCurvature` | 3D surface controlled by cone-angle parameter `beta`, with saddle-like negative-curvature visual. | Not the class/path listed by AGENT. No narration; experimental 3D sketch. |
| Linear algebra/eigenvectors | `experiments/sketches/linear_transform/linear_transform.py` | `EigenvectorTransformation` | Applies matrix `[[3,1],[0,2]]` to a number plane and vectors, highlighting eigenvector behavior. | No narration/French captions; English title string; experiment. |
| Lorenz attractor | `experiments/sketches/lorenz/lorenz.py` | `LorenzAttractor` | 3D Lorenz system with equations in fixed frame and traced solutions from nearby initial conditions to show chaotic divergence. | Uses `scipy.integrate.solve_ivp`; `scipy` is not listed in `pyproject.toml`, so a clean install may not run it. Experimental, not MAT0339-level. |
| Stray algorithm file | `experiments/sketches/sort.py` | `Solution` | LeetCode-style `findMin` function, not a Manim scene. | Not video content. Should not be counted as educational video material. |
| Hairy ball/vector fields | `experiments/wip/hairy_ball/hairy_ball.py` | Many `InteractiveScene` classes | Advanced 3D/topology visual experiments: sphere streamlines, tangent vector fields, stereographic projection, hairy ball theorem, inside-out sphere, normal fields, projected hypersphere flows. | Uses `manim_imports_ext`/ManimGL-style infrastructure, not standard Manim Community. Likely not runnable in the current project setup without extra dependencies. Far beyond MAT0339. |
| Law of cosines | `experiments/wip/law_of_cosines/Lawofcosinus.py` | `LawOfCos`, `LawOfCosTh` | Derives `c^2 = a^2 + b^2 - 2ab cos(gamma)` by decomposing a triangle into right-triangle components `b sin gamma` and `b cos gamma`, then applying Pythagore. | Has Azure voiceover script/bookmarks, but uses dark-style white geometry and lives in WIP. Could be promoted after style/path cleanup. |
| Legendre transform | `experiments/wip/legendre_transform/Legendre.py` | `LegendreTangentIntercept` | Visualizes Legendre transform via tangent slope `p=f'(x0)`, intercept `b`, and dual point `(p,f*(p))` for a convex function. | Whiteboard-like and narrated, but mathematically advanced and outside likely MAT0339 scope. |

## Documentation Discrepancies

### Listed In Docs But Missing Or Different In Tree

- `AGENT.md` lists `HyperbolicConeToCusp` at `scenes/hyperbolic_cone_to_cusp/hyperbolic_cone_to_cusp.py`; that path does not exist. The live related experiment is `experiments/sketches/hyperbolic_cone_to_cusp/hyperbolic_cone_to_cusp.py`, and its class is `ConeAngleNegativeCurvature`.
- `AGENT.md` and `README.md` list `VariablesEtPolynomesFR`; the actual scene class is `VariablesEtPolynomes`.
- `AGENT.md` still presents a smaller "Main Scene Entry Points" table than the live `scenes/` tree.

### Present In Tree But Not Listed In README Or AGENT

- `CircleAreaFR` in `scenes/circle_area/circle_area_scenes.py`
- `LogarithmeProprietes` as a distinct renderable class
- `SineCurveUnitCircle` in both trigonometry files
- `UQAMLogoBumper` and `UQAMCornerBug`

### Present In README But Not AGENT Main Table

- `GraphProperties`
- `CompleteTheSquare`
- `Logarithme`

### Present In CI But Incompletely Documented

CI smoke-renders `CircleAreaFR` and `LogarithmeProprietes`, even though they are not fully reflected in the README/AGENT production tables.

## Pedagogical Coverage Map

Existing production-style coverage is strongest in these areas:

- Geometry proofs and area reasoning: Pythagore, circle area.
- Introductory functions: intuitive definition, graph interpretation, graph properties.
- Algebra and polynomials: variables/constants, polynomial structure, completing the square, quadratic formula.
- Exponential/logarithmic thinking: logarithm as inverse, logarithm properties.
- Discrete notation: sigma notation.
- Trigonometric intuition: sine as unit-circle height, but currently not documented and visually outside the whiteboard standard.

Existing experimental coverage includes advanced topics:

- Fourier visualization.
- Lorenz/chaos.
- Linear transformations/eigenvectors.
- Hyperbolic or negative-curvature surface sketching.
- Law of cosines.
- Legendre transform.
- Hairy ball theorem/topology/vector fields.

For MAT0339 planning, the current repo already has useful destination videos, but it lacks several bridge videos that would make the sequence feel complete for algebra/functions learners.

## Suggested New Videos To Complement MAT0339

These suggestions are inferred from the repo content, not from an official MAT0339 syllabus.

1. **Order of operations and algebraic expressions**
   Existing scenes use expressions heavily, but there is no foundation video on evaluating, simplifying, and reading expressions.

2. **Fractions, powers, roots, and exponent rules**
   Logarithms and quadratic formula rely on exponents/radicals, but the repository has no explicit prerequisite video for exponent laws, square roots, or fractional arithmetic.

3. **Linear equations as balance**
   There is no video on solving first-degree equations step by step. This would bridge variables/polynomials to functions and graphing.

4. **Inequalities and interval notation**
   `GraphProperties` uses restrictions like `y>0`, `x<3`, and intervals, but there is no dedicated introduction to inequalities, number-line intervals, and endpoint conventions.

5. **The Cartesian plane and reading coordinates**
   Many scenes assume axes, coordinates, roots, and graph reading. A short video on points, axes, quadrants, intercepts, and scale would support later graph videos.

6. **Affine/linear functions**
   The repository lacks a production scene on `f(x)=mx+b`, slope, intercept, rate of change, and reading slope from a graph. This is a major gap before graph properties and polynomial analysis.

7. **Factoring polynomials and the zero-product property**
   `GraphProperties` factors `x^2-2x-3`, and `CompleteTheSquare` derives quadratics, but factoring itself is not taught in a standalone scene.

8. **Quadratic functions: standard, factored, and vertex forms**
   `CompleteTheSquare` is strong, but a broader synthesis video could compare the three forms and explain when each is useful.

9. **Domain and range**
   `Logarithme` mentions domains/images for exponential and log functions. A general video on domain/range, restrictions, and graphical reading would connect functions to logs.

10. **Composition and inverse functions**
   The logarithm scene uses inverse-function ideas. A prerequisite video on inverse functions, reflection over `y=x`, and composition checks would make that transition cleaner.

11. **Exponentials before logarithms**
   The log scenes use bacteria doubling. A full production video on exponential growth/decay and exponent notation would make the logarithm videos feel less abrupt.

12. **A cleaned production trigonometry sequence**
   Since trigonometry exists only as undocumented duplicate files with dark-style visuals, decide whether MAT0339 needs trig. If yes, promote one version to the documented whiteboard standard and remove the duplicate ambiguity in a later code cleanup.

## Suggested Ordering From Existing And New Content

A coherent MAT0339-oriented path could be:

1. New: algebraic expressions, constants, variables.
2. Existing: `VariablesEtPolynomes`.
3. New: linear equations.
4. New: Cartesian plane and affine functions.
5. Existing: `FunctionIntuitive`.
6. New: domain/range and graph reading.
7. Existing: `GraphProperties`.
8. New: factoring and zero-product property.
9. Existing: `CompleteTheSquare`.
10. New: exponent rules and exponential growth.
11. Existing: `Logarithme`.
12. Existing: `LogarithmeProprietes`.
13. Existing or optional: `PythagoreAireFR`, `CircleAreaFR`, `SigmaSommeBoucleFR`.
14. Optional after cleanup: `SineCurveUnitCircle`.

## Cleanup Notes For Future Work

No source changes were made, but the inventory suggests these future cleanup decisions:

- Decide whether every directory under `scenes/` is production-ready or whether some should move to `experiments/`.
- Choose one trigonometry implementation or document why both exist; they share the same class name.
- Update `AGENT.md` so its authoritative scene table matches the live tree.
- Update `README.md` to include `CircleAreaFR`, `LogarithmeProprietes`, trigonometry status, and UQAM bumper status if they should be discoverable.
- Fix the `VariablesEtPolynomesFR` vs `VariablesEtPolynomes` naming discrepancy in docs or code.
- Decide whether experiments that require non-declared dependencies (`scipy`, `manim_imports_ext`) should remain in this repo, be documented as external, or be isolated.

