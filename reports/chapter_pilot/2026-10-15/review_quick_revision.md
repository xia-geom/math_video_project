# Independent simulated student review — quick revision after class

Date: 2026-10-15. Reviewer role: a ChatGPT simulation of a student returning after class to locate a concept, recover the correction to a mistake, and find relevant book material. This is not feedback from a real student or a usability study.

## Result

The sampled artifacts support quick revision. The repeated four-item plans make the two lessons easy to orient within; the active item is visibly bold, and the wording and order remain unchanged. Lesson 43 gives especially clear visual retrieval cues for the wrong cancellation and its correction. I found no blocking navigation, title-readability, or correction defect in the inspected frames. One minor positioning inconsistency is confirmed below. Book references are explicit section references, with a useful distinction between the manual and exercise book; their underlying content was not independently checked in this review.

## Input identity and scope

SHA-256 hashes were recomputed from the actual MP4/PDF bytes. The MP4 hashes match their respective `STATUS.json` values.

| Input | SHA-256 |
|---|---|
| `review_artifacts/chapter_pilot/2026-10-15/15/media/videos/480p15/15_chapter_pilot_silent.mp4` | `9c529b032bed106ed86900da509a6ae340cc2fb5ab260799bcb300f7f033285e` |
| `review_artifacts/chapter_pilot/2026-10-15/43/media/videos/480p15/43_chapter_pilot_silent.mp4` | `c2804200a18a3be4e1751923a98797d34aa3e197663ae0f496f369faac2640cc` |
| `review_artifacts/teaching_navigation/catalogue/catalogue-videos.pdf` | `97d538edcc875786e68bf436fc3e86cc01cba1bc3641d63bcb7a7de8f7ba3520` |

The supplied `ffprobe.json` files identify 854 × 480, 15 fps, video-only MP4s lasting 271.466667 s and 130.600000 s. The review inspected encoded-frame samples and supplied timing/narration metadata. It did not watch either entire video in motion, listen to audio, inspect implementation sources, consult other reviewers, validate the book contents, or establish institutional approval. Intended narration is written intent, not proof of delivered speech, pronunciation, or synchronization. No production code, media, publication state, or Git state was changed by this review.

## Revision tasks and evidence

### Find a concept

- **Lesson 15: hole versus asymptote.** Catalogue page 2, row 15 names “Fonctions rationnelles et leurs asymptotes” and the goal of preserving the domain and distinguishing a hole from asymptotes. In the video, the third plan item is “Distinguer trou et asymptote” at **52.567 s, frame_024**. The correction is visible at **64.843 s, frame_029**: `g(x) = (x² − 1)/(x − 1) = x + 1 (x ≠ 1)` and “La simplification ne rétablit pas la valeur interdite.” At **71.310 s, frame_031**, the open circle at `(1, 2)` makes the missing point concrete. These cues are sufficient for the simulated quick-revision task.
- **Lesson 15: asymptotes.** “Lire les asymptotes” is bold at **29.233 s, frame_015**; the graph with `x = 1` and `y = 1` appears at **38.910 s, frame_019**; the two directional limits and the horizontal limit appear at **50.977 s, frame_022**. The graph and formulas provide recognizable destinations while scanning the video.
- **Lesson 43: factors versus terms.** The second plan item is bold at **22.433 s, frame_014**. At **20.043 s, frame_012**, substituting `x = 3` gives `5/8 ≠ 2/5` and the explicit red statement “La simplification proposée est fausse.” At **37.110 s, frame_021**, the product example explains the common factor through a quotient equal to 1. At **48.910 s, frame_026**, the boxed rule “On simplifie des facteurs, jamais des termes” is easy to recover without rereading the whole lesson.

### Recover the correction and its conditions

