# P18 — Déplacement et composantes

## Audit target

- Scene: `VecteursDeplacementComposantesFR`
- Source: `scenes/vecteurs_fr/18_deplacement_et_composantes_fr/18_deplacement_et_composantes_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P18-vecteurs_deplacement_et_composantes` (`10288024369`)
- Render: 854×480, 15 fps, duration about 27.47 s
- Render mode: silent low-quality structural visual audit

## Verdict

**REVISE — one P1 frame-boundary defect confirmed.**

## Findings

### VIS-P18-001 — P1 — explanatory box extends beyond the right edge

- Category: frame boundaries / visibility
- Interval: approximately **12.5–13.5 s**

The right-hand explanatory box accompanying the equality of displacement vectors extends outside the frame. The sentence beginning `même direction · même sens · ...` is visibly truncated at the right boundary, so the intended explanatory condition cannot be read in full.

**Closure condition:** reposition, resize, or wrap the explanatory box so the entire sentence remains inside a safe horizontal margin.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS | No independent persistent collision confirmed. |
| Frame boundaries | **FAIL** | Right-hand explanatory box is cut off. |
| Visibility | **FAIL** | Explanatory sentence is incomplete on screen. |
| Animation correctness | PASS | No separate corrupted transform confirmed. |
| Timing | PASS* | No obvious structural timing failure; narration synchronization is not reviewed. |

`PASS*` remains subject to final-resolution and narrated-master checks where applicable.
