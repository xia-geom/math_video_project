# Syllabus expansion and retained audit lessons — 20 September 2026

## Result and scope

Implemented on `feat/syllabus-expansion-audit-lessons`, in
[PR #11](https://github.com/xia-geom/math_video_project/pull/11).
This report records candidate production, not publication or release approval.
The branch was left unmerged when this report was written.

The requested syllabus basis is
[`curriculum/couverture_programme.md`](../../../curriculum/couverture_programme.md)
as read at base commit `0e5c9b0ea0e38bcc1cbb60aa45fd88976beee67e`.
Its ten non-optional missing topics now have authored French Manim sources,
spoken scripts, worked examples and self-checks. The examples are new authoring
to realize those topics, not quotations or transcriptions of the textbook.
Introductory coverage is not a claim of exhaustive syllabus coverage.

## Where future authors find the audit lessons

- [`docs/TEACHING_STANDARD.md`](../../../docs/TEACHING_STANDARD.md), section
  **Lessons retained from the visual audit**, translates observed defects into
  prevention rules and regression checks, while linking the historical evidence.
- [`scenes/AGENTS.md`](../../../scenes/AGENTS.md) makes those rules discoverable
  when an agent creates or edits a teaching scene.
- [`curriculum/README.md`](../../../curriculum/README.md) explains the candidate
  queue, preview commands and promotion requirements.
- [`curriculum/extension_syllabus_fr.yaml`](../../../curriculum/extension_syllabus_fr.yaml)
  records each candidate's objective, prerequisites, source, public class and
  self-check. S identifiers do not replace the existing P/E audit identifiers.

Retained rules include clearing the whole outgoing case before introducing the
next, using sequential fades for unrelated text instead of scrambled glyph
morphs, separating title/body/caption regions, shortening or splitting content
rather than shrinking an overcrowded page, removing stale labels and updaters,
and selecting explicit silent mode before creating an Azure service. Meaningful
geometric transformations remain appropriate. Rendering, visual inspection,
listening and publication approval are distinct checks.

The root instruction files were not changed, avoiding competing edits with
PR #7's guide simplification. Existing scene sources, public classes and delivery
orders for P01–P27 and E01–E06 were not changed. Neither shared voice settings,
promotional scenes nor textbook files were changed. No archived patch script
was replayed; no Drive copy or publication was performed.

## Tested source and retained evidence

- Tested source commit: `4a9ea4f5daf7f67f550d5416edd1dbe50f4cbb20`.
- Successful candidate workflow:
  [run 35529144669](https://github.com/xia-geom/math_video_project/actions/runs/35529144669).
- Artifact: `syllabus-preview-35529144669`, ID `10610647379`.
- Artifact SHA-256:
  `4f92bb1d7da9fe6a6dc9d3c238fa653f8481c1b3f90879dbf4c50b077eaa68209`.
- Artifact expiry recorded by GitHub: 4 October 2026. Media are temporary;
  this report is the durable record. The source remains reproducible in Git.
- Manifest SHA-256:
  `b1d46c8ac1fe3a42be3a70671f3f62933576e03a73c375e8c944e618f2a9d8252`.

The artifact contains `tested_commit.txt`, `source.zip`, `environment.txt`,
`tests.log`, JUnit XML, per-scene render logs, MP4s, ffprobe metadata, sampled
frames, and `rendered/STATUS.json`. That JSON records source, shared-service and
video hashes. Generated videos and font files were not committed to source Git.
A later documentation-only commit containing this report is not the tested
source commit above.

## Measured verification

**34 focused tests passed.** They cover candidate registration and prerequisites,
worked-example calculations and invalid inputs, the shared scene contract,
one opening per candidate, explicit silent/real-narration routing with mocked
services, encoded-stream mode checking, and all authored headings/plain text at
their intended font sizes. Narrow syntax-critical lint also passed in the
candidate workflow. These tests are not an independent full mathematics or
pedagogy certification.

**All ten fresh MP4 previews rendered and passed stream checks:** 854 by 480
pixels, 15 frames per second, positive duration, no audio stream. They are
explicitly labelled `silent_preview`. The durations below are silent preview
timings, not final narrated durations.

| Candidate | Topic | Silent seconds | Sampled frames |
|---|---|---:|---:|
| S01 | Opérations sur les nombres réels | 65.8 | 22 |
| S02 | Fonctions rationnelles et asymptotes | 68.8 | 23 |
| S03 | Modèles probabilistes élémentaires | 75.0 | 25 |
| S04 | Équations de la droite et du plan | 71.8 | 24 |
| S05 | Règle de Cramer | 72.0 | 24 |
| S06 | Élimination de variables | 77.8 | 26 |
| S07 | Programmation linéaire à deux variables | 81.2 | 27 |
| S08 | Trigonométrie du triangle | 78.8 | 26 |
| S09 | Lois des sinus et des cosinus | 78.8 | 26 |
| S10 | Fonctions trigonométriques inverses | 71.8 | 24 |

The 247 frame samples, extracted at three-second intervals, were visually
inspected as contact sheets. The corrected S02 hole label and S06 intersection
label were additionally inspected at the full encoded preview resolution:
`S02/frames/sample_0018.png` and `S06/frames/sample_0013.png`. Both labels now
have clear separation from the interfering axes/lines. No further structural
collision was identified in that sampled inspection. This does not cover every
in-between animation frame, final-resolution legibility or listening.

The automated JSON intentionally leaves visual review pending: rendering alone
does not set that status. The manual sampled review is recorded here separately;
full-motion review remains pending.

### Separate repository-wide failure

The existing broad `ci-smoke` workflow at the same source commit,
[run 35529144662](https://github.com/xia-geom/math_video_project/actions/runs/35529144662),
passed Python compilation but failed its Ruff lint step. The connector returned
empty job logs for the failing job, so the detailed cause was not established.
It is not justified to label all those failures pre-existing or to describe the
entire PR as green. The successful candidate checks above do not override that
failure. It remains an integration item before merging.

## Defects caught and repaired during production

The initial candidate render was not accepted as finished. Oversized headings
blocked six scenes; they were shortened without reducing font size. New
preflight tests for every title and plain-text item subsequently caught two
additional captions, which were also shortened. The full candidate set was
then rerendered.

Further fixes included explicit dark number-line labels in S01, graph-coordinate
label placement in S04, and anchoring S07's late-revealed optimum marker to the
axes after page layout had moved them. Probability wording was clarified so
counting alone is not mistaken for a probability model, and the spoken linear
programming bound was made unambiguous.

Actual frame review then exposed two collisions not caught by successful
rendering: S02's hole coordinate label crossed the vertical axis, and S06's
intersection label met a graph line. Commit `4a9ea4f` moves those labels into
clear regions. The successful workflow and manual checks above refer to the
fresh corrected renders, not to the earlier videos.

## Remaining production gates

The canonical programme remains the existing 27 main lessons and six common-error
lessons. S01–S10 are authored and previewed candidates, not yet approved additions
to its delivery manifest. S11, introductory complex numbers, remains explicitly
optional and unimplemented, as in the source plan.

Before promoting candidates: resolve the broad lint failure; complete pedagogical
review and full-motion/final-resolution inspection; synthesize real narration
using the existing shared profile; listen through joins and check pacing and
captions; then explicitly update the canonical curriculum, validator and delivery
indexes. Preserve existing public identifiers and keep geometry/Sigma placement
consistent with the plan. No release, external mirror or institutional
publication is authorized merely by an automated test or preview pass.
