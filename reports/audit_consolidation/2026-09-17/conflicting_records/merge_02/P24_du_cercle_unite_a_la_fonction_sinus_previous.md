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
