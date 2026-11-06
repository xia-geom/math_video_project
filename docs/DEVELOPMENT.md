# Development environments and validation

Use the teaching profile for the numbered mathematics lessons. Use the lightweight
profile for catalogue, provenance and workflow checks that do not import Manim.
The [roadmap](DEVELOPMENT_ROADMAP.md) describes the next work; dated reports record
the environments and artifacts actually checked.

## Choose an environment

| Work | Python | Dependency entry point |
| --- | --- | --- |
| Catalogue, workflow and public-audit checks | 3.11 or 3.13 | [Hashed checks lock](../requirements/locks/checks-py311.txt) |
| Numbered teaching scenes and review tools | 3.13 | [Platform-specific runtime and build locks](../requirements/README.md) |
| UQAM promotion films | Their project documentation | [Collection boundaries](../miscellaneous/README.md) |
| Silent English product clip | Its project documentation | [Clip README](../miscellaneous/conversation_archive_intro_en/README.md) |
| MAT0339 book verification | 3.11 or later, standard library | [Book README](../books/mat0339/README.md) |

The rendering profile preserves Manim 0.19.0, voiceover 0.3.7, python-dotenv 0.21.1
and setuptools 80.9.0. Its numeric pins were selected from the working Python 3.13
review environment. Some require Python 3.12 or later, so this profile is not the
Python 3.11 check environment. Manim's [0.19 release notes](https://docs.manim.community/en/stable/changelog/0.19.0-changelog.html)
document support for Python 3.13 and continued support for pip installation.

Use a new, separately named virtual environment when testing a dependency change.
The commands below run from the repository root.

```sh
# Fast checks, with no rendering or cloud SDK installation.
python3.11 -m venv .venv-checks
.venv-checks/bin/python -m pip install --require-hashes --only-binary=:all: \
  -r requirements/locks/checks-py311.txt
.venv-checks/bin/python -m pip check
.venv-checks/bin/python tools/course_catalog.py --check-indexes
.venv-checks/bin/python -m pytest tests/test_teaching_dependencies.py \
  tests/test_course_catalog.py tests/test_course_source_snapshot.py \
  tests/test_public_workflow_policy.py tests/test_course_workflow_syntax.py -q
```

For teaching, follow the [native prerequisites and hashed installation](../requirements/README.md#install)
for macOS arm64 or Linux x86_64. Install the build-tool lock first, put that
environment's executables on `PATH`, then install the matching runtime lock with
hash checking and build isolation disabled. The editable project installation
does not resolve a second dependency set. Optional extras such as mypy are
outside the reviewed locks and require a separate environment/validation.

## Dependency responsibilities

[teaching.txt](../requirements/teaching.txt) requests packages and the Azure extra;
[teaching-constraints.txt](../requirements/teaching-constraints.txt) limits runtime
versions. A constraint does not itself install a package, and extras belong in
the requested requirements, as documented by [pip](https://pip.pypa.io/en/stable/user_guide/#constraints-files).
[checks.txt](../requirements/checks.txt) is the shared version authority for
pytest, Ruff and PyYAML. The Ruff pre-commit revision must match that file; the
dependency tests check this, using the supported `ruff-check` hook.

Teaching CI and root smoke jobs consume the generated hashed locks. Filtered teaching workflows
include dependency changes in their triggers; their source evidence includes the
profiles. Lesson input hashes include the four request/constraint files and all
four generated locks, so changing them
invalidates prior input evidence. Promotion projects retain their own dependency
versions and validation procedures.

The locks include transitive distributions and published artifact hashes. The
[lock guide](../requirements/README.md#update-and-verify-a-lock) explains native
wheel-bundle verification and the limits of metadata projected to another target.
This follows [pip's repeatable-install guidance](https://pip.pypa.io/en/stable/topics/repeatable-installs/).
Keep the package, native-tool/library and font inventory with each review attempt;
matching package names alone do not establish identical native output.

## Native tools and validation

Rendering requires Cairo/Pango, a suitable LaTeX installation and `dvisvgm`.
The repository's inspection/packaging tools also call FFmpeg and `ffprobe`;
retain them even though Manim 0.19 uses PyAV for encoding. Record these versions
and the fonts used alongside the Python inventory.

Before promoting a changed profile:

1. Install it in a fresh environment and run `python -m pip check`.
2. Run the dependency, catalogue, source-snapshot and workflow-policy tests.
3. Run the affected teaching tests, then one representative silent 480p preview.
4. Inspect the encoded streams and sampled frames; record the actual scope.
5. Review the requirements, workflow and evidence diffs before committing.

Use the explicit silent review runners in [COURSE_REVIEW.md](COURSE_REVIEW.md).
Preserve existing voices, narration gates and output identities. Test success,
a silent preview, complete playback, listening and publication approval are
different checks. Dependency maintenance does not provide the latter approvals.

Ruff hooks retain their existing fix behavior, but a version change is not a
request to apply fixes across the repository. Review any source changes produced
by a hook. Existing lint failures remain visible until addressed in a separate,
scoped change.
