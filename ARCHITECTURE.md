# Where things belong

The repository contains teaching videos, three UQAM promotional videos and
textbook work. Their sources stay separate; they share utilities where useful.

## Three root documents, three jobs

| File | Purpose |
|---|---|
| [README.md](README.md) | How to install the project, find lessons and run commands. |
| [AGENTS.md](AGENTS.md) | Instructions for coding agents working on the repository. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | This short map: where files belong and what stays separate. |

There is one root agent instruction file, not an entry-point file plus a second
production guide. Detailed project settings belong with the project that owns
them; this map does not repeat scripts, voice settings or dated test results.

## The folders you work in

| Work | Location |
|---|---|
| Mathematics teaching videos | `scenes/<category>/<topic>/` |
| The three UQAM promotional videos | `miscellaneous/` |
| Textbook revisions and exams | `books/`, including `books/mat0339/` |
| Shared logos, photographs and other source assets | `assets/` |

The promotional videos are siblings, not versions nested inside one another:

```text
miscellaneous/
├── uqam-baccalaureat-mathematiques-cheminements/  # Detailed programme presentation
├── bac_math_uqam_fr/                            # General mathematics promotion
└── bac_sciences_ouvertures_fr/                   # 20-second interdisciplinary clip
```

Use [the promotion index](miscellaneous/README.md) to enter the right project.
Its [catalogue](miscellaneous/uqam_promotion.json) records the three identities;
each project's own README and configuration hold its scenario and build command.

## The supporting folders

| Location | What it does |
|---|---|
| `curriculum/` | Teaching-video order, collections and delivery destinations. |
| `tools/` | Python helpers that scenes and scripts **import**. |
| `scripts/` | Commands that you **run** to render, package or audit. |
| `tests/` | Automated checks. |
| `docs/` | Technical references, including the teaching production standard. |
| `documents/` | Existing reference documents and manual/exercise snapshots. |
| `reports/` | Dated audits, findings and validation evidence. |
| `experiments/` | Work in progress that is not yet a production scene. |
| `archive/` | Retired code and historical utilities. |

These names have different jobs: `books/` is active book work, while `documents/`
holds reference material; `reports/` records what was checked, while `archive/`
keeps retired implementations. They are not additional places to maintain copies
of the same current project. Historical migration scripts under
`scripts/teaching_revision/` are records of earlier changes, not build steps to rerun.

Dependency settings are in `pyproject.toml` or a production's own requirements file.
`.env.example` documents variable names; real credentials stay outside Git.
`.github/workflows/` runs automated checks, and `.vscode/` holds editor settings.
These are supporting configuration, not content projects.

## How a video is built

```text
Scene + source assets + project settings
                  ↓
       Shared helpers in tools/
                  ↓
    Build command / Manim / Azure
                  ↓
   Encoded video and evidence in dist/
```

Teaching order and routing come from
[curriculum/programme_principal_fr.yaml](curriculum/programme_principal_fr.yaml),
not from historical folder numbers. Teaching layout, narration and the single
UQAM opening follow [docs/TEACHING_STANDARD.md](docs/TEACHING_STANDARD.md).
`tools/tts.py` owns voice configuration; `tools/teaching_voiceover.py` is the
teaching adapter, and `tools/branding.py` owns the shared opening.

Each promotion keeps its own entry point and dependency requirements. Shared
utilities must not import a particular video's scene, and sibling films must not
import each other's scene implementations. Keep source/asset provenance with the
project rather than duplicating it in this root map.

## Sources are not rendered outputs

`dist/` contains generated deliverables; `media/` contains renderer work files;
`review_artifacts/` contains temporary review evidence. They may be absent from a
fresh checkout. They are not new source folders and generated media should not be
added to Git. The local render history is under `dist/_render_archive/`, separate
from the retired source code in `archive/`. See README for archive commands.

A source change, a successful render and a Drive replacement are different events.
Check the actual output's provenance and requested destination. Do not treat a
silent preview as a narrated master or a test pass as publication approval.

Keep existing project paths and scene class names stable. This simplification
consolidates documentation; it does not relocate videos, books, assets or outputs.
Dated reports may retain earlier filenames because they describe earlier commits.
