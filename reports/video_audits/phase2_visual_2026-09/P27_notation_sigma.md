# P27 — Notation sigma

- Scene: `SigmaSommeBoucleFR`
- Artifact: `visual-audit-P27-notation_sigma` (`10288019931`)
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Render: 854×480, 15 fps, duration about 81 s

## Verdict

**REVISE — two P1 visual defects confirmed.**

### VIS-P27-001 — P1 — explanatory sentence scrambles during morph

- Category: animation correctness / visibility
- Interval: approximately **9.3–9.6 s**
- Confirmed by a 0.1 s rescan.

The teal sentence `100 termes à additionner` is morphed into `Une consigne compacte doit remplacer la liste.` through a character-level intermediate state that is visibly scrambled and unreadable.

### VIS-P27-002 — P1 — summary-card captions collide with box borders

- Category: object collisions / text outside boxes
- Interval: approximately **73.5 s to the end of the summary**

The captions `calculer f(i), puis additionner` and `calculer f(i), puis multiplier` sit across the lower borders of the two summary boxes. The border visibly passes through the caption area instead of containing the text cleanly.

**Closure conditions:** use a clean sentence replacement for `VIS-P27-001`; move the summary captions fully inside the cards or below them with clear separation for `VIS-P27-002`.

| Gate | Result |
|---|---|
| Object collisions | **FAIL** |
| Frame boundaries | PASS |
| Visibility | **FAIL** |
| Animation correctness | **FAIL** |
| Timing | PASS* |
