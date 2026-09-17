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
