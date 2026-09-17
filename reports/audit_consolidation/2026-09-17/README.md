# Audit integration — September 17, 2026

All 15 inventoried audit branch tips are preserved as ancestors of this integration.
Five ordered merge commits incorporate independent work; duplicate branch pointers
and intermediate branches do not need separate content merges. Original remote
branches are retained. No force-push, textbook update, or video publication is part
of this operation.

## Current source ownership

- P01–P04, P21–P27, E01–E06: `fix-video-visual-our-scope-2026-09`.
- P05–P20: `fix-video-visual-p05-p20-2026-09`, including its later refinements.
- UQAM short/long films: the exact source from PR #2, except workflow cleanup.

Every changed teaching scene must be byte-identical to its designated source in
the integration snapshot. Future intentional edits remain possible. The earlier
implementation branch stays in history without overwriting newer scoped fixes.
Conflicting capsule reports preserve both original texts. Original master reports
are in `source_status/`; conflict originals are in `conflicting_records/`.
No historical observation is silently upgraded to a pass.

## Navigation and automation

[Repository audit index](../../AUDIT_INDEX.md) is the entrypoint.
One-off visual patch/render workflows were moved unchanged into `legacy_workflows/`.
Their old branch assumptions must not run on main. The UQAM revision workflow is
manual-only; completed migration and stale-badge steps were removed. It retains
testing/rendering and separate narration gates. Preparation is strictly limited to
`integration/audits-2026-09-17`, never main.

## Validation and remaining gates

[Integration validation run](https://github.com/xia-geom/math_video_project/actions/runs/35271768479) records the tested commit, compilation,
per-blob preservation, ancestry and JUnit results. Consult the actual run outcome;
this document is not itself evidence of a pass. Historical whitespace is reported
without altering imported records; newly authored integration files are checked
strictly and conflict markers always fail.

No new narrated film is certified. Speech credentials, listening, real subtitle
synchronization, final-resolution review and release approval remain separate.

## Source branch inventory

| Branch | Inventoried head |
|---|---|
| `audit-video-visual-2026-09` | `aed409ea4c1e8e450643f5cfed47053cd22ef31f` |
| `audit-video-visual-evidence-2026-09` | `dd0fb52dcb397d1739bcf152b338a7cfe84407d0` |
| `audit-video-visual-evidence-final` | `dd0fb52dcb397d1739bcf152b338a7cfe84407d0` |
| `audit-video-visual-evidence-merge` | `dd0fb52dcb397d1739bcf152b338a7cfe84407d0` |
| `audit-video-visual-evidence-pr` | `dd0fb52dcb397d1739bcf152b338a7cfe84407d0` |
| `audit-video-visual-remainder-2026-09` | `10abeb40b4ee98e7e990ebd28e80584a634f6d3d` |
| `fix-video-visual-our-scope-2026-09-2` | `55f0ca64f741ac542132395e1c294bf5f0c29131` |
| `fix-video-visual-our-scope-2026-09-work` | `55f0ca64f741ac542132395e1c294bf5f0c29131` |
| `fix-video-visual-our-scope-2026-09-work2` | `55f0ca64f741ac542132395e1c294bf5f0c29131` |
| `fix-video-visual-our-scope-2026-09-final` | `678ffaa6519b2c15ed10d69ae36935acd42f5ed0` |
| `fix-video-visual-our-scope-2026-09-run` | `678ffaa6519b2c15ed10d69ae36935acd42f5ed0` |
| `fix-video-visual-our-scope-2026-09-implementation` | `ca7ede74ca589b9d023710d91fbc51d10552fc88` |
| `fix-video-visual-our-scope-2026-09` | `950d8095e7064ecfbafcf75bc8da921273c5b0f1` |
| `fix-video-visual-p05-p20-2026-09` | `86ce0f74114fb4dc7d30fb8c5cc7c61e90b7dadb` |
| `fix/uqam-video-audit-2026-09-14` | `095697e5f5de550795c7d18879f85fa5163fe81c` |
