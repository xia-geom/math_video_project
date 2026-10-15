# Independent simulated student review: mechanical-rule errors

Date: 2026-10-15. Reviewer role: a revising student liable to cancel terms, forget original restrictions, or treat every zero of a denominator as an asymptote. This is a ChatGPT simulation, not an observation of real learners or evidence of learning gains. I did not read the implementation or other reviewers' reports.

## Result

No incorrect final algebraic result, restriction, numerical counterexample, limit, or graph point was found in the inspected samples. Both lessons are suitable for further review from this perspective. I found no confirmed mathematical defect or sampled answer leak that requires blocking the pilot. The main improvements below concern the order in which restrictions appear and what the final exercises actually test; they are not claims that the displayed final answers are wrong.

This conclusion covers sampled encoded frames and intended narration text. It is not a full-motion, listening, final-resolution, or institutional approval.

## Input identities and review method

SHA-256 values were recomputed from the actual files, rather than copied without verification.

| Input | SHA-256 |
| --- | --- |
| `review_artifacts/chapter_pilot/2026-10-15/15/media/videos/480p15/15_chapter_pilot_silent.mp4` | `9c529b032bed106ed86900da509a6ae340cc2fb5ab260799bcb300f7f033285e` |
| `review_artifacts/chapter_pilot/2026-10-15/43/media/videos/480p15/43_chapter_pilot_silent.mp4` | `c2804200a18a3be4e1751923a98797d34aa3e197663ae0f496f369faac2640cc` |
| `review_artifacts/teaching_navigation/catalogue/catalogue-videos.pdf` | `97d538edcc875786e68bf436fc3e86cc01cba1bc3641d63bcb7a7de8f7ba3520` |

The supplied `ffprobe.json` records video-only 854 x 480, 15 fps outputs: lesson 15 lasts 271.466667 seconds and lesson 43 lasts 130.600000 seconds. Both `STATUS.json` files identify silent previews, blocked Azure audio, listening and full motion not checked, and release readiness false. `narration.json` is authored intended speech with silent-preview timing, not heard speech or measured spoken-word timing.

I inspected all five lesson-15 contact sheets and all six lesson-43 contact sheets, covering the 58 and 61 indexed sample frames respectively. I then examined critical individual frames at their full encoded size. Times below are the `frame_index.json` sample times; a sample time is not an exact transition boundary.

## Confirmed mathematical observations

### Lesson 43: factors, terms, and restrictions

- At 20.043 s (`43/frame_012`), the numerical test gives `(3+2)/(3+5) = 5/8 != 2/5`, explicitly labelled as a false proposed simplification. A single counterexample correctly refutes the proposed general cancellation; it does not pretend to prove the general rule by itself.
- At 33.377 s (`43/frame_020`), `(3*2)/(3*5) = (3/3)*(2/5) = 1*(2/5) = 2/5`. This directly explains cancellation as replacing a nonzero common-factor quotient by one. At 48.910 s (`43/frame_026`), the addition comparison and the sentence “On simplifie des facteurs, jamais des termes” make the structural difference explicit.
- At 62.310 s (`43/frame_035`), `x(x+2)/[x(x+5)]` simplifies to `(x+2)/(x+5)` with both `x != 0` and `x != -5`. The removed factor's exclusion is retained.
- At 77.243 s (`43/frame_039`), the factorizations `x^2-4=(x-2)(x+2)` and `x^2+3x+2=(x+1)(x+2)` are correct. At 83.443 s (`43/frame_042`), the simplified result `(x-2)/(x+1)` retains `x != -2` and `x != -1`.
- The three final answers at 99.777, 110.643, and 121.510 s (`43/frame_048`, `050`, `052`) correctly distinguish `5x/(5y)`, `(5+x)/(5+y)`, and `5(x+1)/[5(x-2)]`. Their restrictions are respectively `y != 0`, `y != -5`, and `x != 2`. The “NON” in the second answer applies to canceling the two 5 terms as a general algebraic operation.

Relevant book route: catalogue page 3, video 43, manual § 2.2 and exercise book § 2.2.

### Lesson 15: a missing value is not automatically an asymptote

