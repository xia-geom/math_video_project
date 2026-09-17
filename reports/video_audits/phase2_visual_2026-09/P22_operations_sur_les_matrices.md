# Preserved independent audit records: P22_operations_sur_les_matrices

These are historical observations, not a combined release approval. Both source records are retained below; their status and scope may differ.

## Previously integrated audit record

# P22 — Opérations sur les matrices

- Scene: `OperationsMatricesFR`
- Artifact: `visual-audit-P22-operations_sur_les_matrices` (`10288239347`)
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Render: 854×480, 15 fps, duration about 83.93 s

## Verdict

**REVISE — one P1 intro collision/animation defect confirmed.**

### VIS-P22-001 — P1 — intro title, subtitle, and matrix content pile up

- Category: object collisions / visibility / animation correctness
- Interval: approximately **2.5–5.5 s**

The opening `Matrices 2 — opérations` title remains overlaid with incoming question text and matrix content for several seconds. Multiple unrelated objects occupy the same horizontal band, making the intro visibly cluttered and partially unreadable.

**Closure condition:** finish or clear the title/question transition before introducing the matrices, then re-render and inspect the complete intro.

| Gate | Result |
|---|---|
| Object collisions | **FAIL** |
| Frame boundaries | PASS |
| Visibility | **FAIL** |
| Animation correctness | **FAIL** |
| Timing | PASS* |


## Audit record from `fix-video-visual-our-scope-2026-09-implementation` (ca7ede74ca58)

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

