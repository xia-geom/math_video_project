# Roadmap implementation and validation — 6 November 2026

The requested book revision is complete. The engineering packages are implemented;
the [resumed implementation record](resumed_implementation.md) documents further
active-course lint repair and a newly inspected layout correction. The earlier
claim that engineering work was complete understated that remaining lint work.
Actual listening and whole-video review for the selected historical recordings
remain pending. Global Ruff remains enabled and failing; this is not a claim
that every repository check or audiovisual acceptance gate passes.

Source changes are on `codex/repo-priorities-completion` in
[draft PR #33](https://github.com/xia-geom/math_video_project/pull/33), isolated from
unrelated work in the original checkout. The integration checkpoint is
`039fca094af46426b306eb8823dae55c4afebc4a`, combining the development branch with
main `cd4f2e43391ab4f109e93eacecc6ae18a08ddcb9`. A subsequent lesson 43 transition
correction is in `cb8507b7af7701faed5a5a13b063e8a868c3354d`.

The hosted reports below describe the initial checkpoint. The correction has
separate local regression, construction and encoded-frame evidence. Later PR
checks and the PR description record final-head CI without relabelling these
dated observations or repeatedly committing reports that restart every render.
No source changes are introduced by the final evidence/documentation checkpoint.

## Priority status

| Priority | Implemented and verified | Remaining work or limit |
| --- | --- | --- |
| 1. Reproducible environment | Complete hashed build/check/runtime locks; clean native macOS installation; actual Linux installation; native tools and fonts inventoried | Native platforms are not byte-identical; retain per-render inventories |
| 2. Tests and workflow policy | All 15 workflows and 21 jobs classified; unsafe policy fixtures rejected; test groups documented and integrated into CI | Final-head checks are visible on the PR |
| 3. Current production evidence | Generated ledger for all 73 identities separates fresh, stale, unavailable and unreviewed evidence; corrected preview selected | Three current silent artifacts; zero full visual/narrated approvals |
| 4. Rendering and lint | Conservative affected-lesson selection; manual full scope retained; scoped lint and layout repairs | Global Ruff backlog remains blocking; broader visual candidates are not automatically approved |
| 5. Listening decisions | Immutable local queue; hash-bound flag decisions and separate whole-video review records; replacement media invalidates decisions | Actual reviewer playback/listening and exported decisions |
| 6. Teaching and utilities | Definition/prerequisite remarks addressed; complex-number chapter and matching exercises; circular-motion appendix; eleven historical scripts safe to import | Requested targeted book checks complete; broader certification/publication outside this revision |

Operational references: [setup](../../../docs/DEVELOPMENT.md),
[test scopes](../../../docs/TESTING.md), [workflow policy](../../../docs/WORKFLOW_POLICY.md),
[environment locks](../../../requirements/README.md),
[render selection](../../../docs/RENDER_SELECTION.md) and
[listening review](../../../docs/LISTENING_REVIEW.md).

## Local tests and environment

The [local validation record](local_validation.json) records a broad teaching/tool
run of **825 tests and 1,387 subtests**, with zero failures or skips. It took
639.94 seconds and emitted 115 dependency/deprecation warnings. This selection
uses the teaching profile; unrestricted repository collection lacks the separate
UQAM MoviePy dependency and is not an all-project validation.

The earlier broad run had 30 opening-test scope failures. The correction keeps
one shared opening and the narration adapter mandatory for all 73 lessons, while
the title opening/closing rollout remains enforced for the 43 stable identities
in the dated ledger. The 30 later scene files remain byte-identical to integrated
main. The passing broad run supersedes that failed observation for the initial
checkpoint. After the later transition fix, its two affected regression tests,
construction audit and real preview were rerun separately.

The [macOS environment proof](environment_lock_verification.json) records 61
native wheels, a second clean offline hash-checked install, dependency checks,
isolated editable import and 166 environment/source tests plus 144 subtests.
Pillow 11.3.0 and existing narration profiles were retained. Fontconfig requests
for DejaVu Sans and Roboto resolved to Verdana on this host; that is an explicit
fallback, not a claim that those requested families were installed.

Eleven historical migration utilities were imported with source reads/writes
forbidden. Their executable statements and multiline patch payloads were
preserved; they remain historical commands, not current production steps.

## Hosted Linux evidence

The [contract report](hosted_contract_validation.json) and
[runtime report](hosted_runtime_validation.json) bind results to exact revisions,
checkout trees, job steps and artifacts. The former distinguishes PR-head
checkout from the identical-tree GitHub merge commit. Counts from separate
runs overlap and must not be summed as one suite.

| Workflow at initial checkpoint | Observed result |
| --- | --- |
| Public repository safeguards | Passed; hosted Python 3.11 lock install, policy/scanner regressions and scoped Ruff passed |
| Private data guard | Passed |
| Unified numbering | Catalogue/contracts passed; manual deep audit intentionally not run on a PR |
| Syllabus previews | Passed; 34 tests and ten silent 480p15 previews |
| Teaching review | Passed; 132 tests, 73 construction subprocesses and two silent previews; geometry candidates inspected separately |
| Ten-lesson recheck | Passed; 400 tests and 19 subtests, one explicit integration skip, ten silent 1080p60 renders; render step took 38m17s |
| Smoke | Compile and selection passed; global Ruff failed with 7,168 diagnostics, so rendering was skipped |

The Linux runtime inventory exactly matches the 64-package union of the build
and teaching locks. Its Python 3.13.18, Cairo/Pango, FFmpeg and TeX versions differ
from the Mac inventory. DejaVu Sans is present; Roboto falls back to DejaVu Sans.
Three artifact archive digests and all twenty syllabus/ten-lesson video digests
were verified. A package lock does not freeze native libraries, fonts or OS bytes.

The 73-lesson construction audit had zero construction failures and zero frame-
clipping candidates. It also produced 916 stricter safe-margin candidate states
across 28 lessons, which remain unreviewed candidates rather than confirmed
clipping defects. Two overlap states in lesson 43 were confirmed as a real defect
and corrected below. A green job alone does not clear geometry or visual review.

The ten rendered lessons have no changed rendering inputs between the initial
checkpoint and the transition-fix commit, verified with the actual input-hash
closure. This preserves that scoped evidence; it does not claim later CI has run.

## Encoded inspection and the transition correction

The [initial preview review](locked_preview_review.json) records 60 sampled
frames across lessons 1, 5 and 43. No defect was found in those samples; the later
construction audit revealed an unsampled overlap in lesson 43. The
[Linux preview review](hosted_encoded_preview_review.json) separately records ten
frames from the rational-functions lesson, with no observed clipping, overlap
or incorrect displayed formula in those samples.

The [transition correction](fraction_transition_correction.json) removes the
outgoing factor explanation before the denominator restrictions enter their
shared caption band. The original fraction stays visible until the restrictions
are established, then the simplification appears once. Total narration-block
and encoded-video duration remain unchanged.

The corrected source passed two targeted regression tests and an independent
46-state construction audit with zero overlap or boundary candidates. Six real
encoded transition frames confirmed caption clearance and formula persistence.
Construction captures and actual encoded frames are recorded separately. Full
motion, complete listening and final-resolution visual approval were not inferred.

## Current evidence view

The [final current-evidence summary](final_evidence_summary.json) records 73
lessons, three current silent artifacts, zero visual-completion approvals and
zero narrated-completion approvals. Lesson 43 now uses the corrected preview;
its preceding preview remains historical/stale. Every catalogue input file
matches the transition-fix commit; the dirty working-tree flag reflects later
documentation/evidence updates.

The earlier [precommit summary](current_evidence_summary.json) and
[clean integration-checkpoint summary](postcommit_evidence_summary.json) remain
unchanged dated observations. Missing historical coherence/narration artifacts
are unavailable, not accepted. Full ledgers and media remain ignored local files.

## Book revision

The [book revision](../../../books/mat0339/docs/revision-2026-11-06.md) and
[verification record](../../../books/mat0339/docs/verification-2026-11-06.json)
cover real coefficients/monomials, quadratic domains, real exponents, integer
counting quotients and cosine before the dot product. Chapter 17 now introduces
complex numbers with 24 exercise questions, three synthesis problems and answers.
Circular motion, its exercises and answers remain in appendix A.

All 126 historical section identities and their video references are preserved;
eight complex-number identities bring the total to 134. Seventy-seven standalone
checks and six explicit catalogue integration tests passed. The manual, student
workbook and answer workbook compiled to **211, 68 and 88 pages**, plus a five-page
video catalogue. Forty-six targeted pages were inspected, with independent review
of the affected mathematics. This is not an exhaustive visual or PDF/UA audit.

Generated PDFs are in `books/mat0339/dist/`; verified identical copies were placed
in that ignored directory of the original checkout. No dated release, Drive
replacement, archive mutation, exam change or institutional approval was created.

## Listening handoff and publication boundaries

The local queue contains 12 screening flags in nine unchanged utterance clips
and three full historical videos: `variables_et_polynomes`, `fonction_reciproque`
and `annulation_dans_les_fractions`. They predate later narration wording. The
full screen has 86 candidates, not 86 established audio defects.

The page and validator require exact report/media bindings, named dated reasons
and strict listening confirmations; whole-video observations are separate from
flag dispositions. No reviewer observations or acceptance records were invented.
The ignored queue is under
`review_artifacts/listening_review/selected-historical-lessons-20261106/` and is
not available in a fresh clone. Actual listening and exported decisions remain
required to finish this priority.

Local and hosted scoped secret scans passed after exact source-fingerprint proof.
The hosted contract report records sampled public responses/logs and artifact
metadata, plus omitted payloads, binary material, older logs and administrative
settings. A passing scan is not privacy or licensing clearance. Existing notices,
voices, manual narration gates and separate promotion-project boundaries remain
intact. No new paid narration, publication or release approval is implied.
