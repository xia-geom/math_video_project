# Repository development roadmap

Updated 6 November 2026. The next development cycle should make the existing
course tools easier to run, make review evidence easier to assess, and complete
targeted teaching improvements. The catalogue, separate production projects,
render archive and review ledger already provide the main structure.

This roadmap is a queue of engineering work. Lesson identity and order remain
in the [unified catalogue](../curriculum/README.md); production evidence remains
in the [dated audit records](../reports/AUDIT_INDEX.md). Effort below is relative:
small means a focused change, medium means several related changes, and large
means a staged migration or review campaign.

## First implementation

The initial changes address three concrete maintenance problems:

- Catalogue checks gain `--check-indexes`, which compares the generated indexes
  without rewriting them. Both index-checking workflows use it, and catalogue
  generation tests use temporary fixtures. `--write-indexes` remains the explicit
  regeneration command.
- The coherence runner defaults to two workers and accepts one or two, matching
  the [review concurrency contract](COURSE_REVIEW.md). This limits one invocation;
  the coordinator still keeps the total across separate queues at two.
- Active navigation points to the October 15 coherence and narration records.
  Architecture guidance reflects the existing manual-main narration gates.
  Historical reports keep their original claims and dates.

These changes do not establish new audiovisual approval. The latest recorded
43-lesson coherence rollout is silent; subsequent narration-source changes mean
older input hashes must be reconciled before reusing its evidence.
The [initial implementation checks](../reports/repo_development/2026-11-05/README.md)
record the validation performed for this batch.

## Review fixes

The subsequent review of all eight unpublished commits identified four concrete
issues. The follow-up implementation restricts source snapshots to reviewed
tracked inputs, verifies source fingerprints before clearing detector matches,
requires Boolean acceptance to close a finding, and separates book-only
verification from video-catalogue integration. The
[review-fix record](../reports/repo_development/2026-11-05/review_fixes.md)
records the regression checks and remaining limits.

