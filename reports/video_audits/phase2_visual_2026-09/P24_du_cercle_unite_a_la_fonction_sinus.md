# Preserved independent audit records: P24_du_cercle_unite_a_la_fonction_sinus

These are historical observations, not a combined release approval. Both source records are retained below; their status and scope may differ.

## Previously integrated audit record

# P24 — Du cercle unité à la fonction sinus

- Scene: `SineCurveUnitCircle`
- Artifact: `visual-audit-P24-du_cercle_unite_a_la_fonction_sinus` (`10288069568`)
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Render: 854×480, 15 fps, duration about 83.33 s

## Verdict

**REVISE — repeated P1 heading-morph corruption confirmed.**

### VIS-P24-001 — P1 — section headings scramble during text morphs

- Category: animation correctness / visibility
- Confirmed intervals: approximately **42.2–42.4 s** and **57.2–57.4 s**
- Both intervals were rescanned at 0.1 s cadence.

Transitions between numbered explanatory headings morph unrelated sentences character-by-character. The intermediate frames show visibly scrambled black glyphs and are not readable as French text.

**Closure condition:** use fade/replacement transitions for unrelated headings, or explicitly map corresponding text only, then re-render and inspect both intervals.

| Gate | Result |
|---|---|
| Object collisions | PASS* |
| Frame boundaries | PASS |
| Visibility | **FAIL** |
| Animation correctness | **FAIL** |
| Timing | PASS* |


## Audit record from `fix-video-visual-our-scope-2026-09-implementation` (ca7ede74ca58)

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

