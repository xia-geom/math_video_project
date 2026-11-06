# Shared teaching environment and check tools

6 November 2026. Starting revision: `032c3f9`. This batch implements the next
bounded step in the [development roadmap](../../../docs/DEVELOPMENT_ROADMAP.md):
consistent dependency selection for teaching reviews, local development and CI.

## Research and decisions

- [pip constraints](https://pip.pypa.io/en/stable/user_guide/#constraints-files)
  restrict versions without requesting installation. The teaching requirements
  request the Azure extra; the constraints file uses plain package names.
- [pip repeatable installs](https://pip.pypa.io/en/stable/topics/repeatable-installs/)
  distinguish selected pins, full transitive pins, hashes and wheel bundles. This
  change is a selected profile, not a complete lock or a cross-platform guarantee.
- [Manim 0.19 release notes](https://docs.manim.community/en/stable/changelog/0.19.0-changelog.html)
  support the established Python 3.13 baseline and continued pip installation.
  A package-manager migration is not required for this step.
- [Ruff integrations](https://docs.astral.sh/ruff/integrations/#pre-commit)
  document the matching version revision and `ruff-check` hook. The selected
  Ruff version matches the existing local review environment, rather than an
  automatic upgrade to the newest release.

The prior teaching CI already agreed on Manim 0.19.0, voiceover 0.3.7,
python-dotenv 0.21.1 and setuptools 80.9.0. Those choices are preserved. The
working environment's NumPy 2.5.4 and SciPy 1.18.1 require Python 3.12 or later,
so its rendering profile cannot serve the Python 3.11 lightweight jobs.

## Changes

[checks.txt](../../../requirements/checks.txt) pins pytest 9.1.1, Ruff 0.17.0
and PyYAML 6.0.3. [teaching.txt](../../../requirements/teaching.txt) includes
those tools and requests the rendering packages under
[teaching-constraints.txt](../../../requirements/teaching-constraints.txt).
Selected numeric/data/encoding pins include NumPy 2.5.4, SciPy 1.18.1,
pandas 3.0.6, xlrd 2.0.2 and PyAV 13.1.0.

Four teaching review workflows and root smoke rendering now use the Python 3.13
profile. Lightweight smoke, catalogue and public-audit jobs use the check profile
on Python 3.11. The Ruff hook shares that version. Dependency files participate
in filtered workflow triggers, the existing pip cache key, source snapshots and
lesson input hashes. Changing profile bytes makes prior lesson evidence stale.

Existing narration conditions, cloud credentials, write permissions and release
gates were preserved. UQAM promotion runtimes, the English clip and the book's
independent verification remain separate. The updated
[development guide](../../../docs/DEVELOPMENT.md) explains installation and the
remaining reproducibility work.

## Validation

A fresh isolated environment was created outside the working environment using
CPython 3.13.5 on macOS ARM64. It installed the teaching profile from PyPI, then
installed the project editable with `--no-deps --no-build-isolation`.
`pip check` reported no broken requirements. The resolved inventory contains
62 distributions, including the editable project. No working virtual environment
was changed. The initial sandboxed download failed to resolve packages; the
network-enabled retry completed successfully.

Python 3.11-compatible wheels and dependencies for the lightweight profile also
resolved successfully. No local Python 3.11 interpreter was available, so this
is resolution evidence, not an executed Python 3.11 test run. Linux CI execution
remains pending.

| Check | Evidence |
| --- | --- |
| Fresh-environment teaching regressions | 125 tests and 30 subtests passed: teaching layout/narration mocks, catalogue, workflow policy/syntax, coherence runner and review ledger. |
| Final fresh-environment dependency/consumer suite | 171 tests and 44 subtests passed, including the new dependency contracts, snapshot/privacy checks, catalogue/review ledger, workflow checks and curriculum/syllabus consumers. This overlaps the earlier suite; counts are not additive. |
| Profile provenance regressions | Tracked profile bytes appear in archives; each changed file changes the lesson signature; untracked inputs are rejected before reading; an incomplete declared profile blocks. |
| Dependency contracts | 18 new cases check project dependency coverage, requested extras, exact version selection, Python roles, Ruff hook parity, workflow consumers, triggers, cache and archive inclusion. |
| Syntax/lint/indexes | Six changed Python files parsed; full scoped Ruff passed; generated catalogue indexes remained current without regeneration. |
| Independent review | No actionable configuration issue found; profile semantics, project boundaries and unchanged narration gates were reviewed separately. |

The fresh-environment teaching test command was:

```sh
python -B -m pytest -p no:cacheprovider \
  tests/test_teaching_revision.py tests/test_course_catalog.py \
  tests/test_course_workflow_syntax.py tests/test_public_workflow_policy.py \
  tests/test_course_coherence_runner.py tests/test_course_review.py -q
```

The final dependency/consumer command was:

```sh
python -B -m pytest -p no:cacheprovider \
  tests/test_teaching_dependencies.py tests/test_course_source_snapshot.py \
  tests/test_private_data_guard.py tests/test_course_catalog.py \
  tests/test_course_review.py tests/test_course_workflow_syntax.py \
  tests/test_public_workflow_policy.py tests/test_course_delivery_regressions.py \
  tests/test_render_curriculum.py tests/test_syllabus_expansion.py -q
```

The existing voiceover package emits its `pkg_resources` deprecation warning.
The reviewed setuptools pin preserves compatibility; the warning is not hidden.
No repository-wide automatic lint fix was applied.

## Encoded preview and visual inspection

One actual lesson was rendered with the new environment:

```sh
python -B scripts/render_course_coherence.py --order 1 --jobs 1 \
  --output review_artifacts/repo_development/2026-11-06/teaching-profile-preview
```

Lesson `variables_et_polynomes` passed the runner's checks: H.264 video,
854×480 at 15 fps, duration 107.333333 seconds, four authored chapters and no
audio stream. Azure initialization was explicitly blocked by the silent runner.
Its input record contains all three dependency-profile hashes. No clipped-state
candidates were reported by the runner.

Six actual encoded frames at 2, 22, 60, 82, 93 and 106 seconds were inspected.
They show the opening, variable/expression work, polynomial, graph, recap and
closing without an observed clipping or missing-text defect in those samples.
This does not establish complete playback, listening, final-resolution review,
mathematical coverage of the entire lesson or institutional approval.

Native tools used: FFmpeg/ffprobe 8.0.1, TeX Live 2024 (pdfTeX 1.40.26),
dvisvgm 3.2.2; the local native inventory also reported Cairo 1.18.4 and Pango
1.57.0. The resolved package/native inventory, preview, stream data and sampled
frames remain under the ignored local
`review_artifacts/repo_development/2026-11-06/` directory.

## Remaining work

Run the changed workflows on Linux before claiming that platform is validated.
Generate and review complete transitive locks from clean tested installations;
record platform-specific native tools and fonts alongside them. The shared
profile does not yet pin every dependency, isolated build tool or system package.

Book definitions, chapter order and the proposed complex-number chapter remain
the separate editorial backlog recorded in the roadmap. This batch produced no
paid narration, Drive delivery or release. Unrelated UQAM working files and
photos were excluded from the checkpoint; generated media were not committed.
