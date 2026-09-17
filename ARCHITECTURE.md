# Repository architecture — Math Video Project

**Inspected baseline:** `219a4d0decc6c939521073e4355f05f4a55b5bc6` on `main`, 17 September 2026.  
**Scope of this document:** the existing repository plus the new, third UQAM promotional clip. This is a map of actual locations, not a proposal to relocate the entire repository. Operational test results belong in dated reports, not in this architecture document.

## 1. Start here

| Question | Authoritative entry point |
|---|---|
| How do I install and render a standard mathematics lesson? | [README.md](README.md), [pyproject.toml](pyproject.toml), [scripts/render.sh](scripts/render.sh) |
| What should a coding agent preserve? | [AGENTS.md](AGENTS.md), then the detailed [AGENT.md](AGENT.md) production guide |
| In which order do the numbered lessons belong? | [curriculum/programme_principal_fr.yaml](curriculum/programme_principal_fr.yaml) |
| Where are the three UQAM promotion/orientation videos? | [miscellaneous/README.md](miscellaneous/README.md) and [miscellaneous/uqam_promotion.json](miscellaneous/uqam_promotion.json) |
| Where is shared Azure voice configuration? | [tools/tts.py](tools/tts.py) |
| Where are historical audit and consolidation records? | [reports/AUDIT_INDEX.md](reports/AUDIT_INDEX.md) |
| Where is the 20-second interdisciplinary clip? | [miscellaneous/bac_sciences_ouvertures_fr/README.md](miscellaneous/bac_sciences_ouvertures_fr/README.md) |

The root README is the onboarding guide. This file explains boundaries and ownership. Project READMEs explain a single production. Manifests hold machine-readable configuration; audit reports record dated evidence. These roles should not be collapsed into an ever-growing root README.

## 2. Top-level map

```text
math_video_project/
├── README.md                      # Installation, lessons, shared rendering
├── ARCHITECTURE.md                # This map and architectural invariants
├── AGENTS.md                      # Short discoverable agent entry point
├── AGENT.md                       # Existing detailed production guide
├── pyproject.toml                 # Main Python package/environment definition
├── .env.example                   # Names/examples only, never actual credentials
├── .github/workflows/             # Active GitHub Actions workflows
├── .vscode/                       # Editor launch configuration
├── assets/                        # Shared branding and sourced media
├── curriculum/                    # Lesson ordering, grouping and routing manifests
├── scenes/                        # Main educational Manim scenes by category
├── miscellaneous/                 # Existing UQAM promotion/orientation collection
│   ├── README.md
│   ├── uqam_promotion.json
│   ├── uqam-baccalaureat-mathematiques-cheminements/
│   ├── bac_math_uqam_fr/
│   └── bac_sciences_ouvertures_fr/
├── tools/                         # Shared imported utilities
├── scripts/                       # Command-line orchestration and audits
├── tests/                         # Cross-project and project-specific regressions
├── books/                         # Book projects, including MAT0339 revision work
├── documents/                     # Existing reference/manual/exercise documents
├── experiments/                   # Exploratory sketches and work in progress
├── archive/                      # Superseded code and historical utilities
└── reports/                       # Dated findings, implementation and validation evidence
```

`dist/`, `media/`, `review_artifacts/` and virtual environments are generated working locations, not additional source collections. Their absence from a fresh checkout is normal. Historical tracked binaries already in the repository are not a reason to commit new renders, nor authorization to delete them.

The root also contains dated inventory/status reports such as `PROJECT_STATUS_REPORT.md`, `SCENE_FILE_CONDITION_AUDIT.md` and `SCENE_INVENTORY_REPORT.md`. Treat their counts as historical snapshots. Consult actual files and manifests when current counts matter.

## 3. Content domains

### 3.1 Main mathematics programme

Production lesson sources normally follow:

```text
scenes/<category_slug>/<topic_slug>/<topic_slug>_scene.py
```

Categories include algebra/polynomials, functions/graphs, logarithms, probability, vectors, matrices, geometry, notation and trigonometry. Visual identity and common-error scenes also have dedicated categories. The curriculum manifest, not lexical folder order, determines the educational sequence. Historical folder numbers do not always equal their current position in the assembled programme.

Scene classes are public render interfaces. Preserve them when reorganizing supporting files. A curriculum lesson belongs in the curriculum manifest; a recruitment video does not.

### 3.2 Three parallel UQAM videos

| Identity | Canonical directory | Production entry point | Intended scope |
|---|---|---|---|
| Long programme/pathways presentation | `miscellaneous/uqam-baccalaureat-mathematiques-cheminements/` | `render_v4.py`, `project-manifest.toml` | Detailed programme explanation; its own versions, assets and tests |
| General mathematics recruitment | `miscellaneous/bac_math_uqam_fr/` | `build_release.py`; scene `BacMathUQAMFR` | Existing general short promotion, with its own narration and release safeguards |
| Interdisciplinary openings | `miscellaneous/bac_sciences_ouvertures_fr/` | `build.py`; scene `BacSciencesOuverturesFR` | Approximately 20 seconds: major + complementary certificate + bachelor by accumulation |

