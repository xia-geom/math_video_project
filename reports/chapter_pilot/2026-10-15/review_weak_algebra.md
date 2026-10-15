# Independent simulated review: weak algebra foundations

Date: 2026-10-15. Reviewer: a ChatGPT role simulating the questions of a learner revising after class with weak algebra foundations. This is not a real student review, an empirical learning test, or evidence that any learner improved or became confused.

## Scope and input identity

Only the supplied encoded-preview frame extractions, intended narration, chapter audit metadata, and rendered catalogue were used to assess teaching. No lesson implementation, curriculum source, or other review was inspected. Repository entry guides `ARCHITECTURE.md` and `AGENT.md` were read for working boundaries.

| Input | SHA-256 | Status |
|---|---|---|
| `review_artifacts/chapter_pilot/2026-10-15/15/media/videos/480p15/15_chapter_pilot_silent.mp4` | `9c529b032bed106ed86900da509a6ae340cc2fb5ab260799bcb300f7f033285e` | Actual bytes independently hashed; agrees with lesson 15 `STATUS.json`. |
| `review_artifacts/chapter_pilot/2026-10-15/43/media/videos/480p15/43_chapter_pilot_silent.mp4` | `c2804200a18a3be4e1751923a98797d34aa3e197663ae0f496f369faac2640cc` | Actual bytes independently hashed; agrees with lesson 43 `STATUS.json`. |
| `review_artifacts/teaching_navigation/catalogue/catalogue-videos.pdf` | `97d538edcc875786e68bf436fc3e86cc01cba1bc3641d63bcb7a7de8f7ba3520` | Actual PDF bytes independently hashed; visual review used its supplied PNG pages. |

Both previews are 854 × 480 at 15 fps. Supplied `ffprobe.json` records only a video stream: lesson 15 is 271.466667 seconds; lesson 43 is 130.600000 seconds. The `STATUS.json` files say Azure audio is blocked by missing credentials, full-motion and listening checks are not done, release readiness is false, and institutional approval is pending. Narration below means intended text, never heard audio. Silent-preview timings cannot establish the pacing or synchronization of a future narrated render.

## Actionable findings

### WA-1 — Lesson 15: the worked-example narration refers to a drawing that its sampled endpoint does not display

Evidence: at **02:14.177 / 134.177 s**, `15/frames/frame_042.png`, the page “Un facteur disparaît, pas le trou” contains only the original quotient and `lim r(x) = 4`, with `r(2) non défini`. The intended narration for **123.667–134.267 s** says “On dessine un cercle vide au point deux, quatre.” There is no drawing or open point in this endpoint. All supplied sampled frames of that worked example, `frame_036`–`frame_042` (**75.977–134.177 s**), show algebra or transitions rather than a graph. This differs from the earlier example at **01:11.310 / 71.310 s**, `frame_031.png`, where the open point `(1, 2)` is actually visible.

A related mismatch occurs at **03:16.243 / 196.243 s**, `15/frames/frame_049.png`: the only supporting content is `f(0) = −3` and `f(−3/2) = 0`. The intended text at **185.733–196.333 s** describes using these points to catch “une branche dessinée du mauvais côté,” but the sampled worked-example page has no drawn branch. Its supplied samples `frame_043`–`frame_049` (**135.043–196.243 s**) contain formulas only.

For the simulated learner, these are precisely the occasions where linking a formula to a missing point or to a branch would help make the distinction concrete. The issue is the observed text–picture mismatch, not a claim that a real learner was confused. Add the corresponding small graph/open point and plotted intercepts, or explicitly ask the learner to sketch them rather than describing a displayed drawing. Retain the difference between a limit and a defined value.

Book navigation: catalogue **page 2, entry 15**, maps this work to **Manuel §§ 5.2, 5.3, 5.4** and **Cahier §§ 5.1, 5.2, 5.3**. These are catalogue-provided references; the underlying book sections were not independently reviewed here. The claim is bounded by sampled frames; a full-motion review should confirm what appears between them.

### WA-2 — Lesson 43: show the original restrictions before the cancellation and preserve them during it

Evidence: **01:01.243 / 61.243 s**, `43/frames/frame_034.png`, shows

`x(x+2) / [x(x+5)] = (x/x) · [(x+2)/(x+5)] = (x+2)/(x+5)`

without `x ≠ 0` or `x ≠ −5`; they are present in `frame_035.png` at **01:02.310 / 62.310 s**. Again, at **01:19.377 / 79.377 s**, `frame_041.png` shows the cancellation of `(x+2)` without its restrictions; `x ≠ −2` and `x ≠ −1` appear in `frame_042.png` at **01:23.443 / 83.443 s**. The final ordered recap, `frame_060.png` at **02:10.510 / 130.510 s**, places “Conserver les valeurs interdites d’origine” fourth, after rewriting and simplifying. The final intended narration likewise places preserving restrictions last.

