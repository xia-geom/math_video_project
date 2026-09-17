# P04 — Domaine et image d'une fonction

## Audit target

- Scene: `FonctionsDomaineImageFR`
- Source: `scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P04-domaine_et_image_d_une_fonction` (`10288307970`)
- Render: 854×480, 15 fps, duration about 68.06 s
- Render mode: silent low-quality structural visual audit

## Verdict

**REVISE — one repeated P1 animation defect confirmed.**

The complete timeline was scanned at 0.5 s cadence, with finer 0.1–0.2 s scans around suspect text transitions. The principal defect is not a persistent layout collision; it is the repeated use of transformations between unrelated strings, which produces visibly scrambled intermediate glyphs.

## Findings

### VIS-P04-001 — P1 — unrelated text morphs become unreadable

- Category: animation correctness / visibility
- Confirmed intervals: approximately **56.1–56.3 s**, **64.6–64.8 s**, and around **66.2 s**
- Evidence: `evidence/P04/VIS-P04-001.jpg` (representative frame near 56.2 s)

At about 56.2 s, the outgoing title `Le graphe montre le domaine et l’image` is being transformed into `Une relation n’est pas toujours une fonction`. Their glyphs morph through an intermediate state that is visibly scrambled and unreadable. The same mechanism recurs in the recap text near 64.6–64.8 s and again around 66.2 s.

**Closure condition:** replace transformations between semantically unrelated text objects with a clean fade/write or other non-scrambling replacement, then inspect every text change in the scene frame-by-frame after re-rendering.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS* | No persistent layout collision confirmed; the repeated failure is transitional glyph superposition/morphing. |
| Frame boundaries | PASS | No cut-off title, formula, graph, or caption confirmed in the structural render. |
| Visibility | **FAIL** | Intermediate transformed text becomes unreadable (`VIS-P04-001`). |
| Animation correctness | **FAIL** | Repeated unrelated-text morphs scramble glyphs. |
| Timing | PASS* | No obvious long dead interval or unreadably short stable hold. Narration synchronization is not reviewed in the silent audit render. |

`PASS*` means passed at the low-quality structural stage and remains subject to final-resolution or narrated-master checks where applicable.