Lesson 43 retains the original restrictions visibly: `x ≠ 0` and `x ≠ −5` at **65.310 s, frame_036**, then `x ≠ −2` and `x ≠ −1` at **83.443 s, frame_042**. The practice answers at **99.777 s/frame_048**, **110.643 s/frame_050**, and **121.510 s/frame_052** state YES/NO and a reason, so meaning does not depend on green/red color alone. The final four-step recap and “Même symbole ≠ facteur commun” at **130.510 s, frame_060** form a strong revision endpoint.

Lesson 15 also shows the distinction between an existing limit and an undefined function value at **134.177 s/frame_042**, **258.310 s/frame_054**, and **271.377 s/frame_057**. These are useful correction checkpoints. The intended narration consistently reinforces preserving the original domain. This finding does not certify that the intended narration was spoken.

### Find the relevant book material

All three catalogue pages are visually readable, with repeated column headings on continuation pages. Page 1 explicitly says that manual and exercise-book references are read separately and defines `§` versus `Ch.`. It also identifies the MAT0339 edition as **2026-10-10** and avoids implying that every listed video is available or validated.

| Revision target | Catalogue location | Manuel | Cahier |
|---|---|---|---|
| 15 — Fonctions rationnelles et leurs asymptotes | Page 2, first row | **§§ 5.2, 5.3, 5.4** | **§§ 5.1, 5.2, 5.3** |
| 43 — Annulation dans les fractions | Page 3, final row under “Erreurs fréquentes” | **§ 2.2** | **§ 2.2** |

The unequal reference sets for lesson 15 are clearly separated rather than falsely treated as interchangeable. Lesson 43 gives an exact single-section destination in each book. For lesson 15, the catalogue provides an exact three-section set but does not identify which section covers each video subtopic or name specific exercises. A student can reach the relevant area but must scan those sections. That is a precision limit, not evidence that any reference is wrong.

## Outline, titles, and reading time

The title/objective cards are readable at the encoded resolution: **1.100 s/frame_001** for each lesson. The chapter cards show exactly one bold current item at lesson 15 **6.300/frame_005, 29.233/frame_015, 52.567/frame_024, 72.900/frame_033**, and lesson 43 **6.300/frame_005, 22.433/frame_014, 51.233/frame_028, 85.767/frame_044**. “Étape n sur 4” supplies a second, explicit progress cue. No inspected title is clipped or overlaps content.

According to `chapter_review.json`, each opening is fully visible from **0.400–4.400 s**. Each first plan is fully visible from **5.600–9.600 s**. Later fully visible plan intervals are:

| Lesson | Step 2 | Step 3 | Step 4 |
|---|---|---|---|
| 15 | 28.533–31.533 s | 51.867–54.867 s | 72.200–75.200 s |
| 43 | 21.733–24.733 s | 50.533–53.533 s | 85.067–88.067 s |

For this role, four seconds is plausible for reading the opening and recognizing the first plan; the recurring three-second plans are adequate for identifying the newly bold item. The first plan can feel brisk if the learner tries to read and memorize every entry on first exposure. That is a pacing preference to check with actual learners, not a confirmed failure. The sparse formulas and short correction statements are legible in the full-size frames. Lesson 15's metadata specifies longer 9–14 second visible windows for several worked-example steps, which supports deliberate review. Sampled endpoints cannot establish every animation's reading time, and the silent timing must not be used to certify spoken pacing.

## Confirmed issue and optional improvements

**Minor confirmed visual inconsistency:** the item list recenters slightly horizontally when the longest third entry becomes bold. Compare lesson 15 **frame_024 at 52.567 s** with **frame_005 at 6.300 s** and **frame_033 at 72.900 s**; compare lesson 43 **frame_028 at 51.233 s** with **frame_005 at 6.300 s** and **frame_044 at 85.767 s**. The row heights, wording, and sequence stay stable. Anchoring all rows to a fixed left edge would improve positional stability, but this did not prevent locating the current chapter. No numerical pixel displacement is claimed.

Optional design preferences, not confirmed defects:

- For book-based revision, add subtopic-to-section or exercise references to the catalogue when those mappings have been checked against the actual books. Avoid guessing which lesson-15 section corresponds to holes versus asymptotes.
- Including the catalogue number on the opening card, and using the same lesson-15 title as the catalogue, would make cross-identification faster. The current shorter video title “Fonctions rationnelles” remains recognizable.
- Lesson 15's fourth chapter covers worked examples and practice from roughly **75.6 s to the end**. Optional subchapter timestamps would make it easier to return directly to the exercise or final domain check.

## Exact inspected artifact files

All paths below are relative to `/Users/xiaxiao/Desktop/video/math_video_project_clean`.

- For each of `review_artifacts/chapter_pilot/2026-10-15/15/` and `review_artifacts/chapter_pilot/2026-10-15/43/`: `STATUS.json`, `frame_index.json`, `chapter_review.json`, `narration.json`, and `ffprobe.json`.
- Lesson 15 contact sheets: `contact_00.png`, `contact_01.png`, `contact_02.png`, `contact_03.png`, `contact_04.png`. These display all 58 supplied sampled frames.
- Lesson 43 contact sheets: `contact_00.png`, `contact_01.png`, `contact_02.png`, `contact_03.png`, `contact_04.png`, `contact_05.png`. These display all 61 supplied sampled frames.
- Lesson 15 frames opened individually at full size under `15/frames/`: `frame_001.png`, `frame_005.png`, `frame_015.png`, `frame_019.png`, `frame_022.png`, `frame_024.png`, `frame_029.png`, `frame_031.png`, `frame_033.png`, `frame_042.png`, `frame_049.png`, `frame_054.png`, `frame_057.png`.
- Lesson 43 frames opened individually at full size under `43/frames/`: `frame_001.png`, `frame_005.png`, `frame_012.png`, `frame_014.png`, `frame_021.png`, `frame_026.png`, `frame_028.png`, `frame_036.png`, `frame_042.png`, `frame_044.png`, `frame_048.png`, `frame_050.png`, `frame_052.png`, `frame_060.png`.
- Under `review_artifacts/teaching_navigation/catalogue/`: `page-1.png`, `page-2.png`, `page-3.png`, and `catalogue-videos.txt`. PDF visual inspection used these supplied page renderings; the PDF itself and the two MP4s listed above were read for byte hashes, not full-motion playback or independent re-rendering.
- Repository entry instructions read: `ARCHITECTURE.md` and `AGENT.md`. No lesson implementation/source or other review report was consulted.

This report records sampled visual review and a simulated revision workflow only. Full-motion review, listening, actual learner feedback, source-book verification, and release approval remain separate activities.

## Final-v2 independent verification — appended 2026-10-15

The initial review above is preserved as a record of the original artifacts. This addendum concerns only `review_artifacts/chapter_pilot/2026-10-15/final_v2/`. The minor confirmed list-position drift **is resolved in the newly inspected chapter-card frames**. No new blocking revision-navigation or legibility issue was found in this sample review.

### Final input identity

The following SHA-256 values were recomputed from actual MP4 bytes and match the final-v2 `STATUS.json` records:

| Final input | Actual SHA-256 |
|---|---|
| `final_v2/15/media/videos/480p15/15_chapter_pilot_silent.mp4` | `ec057d46ad63d35a869d5c48d3c03d8006e1b8670faf178757ca10f59a930b20` |
| `final_v2/43/media/videos/480p15/43_chapter_pilot_silent.mp4` | `091b3f39c353c08cdcc182d90b58d278fe88a5d0206233641f7b74f1933adb1a` |

The catalogue PDF was rehashed: **`97d538edcc875786e68bf436fc3e86cc01cba1bc3641d63bcb7a7de8f7ba3520`**, identical to the initial review. Its book references therefore remain lesson 15 **Manuel §§ 5.2, 5.3, 5.4 / Cahier §§ 5.1, 5.2, 5.3**, and lesson 43 **§ 2.2 in both**. The optional precision improvements in the initial review remain optional and unresolved; this addendum does not claim a catalogue change.