The first two directories already live in `miscellaneous/`. The third is deliberately their sibling. Do not create copies under `scenes/promotion_fr/`, and do not turn one film into a subdirectory or alternate version of another. Their messages, timing and output identities differ.

The long film retains its hyphenated historical directory. Renaming it merely to conform to newer snake-case names would break existing references without helping the requested clip. A future migration must inventory and update imports, scripts, workflows, manifests and documentation together; it is outside this change.

The collection registry holds identity and discovery metadata. It is not another source of narration or measured runtime. Exact content belongs to each project's own manifest; actual duration belongs to the rendered artifact's manifest.

### 3.3 Books and reference documents

`books/` and `documents/` both already exist. MAT0339 revision work belongs under `books/mat0339/`; existing manual and exercise-document snapshots also remain under `documents/mat0339/`. They are not promotion assets. Do not copy them into the video collection or merge these two trees without a separate source-authority audit.

### 3.4 Experiments and archive

Exploratory material belongs in `experiments/`, including the existing `sketches/` and `wip/` areas. `archive/` preserves superseded implementations. Neither is the default import location for a new production scene. Promotion into production should create an explicit canonical entry point and tests rather than relying on an undocumented experimental copy.

## 4. Shared services and dependency direction

```text
Content / source document
          |
          v
Project manifest and narration -----> Scene implementation
          |                                  |
          |                                  v
          |                        tools/tts.py -> Azure adapter
          |                                  |
          v                                  v
Project build command -------------> Manim rendering
          |
          v
FFmpeg packaging / subtitles / ffprobe validation
          |
          v
Isolated dist folder + evidence manifest + review frames
```

`tools/` is for imported reusable behaviour. `scripts/` is for execution and orchestration. A project can own a specialized builder without creating another global framework. Shared utilities must not import one project's scene module. Parallel projects should not import each other's scene implementations.

The new clip imports the existing TTS service helpers but no code from either older film. It adds no project-wide voice, rate, font or timing override. Its small `project.py` is local because its four-beat contract is specific to this clip.

### Azure boundary

`tools/tts.py` owns voice aliases, locale/prosody helpers, pronunciation utilities, output format and credential-environment validation. Project code selects a profile through those helpers; it must not duplicate the voice table or embed a key.

The curriculum's default voice and a promotion project's selected voice are different scopes. The new clip follows the existing promotion selector `MAI-Voice-2` and rate `+2%`; the shared resolver provides its concrete voice ID. Its supported override order is project-specific voice, existing promotion voice, general Manim voice, then the declared project default.

The shared helper accepts `SPEECH_KEY`/`SPEECH_REGION` and the legacy adapter names, detects conflicting aliases and enforces the repository's MAI region configuration. Missing credentials are a blocked narrated build, never authorization to substitute another cloud provider or a different voice.

### Rendering boundary

The generic `scripts/render.sh` renders a Manim class and copies outputs using the topic folder name. It expects the main `.venv` and has existing output/Drive-routing behaviour. Specialized production builders provide project-specific validation, provenance and isolation.

The new builder invokes the same Manim/Azure stack directly in the selected Python environment. This is intentional: it needs a fresh temporary render directory, an explicit silent/narrated distinction and no implicit Drive copy. It does not modify the generic render script or the older release builders.

## 5. New clip: file-by-file responsibility

```text
miscellaneous/bac_sciences_ouvertures_fr/
├── README.md                            # Brief, storyboard, commands and limits
├── project.json                         # Copy, captions, timing, profile and source identity
├── project.py                           # Contract validation and SRT serialization
├── bac_sciences_ouvertures_fr_scene.py   # Four Manim acts and real narration-clock timeline
├── build.py                             # Fresh render, package, validate and record provenance
├── requirements.txt                    # Isolated short-promotion dependencies
└── sources/
    └── accueil_septembre_2026.md         # Page-specific source reading and claim map
```

Related repository files:

- `tests/test_uqam_ouvertures.py`: source, timing, subtitle, media-stream and parallel-project contracts.
- `.github/workflows/uqam-ouvertures.yml`: narrow validation and review-artifact production.
- `reports/uqam_ouvertures/2026-09-17/`: dated implementation and verification record.

The JSON file is the only editable narration/subtitle source. The scene lays it out; the builder does not maintain a second script. Caption text must equal narration text after whitespace normalization. Source-page references accompany each beat. The uploaded PDF's hash and the fact that its original bytes are not stored in Git are explicit.

## 6. Build and artifact lifecycle

1. Validate the project contract and, for Azure, validate credential configuration.
2. Create a new timestamped output directory. Refuse an existing directory.
3. Hash source files and render in a fresh temporary media directory.
4. In silent mode, use the declared 20-second storyboard and mark the image as an unvoiced preview.
5. In Azure mode, synchronize each act to its actual audio duration. Keep a comfortable visual hold; never crop narration to meet the target.
6. Encode a standard MP4; generate SRT from the actual scene timeline and a separate burned-caption MP4.
7. Check aspect ratio, duration, audio-stream presence/absence, subtitle timing and source freshness. Extract actual encoded frames.
8. Save source/output hashes, commit, effective voice/font/rate, software versions and pending human-review gates.

