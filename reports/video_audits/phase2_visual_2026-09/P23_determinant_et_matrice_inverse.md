# Preserved independent audit records: P23_determinant_et_matrice_inverse

These are historical observations, not a combined release approval. Both source records are retained below; their status and scope may differ.

## Previously integrated audit record

# P23 — Déterminant et matrice inverse

- Scene: `DeterminantEtMatriceInverseFR`
- Artifact: `visual-audit-P23-determinant_et_matrice_inverse` (`10288069590`)
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Render: 854×480, 15 fps, duration about 88.80 s

## Verdict

**REVISE — one P1 frame-boundary defect confirmed.**

### VIS-P23-001 — P1 — opening title exceeds the horizontal frame

- Category: frame boundaries / visibility
- Interval: approximately **2.5–4.5 s**

The opening `Matrices 3 — déterminant et matrice inverse` title is wider than the frame. Its beginning and ending are visibly cut off during the intro.

**Closure condition:** reduce or reflow the title and preserve a clear horizontal safe margin.

| Gate | Result |
|---|---|
| Object collisions | PASS |
| Frame boundaries | **FAIL** |
| Visibility | **FAIL** |
| Animation correctness | PASS |
| Timing | PASS* |


## Audit record from `fix-video-visual-our-scope-2026-09-implementation` (ca7ede74ca58)

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