The completed examples are correct: this is a sequencing problem, not a claim of an incorrect final answer. During the displayed intermediate equalities, a learner who copies a line has no visible reminder of the original excluded input. The stated objective is to retain precisely those inputs that disappear from the simplified denominator. Record the original denominator's zeros before cancellation, keep that condition on screen through the equality, and put “Repérer les valeurs interdites d’origine” before simplifying in the final method. A short calculation such as `x(x+5)=0 ⇒ x=0 ou x=−5` would make the source of the restrictions explicit.

Book navigation: catalogue **page 3, entry 43**, **Manuel § 2.2** and **Cahier § 2.2**. The concern is pedagogical ordering for this reviewer role; later frames and narration do correctly restore the restrictions.

## Optional suggestions, not defects or release blockers

- In lesson 43, **01:17.243 / 77.243 s**, `frame_039.png`, gives `x²+3x+2=(x+1)(x+2)` directly, and the intended narration at **71.933–77.333 s** states the factorization without showing how it is found. For weak algebra foundations, a brief expansion check or the pair `1+2=3`, `1×2=2` would support that step. The equality is correct, and factorization may reasonably be assumed in a revision capsule. Catalogue entry 43 points to both books' § 2.2.
- In lesson 15, **00:50.977 / 50.977 s**, `frame_022.png`, introduces one-sided limit symbols on a separate page after the graph. The narration explains “à gauche” and “à droite,” but a small `1⁻ : par la gauche` / `1⁺ : par la droite` cue would help a learner who recognizes the graph but not the notation. This is optional scaffolding, not a mathematical error. Catalogue entry 15 supplies the section references above.
- Both chapter cards are readable in the inspected native-size frames, and bold active items plus “Étape … sur 4” orient the learner. Lesson 15's fourth chapter at **01:12.900 / 72.900 s**, `frame_033.png`, includes two further guided examples before independent practice at about **197.200 s**. “Exemples guidés et entraînement” would describe that portion more specifically than “S’entraîner et vérifier”; the present title is not false.

## Positive checks and limits

The samples and intended text consistently distinguish terms from factors, preserve the final original domains, distinguish a hole from a vertical asymptote, and distinguish a limit from a function value. The lesson 43 counterexample using `x=3` visibly disproves the proposed cancellation. The lesson 15 text also correctly says a horizontal asymptote need not be an uncrossable line. No incorrect final mathematical result was identified in the reviewed material.

Catalogue pages 2 and 3 separate the manual and workbook references clearly. Entry 15 describes preserving the domain and distinguishing holes from asymptotes; entry 43 describes simplifying factors while retaining restrictions. These descriptions agree with the sampled topics. Page 1 explicitly warns that the catalogue is partial support and does not certify video availability or validation. I found no corroborated catalogue readability or mapping-presentation defect in the relevant entries.

This review does not certify phone-scale readability, transitions, complete motion, speech intelligibility, actual speech timing, learner outcomes, book contents, or institutional approval. The only file changed by this reviewer is this report. No source code, media, publication state, or release status was changed.

## Exact inspection coverage

Paths below are relative to `/Users/xiaxiao/Desktop/video/math_video_project_clean`.

- Read for each of `review_artifacts/chapter_pilot/2026-10-15/15/` and `.../43/`: `STATUS.json`, `chapter_review.json`, `frame_index.json`, `narration.json`, and `ffprobe.json` (probe stream type, duration, and dimensions).
- Visually inspected all lesson 15 contact sheets: `15/contact_00.png`, `contact_01.png`, `contact_02.png`, `contact_03.png`, `contact_04.png`. Together these show all **58 supplied sampled frames**, IDs `000`–`057`.
- Visually inspected all lesson 43 contact sheets: `43/contact_00.png`, `contact_01.png`, `contact_02.png`, `contact_03.png`, `contact_04.png`, `contact_05.png`. Together these show all **61 supplied sampled frames**, IDs `000`–`060`.
- Additionally inspected individual native-size lesson 15 files under `15/frames/`: `frame_019.png`, `frame_022.png`, `frame_028.png`, `frame_031.png`, `frame_033.png`, `frame_042.png`, `frame_049.png`.
- Additionally inspected individual native-size lesson 43 files under `43/frames/`: `frame_028.png`, `frame_033.png`, `frame_034.png`, `frame_035.png`, `frame_039.png`, `frame_041.png`, `frame_042.png`, `frame_060.png`.
- Visually inspected `review_artifacts/teaching_navigation/catalogue/page-1.png`, `page-2.png`, `page-3.png`; read `catalogue-videos.txt`; hashed `catalogue-videos.pdf`. Relevant entries 15 and 43 were checked against both page images and extracted text.
- Hashed the two encoded MP4 files identified above. **No continuous playback and no listening were performed.** Contact-sheet coverage of all supplied samples is not coverage of every video frame.

