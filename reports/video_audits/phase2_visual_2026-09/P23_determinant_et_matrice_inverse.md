# P23 — Déterminant et matrice inverse

- Scene: `DeterminantEtMatriceInverseFR`
- Artifact: `visual-audit-P23-determinant_et_matrice_inverse` (`10288069590`)
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Render: 854×480, 15 fps, duration about 88.80 s

## Verdict

**REVISE — one P1 frame-boundary defect confirmed.**

### VIS-P23-001 — P1 — opening title exceeds the horizontal frame

- Category: frame boundaries / visibility
- Interval: approximately **2.5–4.5 s**

The opening `Matrices 3 — déterminant et matrice inverse` title is wider than the frame. Its beginning and ending are visibly cut off during the intro.

**Closure condition:** reduce or reflow the title and preserve a clear horizontal safe margin.

| Gate | Result |
|---|---|
| Object collisions | PASS |
| Frame boundaries | **FAIL** |
| Visibility | **FAIL** |
| Animation correctness | PASS |
| Timing | PASS* |
