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
