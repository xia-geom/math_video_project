# Roadmap implementation — validation in progress, 6 November 2026

Implementation for all six roadmap priorities is present in the integrated
worktree. Targeted independent reviews found no remaining actionable regressions
in their reviewed scope. Hosted Linux validation, a final broad-suite rerun and
human audiovisual acceptance are still outstanding; this record
is not a release approval or a claim that every repository check passes.

Integration uses `codex/repo-priorities-completion`, combining the earlier
repository-development branch with main
`cd4f2e43391ab4f109e93eacecc6ae18a08ddcb9`. Main's 73-lesson catalogue, October 17
book corrections, newer audio/evidence checks, workflow Action pins and existing
production gates were retained. Work was isolated from unrelated files in the
original checkout. UQAM projects and the separate silent English clip retain
their own dependency and production boundaries.

## Implemented priorities

| Priority | Implemented result | Remaining validation or acceptance |
| --- | --- | --- |
| 1. Reproducible environment | Hashed build/check/runtime locks; platform-specific teaching locks; native-tool and font inventories; shared CI installation contracts | Actual hosted Linux and Python 3.11 lock installation/tests |
| 2. Tests and workflow policy | All 15 workflows and 21 jobs classified; permissions, triggers, pinned Actions and paid/manual gates validated; unsafe synthetic fixtures rejected; test groups documented | Integrated hosted CI |
| 3. Current production evidence | Existing ledger reconciles historical source, coherence and narration records with explicit freshness and media availability; acceptance remains separate | Human review for current artifacts; historical media unavailable in this worktree |
| 4. Rendering and lint | Conservative affected-lesson selection with full manual smoke retained; selected source/layout repairs; scoped lint fixes without disabling global lint | Hosted selection/render results and the remaining global lint backlog |
| 5. Listening decisions | Immutable local queue, hash-bound flag decisions and separate whole-video review records; replacement media invalidates decisions | Reviewer playback, listening and exported decisions |
| 6. Teaching and utilities | Book definitions corrected, a complex-number chapter added, prior circular-motion material preserved in Appendix A; eleven historical migration scripts made safe to import | Requested targeted checks complete; wider certification and publication are outside this revision |

See [development setup](../../../docs/DEVELOPMENT.md),
[test scopes](../../../docs/TESTING.md),
[workflow policy](../../../docs/WORKFLOW_POLICY.md),
[environment locks](../../../requirements/README.md) and
[listening review](../../../docs/LISTENING_REVIEW.md) for the operational contracts.

## Environment, previews and evidence

The [environment verification record](environment_lock_verification.json)
records a native macOS arm64 Python 3.13 build of 61 wheels, followed by a clean,
fully offline, hash-checked runtime installation. Dependency checking and an
isolated editable import passed. The recorded environment/source suite passed
166 tests and 144 subtests. Pillow 11.3.0 was preserved. Linux runtime and Python
3.11 check locks have target metadata validation but have not yet been executed
in hosted CI. Native tools, libraries, OS and fonts are inventoried rather than
locked in an immutable OS image. Fontconfig requests for DejaVu Sans and Roboto
resolved to Verdana on this host; the inventory records that fallback explicitly.

Three new silent previews completed for lessons 1, 5 and 43. The
[encoded-frame review](locked_preview_review.json) records inspection of 60
frames across those previews, with no clipping, collisions or incorrect displayed
mathematics found in the inspected samples. Twenty-four additional extracted
hold/end frames were not inspected. The lesson 5 circle conclusion now uses the
lower caption band; lesson 43 reveals each simplification once after its domain
restrictions. These are sample-frame observations, not complete motion or
listening passes, and the previews contain no newly synthesized narration.

The [dated current-evidence summary](current_evidence_summary.json) records 73
lessons, three current artifacts, zero visual-completion approvals and zero
narrated-completion approvals. Only the three previews have fresh technical
evidence; historical source checks are stale, and absent historical media is
reported as unavailable. The summary intentionally identifies the dirty working
source state at observation time; it is not evidence for an unspecified later
commit. Full local ledger data and media remain ignored review artifacts.

## Book verification

The [book revision report](../../../books/mat0339/docs/revision-2026-11-06.md)
and [machine-readable verification](../../../books/mat0339/docs/verification-2026-11-06.json)
record 77 standalone checks plus six explicit video-catalogue integration tests.
All 126 previous section IDs were preserved and eight complex-number IDs were
added, giving 134 IDs. Prior circular-motion exercises and answers remain in
Appendix A with their historical identities; the new complex-number chapter
occupies chapter 17.