- At 18.577 and 27.643 s (`15/frame_010`, `013`), `(x+1)/(x-1) = 1 + 2/(x-1)` retains `x != 1`. The graph at 38.910 s (`15/frame_019`) agrees with the vertical asymptote `x=1`, horizontal asymptote `y=1`, and the signs and crossings. The left/right infinite limits at 45.377 s and the limit at infinity at 50.977 s (`15/frame_021`, `022`) are correct.
- At 60.243 s (`15/frame_028`), `(x^2-1)/(x-1) = x+1` explicitly retains `x != 1`. At 71.310 s (`15/frame_031`), the open circle at `(1,2)` agrees with that restriction. These samples give a direct counterexample to the mechanical rule “denominator zero means vertical asymptote.”
- At 92.177, 112.177, and 134.177 s (`15/frame_037`, `039`, `042`), the example `(x^2-4)/(x-2)` establishes the original domain, then `x+2` for `x != 2`, and finally limit 4 with `r(2)` undefined. Its order is particularly helpful for this simulated reviewer.
- At 162.243, 174.243, 185.243, and 196.243 s (`15/frame_045`, `046`, `047`, `049`), `(2x+3)/(x-1) = 2+5/(x-1)`, the one-sided limits, horizontal limit 2, and checks `f(0)=-3`, `f(-3/2)=0` are correct.
- At 228.310 and 243.310 s (`15/frame_051`, `052`), the mixed denominator example keeps both `-1` and `2` excluded after simplification. At 258.310 s (`15/frame_054`), `h(2)` remains undefined while the limit is `4/3`. This correctly separates the missing value from the height approached.

Relevant book route: catalogue page 2, video 15, manual §§ 5.2, 5.3, 5.4 and exercise book §§ 5.1, 5.2, 5.3. These are the catalogue's references; I did not independently audit the books' section contents.

## Actionable improvements, separated from defects

### 1. Show the original restrictions before the cancellation in lesson 43

Confirmed observation: at 61.243 s (`43/frame_034`), the entire cancellation equality is visible before the restriction line, which is present at 62.310 s (`43/frame_035`). The same sequence occurs at 79.377 s (`43/frame_041`) and 83.443 s (`43/frame_042`). This does not make the completed worked example wrong: its subsequent condition and intended narration repair the possible interpretation. The sample spacing does not measure the exact duration of the omission.

Pedagogical judgment: a student who copies only the shorter formula may still treat the restriction as an afterthought. Display the original exclusions before simplifying and keep them visible through the equality. This would match lesson 15's stronger “domain first” model and the video-43 catalogue promise to preserve initial restrictions. Nonblocking improvement, manual/cahier § 2.2.

### 2. Make one final exercise elicit the restriction rather than supply it

Confirmed observation: all three lesson-43 question frames already print their restriction: 94.843, 105.710, and 116.577 s (`43/frame_047`, `049`, `051`). The answer itself is still hidden at each of those samples. The exercises test recognition of factors versus terms, but cannot independently show whether the learner remembered to recover the excluded values.

Pedagogical judgment: retain at least one factor/term comparison, and make another prompt ask for both the simplified expression and the original exclusions before revealing either. An example with a canceled variable factor would address the specific error of enlarging the domain. This is an assessment-coverage preference, not a wrong exercise or answer leak. Manual/cahier § 2.2; compare lesson 15's final domain question below.

### 3. Optionally use the mixed example to classify both excluded values

The example at 228.310-258.310 s (`15/frame_051`-`054`) preserves `-1` and `2`, but the visible resolution focuses on the hole at 2. For a student who treats all denominator zeros alike, explicitly asking what happens at `-1` as well would complete the comparison within one example: the remaining denominator creates a vertical asymptote there. The existing examples are correct; this is an optional transfer exercise, not missing mathematics required to justify the stated result. Catalogue page 2, manual §§ 5.2-5.4 / cahier §§ 5.1-5.3.

## Chapters and self-check timing

The chapter cards show only the current chapter in bold while retaining the same list. Full-size samples checked: lesson 15 at 6.300, 29.233, 52.567, 72.900 s (`005`, `015`, `024`, `033`), and lesson 43 at 6.300, 22.433, 51.233, 85.767 s (`005`, `014`, `028`, `044`). The “Étape n sur 4” line reinforces the position without relying on color. I can distinguish returning to the cancellation rule from beginning its practice. This is a simulated usability judgment, not measured learner evidence. Contact-sheet transition samples show no stale mathematical content on these cards.

