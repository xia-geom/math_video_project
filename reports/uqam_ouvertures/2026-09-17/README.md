# UQAM — interdisciplinary openings: implementation and verification

**Date:** 17 September 2026.  
**Repository:** `xia-geom/math_video_project`.  
**Pull request:** [#4](https://github.com/xia-geom/math_video_project/pull/4).  
**Reviewed implementation commit:** `5feb55ad1a2cd8d5d23b4beeacdbb94696d481d9`.  
**Baseline:** `219a4d0decc6c939521073e4355f05f4a55b5bc6`.

## Delivered scope

The third UQAM film lives in `miscellaneous/bac_sciences_ouvertures_fr/`, beside the existing long presentation and general recruitment clip. Neither older production was moved, copied or edited. Shared `tools/tts.py`, root dependencies, existing workflows, curriculum, books and historical audits remain unchanged.

The addition includes the French script, four-act Manim scene, Azure integration through the existing shared helpers, isolated build command, subtitle generation, provenance and media checks, 16 regression tests, a dedicated GitHub workflow, a three-video registry, collection README, a discoverable `AGENTS.md` entry point and the root `ARCHITECTURE.md`.

The architecture document maps actual repository locations, project responsibilities, dependency direction, render and artifact lifecycle, Azure configuration, runtime boundaries, CI, source/asset provenance and future migration rules. It does not claim that historical repository-wide issues have all been repaired.

## Editorial basis

The source is the user-supplied `Accueil Nouveaux-2026-Septembre.pdf`, physical PDF pages 21–23. The original file's SHA-256 and a page-specific claim map are recorded under the new project's `sources/` directory. The original PDF is not stored in Git.

The narrative is **a major in mathematics or statistics, then a complementary certificate, then a bachelor in sciences by accumulation**. “Two years” is attributed to the user's full-time-pathway brief, not presented as an unconditional duration guarantee. The film displays a programme-conditions qualifier. It does not promise a complete bachelor in two years, automatic graduate admission or an employment outcome.

The four fields follow the supplied slide: communication, finance, économique and informatique. No institutional portraits, photos, diploma facsimiles or official logo were copied into the clip. Music was not added.

## Verification evidence

The reviewed [GitHub run 35282186106](https://github.com/xia-geom/math_video_project/actions/runs/35282186106) completed successfully. Its artifact is [10522489896](https://github.com/xia-geom/math_video_project/actions/runs/35282186106/artifacts/10522489896), named `uqam-ouvertures-review-35282186106`.

| Check | Observed result |
|---|---|
| Dependency installation and `pip check` | Passed |
| Python compilation for the new project | Passed |
| All configured repository Ruff rules, applied to the new project and its test | Passed; no narrowed rule subset in the reviewed run |
| Pytest in the actual repository | 16 passed, zero failures/errors/skips |
| Real Manim render | Passed, not a mocked renderer |
| Encoded silent review | 1920 × 1080, 60 frames/second, H.264, 19.95 seconds |
| Audio in the silent review | No audio stream, as required |
| Caption files | Clean MP4, separately burned-caption MP4, and matching SRT produced |
| Timing, aspect, stream, layout and source-freshness contracts | Passed |
| Artifact integrity after retrieval | MP4 and SRT SHA-256 values checked against the build manifest |
| Visual inspection | Four encoded 1080p checkpoints inspected; labels, cards, conditions line and subtitles remain separated |
| Full Azure narration and listening | Not performed; blocked as detailed below |
| Institutional approval | Not obtained or inferred |

The silent review has an explicit visible watermark. Its 19.95-second duration is the encoded measurement; the editorial storyboard totals 20 seconds. No output is described as an approved narrated master.

Runtime recorded by the build: Manim Community 0.19.0, manim-voiceover 0.3.7 and Azure Speech SDK 1.51.2. The scene used the repository's Roboto font. No font files are included in the review artifact.

The first run passed its 15 initial tests and rendered a 480p preview, but a strict aspect-ratio check incorrectly rejected Manim's pixel-rounded 854 × 480 format. The check was corrected to allow only one-pixel rounding, and a regression was added. A subsequent run passed all 16 tests and produced a 19.933333-second 480p review. The reviewed final implementation additionally enforces the full lint rules and builds the preview at 1080p.

## Azure blocker: exact observed state

The workflow requested Azure on a trusted same-repository PR. Its `narrated_status.json` reported:

```json
{
  "status": "blocked",
  "reason": "Configured Speech key and/or region unavailable",
  "requested": true,
  "trusted_source": true,
  "key_present": false,
  "region_present": false,
  "listening_review": "pending",
  "release_ready": false
}
```

Thus no Azure service call or narrated MP4 was produced in this verification. The implementation uses the existing `MAI-Voice-2` selector and `+2%` rate, but no assertion is made about how an ungenerated take sounds. No alternate provider, stock voice or silent track was substituted.

To unblock GitHub narration, make `SPEECH_KEY` and `SPEECH_REGION` available as Actions secrets to this workflow; supported legacy aliases are `AZURE_SUBSCRIPTION_KEY` and `AZURE_SERVICE_REGION`. The existing shared helper requires the MAI profile's `canadacentral` region. Credentials must not be placed in Git or pasted into a report. Alternatively, use the documented Azure build command in the user's existing credentialed local environment.

A real Azure build must still pass the duration checks and receive a complete listening review. The silent preview does not establish those results.

## Repository-wide CI and merge state

The separate [smoke run 35282186061](https://github.com/xia-geom/math_video_project/actions/runs/35282186061) passed its repository-wide Python compilation job but failed its repository-wide Ruff job. Its broad render job was skipped. The new project's full Ruff check passed independently. Existing global lint problems were not hidden by disabling or rewriting that workflow.

This work is saved on `feat/uqam-bac-sciences-20s` and proposed in PR #4. It has not been merged into `main`. No institutional video publication, release creation, Drive upload, audit-branch deletion or force-push was performed.

## Evidence retention and scope

The workflow artifact contains both silent MP4 variants, SRT, four checkpoint images, `ffprobe.json`, `timeline.json`, `manifest.json`, test XML, lint log, installed-environment list, tested commit and render log. GitHub retention is 30 days, with the reviewed artifact expiring on 17 October 2026. Generated media are not committed to source Git.

[validation.json](validation.json) preserves the reviewed run identifiers, observed status and output checksums in Git. This report is a dated snapshot of the specified implementation commit, not an automatically changing declaration about every future build. A documentation-only follow-up commit does not change the reviewed script or renderer.
