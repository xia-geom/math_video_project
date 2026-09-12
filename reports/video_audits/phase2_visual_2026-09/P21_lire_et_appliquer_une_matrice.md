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
