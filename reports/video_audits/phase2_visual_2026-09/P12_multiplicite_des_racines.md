# P12 — Multiplicité des racines

## Audit target

- Scene: `MultipliciteRacinesFR`
- Source: `scenes/fonctions_et_graphiques_fr/12_multiplicite_des_racines_fr/12_multiplicite_des_racines_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P12-multiplicite_des_racines` (`10288313469`)
- Render: 854×480, 15 fps, duration about 42.40 s
- Render mode: silent low-quality structural visual audit

## Verdict

**REVISE — two P1 visual defects confirmed.**

## Findings

### VIS-P12-001 — P1 — title touches and is clipped by both horizontal frame edges

- Category: frame boundaries / visibility
- Persistent through most of the main scene

The title `Pourquoi une racine traverse ou touche l’axe ?` is scaled too wide for the frame. In representative frames, non-white title pixels reach both pixel columns 0 and 853 of the 854-pixel-wide render, confirming that the title is not contained within a safe margin and is visibly clipped at the edges.

**Closure condition:** reduce or reflow the title and preserve a clear horizontal safe margin in every shot.

### VIS-P12-002 — P1 — formula becomes black scrambled glyphs during transformation

- Category: animation correctness / visibility
- Representative frame: approximately **11.5 s**

During the transition from the line example to the quadratic example, the displayed formula passes through an opaque black scrambled state directly below the already overwide title. The intermediate image is not readable as mathematics.

**Closure condition:** replace or remap the formula transformation so all intermediate frames remain readable, then re-render and inspect the full interval at sub-second cadence.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS* | No independent persistent collision confirmed. |
| Frame boundaries | **FAIL** | Main title reaches both horizontal image boundaries. |
| Visibility | **FAIL** | Title is clipped and formula becomes unreadable during `VIS-P12-002`. |
| Animation correctness | **FAIL** | Formula transform produces scrambled black glyphs. |
| Timing | PASS* | No separate structural timing failure; narration synchronization is not reviewed. |

`PASS*` remains subject to final-resolution and narrated-master checks where applicable.
