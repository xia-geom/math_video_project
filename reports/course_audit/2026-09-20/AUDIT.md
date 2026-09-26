# Global course audit and numbering — 20 September 2026

## Scope and current checkpoint

Requested follow-up to PR #11: audit the complete course, and make every course
video use consistent global numbering. Baseline:
`0bcd9451b644256a2ad2927d5eccc5aa8797404e`.

This initial checkpoint contains the tested migration recipe, catalogue helpers
and audit workflow. The full GitHub checkout migration and new encoded renders
are not yet reported as verified here. This report will receive measured results
from the exact tested commit. The PR is not merged and no video is published.

## Numbering decision

Use 01–37 for the main syllabus in chapter order, then 38–43 for the six
common-error supplements. Identity animation and promotional films are outside
the course sequence. Integrate the ten new lessons within their chapters,
including elimination before Cramer and linear programming. Preserve the planned
geometry and Sigma conclusion. Complex numbers remains optional and unimplemented.

The canonical manifest becomes version 3. Stable semantic `lesson_id` values
identify lessons; `order` supplies the global display number. Old P/E/S codes are
historical aliases. Source folders, source filenames, delivery names, selections,
indexes and routes are changed together. Public scene classes are preserved.
`numbering_migration.json` and the generated legacy index preserve old-to-new paths,
old delivery names, old track positions and source hashes. Historical reports are
not rewritten. Existing local MP4s, render archives and Drive files are untouched.

## Audit findings addressed by the migration

1. Two manifests held different course inventories and source numbering. New
   lessons now belong to the unified catalogue; the extension file becomes a
   production-scope selection without a second copy of paths or prerequisites.
2. Production validation stopped at old position 24. Audio and quality
   requirements become explicit for every teaching entry, independent of order.
3. Construction review used a numeric subset and smoke CI a hand-maintained
   matrix. Both are changed to read all 43 registered course entries.
4. Generic render names came from source folders while curriculum packaging used
   delivery slugs. Both now use the catalogue's same numbered delivery name.
5. Drive routing inferred modules from source categories; completing the square
   belongs to the functions module despite its algebra source folder. Routing now
   follows the manifest, with unregistered productions kept local.
6. The batch auditor selected a production path after rendering a low-quality
   preview. It now inspects the fresh preview path, not a possibly stale master.
7. Root inventories duplicated stale counts. Generated Markdown/CSV indexes
   replace manually copied course lists and have drift checks.
8. The triangle lesson depended on a later Pythagoras proof. Keeping the syllabus
   conclusion, school-level Pythagoras is now explicit assumed knowledge and the
   later proof is a related lesson, not a forward video prerequisite.
9. The documented editable installation used a nonexistent setuptools backend.
   The backend and package discovery are corrected without changing runtime
   dependency versions; actual editable installation is included in CI.

## Verification at the initial checkpoint

Local replay on the previous source snapshot validated all 43 sources, unique
contiguous global numbers, prerequisites, historical aliases, delivery names,
Drive routes, preview paths, generated indexes and candidate selections. Forty
pure checks passed, including YAML and the embedded dynamic-matrix Python syntax.
Python compilation passed for the locally available scenes, tools and scripts.

Manim is not installed in this local environment, so those checks do not establish
rendering or visual correctness. The new workflow will record construction states,
fresh silent MP4s and frame samples for every lesson, plus full test and Ruff
artifacts. Broad repository lint remains an explicit separate result; it is not
disabled, silently narrowed or assumed to have passed. Sampled frame intersections
are candidates for review, not automatic proof of a visual defect.

## Remaining audiovisual gates

Do not infer final readiness from renumbering. Full-motion review, final-resolution
legibility, real narration, complete listening and publication approval remain
separate. A silent preview is not a narrated release, and old evidence must not
be attributed to new source bytes without verification.