Lesson 15's final question is still unanswered at 265.777 s (`15/frame_056`); the answer at 271.377 s (`15/frame_057`) correctly reads `h(x)=1 (x != 2), h(2) non défini`. The intended timing record gives full question visibility from 259.8667 s and the start of answer reveal at 265.8667 s: six seconds before reveal. That is a plausible independent attempt interval for this short question. The record is silent-preview evidence; I have not certified a six-second interval after actual spoken narration.

Lesson 43's intended timing separates each question ending from its answer start by three seconds: 91.9333-94.9333 s, 102.8000-105.8000 s, and 113.6667-116.6667 s. The question-only frames just before those answer starts corroborate concealment. Three seconds is plausible for a quick yes/no factor decision, but I would prefer six seconds or an explicit pause cue if the student must also write a reason and derive restrictions. This is a pacing preference, not a demonstrated universal minimum or a claimed violation of a requirement for these three questions.

## Catalogue usability

All three supplied page images were examined. The separate “Manuel” and “Cahier” columns and the bold instruction on page 1 prevent an assumption that section numbering must match between books. Page 2's video-15 row appropriately emphasizes preserving the domain and distinguishing holes from asymptotes; page 3's video-43 row states the factor/term and restriction objectives explicitly. No ambiguous row alignment or clipped entry was observed in these two mappings. The catalogue expressly states that it does not attest that every video is available or validated.

## Files inspected and remaining limits

- Governing guidance: `ARCHITECTURE.md`, `AGENT.md`, `scenes/AGENTS.md`, `curriculum/README.md`, `docs/TEACHING_STANDARD.md`; the PDF skill was used for read-only visual review.
- For each pilot: `STATUS.json`, `ffprobe.json`, `frame_index.json`, `narration.json`; MP4 bytes for recomputed hashes. No implementation source was opened.
- Lesson 15: `contact_00.png` through `contact_04.png`; individual full-size frames `005, 010, 013, 015, 019, 021, 022, 024, 028, 031, 033, 037, 039, 042, 045, 046, 047, 049, 051, 052, 054, 056, 057` under `review_artifacts/chapter_pilot/2026-10-15/15/frames/`.
- Lesson 43: `contact_00.png` through `contact_05.png`; individual full-size frames `005, 012, 014, 020, 026, 028, 034, 035, 039, 041, 042, 044, 047, 048, 049, 050, 051, 052, 060` under the corresponding `43/frames/` directory.
- Catalogue: PDF bytes for the hash, `catalogue-videos.txt`, and full-page `page-1.png`, `page-2.png`, `page-3.png` under `review_artifacts/teaching_navigation/catalogue/`.

No real audio exists in these reviewed MP4s. No synthesis, listening, full-motion playback, fresh render, source tests, institutional approval, or publication was performed. Unsampled motion, final narration timing, pronunciation, and higher-resolution presentation remain outside this review. Only this review report was written.

## Final-v2 verification addendum — 2026-10-15

This addendum preserves the initial review above and verifies the new encoded deliverables under `review_artifacts/chapter_pilot/2026-10-15/final_v2/`. The initial restriction-order observation is resolved in these sampled final states. No new mathematical issue was found in the affected examples, recap, or sampled lesson-15 states.

### Final artifact identities

The actual final MP4 bytes were independently hashed, and the results match their corresponding final `STATUS.json` entries:

| Final input | Recomputed SHA-256 |
| --- | --- |
| `review_artifacts/chapter_pilot/2026-10-15/final_v2/15/media/videos/480p15/15_chapter_pilot_silent.mp4` | `ec057d46ad63d35a869d5c48d3c03d8006e1b8670faf178757ca10f59a930b20` |
| `review_artifacts/chapter_pilot/2026-10-15/final_v2/43/media/videos/480p15/43_chapter_pilot_silent.mp4` | `091b3f39c353c08cdcc182d90b58d278fe88a5d0206233641f7b74f1933adb1a` |

