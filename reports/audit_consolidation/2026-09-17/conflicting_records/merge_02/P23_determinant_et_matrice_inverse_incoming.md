# P23 — Déterminant et matrice inverse

**Verdict: REVISE**

- Render: PASS
- Object collisions: PASS*
- Frame boundaries: **FAIL**
- Visibility: **FAIL**
- Animation correctness: **FAIL**
- Visual timing: PASS*

## Finding VIS-P23-001 — P1

From approximately **2.0–5.2 s**, the opening title “Matrices 3 — déterminant et matrice inverse” is wider than the frame. Both left and right ends are visibly clipped, leaving no safe horizontal margin.

Evidence: `evidence/P23/VIS-P23-001.jpg`.

## Finding VIS-P23-002 — P1

At approximately **74.4–74.7 s**, the matrix-product expression is transformed into the determinant identity through a scrambled intermediate glyph state. The formula is briefly unreadable before resolving.

**Fix:** replace unrelated formula groups with a clean fade/write or transform only explicitly corresponding subexpressions.

Evidence: `evidence/P23/VIS-P23-002.jpg`.

## Audit scope

This verdict is based on a fresh silent 854×480 render inspected at dense cadence, with suspicious transitions rescanned at sub-second cadence. Narration synchronization is **NOT REVIEWED** in this silent pass. `PASS*` means the structural visual audit passed, but final-resolution visibility and/or narrated-master checks remain.
