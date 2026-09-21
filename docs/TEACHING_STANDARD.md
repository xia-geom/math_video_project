# Teaching-video standard

Applies to all 43 course videos in `curriculum/programme_principal_fr.yaml`: 37
main lessons and six common-error supplements, with unique global numbers 01–43.
`curriculum/extension_syllabus_fr.yaml` is only a production-scope selection. Promotional films retain their separate
editorial treatment.

## Readability before fitting everything on screen

Keep one question or comparison on screen. Reveal calculations one meaningful
step at a time. Clear the previous case instead of accumulating headings,
conclusions, side notes and tables. First shorten prose, split the explanation,
reposition objects or enlarge containers; do not shrink an entire page to hide
overcrowding. Body text should ordinarily be at least 28 points. Secondary axis
labels can be smaller, but must not collide with annotations.

Use mathematical notation in tables where it is clearer than sentences. Define
symbols once in a readable legend. In the root-product table, a check mark means
“defined in the reals”, not “the equality is true”. Retain zero cases, negative
cases and the hypotheses needed for the rule.

## Panels and pages

`tools/teaching_layout.py` provides `panel`, `assert_inside` and `TeachingScene`.
A panel has minimum dimensions and grows with its contents without changing
font size. An oversized panel or page raises an error asking for reorganization.
The two rebuilt error lessons use this contract. Other scene-local builders
still need inspection; they are not automatically certified by this helper.

Reserve distinct heading, body and lower-caption regions. Do not place a moving
input on the function-machine formula: hide that formula while the token passes,
then restore it. Clear old coordinate labels before a new annotation occupies
the same position. Preserve equal visual scales for geometry.

## Voice: existing MAI profile, now the teaching default

`tools/tts.py` resolves the default to the existing `MAI-Voice-2` alias for
`fr-FR-Soleil:MAI-Voice-2`, at its existing `-3%` teaching rate, `fr-FR` locale
and neutral style. The promotion rate of `+2%` is not the teaching rate. Explicit
`MANIM_VOICE` overrides and the selectable prerecorded Sigma track remain.

Teaching lessons use `tools.teaching_voiceover.TeachingAzureService`, which
shares the existing Azure configuration. Do not add a second `global_speed`
transformation. Write complete spoken thoughts, short transitions and natural
questions. Explain symbols aloud rather than filling the screen with prose.

For MAI passages containing bookmarks, the adapter synthesizes balanced SSML
fragments, joins them at measured PCM sample boundaries and encodes one MP3
compatible with the installed voiceover tracker. Timing records are labelled
`AuthoredBookmarkAnchor`, not recognized word timestamps. Non-MAI voices retain
the upstream adapter's boundary events. Place bookmarks at complete thought
boundaries where possible. Listening across joins remains a release requirement:
passing a timing test cannot establish that narration sounds natural.

The rebuilt root-product and function-equality lessons use separate complete
spoken thoughts. Keep captions plain French and retain shared pronunciation
helpers. Missing Speech credentials must be reported as blocked, not as an
unannounced silent substitute for a requested narrated release.

## One UQAM opening

Call `tools.branding.play_uqam_intro(self)` once before lesson content. Use the
existing official `assets/branding/uqam_logo.png`, centered at width 4.0 on white:
0.4-second fade-in, 0.5-second hold, 0.4-second fade-out, 0.2-second padding.
The helper rejects duplicate openings and missing assets. Do not add a second
scene-local logo animation. The standalone identity animation remains separate.

## Verification layers

Syntax/lint, unit tests, construction-state inspection, encoded video review and
listening are different checks. `review.py` samples stable play/wait endpoints,
not every in-between frame. Candidate bounding-box intersections require visual
interpretation; safe-margin warnings are not physical frame clipping.

The construction review covers every catalogue entry, independent of its number.
It also renders the two rebuilt error lessons. Record exact source commits,
source hashes and whether the output is silent or actually narrated.

Before release, review edited sequences at their intended display size and
listen through every narrated transition. An automated pass does not authorize
institutional publication. Generated media belong in ignored output directories
or private review artifacts, not source Git.

## Lessons retained from the visual audit

These rules apply during authoring, not only when a defect is found afterwards.
The [consolidated visual-audit index](../reports/video_audits/phase2_visual_2026-09/MASTER_STATUS.md)
links to the original findings and post-fix evidence. Historical reports remain
historical; the rules here are the reusable guidance.

| Observed defect | Prevention for the next video | Regression check |
|---|---|---|
| P01/P26: outgoing annotations crossed incoming definitions or calculations. | Fade out the complete outgoing group before revealing a different case. Clear braces, arrows and updaters as well as the main formula. | Inspect both the stable endpoint and the intervening transition. |
| P03/P04/P21/P24/P27: unrelated text or formula morphs produced scrambled glyphs. | Use separate fade-out and fade-in actions for unrelated content. A mathematical transform is appropriate only when the correspondence is intentional and legible. Do not ban meaningful geometric motion. | Inspect a few frames during the replacement, not just before and after it. |
| P22/P23/E01/E04: title/question collisions and clipped long text. | Reserve heading/body/caption bands. Shorten or split prose and grow panels before considering any size reduction. Fit content at its authored size; do not shrink a whole lesson page. | Check the longest title, conclusion and formula at final display size. |
| P03/E03: stale braces, captions and conclusions crowded a new case. | Make each case own its labels; remove them with that case. Do not leave a hidden updater able to recreate an old label. | Inspect every case boundary and the final reminder. |
| P03/E01/E03/E04: a silent audit reached interactive Azure setup. | Select explicit silent preview mode before constructing the speech service. For narrated mode, validate credentials and use the shared adapter. Never silently fall back or monkeypatch a method to call itself. | Exercise explicit silent mode and credential validation separately; mock services in unit tests, then test real speech when available. |
| A successful render was mistaken for complete verification. | Keep source checks, encoded-frame review, full-motion review, narration/listening and release approval separate. | Record what actually ran, the source commit/hash and the audio mode. Never promote `PASS*` to production approval. |

### Minimum handoff for a new syllabus lesson

Give it one objective, prerequisites, an authored example with its hypotheses,
a visual explanation and a short self-check. Register its stable ID, global number, canonical scene path
and public class in the unified catalogue before rendering. Keep optional
syllabus items optional and do not advertise an authored candidate as complete
syllabus coverage.

Run focused mathematics/manifest tests and a fresh low-quality preview. Inspect
the mathematical example, the longest text and changed transitions. If the
render exposes another defect, fix and rerender the affected lesson before
closing that finding. Save the measured result in a dated report, not in this
standard. Audio and final-resolution review remain explicit release gates.

## Global numbering

Use the catalogue number in source paths and all delivery names. Dependencies and
audit targeting use stable lesson identities, not position ranges. Keep the old
P/E/S codes only as historical aliases with the explicit migration lookup.
Production audio and quality checks apply to all course entries, never only the
first numbered subset. Numbering is independent of release readiness.
