# P08 — Opérations sur les fonctions

## Audit target

- Scene: `OperationsFonctionsFR`
- Source: `scenes/fonctions_et_graphiques_fr/08_operations_sur_les_fonctions_fr/08_operations_sur_les_fonctions_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P08-operations_sur_les_fonctions` (`10288570692`)
- Render: 854×480, 15 fps, duration about 63.47 s
- Render mode: silent low-quality structural visual audit

## Verdict

**REVISE — one P1 frame-boundary/visibility defect confirmed.**

## Findings

### VIS-P08-001 — P1 — common-domain annotation is clipped by the right frame edge

- Category: frame boundaries / visibility
- Interval: approximately **7.5–8.5 s** in the sampled audit timeline
- Representative frames show the boxed annotation beginning with `domaine commun : x ∈ Dom(f) ∩ ...` extending beyond the right boundary of the 854×480 frame.

The annotation is not merely close to the safe area: its text and box are visibly truncated by the video edge. This makes the mathematical condition incomplete on screen.

**Closure condition:** reposition or rescale the annotation so the complete domain statement remains inside the frame with a visible safe margin, then re-render and inspect the full interval.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS | No other persistent layout collision confirmed. |
| Frame boundaries | **FAIL** | The common-domain annotation is cut off on the right. |
| Visibility | **FAIL** | The truncated domain statement cannot be read in full. |
| Animation correctness | PASS | No separate transform corruption confirmed in this pass. |
| Timing | PASS* | No obvious structural timing failure; narration synchronization is not reviewed. |

`PASS*` remains subject to final-resolution and narrated-master checks where applicable.
