# October 13 finalization follow-up

The latest completed dedicated CI runs at `8d11ba3` passed: ten-lesson
containment ([38149488998](https://github.com/xia-geom/math_video_project/actions/runs/38149488998)),
syllabus previews ([38149488802](https://github.com/xia-geom/math_video_project/actions/runs/38149488802)),
and teaching review ([38149488863](https://github.com/xia-geom/math_video_project/actions/runs/38149488863)).
Independent inspection matched all 22 encoded video hashes, 20 complete render
input maps and 43 teaching source hashes. These runs precede the title correction
below; their unchanged lesson evidence remains reusable by input identity.

The ten-lesson run passed 311 tests and 19 subtests, with one unrelated history
integration test skipped. Syllabus tests passed 34; teaching tests passed 56.
All 43 teaching constructions passed. Full-repository Ruff remains failing as
previously disclosed; no checks were disabled.

## Lesson 31 title portability

The hosted construction audit reported the opening question at horizontal bounds
[-7.140625, 7.140625], just beyond the physical 16:9 frame. Two candidate states
refer to the same title. Ranked retention had discarded those original title
images; this is a confirmed geometric overflow, not an inspected original hosted
video frame. The matching local rendering used narrower text metrics.

The question now wraps after “cercle”, retaining its wording, 42-point bold type,
subtitle, narration, timing and diagram scale. An actual source-derived geometry
regression reproduced the old overflow using Verdana and passes after the fix.
Syntax and focused lint pass. Worker A independently reviewed the source change
and its regression.

A fresh complete 1080p60 silent lesson rendered successfully (84.683333 seconds).
A separate 1080p60 Verdana opening excerpt explicitly tests wide font metrics;
it is a diagnostic artifact, not a replacement lesson or a font change. Worker A
inspected both encoded openings at original resolution and closed the title
finding. All 4,611 decoded frames after the opening match the previously reviewed
artifact exactly; A verified the prior evidence hashes and revalidated both older
formula/annotation findings against the replacement. No whole-video pass was added.

## Evidence retention and current review

All three complete CI bundles were copied to the ignored local
`review_artifacts/course_review/2026-10-13/ci_evidence/` archive. Every copied
file hash was checked. The GitHub copies expire October 25; the local archive
has no Actions retention deadline. Existing older local renders were retained.
Generated media, cache files and credentials remain outside new Git commits.

The current JSON ledger, Markdown table and CSV are generated under
`review_artifacts/course_review/2026-10-13/current/`. Historical October 10 and 11
reports are unchanged. The ledger includes all 43 stable catalogue identities;
only lesson 31's selected output changes after this correction. The ledger retains
84 narrow independent closures, 44 awaiting audiovisual verification and two
explicitly deferred cosmetic findings. Source and
technical checks pass for all 43 matching silent artifacts. Complete visual
review and narrated acceptance remain 0/43.

No full playback, full listening, narration approval or publication approval is
claimed. Local credentials are available for an explicit narrated build from
reviewed main; they have not been copied to GitHub. A capable reviewer still needs
to inspect every complete matching narrated video before final acceptance.