Online guidance supports keeping these changes focused:
[Diátaxis recommends small responsive improvements](https://diataxis.fr/how-to-use-diataxis/),
and [Gitleaks documents the scope of its allowlists](https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md#configuration).
This implementation uses source-byte verification for fingerprint exceptions,
so a filename or directory match alone cannot clear a detector finding.

## Shared teaching environment

This implementation centralizes the teaching dependency profile and check
tools. [Development setup](DEVELOPMENT.md) distinguishes the Python 3.13 rendering
profile from lightweight checks that also support Python 3.11. Teaching workflows,
root smoke checks and pre-commit consume matching versions; promotion projects
retain their own dependency authorities. Profile changes participate in source
snapshots and lesson input hashes.

The working environment cannot be copied blindly into every CI job: its NumPy
and SciPy versions require Python 3.12 or later. The selected profile therefore
keeps rendering on Python 3.13. This step constrains selected dependencies;
complete transitive locks and Linux execution remain separate validation work.
The [6 November record](../reports/repo_development/2026-11-06/README.md) records
the clean installation, checks and preview actually performed.

## Recommended sequence

| Order | Work package | Effort | Completion condition |
| --- | --- | --- | --- |
| 1 | Complete environment reproducibility | Medium | Build on the shared profile; verify Linux CI, then review platform-specific transitive locks and native-tool inventories against a representative silent preview. |
| 2 | Test groups and complete workflow policy coverage | Medium | Fast checks have a documented scope; every active workflow is classified; synthetic policy violations fail the validator. |
| 3 | Current production evidence from the existing ledger | Medium | One generated view distinguishes fresh, stale, unavailable and unreviewed evidence for catalogue identities. |
| 4 | Efficient rendering and scoped lint repairs | Large | Affected-lesson selection is tested against shared dependencies, with conservative fallback and full-course review retained. |
| 5 | Listening decisions and targeted audiovisual completion | Medium plus review time | Decisions identify exact audio/video hashes; replacement media invalidates dependent checks; selected lessons receive complete playback and listening records. |
| 6 | Focused teaching development and utility cleanup | Medium per change | A selected pedagogical gap is independently checked; historical patch scripts cannot alter sources merely by being imported. |

### Reproducible environments

The root [pyproject.toml](../pyproject.toml) retains broad package compatibility.
The [teaching profile](../requirements/teaching.txt) supplies the selected runtime
constraints, and [check-tool pins](../requirements/checks.txt) align teaching CI,
root smoke/public-audit checks and the Ruff hook. The separate dependency
authorities of the long UQAM film and short promotions remain unchanged.

Test resolution in a new disposable environment before replacing any working
environment. Record Python, rendering libraries, FFmpeg, LaTeX and font versions.
Use a constrained installation first; consider `uv` only if it simplifies the
existing workflow. Its documentation describes both
[requirements locking](https://docs.astral.sh/uv/pip/compile/) and
[locked CI installation](https://docs.astral.sh/uv/guides/integration/github/).
A Python lock alone does not fix native-library or font differences.
As [pip documents](https://pip.pypa.io/en/stable/topics/repeatable-installs/), a
fully pinned transitive environment and hash verification are stronger steps
than selected constraints. Generate candidate locks from clean tested installs,
not from an environment containing unrelated tools. Verify each supported
platform before promoting its lock.

### Test groups and workflow coverage

The current workflow-policy test names five workflows, while the repository has
15 active workflow files at this inspection. Classify all active workflows by
their intended privileges and triggers, including the existing publishing and
maintenance workflows. Validate permissions, checkout credentials, pinned
Actions and cloud-secret gates at the relevant workflow, job and step scopes.
Use synthetic unsafe fixtures to show that new workflows cannot escape coverage.
Follow [GitHub's least-privilege guidance](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions).

Document fast contract tests, construction tests, real renders and narration as
separate groups. Extend existing tests instead of adding another runner before
the groups are understood. The [pytest integration guide](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
provides layout and import guidance; changing the repo's import mode requires a
compatibility check rather than a mechanical configuration edit.

### Current evidence

Extend [scripts/course_review.py](../scripts/course_review.py) and its generated
views to incorporate the later coherence and narration records. Use the existing
catalogue IDs and dependency hashes. Keep source mathematics, technical validity,
encoded samples, complete motion, listening, timing and final-size review
separate. Missing local artifacts should show as unavailable, and changed input
or runtime fingerprints should make earlier passes stale.

Acceptance includes fixtures where a shared helper changes, an artifact is
missing, and a reviewed movie is replaced. Historical conclusions must remain
recoverable, and a successful reconciliation must not imply publication approval.
The [October 15 coherence report](../reports/course_coherence/2026-10-15/README.md)
and [offline narration record](../reports/narration_quality/2026-10-15/offline_revision.json)
provide the first integration targets.

### CI cost and lint backlog

The current smoke workflow selects all 43 course scenes on every pull request;
its render jobs depend on global lint. Measure job duration and failures before
changing this behavior. Repair the lint backlog in coherent modules, reviewing
even automated fixes. [Ruff distinguishes safe and unsafe fixes](https://docs.astral.sh/ruff/linter/),
but any changed scene still needs checks appropriate to its behavior.

Then build affected-lesson selection from the catalogue and actual shared inputs.
Test documentation-only edits, one-scene edits, catalogue changes and shared
layout/voice changes. Unknown dependencies should select the broader scope.
Preserve the existing global lint check and full-course manual audit; report
which render scopes were selected or skipped. Review the existing policy tests
alongside the design rather than weakening them to accommodate a shortcut.

For visual regressions, use a few representative layouts and selected animation
states before expanding coverage. [Manim's testing guide](https://docs.manim.community/en/stable/contributing/testing.html)
distinguishes behavior tests, frame comparisons and video-output tests. Treat
this as a testing pattern: its current internal helpers may differ from the
repo's established runtime. Keep generated review media outside source Git and
inspect differences before accepting new reference evidence.

### Listening and audiovisual completion

The offline narration record contains 86 screening flags in 64 utterances across
31 lessons. These are review candidates, not 86 confirmed defects. Add a local
decision workflow around the existing review CSV, with the clip hash, timestamp,
reviewer, reason and disposition. Preserve intentional reflection pauses.

Start with a small representative batch and the already prepared pronunciation
samples. Paid narration requires explicit manual selection on reviewed `main`
under the existing policy; preserve `tools/tts.py` and all voice profiles.
New audio must trigger the appropriate timing, subtitle and playback checks.
Complete listening and full-motion review require actual review records, not a
status inferred from duration or silence detection.

### Teaching development and historical utilities

The user's book feedback remains a separate editorial backlog. A source check
of the active MAT0339 edition (10 October 2026) found these items still open:

- Definition 2.1 does not specify real coefficients or define a monomial;
  Definition 4.2 does not explicitly specify real quadratic coefficients.
- Definition 6.1 uses real exponents without explaining their extension beyond
  the integer and fractional powers introduced earlier.
- Proposition 7.4 and Definition 7.5 leave the integer-valued factorial quotients
  implicit. Integer bounds on the arrangement parameters are already present.
- The dot product uses cosine in chapter 9, before the unit circle in chapter 14.
- Chapter 17 still covers circular motion and sinusoidal models; replacing it
  with complex numbers remains a proposal, not an implemented curriculum change.

Check these against the [active manual sources](../books/mat0339/sources/manual/chapters/)
and preserve manual–workbook section identities when preparing corrections.
The engineering checks below do not resolve this pedagogical feedback. Any
reordering or replacement requires a documented editorial decision and matching
workbook changes, followed by compilation and inspection of the affected pages.

Use the existing [misconception priorities](../curriculum/misconceptions_prioritaires_fr.md)
to select a bounded next lesson improvement: amplitude versus maximum, period
and phase shift, or radians/degrees. New capsules remain editorial candidates.
For each selected change, define one learning objective, verify examples and
counterexamples, preserve textbook links, render a low-quality preview and have
a different reviewer inspect it. Do not allocate new course numbers until the
lesson scope is selected.

Separately inventory historical `patch_*`, `fix_*` and migration scripts under
`tools/`. Some execute source rewrites at import time. Check active references
and original assumptions before adding execution guards or moving a proven
historical-only script to the existing migration/archive area. Test imports in
a synthetic temporary tree; importing supported utilities must leave sources
unchanged. Preserve historical paths in audit records.

## Fast local checks

Use a Python environment with PyYAML and pytest, such as the established review
environment when available. These commands validate a focused foundation; they
do not perform a render, synthesize speech, or copy outputs to Drive.

```sh
python tools/course_catalog.py check
python tools/course_catalog.py --check-indexes
python scripts/render_syllabus_expansion.py --check-only
python -m pytest tests/test_course_catalog.py tests/test_course_workflow_syntax.py tests/test_public_workflow_policy.py tests/test_course_coherence_runner.py -q
```

After intentionally editing the catalogue or migration mapping, regenerate with
`python tools/course_catalog.py --write-indexes`, review the diff, and run the
checks again. Select additional tests for the files actually changed.

## Working in parallel

Keep implementation work split by ownership: one worker for environment/CI,
one for evidence tooling, and one for selected educational content. A coordinator
owns shared helpers, integration and Git operations. Assign another worker to
review each change. Run no more than two Manim processes across the whole team.

Organize documentation by reader task: onboarding in the root README, production
commands beside their project, contracts in reference documentation, and dated
results in reports. This applies the [Diátaxis documentation framework](https://diataxis.fr/)
without moving the established source trees. Maintain one lesson catalogue,
preserve the parallel UQAM projects and English clip, and stage only inspected
task files for public-repository maintenance.