## Final-v2 independent correction check — 2026-10-15

The original findings above are preserved as a record of the initial inputs. This addendum applies only to the final-v2 inputs below. The same simulated reviewer role was used; no implementation or other review was inspected.

| Final input | Independently computed SHA-256 |
|---|---|
| `review_artifacts/chapter_pilot/2026-10-15/final_v2/15/media/videos/480p15/15_chapter_pilot_silent.mp4` | `ec057d46ad63d35a869d5c48d3c03d8006e1b8670faf178757ca10f59a930b20` |
| `review_artifacts/chapter_pilot/2026-10-15/final_v2/43/media/videos/480p15/43_chapter_pilot_silent.mp4` | `091b3f39c353c08cdcc182d90b58d278fe88a5d0206233641f7b74f1933adb1a` |

Both actual MP4 hashes match their final-v2 `STATUS.json`. The catalogue PDF was rehashed and remains `97d538edcc875786e68bf436fc3e86cc01cba1bc3641d63bcb7a7de8f7ba3520`; the initial catalogue inspection and book references therefore remain applicable.

**WA-1: corrected at the authored-text level.** Final-v2 lesson 15 `narration.json`, **123.667–134.267 s**, now explicitly says “Pour votre croquis sur papier, marquez un cercle vide au point deux, quatre.” At **185.733–196.333 s**, it says “Pour vérifier votre croquis sur papier” and directs the learner to place `(0, −3)` and `(−3/2, 0)`. The endpoint frames remain algebraic: `final_v2/15/frames/frame_042.png` at **02:14.177 / 134.177 s** shows the limit and undefined value; `frame_049.png` at **03:16.243 / 196.243 s** shows the two intercept calculations. The new wording accurately makes the sketch the learner's paper task rather than a claimed on-screen drawing. This resolves the two specific text–picture mismatches identified in WA-1. It does not establish delivery or synchronization of that text in real audio.

**WA-2: corrected in the sampled encoded sequence and intended text.** Final-v2 lesson 43 now displays `x ≠ 0` and `x ≠ −5` in `frame_034.png` at **01:01.443 / 61.443 s**, before the final cancellation equality. `frame_035.png` at **01:02.510 / 62.510 s** adds their origin, and `frame_036.png` at **01:05.310 / 65.310 s** retains both restrictions beside the completed equality. In the polynomial example, `frame_041.png` at **01:19.710 / 79.710 s** displays `x ≠ −2` and `x ≠ −1` before the final equality, and `frame_042.png` at **01:23.443 / 83.443 s** keeps them with that equality. The intended narration at **59.600–65.400 s** and **77.333–83.533 s** now states the original denominator restrictions before explaining simplification.

The final recap begins with “Repérer les valeurs interdites d'origine” in `final_v2/43/frames/frame_056.png` at **02:04.443 / 124.443 s**. The complete recap at `frame_060.png`, **02:10.510 / 130.510 s**, preserves that order and ends with keeping restrictions after simplification. Intended narration at **122.533–129.600 s** agrees. Thus the restriction-order concern in WA-2 is resolved in the evidence reviewed.

**Remaining status:** no confirmed problem from WA-1 or WA-2 remains in these authored-text and sampled-sequence checks. The earlier optional scaffolding suggestions remain optional; they were not promoted to defects. Both final status files still say `blocked_missing_azure_credentials`, `release_ready: false`, `full_motion: not_checked`, and `listening: not_checked`. No actual audio was available, no listening or continuous playback occurred, and this correction check is not audiovisual synchronization, complete-motion, learner-outcome, or institutional approval.

Exact additional coverage, relative to `review_artifacts/chapter_pilot/2026-10-15/final_v2/`:

- Read `15/STATUS.json`, `15/frame_index.json`, `15/narration.json`, and the same three files under `43/`; hashed both encoded MP4 files above.
- Viewed `15/contact_03.png` and `15/contact_04.png` (sample IDs `036`–`057`); viewed `43/contact_02.png`, `contact_03.png`, `contact_04.png`, `contact_05.png` (sample IDs `024`–`060`). This correction pass covers **59 supplied samples through six contact sheets**, not every frame of either video.
- Viewed nine individual native-size files: `15/frames/frame_042.png`, `15/frames/frame_049.png`; `43/frames/frame_034.png`, `frame_035.png`, `frame_036.png`, `frame_041.png`, `frame_042.png`, `frame_056.png`, `frame_060.png`.
- Rehashed the unchanged catalogue PDF; did not repeat its visual review. Only this assigned report was edited.
