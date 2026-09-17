# P17 — Répétitions en dénombrement

## Audit target

- Scene: `RepetitionsDenombrementFR`
- Source: `scenes/probabilites_fr/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P17-repetitions_en_denombrement` (`10287834750`)
- Render: 854×480, 15 fps, duration about 63.87 s
- Render mode: silent low-quality structural visual audit

## Verdict

**REVISE — one P1 text-animation defect confirmed.**

## Findings

### VIS-P17-001 — P1 — section subtitle scrambles during transition

- Category: animation correctness / visibility
- Interval: approximately **20.4–20.5 s**
- Confirmed by a 0.1 s rescan

The subtitle transitions from the first-case statement to `Pourquoi ce n'est pas 4 × 3 × 2`. During the morph, the teal text passes through a visibly scrambled, unreadable glyph state. This is the same class of unrelated-text morph failure already observed in other capsules.

**Closure condition:** replace the subtitle morph by a clean fade/replacement or another transition whose intermediate frames remain readable.

## Phase-2 checklist

| Gate | Result | Notes |
|---|---|---|
| Object collisions | PASS* | No independent persistent layout collision confirmed. |
| Frame boundaries | PASS | No cut-off title, diagram, or formula confirmed. |
| Visibility | **FAIL** | Subtitle becomes unreadable during `VIS-P17-001`. |
| Animation correctness | **FAIL** | Unrelated subtitle text is morphed through scrambled glyphs. |
| Timing | PASS* | No separate structural timing failure; narration synchronization is not reviewed. |

`PASS*` remains subject to final-resolution and narrated-master checks where applicable.
