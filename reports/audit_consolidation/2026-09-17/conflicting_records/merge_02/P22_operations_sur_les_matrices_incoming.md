# P22 — Opérations sur les matrices

**Verdict: REVISE**

- Render: PASS
- Object collisions: **FAIL**
- Frame boundaries: PASS
- Visibility: **FAIL**
- Animation correctness: PASS
- Visual timing: **FAIL**

## Finding VIS-P22-001 — P1

From approximately **2.4–6.4 s**, the opening title “Matrices 2 — opérations” occupies the same horizontal/vertical band as the introductory question. The two text blocks remain superimposed for several seconds, producing a persistent unreadable collision rather than a momentary transition artifact.

**Fix:** vertically separate the question from the title or delay the question until the title moves/fades.

Evidence: `evidence/P22/VIS-P22-001.jpg`.

## Audit scope

This verdict is based on a fresh silent 854×480 render inspected at dense cadence, with suspicious transitions rescanned at sub-second cadence. Narration synchronization is **NOT REVIEWED** in this silent pass. `PASS*` means the structural visual audit passed, but final-resolution visibility and/or narrated-master checks remain.
