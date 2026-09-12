# P01 — Variables et polynômes

## Audit target

- Scene: `VariablesEtPolynomes`
- Source: `scenes/algebre_et_polynomes_fr/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P01-variables_et_polynomes` (`10288452627`)
- Render: 854×480, 15 fps, duration about 70.40 s
- Render mode: silent low-quality structural visual audit

## Verdict

**REVISE — one P1 visual defect confirmed.**

The complete structural timeline was scanned at 0.5–1.0 s cadence, with a finer 0.25 s scan around the confirmed transition. No persistent frame clipping, white-on-white content, caption-over-mathematics collision, or obvious long dead interval was found in this first pass.

## Findings

### VIS-P01-001 — P1 — collision during a text/formula transformation

- Category: object collision / animation correctness
- Interval: approximately **17.50–17.75 s**
- Evidence: `evidence/P01/VIS-P01-001.jpg`

During the transition from the annotated expression `2x+1` to the definition of a variable, outgoing annotations and incoming definition text cross through one another. At approximately 17.50 s the formula, labels, and incoming sentence visibly pile up; remnants remain crossed at approximately 17.75 s. The intermediate state is not readable.

**Closure condition:** replace the crossing morph with a clean transition that never superposes semantically unrelated text/formula objects, re-render, and inspect the full transition frame-by-frame.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | **FAIL** | `VIS-P01-001` at 17.50–17.75 s. |
| Frame boundaries | PASS | No cut-off title/formula or unsafe edge placement confirmed in the structural render. |
| Visibility | PASS* | No obvious contrast/white-on-white problem; small-text legibility still requires the final 1080p confirmation. |
| Animation correctness | **FAIL** | `VIS-P01-001`. |
| Timing | PASS* | No obvious dead interval or unreadably short visual hold in the structural pass. Narration synchronization is not reviewed in the silent audit render. |

`PASS*` means passed at the low-quality structural stage and remains subject to final-resolution or narrated-master checks where applicable.