The manual, student workbook and answer workbook were built at 211, 68 and 88
pages respectively, plus the five-page video catalogue. Forty-six targeted
physical pages were inspected across these outputs. Independent source review
covered the new complex-number questions, synthesis and answers and the selected
definition corrections. No remaining calculation/definition defect or clipping,
overlap or unresolved reference was identified in that reviewed scope. This is
a working edition, not an exhaustive visual audit, PDF/UA certification or
institutional approval. Generated PDFs remain outside source Git.

## Prepared human listening handoff

The selected local queue contains 12 screening flags in nine unchanged utterance
clips and three complete videos: `variables_et_polynomes`,
`fonction_reciproque` and `annulation_dans_les_fractions`. These historical October
recordings predate later narration wording. The full screen has 86 candidate
flags in 64 utterances across 31 lessons; silence screening alone does not
establish a defect.

The queue binds report, lesson, media hashes, utterance index and intervals to
stable IDs. Validation rejects unknown/duplicate IDs, changed original or copied
media, and non-Boolean listening confirmations. Full-video reviews are recorded
separately from flag decisions. No reviewer observations, listening decisions or
whole-video approvals have been generated. The immutable HTML queue is local
under `review_artifacts/listening_review/selected-historical-lessons-20261106/`;
it is ignored and is not available in a fresh clone.

## Integrated checks and known limits

Counts below describe separate, overlapping runs and must not be added together.

- The initial broad run over 42 root test/tool files passed 714 tests and 1,387
  subtests, with 30 failing opening-contract cases for lessons 44–73 introduced
  on main. The test contract was corrected: one shared opening/narration adapter
  remains mandatory for all 73 lessons; title opening/closing remains enforced
  for the 43 stable IDs in the dated ledger. The corrected targeted run passed
  126 tests, scoped Ruff and diff checks. No production or preview inputs changed,
  and all 30 later scene files remain byte-identical to the integrated main
  revision. A final rerun of the complete broad selection is still pending; the
  earlier failing run is retained here rather than described as a pass.
- Unrestricted repository-wide pytest collection is blocked in the teaching
  environment by the separate UQAM MoviePy dependency profile. The teaching lock
  is not an all-repository environment. This does not replace the separate
  project's checks or authorize changing its dependency boundary.
- The workflow/dependency/environment/listening group passed 126 tests and five
  subtests. The local review UI's embedded JavaScript passed a syntax check.
  Targeted evidence, selector, snapshot, scanner and import-safety regression
  suites were also exercised. The latest combined checks following CI test-group
  integration passed 97 tests and 16 subtests. Independent reviews do not certify
  unreviewed repository code.
- Global Ruff remains enabled and failing. The initial run reported 7,173
  diagnostics; five small repairs reduced the final count to 7,168, including
  6,812 `F405` diagnostics. Counts by root are: `archive` 1,743, `experiments`
  1,331, `miscellaneous` 35, `scenes` 4,018, `scripts` 10, `tests` 21 and `tools`
  10. Scoped checks passing do not clear this repository-wide backlog.
- Real Gitleaks checks over local Git history covered 458 commits and 85 refs:
  858 findings were proven source fingerprints and zero remained blocking. The
  current tracked-file scan similarly verified 336 source fingerprints with
  zero remaining findings. Fingerprint exceptions require exact source-byte
  proof; synthetic actual credentials remain blocking in regression tests.
  These local scans do not audit remote settings, discussions, workflow logs or
  downloadable artifacts. Those external GitHub surfaces were not checked in
  this local run and remain part of hosted/public-readiness work.
- The [measured Linux CI baseline](ci_baseline.json) records exact earlier heads,
  run URLs, jobs and step durations. Earlier smoke rendering was skipped after
  global lint failures, so no render-duration result can be inferred from those
  jobs. Earlier successful teaching/syllabus runs predate these new locks and
  do not validate the integrated branch.
- Relative Markdown file links in the reviewed development, testing, workflow,
  course-review, listening and book documentation were checked locally. Remote
  URLs and heading anchors were not validated by that check.

No hosted result for this integrated change, complete audiovisual acceptance,
new paid narration, publication, Drive replacement or institutional approval is
claimed. The final broad-suite rerun and hosted execution need explicit results;
the prepared media and listening queue require actual human review.