The catalogue PDF was rehashed and is unchanged: `97d538edcc875786e68bf436fc3e86cc01cba1bc3641d63bcb7a7de8f7ba3520`. The previously reviewed book mappings therefore still apply: video 43, manual/cahier § 2.2; video 15, manual §§ 5.2-5.4 and cahier §§ 5.1-5.3.

### Restriction order and mathematics in lesson 43

All following frame references are to the final-v2 directories, not the original sample set.

- At 56.843 and 59.510 s (`43/frames/frame_031.png`, `frame_032.png`), the original expression is `x(x+2)/[x(x+5)]`. At 61.443 s (`frame_034.png`), `x != 0` and `x != -5` appear before the cancellation equality. At 62.510 s (`frame_035.png`), the caption explicitly ties those restrictions to the original fraction. At 65.310 s (`frame_036.png`), the complete equality to `(x+2)/(x+5)` appears with both restrictions still present. This resolves the original review's concern that the removed-factor exclusion arrived only after the simplified result.
- At 77.243 s (`43/frames/frame_039.png`), both polynomial factorizations remain correct. At 79.710 s (`frame_041.png`), `x != -2` and `x != -1` are shown before cancellation. At 83.443 s (`frame_042.png`), `(x-2)(x+2)/[(x+1)(x+2)] = (x-2)/(x+1)` retains both exclusions. The removed factor remains correctly subject to its nonzero condition.
- The final intended narration agrees with this order. The 59.6000-65.4000 s passage begins with the original denominator's two restrictions and then explains why `x/x=1`. The 77.3333-83.5333 s passage likewise states the excluded values before canceling `x+2`. This is a text check only; no speech was heard.
- At 124.443 s (`43/frames/frame_056.png`), the first recap item is now “Repérer les valeurs interdites d'origine.” At 130.510 s (`frame_060.png`), the four steps are original restrictions, factorization, factors rather than terms, and preservation of restrictions after simplification. The final narration at 122.5333-129.6000 s matches that order. This provides a consistent method for a student liable to drop restrictions.

The contact sheets still show the three correct final question/answer pairs at 94.843/99.777, 105.710/110.643, and 116.577/121.510 s. The separate initial suggestion to elicit at least one restriction without supplying it remains an optional assessment improvement; it is not reopened as a mathematical defect. The three-second post-question timing preference is also unchanged.

### Lesson 15 spot-check and shared chapter cards

At 134.177 s (`15/frames/frame_042.png`), the limit remains 4 with `r(2)` undefined. At 196.243 s (`frame_049.png`), the checks remain `f(0)=-3` and `f(-3/2)=0`. The intended narration now explicitly asks the learner to mark these features on a paper sketch; it does not require interpreting an absent on-screen drawing as present.

At 243.310 and 258.310 s (`15/frames/frame_052.png`, `frame_054.png`), the simplified mixed example still excludes both `-1` and `2`, and its limit at 2 is correctly `4/3` with no function value there. At 265.777 s (`frame_056.png`), the last self-check answer is still hidden. At 271.377 s (`frame_057.png`), its answer remains `h(x)=1 (x != 2), h(2) non défini`.

Across the final contact sheets, all chapter lists preserve their order, the current chapter remains the sole bold item, and the list entries now share the same left alignment across cards. No new algebraic ambiguity was observed on the sampled chapter-to-content boundaries. This is a sampled visual observation, not a motion-stability measurement.

### Addendum coverage and limits

Read-only evidence examined: both final `STATUS.json`, `ffprobe.json`, `frame_index.json`, and `narration.json`; actual MP4 bytes for hashes; all five final lesson-15 contact sheets and all six final lesson-43 contact sheets; native-size lesson-43 frames `031, 032, 033, 034, 035, 036, 039, 040, 041, 042, 056, 060`; native-size lesson-15 frames `042, 049, 052, 054, 056, 057`; catalogue PDF bytes for the unchanged hash. No implementation or other review report was read.

The final probe records remain video-only, 854 x 480 at 15 fps, with durations 271.466667 s and 130.600000 s. Audio, full-motion inspection, actual speech synchronization, and institutional approval remain unchecked. This addendum verifies sampled affected states of the final hashes; it does not certify every intervening frame or convert silent previews into narrated deliverables. Only this report was edited.
