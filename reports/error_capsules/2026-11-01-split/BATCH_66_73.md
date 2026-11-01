# Separate draft review: MAT0339 capsules 66–73

Validated on 1 November 2026. This branch is stacked on PR #27
(`feat/mat0339-erreurs-lot1-20261016`), not directly on `main`.
Review PR #27 first; after it is merged, retarget this PR to `main` and recheck
the resulting diff and tests. Neither PR is ready for narrated audiovisual acceptance.

## Scope and dependencies

The diff adds the eight original scenes and READMEs, their eight catalogue entries,
regenerated numbering/playlist/book maps, the four catalogue-count test updates,
and batch-specific evidence. All scene and README bytes match verified commit
`340d438f954bcee1cefbbed951ea4187aa600d94`. Capsule 48 and the earlier batches
are inherited unchanged from PR #27; they are not reintroduced as new changes.

Dependencies are resolved by the stack: 66 needs the logarithm lesson 47;
72 needs the amplitude and phase lessons 53–54; 73 needs the doubling-time lesson 56.
The first 65 catalogue entries and the inherited repair are unchanged.
The catalogue has 73 entries (37 main lessons, 36 error supplements),
all new entries remain `authored`, and `release_ready` remains false.

The [historical batch audit](../2026-11-01-batch-66-73/AUDIT.md) and its extracted
records are distinct from the [fresh validation manifest](batch-66-73-validation.json).
The original combined audit remains available at the immutable November 1 commit.
The [parent validation](PR27.md) is inherited without alteration.

## Actual fresh results

| Check | Result |
|---|---|
| Catalogue, book maps and syllabus checks | Pass; 73 catalogue entries, 17 chapter mappings |
| Book mathematical/structural tests | 64 passed |
| Independent new-batch mathematics | Eight source/narration reviews and 29 calculation groups passed; [details](batch-66-73-mathematics.json) |
| Scene syntax and scoped Ruff | All nine selected sources pass, including inherited 48 |
| Correctness lint | Pass |
| New batch construction | 214 stable states for 66–73, zero automated overlap/margin candidates |
| Inherited 48 construction | 29 states, zero candidates |
| Fresh encoded previews | Eight new-batch previews plus 48; all silent, 854×480 at 15 fps |
| Full FFmpeg decoding | All nine previews pass |
| Selected encoded-frame review | 40 new-batch frames plus two frames of 48; no defect observed in those samples |
| Capsule 48 regression | Frames 408 and 410 are pixel-identical to the previously verified repaired encode |
| Provenance | All nine scene hashes, complete input signatures and selected output hashes rechecked against the final source tree |
| Generated student catalogue | Five-page PDF compiled; pages 1, 4 and 5 inspected, including every new row; no clipping/overlap observed |
| Broader course suite | 399 passed, 8 failed, 1,337 subtests passed |
| Repository-wide Ruff | 7,425 existing diagnostics; not a pass |

All eight broad-suite failures reproduce with the exact same assertion messages
on untouched commit `340d438`, and on both split branches. They concern existing
layout tests in `test_course_review_a.py`, `test_course_review_b.py` and
`test_course_review_c.py`, not the eight new capsules. The isolated comparison also
retains its failing result; see [baseline evidence](baseline-failures.json).
No check was disabled. The broad audit runner exits 1; its selected render checks
pass, but its overall automated-course flag is false.

## Reproduction and acceptance

From this branch, with repository dependencies installed, run:

```bash
python scripts/course_audit.py --numbers 48,66,67,68,69,70,71,72,73 --jobs 2 --all-construction-states --output review_artifacts/split-repeat-66-73
python tools/course_catalog.py check
python books/mat0339/scripts/verify.py
python books/mat0339/scripts/video_map.py
```

Use a fresh output directory. The runner executes the broader suite and reports
its failures; it does not synthesize narration unless explicitly requested.
Tests and previews were run from `340d438` plus the reviewed split working tree;
complete per-input hashes in the manifest identify the tested content more precisely
than that original commit field. Later report edits are not renderer inputs.
Generated MP4s, frame PNGs, PDFs and caches remain outside source Git.

**Keep this PR in draft.** Silent renders and sampled frames do not establish narrated
duration, listening, continuous human playback, final-resolution review or release
approval. No narration was synthesized and no video was published.
