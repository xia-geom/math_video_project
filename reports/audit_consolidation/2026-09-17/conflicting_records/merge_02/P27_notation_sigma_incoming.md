# P27 — Notation sigma

**Verdict: REVISE**

- Render: PASS
- Object collisions: PASS*
- Frame boundaries: PASS
- Visibility: **FAIL**
- Animation correctness: **FAIL**
- Visual timing: PASS*

## Finding VIS-P27-001 — P1

Several explanatory-text transitions morph unrelated captions through unreadable intermediate glyph states. Confirmed examples occur around **21.6–21.8 s** (“additionner les résultats” → initial-index explanation), **26.5–26.7 s** (expression explanation → loop instruction), and again around **40.6–40.9 s** when the five computed values transition to their expanded sum.

**Fix:** use fade/replace transitions for unrelated captions and preserve only genuinely corresponding mathematical objects during transforms.

Evidence: `evidence/P27/VIS-P27-001.jpg`.

## Audit scope

This verdict is based on a fresh silent 854×480 render inspected at dense cadence, with suspicious transitions rescanned at sub-second cadence. Narration synchronization is **NOT REVIEWED** in this silent pass. `PASS*` means the structural visual audit passed, but final-resolution visibility and/or narrated-master checks remain.
