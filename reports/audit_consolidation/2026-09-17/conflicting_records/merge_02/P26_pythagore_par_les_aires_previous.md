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
