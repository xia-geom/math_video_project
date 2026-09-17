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
