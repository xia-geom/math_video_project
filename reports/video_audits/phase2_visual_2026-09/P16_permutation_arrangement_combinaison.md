# P16 — Permutation, arrangement et combinaison

## Audit target

- Scene: `PermutationArrangementCombinaisonFR`
- Source: `scenes/probabilites_fr/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P16-permutation_arrangement_combinaison` (`10288423571`)
- Render: 854×480, 15 fps, duration about 70.86 s
- Render mode: silent low-quality structural visual audit

## Verdict

**REVISE — one P1 formula-animation defect confirmed.**

## Findings

### VIS-P16-001 — P1 — arrangement formula becomes scrambled during generalization

- Category: animation correctness / visibility
- Interval: approximately **16.4–16.6 s**
- Confirmed by a 0.1 s rescan of the transition

As the concrete calculation `5 × 4 × 3 = 60` is transformed into the general arrangement formula, the mathematical glyphs pass through a dense, scrambled intermediate state. The formula is not readable as valid mathematics in these frames.

**Closure condition:** replace the direct morph with a mathematically mapped transform or a clean fade/write transition, then inspect the entire transition at sub-second cadence.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS* | No independent persistent collision confirmed. |
| Frame boundaries | PASS | No cut-off title, table, or formula confirmed. |
| Visibility | **FAIL** | Formula is unreadable during `VIS-P16-001`. |
| Animation correctness | **FAIL** | Generalization morph produces scrambled mathematical glyphs. |
| Timing | PASS* | No separate structural timing failure; narration synchronization is not reviewed. |

`PASS*` remains subject to final-resolution and narrated-master checks where applicable.
