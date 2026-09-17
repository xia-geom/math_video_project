# Preserved independent audit records: P26_pythagore_par_les_aires

These are historical observations, not a combined release approval. Both source records are retained below; their status and scope may differ.

## Previously integrated audit record

# P26 — Pythagore par les aires

- Scene: `PythagoreAireFR`
- Artifact: `visual-audit-P26-pythagore_par_les_aires` (`10288024875`)
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Render: 854×480, 15 fps, duration about 35 s

## Verdict

**REVISE — one P1 derivation-transition collision confirmed.**

### VIS-P26-001 — P1 — explanatory derivation overlaps during compression to the identity

- Category: object collisions / animation correctness / visibility
- Interval: approximately **25.2–25.7 s**
- Confirmed by a 0.1 s rescan.

As the multi-line area derivation is compressed into the equation relating the large square, triangles and central square, old and incoming text/formula glyphs occupy the same region. In particular the `Carré central` line becomes overprinted and unreadable for several frames.

**Closure condition:** clear/fade the explanatory block before writing the condensed identity, or explicitly map only corresponding formulas, then re-render the transition.

| Gate | Result |
|---|---|
| Object collisions | **FAIL** |
| Frame boundaries | PASS* |
| Visibility | **FAIL** |
| Animation correctness | **FAIL** |
| Timing | PASS* |


## Audit record from `fix-video-visual-our-scope-2026-09-implementation` (ca7ede74ca58)

# P26 — Pythagore par les aires

**Verdict: REVISE**

- Render: PASS
- Object collisions: **FAIL**
- Frame boundaries: PASS
- Visibility: **FAIL**
- Animation correctness: **FAIL**
- Visual timing: PASS*

## Finding VIS-P26-001 — P1

Around **25.2–25.5 s**, the outgoing area-decomposition text/equations and the incoming simplified identity are simultaneously visible in the same region. The result is a dense superimposed formula block before the new identity settles.

**Fix:** clear the old derivation before introducing the simplified identity, or transform only genuinely corresponding terms.

Evidence: `evidence/P26/VIS-P26-001.jpg`.

## Audit scope

This verdict is based on a fresh silent 854×480 render inspected at dense cadence, with suspicious transitions rescanned at sub-second cadence. Narration synchronization is **NOT REVIEWED** in this silent pass. `PASS*` means the structural visual audit passed, but final-resolution visibility and/or narrated-master checks remain.

