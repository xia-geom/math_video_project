# Preserved independent audit records: P21_lire_et_appliquer_une_matrice

These are historical observations, not a combined release approval. Both source records are retained below; their status and scope may differ.

## Previously integrated audit record

# P21 — Lire et appliquer une matrice

- Scene: `MatricesLireEtAppliquerFR`
- Artifact: `visual-audit-P21-lire_et_appliquer_une_matrice` (`10287939948`)
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Render: 854×480, 15 fps, duration about 32.13 s

## Verdict

**PASS*** — no structural P1/P0 visual defect confirmed in the rendered timeline.

| Gate | Result |
|---|---|
| Object collisions | PASS |
| Frame boundaries | PASS |
| Visibility | PASS* |
| Animation correctness | PASS |
| Timing | PASS* |

`PASS*` remains subject to final-resolution and narrated-master checks.


## Audit record from `fix-video-visual-our-scope-2026-09-implementation` (ca7ede74ca58)

# P21 — Lire et appliquer une matrice

**Verdict: REVISE**

- Render: PASS
- Object collisions: PASS*
- Frame boundaries: PASS
- Visibility: **FAIL**
- Animation correctness: **FAIL**
- Visual timing: PASS*

## Finding VIS-P21-001 — P1

At approximately **10.1–10.2 s**, the transition from “Deux recettes, deux ingrédients” to “La matrice devient une règle de calcul” morphs unrelated title text through a scrambled, unreadable glyph state while the previous scene is still fading. The diagram itself remains stable, so the defect is localized to the transition.

**Fix:** fade/replace the unrelated title instead of morphing its glyphs.

Evidence: `evidence/P21/VIS-P21-001.jpg`.

## Audit scope

This verdict is based on a fresh silent 854×480 render inspected at dense cadence, with suspicious transitions rescanned at sub-second cadence. Narration synchronization is **NOT REVIEWED** in this silent pass. `PASS*` means the structural visual audit passed, but final-resolution visibility and/or narrated-master checks remain.

