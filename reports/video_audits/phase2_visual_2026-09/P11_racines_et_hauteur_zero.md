# P11 — Racines et hauteur zéro

## Audit target

- Scene: `RacineHauteurZeroFR`
- Source: `scenes/fonctions_et_graphiques_fr/11_racines_et_hauteur_zero_fr/11_racines_et_hauteur_zero_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P11-racines_et_hauteur_zero` (`10287634954`)
- Render: 854×480, 15 fps, duration about 35.73 s
- Render mode: silent low-quality structural visual audit

## Verdict

**REVISE — one P1 animation/visibility defect confirmed.**

## Findings

### VIS-P11-001 — P1 — polynomial formula turns into opaque black blobs during transition

- Category: animation correctness / visibility
- Interval: approximately **31.4–31.7 s**
- Worst sampled frames: near **31.5 s**

As the graph and polynomial expression transition into the final root definition, the mathematical formula is temporarily replaced by dense black glyph clusters. The intermediate state is not interpretable as a formula and looks like rendering corruption rather than an intentional transformation.

**Closure condition:** replace or remap the formula transition so every intermediate frame remains mathematically readable, then re-render and inspect the whole transition at sub-second cadence.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS* | No independent persistent layout collision confirmed. |
| Frame boundaries | PASS | No cut-off title, graph, or formula confirmed. |
| Visibility | **FAIL** | Formula becomes unreadable during `VIS-P11-001`. |
| Animation correctness | **FAIL** | Transition produces opaque black glyph clusters. |
| Timing | PASS* | No separate structural timing failure; narration synchronization is not reviewed. |

`PASS*` remains subject to final-resolution and narrated-master checks where applicable.
