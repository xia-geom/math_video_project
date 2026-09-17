# Preserved independent audit records: E05_ordre_de_composition

These are historical observations, not a combined release approval. Both source records are retained below; their status and scope may differ.

## Previously integrated audit record

# E05 — Ordre de composition

- Scene: `CompositionNonCommutativeFR`
- Artifact: `visual-audit-E05-ordre_de_composition` (`10288681251`)
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Render: 854×480, 15 fps, duration about 29 s

## Verdict

**REVISE — one P1 conclusion-transition collision confirmed.**

### VIS-E05-001 — P1 — conclusion text overlaps the two worked-example cards

- Category: object collisions / animation correctness / visibility
- Interval: approximately **24.3–24.7 s**
- Confirmed by a 0.1 s rescan.

The red conclusion (`g∘f ≠ f∘g en général`, followed by `L'ordre fait partie de l'opération.`) and the black explanatory sentence fade in before the two worked-example cards have cleared. Text and formulas visibly occupy the same space for several frames.

**Closure condition:** fully fade/clear the worked-example cards before introducing the conclusion block, then re-render the transition.

| Gate | Result |
|---|---|
| Object collisions | **FAIL** |
| Frame boundaries | PASS |
| Visibility | **FAIL** |
| Animation correctness | **FAIL** |
| Timing | PASS* |


## Audit record from `fix-video-visual-our-scope-2026-09-implementation` (ca7ede74ca58)

# E05 — Ordre de composition

**Verdict: PASS***

- Render: PASS
- Object collisions: PASS
- Frame boundaries: PASS
- Visibility: PASS*
- Animation correctness: PASS
- Visual timing: PASS*

No structural overlap, clipping, broken transformation, or obvious visibility defect was found in the dense silent-render scan.

## Audit scope

This verdict is based on a fresh silent 854×480 render inspected at dense cadence. Narration synchronization is **NOT REVIEWED** in this silent pass. `PASS*` means the structural visual audit passed, but final-resolution visibility and/or narrated-master checks remain.

