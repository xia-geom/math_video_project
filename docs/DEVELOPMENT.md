# Development environments and validation

Use the teaching profile for the numbered mathematics lessons. Use the lightweight
profile for catalogue, provenance and workflow checks that do not import Manim.
The [roadmap](DEVELOPMENT_ROADMAP.md) describes the next work; dated reports record
the environments and artifacts actually checked.

## Choose an environment

| Work | Python | Dependency entry point |
| --- | --- | --- |
| Catalogue, workflow and public-audit checks | 3.11 or 3.13 | [checks.txt](../requirements/checks.txt) |
| Numbered teaching scenes and review tools | 3.13 | [teaching.txt](../requirements/teaching.txt) |
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
.venv-checks/bin/python -m pip install -r requirements/checks.txt
.venv-checks/bin/python -m pip check
.venv-checks/bin/python tools/course_catalog.py --check-indexes
.venv-checks/bin/python -m pytest tests/test_teaching_dependencies.py \
  tests/test_course_catalog.py tests/test_course_source_snapshot.py \
  tests/test_public_workflow_policy.py tests/test_course_workflow_syntax.py -q
```

```sh
# Teaching runtime, including the same check tools.
python3.13 -m venv .venv-teaching
.venv-teaching/bin/python -m pip install -r requirements/teaching.txt
.venv-teaching/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv-teaching/bin/python -m pip check
```

The first install supplies the constrained setuptools version. The editable
install then uses that environment deliberately, without resolving dependencies
again or selecting a different isolated build backend. Additional optional
development extras can use both constraint files:

```sh
.venv-teaching/bin/python -m pip install \
  -c requirements/teaching-constraints.txt -c requirements/checks.txt \
  --no-build-isolation -e '.[dev]'
```

The optional mypy extra is outside the reviewed check-tool pins. Run the tests
appropriate to any additional packages installed.

## Dependency responsibilities

[teaching.txt](../requirements/teaching.txt) requests packages and the Azure extra;
[teaching-constraints.txt](../requirements/teaching-constraints.txt) limits runtime
versions. A constraint does not itself install a package, and extras belong in
the requested requirements, as documented by [pip](https://pip.pypa.io/en/stable/user_guide/#constraints-files).
[checks.txt](../requirements/checks.txt) is the shared version authority for
pytest, Ruff and PyYAML. The Ruff pre-commit revision must match that file; the
dependency tests check this, using the supported `ruff-check` hook.

Teaching CI and root smoke jobs consume these files. Filtered teaching workflows
include dependency changes in their triggers; their source evidence includes the
profiles. Lesson input hashes also include the three files, so changing them
invalidates prior input evidence. Promotion projects retain their own dependency
versions and validation procedures.

These files pin selected packages, not every transitive dependency or build
tool. A complete lock, artifact hashes and platform-specific wheel bundles are
later steps described in [pip's repeatable-install guidance](https://pip.pypa.io/en/stable/topics/repeatable-installs/).
Keep the resolved package inventory with each review attempt. A Python inventory
does not capture native libraries, installed fonts or TeX packages.

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
