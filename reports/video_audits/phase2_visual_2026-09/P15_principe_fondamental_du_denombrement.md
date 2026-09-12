# P15 — Principe fondamental du dénombrement

## Audit target

- Scene: `PrincipeFondamentalDenombrementFR`
- Source: `scenes/probabilites_fr/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P15-principe_fondamental_du_denombrement` (`10288353616`)
- Render: 854×480, 15 fps, duration about 69.86 s
- Render mode: silent low-quality structural visual audit

## Verdict

**REVISE — one P1 frame-boundary/visibility defect confirmed.**

## Findings

### VIS-P15-001 — P1 — intro title is clipped on both horizontal sides

- Category: frame boundaries / visibility
- Interval: approximately **2.5–4.5 s**
- Representative frame: approximately **3.5 s**

The opening title `Dénombrement 1 — principe fondamental ...` is substantially wider than the frame. Its left and right portions are cut off, so the title cannot be read in full.

**Closure condition:** reduce or reflow the title and retain a visible horizontal safe margin, then re-render and inspect the complete intro.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS | No independent persistent collision confirmed. |
| Frame boundaries | **FAIL** | Opening title extends outside the frame. |
| Visibility | **FAIL** | The opening title is incomplete on screen. |
| Animation correctness | PASS | No separate corrupted transform confirmed. |
| Timing | PASS* | No obvious structural timing failure; narration synchronization is not reviewed. |

`PASS*` remains subject to final-resolution and narrated-master checks where applicable.
