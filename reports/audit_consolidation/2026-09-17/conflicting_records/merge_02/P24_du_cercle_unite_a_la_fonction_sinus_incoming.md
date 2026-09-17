# P24 — Du cercle unité à la fonction sinus

**Verdict: REVISE**

- Render: PASS
- Object collisions: PASS*
- Frame boundaries: PASS
- Visibility: **FAIL**
- Animation correctness: **FAIL**
- Visual timing: PASS*

## Finding VIS-P24-001 — P1

Section-heading replacements repeatedly morph unrelated sentences through scrambled, unreadable glyph states. Confirmed intervals include approximately **17.6–17.8 s** (section 1 → 2) and **30.4–30.6 s** (section 2 → 3). The circle/axis animation itself remains clean.

**Fix:** fade out the previous heading and write/fade in the next heading instead of character-morphing unrelated prose.

Evidence: `evidence/P24/VIS-P24-001.jpg`.

## Audit scope

This verdict is based on a fresh silent 854×480 render inspected at dense cadence, with suspicious transitions rescanned at sub-second cadence. Narration synchronization is **NOT REVIEWED** in this silent pass. `PASS*` means the structural visual audit passed, but final-resolution visibility and/or narrated-master checks remain.
