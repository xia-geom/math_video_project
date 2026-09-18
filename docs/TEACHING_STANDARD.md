# Teaching-video standard

Applies to the 27 curriculum lessons and six common-error lessons listed in
`curriculum/programme_principal_fr.yaml`. Promotional films retain their separate
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

The focused review covers the first 17 curriculum lessons, the two geometry
lessons numbered 15/16 in their filenames, and all six common-error lessons.
It also renders the two rebuilt error lessons. Record exact source commits,
source hashes and whether the output is silent or actually narrated.

Before release, review edited sequences at their intended display size and
listen through every narrated transition. An automated pass does not authorize
institutional publication. Generated media belong in ignored output directories
or private review artifacts, not source Git.
