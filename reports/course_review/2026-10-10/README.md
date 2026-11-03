# Parallel course production review — 2026-10-10

This review covers the canonical catalogue's 43 stable lesson identities. The
display numbers describe the assignment made on this date; they do not define
readiness. Source corrections, encoded inspection, complete playback, listening
and publication approval remain distinct.

## Current evidence

- [Generated review table](current/REVIEW.md)
- [CSV](current/review.csv) and [structured ledger](current/review.json)
- [Review procedure and CLI](../../../docs/COURSE_REVIEW.md)
- Worker source records: [A](worker_a.json), [B](worker_b.json),
  [C](worker_c.json), [coordinator](worker_root.json)
- Independent review records: [A](verification_a.json), [B](verification_b.json),
  [C](verification_c.json)
- Artifact-bound finding closures: [A](reviews_a.json), [B](reviews_b.json),
  [C](reviews_c.json)

The generated table is authoritative for matching artifacts and current check
states. Worker reports retain dated source reviews and sampled evidence; they
do not certify complete playback or listening. Older frames and closures remain
in the evidence history when a subsequent correction makes them stale.

Recorded Git HEADs describe the checkout during each audit. The source files
were then uncommitted; exact input hashes and snapshots identify the tested
revisions. The review checkpoint contains inspected source and text reports;
generated media remain local. Unrelated book work in the shared checkout is
excluded from the separate public math-review branch.

## Work performed

Three workers own disjoint lesson files and regression tests. A owns the first
15 catalogue identities, B the next 15, and C the remaining identities except
`racine_d_un_produit`, owned by the coordinator. Independent verification follows
B→A, C→B and A→C/coordinator. The coordinator owns audit tools, scheduling,
workflows and aggregate reports.

Confirmed corrections include mathematical hypotheses and domain exclusions,
an incorrectly labelled matrix-vector product, unequal geometric unit scales,
proof-card overflow, obscured graph annotations, wrong sigma focus targets,
invisible cell values and tick numerals, a disappearing minus sign during decimal
updates, and overlapping formula transitions.
The worker records specify the exact source location, evidence, correction and
closure condition for each finding. Voices and lesson identities are preserved.

Explicit silent mode now stays silent deliberately. A requested narrated render
fails when its adapter or credentials are unavailable instead of silently
producing a misleading deliverable. Tests exercise those paths with fake
services; they do not synthesize speech.

## Render inventory and provenance

Generated media, caches and logs are local ignored evidence under
`review_artifacts/course_review/2026-10-10/`; they are not included in source Git.

| Attempt | Scope | Evidence and limitation |
|---|---|---|
| `pilot-local` | 15, 26, 31, 39 | Four successful construction audits and silent 480p renders; later fixes invalidate affected artifacts. |
| `course-local` | Other 39 | All 39 construction audits and silent 480p renders succeeded; later fixes invalidate affected artifacts. |
| `qh-a` | Initial high-resolution attempt | Stopped during construction, before video rendering, after the invisible-number defect was confirmed. |
| `qh-full` | All 43 | All 43 silent 1080p/60 fps encoded jobs passed. One lesson-23 construction attempt was rejected because its inputs changed, so the aggregate attempt exited nonzero. Replacement construction supersedes that attempt. |
| `construction-final` | 01, 03, 05, 38 | Four successful replacement construction audits. |
| `qh-replacements-ab31` | 14 corrected lessons | All 14 construction audits and encoded jobs passed; subsequent corrections invalidate affected artifacts. |
| `qh-final-corrections-c25` | 25, 41, 43 | All three construction audits and encoded jobs passed. |
| `qh-final-corrections-a` | 07, 10, 12, 13 | All four construction audits and encoded jobs passed; subsequent corrections supersede 07, 10 and 13. |
| `qh-final-corrections-b` | 16, 23, 27 | All three construction audits and encoded jobs passed; subsequent transition correction supersedes 27. |
| `qh-closure-corrections` | 07, 10, 13, 27 | All four construction audits and encoded jobs passed; independent inspection found persistent masks in 27, requiring one more replacement. |
| `qh-final-mask-cleanup` | 27 | Final construction audit and encoded job passed after actual animation-lifecycle cleanup was corrected. |

Across these attempts, all 43 lessons have a successful current construction
audit and a matching silent 1920×1080, 60 fps video. The final coverage check
verified source/dependency maps, inspector identity, retained construction-frame
hashes, renderer versions and actual video hashes. Its per-lesson inventory is
retained locally as `final-coverage.json`.

