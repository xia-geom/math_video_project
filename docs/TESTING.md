# Test groups and evidence

Use [the development setup](DEVELOPMENT.md) for the appropriate Python profile.
These groups describe existing tests and commands; they do not add another test
runner or change test import behavior. A focused group passing is not a claim
that the repository's entire test suite or global lint passes.

## Fast contracts

Catalogue, dependency, workflow and synthetic source/privacy tests can run with
the lightweight checks environment. They do not need Manim, LaTeX, fonts, Azure
credentials or video rendering.

```sh
python scripts/check_workflow_policy.py
python tools/course_catalog.py check
python tools/course_catalog.py --check-indexes
python -m pytest tests/test_teaching_dependencies.py tests/test_workflow_policy.py \
  tests/test_environment_lock.py tests/test_affected_lessons.py \
  tests/test_public_workflow_policy.py tests/test_course_workflow_syntax.py \
  tests/test_course_catalog.py tests/test_course_source_snapshot.py \
  tests/test_public_fingerprints.py tests/test_course_evidence.py \
  tests/test_listening_review.py tests/test_historical_utility_imports.py -q
```

The public-audit and course-numbering workflows retain their existing focused
checks. Real Gitleaks tests are a separate integration group: they require the
checksum-verified detector and use invented fixtures. Without `GITLEAKS_BIN`,
those tests are explicitly skipped; see [public readiness](PUBLIC_READINESS.md).

## Construction and geometry

Tests such as `test_teaching_revision.py`, `test_course_review_a.py`,
`test_course_review_b.py` and `test_course_review_c.py` import the teaching
renderer and exercise geometry, source mathematics, narration contracts and
construction states. Run them in the reviewed teaching environment with native
rendering dependencies and the expected fonts. They can create native text/math
objects and caches; they do not constitute full encoded-video playback or listening.

Record failures against the exact source and environment. Existing dated baseline
reports remain evidence of their own revisions, not exemptions for current tests.
Keep the root smoke workflow's full `ruff check .` blocking check intact.

## Silent render review

An actual preview requires the teaching environment, FFmpeg, Cairo/Pango and
LaTeX. Use a fresh output directory and a stable catalogue identity. For example:

```sh
MANIM_DISABLE_VOICEOVER=1 python scripts/course_audit.py \
  --numbers fonctions_rationnelles --quality ql --jobs 1 \
  --output review_artifacts/course_review/local-rational-preview
```

Report construction, encoding and encoded-frame inspection separately. Sampled
frames do not establish complete motion review. Full-course audits and final-size
reviews remain separate from a selected low-quality smoke preview.

## Narration and release review

Narration uses the existing shared `tools/tts.py` profiles and may incur charges.
CI requests it only by explicit manual selection on reviewed `main`; PR checks
remain silent. Verify audio provenance, measured timing and the exact artifact
before recording listening decisions. A synthesized or successfully encoded file
is not evidence of listening, institutional approval or permission to publish.

UQAM long/short promotions, the silent English clip and the MAT0339 books retain
their own tests, environments and review requirements. The teaching test groups
do not replace those project checks.

## Hosted Linux evidence

[The November 6 metadata snapshot](../reports/repo_development/2026-11-06/ci_baseline.json)
records exact source commits, run URLs and job/selected-step durations. Three
recent smoke runs failed global Ruff and skipped rendering. Their skipped render
durations are unavailable. Contemporary independent teaching and syllabus jobs
completed their silent previews on Ubuntu; those results belong to the recorded
commits, not to later local changes.

After publishing a reviewed branch, use its exact PR head and run metadata to
verify the current Linux checks. Preserve the test/install/render distinctions,
and report unsuccessful or unavailable jobs explicitly. No hosted workflow needs
to be dispatched merely to run the local fast group.
