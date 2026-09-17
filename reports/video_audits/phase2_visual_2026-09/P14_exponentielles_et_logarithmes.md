# P14 — Exponentielles et logarithmes

## Audit target

- Scene: `Logarithme`
- Source: `scenes/exponentielles_et_logarithmes_fr/14_logarithmes_fr/14_logarithmes_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P14-exponentielles_et_logarithmes` (`10288084012`)
- Render: 854×480, 15 fps, duration about 102.80 s
- Render mode: silent low-quality structural visual audit

## Verdict

**PASS* — no structural P1/P0 visual defect confirmed.**

The full timeline was scanned at 1 s cadence. The bacterial-growth tree, inverse-function graphics, logarithm properties, change-of-base derivation, worked example, and synthesis panel remain structurally inside the frame without a confirmed collision or corrupted text/formula morph.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS | No persistent collision confirmed. |
| Frame boundaries | PASS | No cut-off title, graph, table, or formula confirmed. |
| Visibility | PASS* | No structural visibility failure; several small formulas still require final-resolution review. |
| Animation correctness | PASS | No broken or misleading transformation confirmed. |
| Timing | PASS* | No obvious structural timing failure; narration synchronization is not reviewed. |

`PASS*` remains subject to final-resolution and narrated-master checks where applicable.
