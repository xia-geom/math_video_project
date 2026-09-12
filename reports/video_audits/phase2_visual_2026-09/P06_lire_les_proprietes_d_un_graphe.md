# P06 — Lire les propriétés d'un graphe

## Audit target

- Scene: `GraphProperties`
- Source: `scenes/fonctions_et_graphiques_fr/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P06-lire_les_proprietes_d_un_graphe` (`10288203568`)
- Render: 854×480, 15 fps, duration about 208.53 s
- Render mode: silent low-quality structural visual audit

## Verdict

**PASS — structural visual first pass.**

The entire approximately 208.5 s timeline was sampled at 0.5 s cadence and reviewed across the restriction/intersection, parity, monotonicity, periodicity, polynomial, and graph-transformation sequences through the final summary.

No confirmed persistent formula/formula collision, label/graph collision, frame clipping, white-on-white object, obviously broken transformation, or residual object from a previous section was found in this structural pass.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS | No confirmed persistent text/graph/formula collision in the 0.5 s timeline scan. |
| Frame boundaries | PASS | Titles, axes, annotations, formulas, and final summary remain inside the frame. |
| Visibility | PASS* | Structural contrast is adequate; the many small graph annotations require final 1080p confirmation. |
| Animation correctness | PASS | No confirmed jump, residual object, or unreadable transform in the sampled timeline. |
| Timing | PASS* | No obvious long dead interval or unreadably short stable hold. Narration synchronization is not reviewed in the silent audit render. |

No evidence image is retained because no defect was confirmed.

`PASS*` means passed at the low-quality structural stage and remains subject to final-resolution or narrated-master checks where applicable.
