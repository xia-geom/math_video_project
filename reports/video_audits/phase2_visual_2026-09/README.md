# Phase 2 — Visual audit (September 2026)

Audit branch: `audit-video-visual-2026-09`

Base production commit: `0c4556ab07e8ae700c1556148374a83c0808cef1`

Canonical scope: all 33 entries in `curriculum/programme_principal_fr.yaml` (27 programme capsules and 6 `Erreurs fréquentes` capsules).

## Audit rule

A scene is **not** marked visually audited from source inspection alone. A visual verdict requires inspection of a rendered MP4. The older `reports/video_audits/` reports are retained as historical diagnostics only: they sampled eight frames and their frame directories are gitignored, so they do not constitute the intensive Phase 2 timeline review.

The current audit uses fresh low-quality 16:9 renders from the frozen audit branch for the first visual pass. Any suspected frame-boundary, legibility, rasterization, or small-text issue must be rechecked at 1080p before closure.

Narration-dependent timing is not certified by a silent render. Such checks remain `NOT REVIEWED` until a narrated render is available.

## Required visual checks

Each rendered timeline is inspected for:

1. **Object collisions** — formula/formula, label/graph, text outside boxes, arrows through text, captions covering mathematics.
2. **Frame boundaries** — cut-off objects, titles too close to borders, formulas exceeding frame width.
3. **Visibility** — white-on-white, insufficient contrast, tiny labels, thin graph lines, transient objects that disappear too rapidly.
4. **Animation correctness** — incorrect transformations, unexpected jumps, residual objects, or formulas changing meaning during a transformation.
5. **Timing** — visually detectable dead intervals and unreadably short holds; narration/visual synchronization requires narrated evidence.

## Evidence policy

Do not commit frame dumps or complete rendered videos. Temporary GitHub Actions artifacts may contain the low-quality MP4s needed for inspection. For a confirmed finding, retain only the smallest useful evidence: normally one screenshot at the exact timestamp, or a short clip when the problem is temporal.

Every confirmed finding receives an identifier of the form `VIS-P01-001`, a timestamp or interval, severity, category, description, and closure condition.

## Status

Fresh render workflow: `.github/workflows/visual-audit-render.yml`.

Current verdicts will be added only after direct inspection of the newly rendered artifacts.
