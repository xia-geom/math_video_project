# P10 — Fonction réciproque

## Audit target

- Scene: `FonctionReciproqueFR`
- Source: `scenes/fonctions_et_graphiques_fr/10_fonction_reciproque_fr/10_fonction_reciproque_fr_scene.py`
- Audit render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`
- Workflow run: `34663789994`
- Artifact: `visual-audit-P10-fonction_reciproque` (`10287704831`)
- Render mode requested: silent low-quality structural visual audit

## Verdict

**BLOCKED — no auditable MP4 was produced.**

The render exits with code 1 inside the scene's own layout validator before a video is produced:

`ValueError: [act 3] layout overlap between left derivation and inverse result.`

This is strong evidence that the current scene construction contains a layout conflict, but Phase 2 does not convert that source/runtime diagnostic into a rendered-frame verdict.

**Closure condition:** repair the `act 3` layout overlap, produce a successful audit render, then inspect the full rendered timeline.

## Phase-2 checklist

All visual gates are **N/R** because no auditable render exists.