No more than two construction/render subprocesses run concurrently. Each attempt
uses fresh lesson-specific media/cache paths. Input hashes are checked before
and after each job. Encoded records include the actual source/dependency map,
video hash, format, runtime versions and a text-only input snapshot. The full
pass retains all distinct construction endpoints, with individual PNG hashes.

The initial `--skip-tests` batches used an earlier runner that printed aggregate
`course_checks_passed: false`; this meant shared tests were skipped, not that
their 43 renders failed. The updated runner reports skipped shared checks as
`null` and separates `selected_render_checks_passed`. Shared test evidence is
stored separately.

Historical files are inventoried by the canonical migration lookup. Their
existence alone does not establish matching sources, dependencies, audio or
current approval. No old media were treated as approved solely by filename.

## Validation

- Canonical catalogue check: exactly 43 unique lesson identities.
- Combined relevant suite: 344 tests and 458 subtests passed. This includes
  catalogue, delivery, workflow policy, narration contracts, timing, containment,
  practice content and the four new review test modules.
- All 116 recorded source, dependency, test and runner inputs remained unchanged
  throughout that run. Its input snapshot, result, XML and log are retained as
  `final-verified-test-*` / `final-verified-tests.*` in the ignored evidence root.
- Four later scene corrections were checked separately: lessons 07, 10 and 13
  passed the 82-test algebra/teaching/visual suite with 742 subtests; lesson 27
  passed all 25 worker-B tests, including actual scene ownership and fade ordering.
  Both final worker runs have matching before/after input hashes. The final
  lesson-27 regression first failed against the defective animation cleanup,
  then passed after removing the detached masks. It exercises actual Manim
  animation compilation, cleanup and later-scene object inventories. The earlier
  worker-B snapshot captured after its run remains historical evidence only.
- The final cosmetic-only deferral gate passed 21 tests and 14 subtests, then
  passed the same suite independently. Major, mathematical, runtime and
  uncategorized findings cannot use the cosmetic exception; a deferral needs a
  nonblank named reviewer. These later results complement the 344-test run;
  that earlier run is not claimed to cover later edits.
- Separate public-safeguard and audit-tool suite: 33 tests and 14 subtests passed.
- Minimal-runtime compatibility after all final source and gate changes: 75 unittest cases
  completed successfully, including 24 explicit skips where the geometry runtime
  was unavailable.
- Full Ruff checks on the new review modules/tests and correctness lint on
  scenes, tools and changed runners passed; whitespace checks passed.

The earlier combined attempt exposed three geometry tests inheriting font
defaults from preceding tests. The tests now isolate and restore the actual
scene defaults; their layout thresholds were retained. The failed attempt and
subsequent successful logs remain in the ignored local evidence directory. An
intermediate broad rerun was deliberately interrupted when new source corrections
were required; its partial result is not counted as a completed suite.
These are source and geometry checks, separate from render, visual and listening
evidence.

## Completion boundaries

The final ledger contains 43 source-mathematics passes and 43 technical passes
on matching 1080p evidence. Of 129 findings, 83 have independent current-artifact
closures, 44 await narrated or complete audiovisual verification, and two are
explicitly deferred cosmetics. Corrections changed 31 lesson scene files.

Visual completion is **0/43**: whole-video displayed mathematics, readability,
motion and final-size review have not been certified. Narrated completion is
**0/43**: the matching artifacts are silent, so narration and audiovisual timing
are blocked. These totals do not erase the completed source, construction,
encoded-stream and targeted visual checks; they prevent partial inspection from
being mistaken for complete acceptance.

Two minor cosmetic findings are explicitly deferred by the coordinator: brief
grid visibility through partially fading labels in lessons 22 and 26. Settled
labels remain readable. The separate lesson-27 masks that erased later diagram
edges and formula symbols were treated as a substantive defect and corrected.

Visual completion requires matching source, technical, displayed mathematics,
readability, full motion and final-resolution review. Narrated completion also
requires complete listening and audiovisual timing. A strictly audio finding can
remain open without falsely invalidating an otherwise completed visual review.
No sampled-frame review is recorded as whole-video completion.

Narrated builds require the existing explicit manual workflow on reviewed
`main`, as specified in [SECURITY.md](../../../SECURITY.md). The workflow's
`numbers` input retains its default `39,40`; explicitly clearing it selects the
whole catalogue. `narrated_review` remains false by default. No paid synthesis,
manual workflow dispatch, Drive publication or release approval was performed
in this source-review task.

The remaining full playback/listening gates require a reviewer able to inspect
the complete matching audiovisual artifacts. Available frame inspection and
stream tools cannot establish those gates. Publication approval remains a
separate decision.