### Direct checks of the new frames

All eight chapter cards were opened individually at native size and compared visually. Each lesson now holds a fixed left alignment and stable row positions across all four cards, including the longest third item when bold. The wording/order remain unchanged, only the current item is bold, and the footer correctly advances from step 1 to step 4:

| Lesson | Step 1 | Step 2 | Step 3 | Step 4 |
|---|---|---|---|---|
| 15 | **6.300 s, frame_005** | **29.233 s, frame_015** | **52.567 s, frame_024** | **72.900 s, frame_033** |
| 43 | **6.300 s, frame_005** | **22.433 s, frame_014** | **51.233 s, frame_028** | **85.767 s, frame_044** |

These are observations of the encoded frame images, not deductions from implementation. The final chapter timing metadata retains the same four-second first plan and three-second subsequent plan holds as the initial review, so the earlier reading-time assessment still applies.

Both opening title/objective cards remain readable at **1.100 s, frame_001**. Lesson 15's final domain check remains readable at **271.377 s, frame_057**. Lesson 43's updated recap is readable at **130.510 s, frame_060** and now begins with finding the original forbidden values before factorization and simplification. Its four lines and boxed “Même symbole ≠ facteur commun” fit without overlap.

The requested lesson-43 top-margin spot-check passes visually: the main title is fully inside the frame with visible whitespace above it at **12.377 s/frame_008**, **20.043 s/frame_012**, **48.910 s/frame_026**, and **130.510 s/frame_060**. Headings and subheadings remain separated. Original and final `frame_008` were both opened for comparison; no exact pixel-margin measurement or claim about the implementation is made.

The new restriction-first order is visible at **61.443 s/frame_034** and **62.510 s/frame_035**, before the simplified equality at **65.310 s/frame_036**. Likewise, `x ≠ −2` and `x ≠ −1` appear at **79.710 s/frame_041**, before the cancellation equality at **83.443 s/frame_042**. This supports the recap's instruction to preserve the initial domain. Selected final narration entries agree with this order. Lesson 15's intended narration at **123.667–134.267 s** and **185.733–196.333 s** explicitly asks for a sketch on paper; it no longer relies on those passages being interpreted as a newly displayed graph. This is a written-narration check only.

### Exact additional inspected files and limits

- Under each `final_v2/15/` and `final_v2/43/`: `STATUS.json`, `frame_index.json`, `chapter_review.json`, `ffprobe.json`, and selected relevant entries of `narration.json`.
- All final-v2 lesson-15 sheets `contact_00.png`, `contact_01.png`, `contact_02.png`, `contact_03.png`, `contact_04.png`; all final-v2 lesson-43 sheets `contact_00.png`, `contact_01.png`, `contact_02.png`, `contact_03.png`, `contact_04.png`, `contact_05.png`. These cover all 119 supplied sampled frames.
- Individually opened final-v2 lesson-15 images under `15/frames/`: `frame_001.png`, `frame_005.png`, `frame_015.png`, `frame_024.png`, `frame_033.png`, `frame_057.png`.
- Individually opened final-v2 lesson-43 images under `43/frames/`: `frame_001.png`, `frame_005.png`, `frame_008.png`, `frame_012.png`, `frame_014.png`, `frame_026.png`, `frame_028.png`, `frame_034.png`, `frame_035.png`, `frame_036.png`, `frame_041.png`, `frame_042.png`, `frame_044.png`, `frame_060.png`.
- Original `review_artifacts/chapter_pilot/2026-10-15/43/frames/frame_008.png` was additionally opened for the margin comparison. The final MP4s above and the unchanged catalogue PDF were read for hashing.

The final supplied probe records still show video-only 854 × 480, 15 fps files, with unchanged durations of **271.466667 s** and **130.600000 s**. This addendum is a native-frame and contact-sheet verification by a simulated reviewer; it does not constitute full-motion viewing, listening, spoken synchronization validation, real-student feedback, book-content verification, or release approval. Only this review file was edited.
