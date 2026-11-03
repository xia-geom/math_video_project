# New mathematics video audit — 2 November 2026

Capsule 72's period arrow intruded into the time-label band. Its vertical
position now follows the measured label bounds, with 0.18 scene units of
clearance; its endpoints still align with 3 h and 15.4 h. The displayed
mathematics, narration, timing, scene class and catalogue identity are unchanged.

The teaching-review workflow also excluded stacked pull requests because it
accepted only PRs targeting `main`. Removing that base-branch filter enables
the existing silent construction review on dependent PRs. Path filters,
read-only permissions, exact-head checkout and the explicit manual-main
paid-narration gate remain intact. This workflow constructs the entire
catalogue but renders only the two existing E02/E03 reference previews; it
does not establish encoded-video coverage for every new capsule.

## Scope and synchronization

The audit covers the 30 new mathematics capsules 44–73, identified from the
latest GitHub drafts: [PR #27](https://github.com/xia-geom/math_video_project/pull/27)
at `3e700ec0079ad7bb2bc72af672122de321ec51ad` and its dependent
[PR #30](https://github.com/xia-geom/math_video_project/pull/30) at
`2ac08a23ff55c51aa00717d70c34eed3996b5ab9`. Review changes are based on the latter.
The unified catalogue remains the source of identities and numbering.

GitHub references were fetched and local `main` was fast-forwarded to
`4d451c37d483d763e33683a7fb683d1e0fdde62d`. The existing active branch and its
unfinished UQAM photo work were preserved. Audit work used a clean, isolated
checkout; no older draft was merged, no history rewritten, and no asset bundle
or generated media was added to Git.

## Checks completed

- All 30 scene sources received mathematical, hypothesis, example and object
  lifecycle review. No new mathematical correction was identified. The 22
  independent arithmetic check groups for 44–65 passed; those 22 source hashes
  still match the preceding split audit. All 30 sources parse successfully.
- Capsule 72's actual authored geometry reproduced the defect: minimum
  clearance was −0.1294 scene units. The source-linked regression failed before
  the fix and passed afterward. It lives in `tests/test_teaching_revision.py`,
  which both teaching CI and the broader course runner execute.
- The stacked-PR policy regression also failed on the original workflow and
  passed after the one-line trigger change. The final focused run passed
  **89 tests and 5 subtests**, including the existing narration and credential
  guards. Changed Python files pass scoped Ruff and syntax checks;
  `git diff --check` passes.
- Capsule 72 received one fresh low-quality silent render: **854×480,
  15 fps, 47.267 seconds, 709 frames**, with no audio stream. Full FFmpeg
  decoding passed. Encoded samples at 15.900, 16.267 and 16.400 seconds show
  clear labels and a clean exit in those samples. This is not continuous playback.
- An independent reviewer checked the final source/test connection, corrected
  encoded frame and unchanged workflow safety gates; no actionable issue remained.
- Fresh construction checks passed for **all 30 new capsules**, with **744
  distinct stable states** and zero automated overlap/margin candidates.
  These endpoint checks do not inspect every intermediate animation frame.
- The broader local course suite passed **406 tests and 1,337 subtests**.
  Correctness lint passed; repository-wide Ruff still reports **7,425
  existing diagnostics**. The separate focused rerun above covers the final
  two regressions, which were added after collection of the broader run.

The original local review environment stalled while reading NumPy files.
Validation therefore used a fresh temporary environment with the repository
workflow's pinned Manim 0.19.0, voiceover 0.3.7 and Pillow 11.3.0. Dependency
consistency passed. Exact installed renderer versions and the environment
snapshot hash are recorded in [verification.json](verification.json).

## Existing CI limitations and acceptance

The exact GitHub heads of #27 and #30 pass public/private safeguards and smoke
compile/catalog checks. Both report 7,425 repository-wide Ruff findings, matching
the existing baseline diagnostic codes, messages and paths; the dependent smoke
render is skipped. PR #27 additionally has successful teaching and syllabus
checks; #30 previously lacked the teaching workflow because of its base branch.
These are separate from the eight historical geometry assertion failures
documented in [the preceding baseline comparison](../2026-11-01-split/baseline-failures.json).
Those eight historical assertions do not fail in this fresh local Mac runtime;
no source fix or cross-platform clearance is claimed for them. No unrelated
check was disabled or relabelled as passing.

Keep the existing drafts and their review order. All new capsules remain
`authored`, and `release_ready` remains false. Narration synthesis, narrated
duration, listening, continuous playback, final-resolution review and
institutional approval remain pending. This audit neither publishes videos
nor copies deliveries to Drive.

Only the inspected task text is checkpointed. This video audit does not claim
a new complete history/secret scan, repository-settings audit, review of all
discussions/logs/downloadable artifacts, or clearance of media rights.
