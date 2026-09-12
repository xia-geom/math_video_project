# P05 — Modèles affines et quadratiques

## Audit target

- Scene: `ModelesLineairesQuadratiques`
- Source: `scenes/fonctions_et_graphiques_fr/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P05-modeles_affines_et_quadratiques` (`10288123382`)
- Render: 854×480, 15 fps, duration about 45.60 s
- Render mode: silent low-quality structural visual audit

## Verdict

**REVISE — one P1 animation defect confirmed.**

The complete timeline was scanned at 0.5 s cadence, with a finer 0.2 s scan around the suspect quadratic-form transition.

## Findings

### VIS-P05-001 — P1 — quadratic formula becomes scrambled during transformation

- Category: animation correctness / visibility
- Interval: approximately **31.0–31.4 s**, worst representative frame near **31.2 s**
- Evidence: `evidence/P05/VIS-P05-001.jpg`

The scene transitions from the specific example \(g(x)=x^2\) to the general quadratic form \(g(x)=ax^2+bx+c\), with \(a\neq 0\). During the transformation, the outgoing and incoming mathematical glyphs are mapped through an intermediate state that is visibly scrambled and not readable as a valid formula.

**Closure condition:** replace the morph between the distinct formulas with a transition that preserves mathematical readability (for example, fade out/write in or a carefully mapped transform), re-render, and inspect the entire transition frame-by-frame.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS* | No persistent layout collision confirmed outside the defective formula transition. |
| Frame boundaries | PASS | No cut-off title, graph, table, or formula confirmed. |
| Visibility | **FAIL** | The intermediate quadratic formula is unreadable in `VIS-P05-001`. |
| Animation correctness | **FAIL** | Formula morph scrambles mathematical glyphs. |
| Timing | PASS* | No obvious long dead interval or unreadably short stable hold. Narration synchronization is not reviewed in the silent audit render. |

`PASS*` means passed at the low-quality structural stage and remains subject to final-resolution or narrated-master checks where applicable.