Typical generated output:

```text
dist/bac_sciences_ouvertures_fr/<timestamp>-<mode>/
├── bac_sciences_ouvertures_fr_<mode-label>.mp4
├── bac_sciences_ouvertures_fr_<mode-label>_subtitled.mp4
├── bac_sciences_ouvertures_fr_<mode-label>.srt
├── ..._narration.wav                     # Azure only
├── timeline.json
├── manifest.json
├── ffprobe.json
├── render.log
└── frames/                              # One encoded checkpoint per act
```

A successful review build is not an institutional release. `release_ready` remains false. Programme wording, full listening and visual approval are distinct tasks. A silent preview must not be renamed as an Azure master. Generated media belong in artifacts or controlled delivery storage, not as new Git source blobs.

## 7. Environments and reproducibility

The repository already has more than one runtime. Keep those boundaries explicit:

| Workload | Dependency authority |
|---|---|
| Standard lesson environment | Root `pyproject.toml` |
| Existing long UQAM film | Its `requirements.lock` and local project documentation |
| Existing short promotion | Its established Manim/voiceover environment and UQAM revision workflow |
| New 20-second clip | Its focused `requirements.txt`, using the existing short-film Manim/voiceover versions |

Do not apply the long-film lock to every project or upgrade every project to a new Manim release as part of a wording change. The new requirements file pins direct compatibility-sensitive dependencies, not every transitive dependency. Each build records installed versions; GitHub additionally saves the full environment. This is an auditable runtime record, not a claim of fully hermetic builds.

Fonts are a rendering dependency. The existing shared Roboto asset is reused where available, not copied into a new folder. The actual font is recorded; preview-only fallback does not silently become the final brand font. No font distribution is added to delivery artifacts.

## 8. CI and audit boundaries

Existing active workflows inspected at the baseline are `smoke.yml`, `uqam-revision.yml` and `audit-integration.yml`. Their purposes and scopes are not interchangeable. In particular, the existing UQAM revision workflow is manual-only after the audit consolidation. This change does not re-enable it or the archived workflows.

The additional `uqam-ouvertures.yml` is narrowly path-filtered to the new clip, its test, its collection registry and itself. It runs on relevant pull requests and supports manual dispatch. It does not render the two older films or all educational lessons.

Same-repository PRs may use configured Speech secrets for this requested clip; external PRs cannot take that branch. Credential availability is recorded without printing secret values. Missing credentials leave `narrated_status.json` blocked while preserving useful silent-preview evidence. Workflow artifacts expire after the configured retention period; a Git commit containing source is not a permanent archive of those videos.

A job labelled successful must be read with its artifact manifest: automated preview checks can pass while narration is blocked or human review is pending. Do not convert those distinct states into a blanket assertion that all videos are validated.

`reports/AUDIT_INDEX.md`, `reports/audit_consolidation/`, `reports/uqam_video_revision/` and `reports/video_audits/` remain historical evidence. New work goes in a new dated report. It does not overwrite an older report to make an old finding appear resolved.

## 9. Asset and editorial provenance

Shared assets live in `assets/`, including existing branding and UQAM promotional material. The long film also has project-local assets with its own provenance. Preserve those inventories; an asset being present in Git does not establish publication permission.

For the 20-second clip, the supplied September 2026 slides are the editorial source. Pages 21–23 support major/certificate/bachelor-by-accumulation and the four displayed disciplines. The two-year framing is separately attributed to the user's production brief. Page 24's master's-level openings are not used to imply automatic graduate admission. The clip does not reproduce the PDF's portraits, diploma facsimiles or logos.

Do not silently expand the four fields, replace “économique” with an unverified programme name, invent certificate codes, or promise employment outcomes. Changes to an academic claim require an updated source map as well as copy edits.

## 10. Rules for future changes

For a new lesson, create a canonical scene and register it in the correct curriculum collection. For a fourth UQAM video, create another sibling project, add one catalogue entry and give it a dedicated output identity. For a shared helper, establish more than one real consumer before moving project-local code into `tools/`.

Any path migration must update all import, workflow, CLI, manifest and documentation references, and must preserve existing public scene classes or provide tested compatibility. Do not perform a mass move merely to make the tree look more uniform.

Do not combine rendering work with unrelated textbook edits, research exports, site deployment or audit-branch deletion. Preserve the audit consolidation on `main`; create a focused branch, review the diff and run relevant checks. Never force-push, fabricate test results, infer asset permissions or publish a video as a side effect of a source-code update.

When changing this architecture, update both the relevant project README and the collection registry when their contracts change. Keep exact build commands near the project that owns them, and keep measured validation results in dated reports.
