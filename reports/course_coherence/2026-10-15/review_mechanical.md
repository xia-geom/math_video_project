# Mechanical-rule review — encoded lessons 01–14

Date: 2026-10-15. Reviewer: independent simulated revising-student perspective, particularly sensitive to dropped restrictions, invalid cancellation, changed signs, and confusing visual assignments. This is analytical review, not an empirical learner study. These lessons were outside this reviewer’s source-edit ownership.

## Outcome and scope

Six actionable findings were confirmed in the initial encoded outputs: one ambiguous constants label (01), one overlapping graph conclusion (05), three transformation/intersection issues (07), and one formula/question overlap (14). No additional arithmetic error was found in the sampled states of the other lessons. All six findings are resolved in the fresh encoded outputs verified below. The initial findings and hashes remain as historical evidence. No outstanding concrete mathematical, orientation or readability defect was found within the reviewed samples of the latest versions.

All opening, authored chapter, recap, practice and final cards were inspected as encoded images. The current chapter is bold, the list order is consistent, and the opening objective/signature is legible in the sampled outputs. All final practice cards display the problem without its answer; their near-end samples still show the problem. Card audit metadata records an eight-second practice hold and at least a three-second final hold; every sampled last frame contains the final card. This supports a usable pause point, not a claim that eight seconds is sufficient for every learner.

This review uses sampled encoded frames and metadata, not full-motion playback or listening. No Azure calls were made. No lesson source, shared helper implementation or another reviewer’s findings were read for this independent review. Only the extraction utility was inspected to understand and run its sample policy. Intended narration was not evaluated.

## Confirmed findings

1. **01 — ambiguous assignment of the constants label (P2).** At **24.177 s**, the complete expression `2x + 1`, including `x`, is boxed and labeled “constantes fixées”. At the same time `x` is separately labeled “variable”. This visually attaches the constants label to the entire expression. At **46.710 s**, the later frame correctly boxes only `2` and `1`. Use the separate numeral boxes at the first introduction too. Evidence: `attempt_02/01/frames/mechanical_024177.png` and `mechanical_046710.png`. This is a labeling ambiguity, not a claim that the later evaluation arithmetic is wrong.

2. **05 — conclusion overlaps the graph (P2).** At **80.110 s**, “Une même entrée donne deux sorties.” runs through the lower circle arc and the vertical test line. At native 854×480 size, the black strokes intersect the words. Move the conclusion into clear space or lift/reduce the graph. The two-intersection mathematical argument itself is correct. Evidence: `attempt_02/05/frames/mechanical_080110.png`.

3. **07 — intersection fill suppresses the boundary reference (P2).** At **28.777 s**, the near-black intersection region lies behind black axes and ticks, making those references difficult to read. The strict boundaries `y > 0` and `x < 3` deserve clearly visible axes and dashed exclusion boundaries. Use lighter fills or hatching without obscuring the reference lines. Evidence: `attempt_02/07/frames/mechanical_028777.png`.

4. **07 — missing condition in the scaling rule (P2).** At **210.500 s**, the completed summary states `f(kx) ⇒ compression/étirement horizontal` without restricting `k`. At `k = 0` the operation is not a horizontal compression/stretch of the graph; negative `k` also adds a reflection. A concise repair is to state `k > 0` for this scaling row, with the separate `f(-x)` reflection already listed. Alternatively state `k ≠ 0` and explain the sign. Evidence: `attempt_02/07/frames/mechanical_210500.png`.

5. **07 — unrelated old curve remains in a fresh example (P2).** At **205.500 s**, under `y = −(x−2)² + 3`, the correct parabola with vertex `(2,3)` is shown alongside the previous unrelated reference curve, both in solid black and without distinct labels. Remove that old reference curve when beginning the new quadratic example. The completed earlier scaling/reflection states at **171.500 s** and **187.300 s** do use a visibly lighter reference curve and are correct. Evidence: `attempt_02/07/frames/mechanical_205500.png`, with `mechanical_171500.png` and `mechanical_187300.png` as comparison.

6. **14 — graph strokes intersect the opening mathematical prompt (P2).** At **19.243 s**, the vertical axis and curve cut through `f(x) = x² + 6x + 2` and “Où est le sommet ? Où sont les racines ?”. Put the formula/question above the plotted area or lower the graph. The sampled square completion and quadratic formula later in the video are correct. Evidence: `attempt_02/14/frames/mechanical_019243.png`.

## Checks that passed in the sampled mathematics

- **01:** substitution gives `1, 3, 5` for `x = 0, 1, 2`; the later constants boxes isolate `2` and `1`.
- **02:** positive/negative multiplier conditions are explicit; division by `−3` changes `<` to `>`; the open endpoint excludes `−2`; substitution rejects both the boundary and `−3`. Native additional checks: **61.800 s** and **87.300 s**.
- **03:** the false conjecture is explicitly marked and struck through; `√16 = 4` is separated from the two solutions of `u² = 16`; both sign cases establish `√(x²) = |x|` for real `x`.
- **04:** precedence, parentheses, subtracting a negative, common denominators and reciprocal division are correct. The division rule explicitly retains `b ≠ 0`, `c ≠ 0`, `d ≠ 0` at **69.510 s**.
- **05:** the displayed domain examples exclude `2` from `1/(x−2)` and require `x ≥ 3` for `√(x−3)`; the image example and vertical-line rejection are mathematically consistent.
- **06:** first and second differences match the displayed tables; equally spaced inputs are expressly required; the quadratic family states `a ≠ 0` and the recap says its second differences are nonzero.
- **07:** the polynomial’s roots `−1,3`, minimum at `(1,−4)` and variation statements are correct; the completed compression/reflection examples checked at native size have the right direction and coordinates. The separate findings above remain.
- **08:** interval tests and open/closed endpoints are consistent; `C(2.4) = 8`, while `m = 1` uses the first piece.
- **09:** addition/subtraction retain the same abscissa; negation reflects about the horizontal axis; intersections at `x = 0,2` match zeros of `f−g` for the displayed functions.
- **10:** `3 → 4 → 2` respects composition order; `g∘f = √(x+1)` and `x ≥ −1` agree; the test `x = −2` is correctly rejected. The large formula at **52.510 s** remains inside the encoded frame at native size.
- **11:** the affine inverse `(x−1)/2`, coordinate swap, reflection about `y=x`, failure of an inverse for the full square function, and the `x ≥ 0` restriction are consistent. The restriction is stated explicitly; making its retained graph branch even more distinct would be an optional visual preference, not a confirmed mathematical defect.
- **12:** roots are distinguished from graph points, and substitution correctly verifies roots `2` and `−1` of `(x−2)(x+1)`.
- **13:** the sign behavior matches odd/even multiplicity; repeated factors are distinguished from distinct roots. Additional native frame **47.500 s** correctly places the double root of `(x−2)²` at `x = 2`.
- **14:** `x²+6x+2 = (x+3)²−7`, vertex parameters `h = −3`, `k = −7`, the quadratic formula, `a ≠ 0`, and the real discriminant condition are correct in the sampled derivation.

## Input identity and inspected sample counts

The SHA-256 values below were computed directly from the actual MP4 bytes and matched the corresponding STATUS record. Lessons 09/10 use `attempt_03` because their `attempt_02` runs failed before a reviewable encoded deliverable; the parent identified the failure as review instrumentation. The initial 01/05 outputs became stale relative to subsequently edited source while this review was in progress; their hashes below remain the historical evidence reviewed.

| Lesson | Attempt | Actual MP4 SHA-256 | Structural readable samples | Body samples | Practice-end + last-frame samples |
|---|---|---|---:|---:|---:|
| 01 | attempt_02 | `416471fc37001329853674fed42b92edb4c4b94105f7aaf03e7776c91da9a8a9` | 8 | 12 | 2 |
| 02 | attempt_02 | `369f455f1853a4af69ae244e4b5421df665068795678aa0e004e63fa470067d1` | 8 | 12 | 2 |
| 03 | attempt_02 | `47416f36e40e56459c9a80fbf85bd2204ebcbda204156f262ce5fc03d5ce54fc` | 8 | 12 | 2 |
| 04 | attempt_02 | `fb5afc9163ba3ede6c588b29d86ea8ea7f173f0354dc8a3ccf41293781f8d559` | 8 | 12 | 2 |
| 05 | attempt_02 | `dff42e95dfd7417158c64ee5b97a7fd917d9165914b12f59282c3cd9fd5a5eef` | 8 | 12 | 2 |
| 06 | attempt_02 | `df605e9e2a9c850dbc8147e88f4078ec48b0c8e98872011a5e1b3ef393306891` | 8 | 11 | 2 |
| 07 | attempt_02 | `1d78eafd1884006dd8032147af51277ee13c50d60c5a8247ae51a726bc1e78eb` | 8 | 11 | 2 |
| 08 | attempt_02 | `3c496fa22feaeb96180d9e575a459c0247bd7f4776aa4f4446f67816951e0ccc` | 8 | 11 | 2 |
| 09 | attempt_03 | `f031c3c2882b9f71b2222fb0bec5c9feb1618dc6ba62e29ab79b23dc3b579b5f` | 8 | 12 | 2 |
| 10 | attempt_03 | `3ac338da84861409906103491cb4013f8610772fb3ec4836b3817d85b3c7b104` | 8 | 12 | 2 |
| 11 | attempt_02 | `116080e50453663aacc1ece40f64fea4f4dbf996ae8e480cd9a1f79696a3681c` | 8 | 12 | 2 |
| 12 | attempt_02 | `8db3fe27503416f93cf6d2413e985d8266902922d4ec56eb6c5bde3978a03d49` | 7 | 10 | 2 |
| 13 | attempt_02 | `e331cb5510fb7ea2b9861ed03c76496e6468dd674fc5ef80fc0fa7f774c4039a` | 8 | 7 | 2 |
| 14 | attempt_02 | `ab2b83505d00894816f2234c4b1000cca540bc61bd839a5e95ff67cd5cc474a7` | 8 | 12 | 2 |

## Exactly what was inspected

For every row above, inspected the corresponding `cards_00.png` and `body_00.png`, and read `STATUS.json`, `cards.json`, `frame_index.json` and relevant `checkpoints.json` metadata. The MP4 path is the `video_path` in its STATUS record. These are encoded-output samples, not renderer-side screenshots. Also inspected `mechanical_endpoints_01_07.png` and `mechanical_endpoints_08_14.png` under the common artifact root, containing each final-practice hold-end and final encoded sample.

The final body sheets for 02/03/04/06/07/08/11/12/13/14 and 09/10 use the improved stable-reading-hold policy: two matching label states separated by at least 0.5 seconds. The earlier body sheets for 01/05 were reviewed before source edits made their regeneration stale. Earlier exploratory body sheets for 02–08/11/12 were also viewed; the stable-body review supersedes them. The report does not count every generated chapter hold-end frame as visually inspected.

For reproducibility, the exact final indexed images viewed through those sheets are listed below. `frame_NNN` means `frames/frame_NNN.png` within the stated attempt/lesson directory. A full-size/native frame is called out separately afterward.

### 01 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 10.110s (body sample), frame_005 @ 21.177s (body sample), frame_006 @ 24.177s (body sample), frame_007 @ 28.177s (body sample), frame_008 @ 30.967s (chapter readable), frame_010 @ 37.577s (body sample), frame_011 @ 43.377s (body sample), frame_012 @ 46.710s (body sample), frame_013 @ 49.300s (chapter readable), frame_015 @ 56.443s (body sample), frame_016 @ 60.310s (body sample), frame_017 @ 65.643s (body sample), frame_018 @ 71.177s (body sample), frame_019 @ 73.967s (chapter readable), frame_021 @ 84.843s (body sample), frame_022 @ 87.433s (recap readable), frame_024 @ 96.233s (closing_practice readable), frame_025 @ 103.443s (closing_practice hold end), frame_026 @ 105.033s (closing readable), frame_027 @ 107.243s (last frame)

### 02 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 13.910s (body sample), frame_005 @ 18.710s (body sample), frame_006 @ 24.243s (body sample), frame_007 @ 26.977s (body sample), frame_008 @ 28.567s (chapter readable), frame_010 @ 46.577s (body sample), frame_011 @ 49.910s (body sample), frame_012 @ 51.500s (chapter readable), frame_014 @ 64.167s (chapter readable), frame_016 @ 71.510s (body sample), frame_017 @ 73.643s (body sample), frame_018 @ 79.843s (body sample), frame_019 @ 81.310s (body sample), frame_020 @ 93.643s (body sample), frame_021 @ 95.243s (body sample), frame_022 @ 96.833s (recap readable), frame_024 @ 105.633s (closing_practice readable), frame_025 @ 112.843s (closing_practice hold end), frame_026 @ 114.433s (closing readable), frame_027 @ 116.643s (last frame)

### 03 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 13.377s (body sample), frame_005 @ 18.977s (body sample), frame_006 @ 20.710s (body sample), frame_007 @ 25.710s (body sample), frame_008 @ 27.567s (chapter readable), frame_010 @ 35.843s (body sample), frame_011 @ 40.510s (body sample), frame_012 @ 42.367s (chapter readable), frame_014 @ 47.910s (body sample), frame_015 @ 51.443s (body sample), frame_016 @ 57.843s (body sample), frame_017 @ 62.633s (chapter readable), frame_019 @ 67.443s (body sample), frame_020 @ 70.710s (body sample), frame_021 @ 77.843s (body sample), frame_022 @ 79.700s (recap readable), frame_024 @ 88.500s (closing_practice readable), frame_025 @ 95.710s (closing_practice hold end), frame_026 @ 97.300s (closing readable), frame_027 @ 99.510s (last frame)

### 04 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 13.977s (body sample), frame_005 @ 25.643s (body sample), frame_006 @ 27.233s (chapter readable), frame_008 @ 38.510s (body sample), frame_009 @ 48.167s (chapter readable), frame_011 @ 55.843s (body sample), frame_012 @ 69.510s (body sample), frame_013 @ 71.100s (chapter readable), frame_015 @ 90.377s (body sample), frame_016 @ 120.377s (body sample), frame_017 @ 138.843s (body sample), frame_018 @ 171.443s (body sample), frame_019 @ 211.910s (body sample), frame_020 @ 239.510s (body sample), frame_021 @ 267.577s (body sample), frame_022 @ 269.167s (recap readable), frame_024 @ 277.967s (closing_practice readable), frame_025 @ 285.177s (closing_practice hold end), frame_026 @ 286.767s (closing readable), frame_027 @ 288.977s (last frame)

### 05 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 10.377s (body sample), frame_005 @ 13.377s (body sample), frame_006 @ 20.910s (body sample), frame_007 @ 26.233s (chapter readable), frame_009 @ 29.310s (body sample), frame_010 @ 34.977s (body sample), frame_011 @ 40.577s (body sample), frame_012 @ 44.433s (chapter readable), frame_014 @ 49.110s (body sample), frame_015 @ 54.177s (body sample), frame_016 @ 59.243s (body sample), frame_017 @ 64.100s (chapter readable), frame_019 @ 67.177s (body sample), frame_020 @ 74.510s (body sample), frame_021 @ 80.110s (body sample), frame_022 @ 82.367s (recap readable), frame_024 @ 91.167s (closing_practice readable), frame_025 @ 98.377s (closing_practice hold end), frame_026 @ 99.967s (closing readable), frame_027 @ 102.177s (last frame)

### 06 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 13.710s (body sample), frame_005 @ 16.310s (body sample), frame_006 @ 18.777s (body sample), frame_007 @ 21.443s (body sample), frame_008 @ 23.833s (chapter readable), frame_010 @ 29.377s (body sample), frame_011 @ 37.310s (body sample), frame_012 @ 38.777s (body sample), frame_013 @ 42.777s (body sample), frame_014 @ 45.110s (body sample), frame_015 @ 47.500s (chapter readable), frame_017 @ 53.243s (body sample), frame_018 @ 55.633s (chapter readable), frame_020 @ 59.977s (body sample), frame_021 @ 64.167s (recap readable), frame_023 @ 72.967s (closing_practice readable), frame_024 @ 80.177s (closing_practice hold end), frame_025 @ 81.767s (closing readable), frame_026 @ 83.977s (last frame)

### 07 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 13.910s (body sample), frame_005 @ 28.777s (body sample), frame_006 @ 36.300s (chapter readable), frame_008 @ 59.377s (body sample), frame_009 @ 81.110s (body sample), frame_010 @ 95.500s (chapter readable), frame_012 @ 104.110s (body sample), frame_013 @ 115.577s (body sample), frame_014 @ 126.510s (body sample), frame_015 @ 133.633s (chapter readable), frame_017 @ 148.243s (body sample), frame_018 @ 172.643s (body sample), frame_019 @ 194.643s (body sample), frame_020 @ 203.710s (body sample), frame_021 @ 213.767s (recap readable), frame_023 @ 222.567s (closing_practice readable), frame_024 @ 229.777s (closing_practice hold end), frame_025 @ 231.367s (closing readable), frame_027 @ 234.577s (last frame)

### 08 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 13.710s (body sample), frame_005 @ 23.377s (body sample), frame_006 @ 31.577s (body sample), frame_007 @ 38.510s (body sample), frame_008 @ 45.377s (body sample), frame_009 @ 50.500s (chapter readable), frame_011 @ 57.243s (body sample), frame_012 @ 65.910s (body sample), frame_013 @ 71.967s (chapter readable), frame_015 @ 81.510s (body sample), frame_016 @ 90.310s (body sample), frame_017 @ 97.500s (chapter readable), frame_019 @ 104.510s (body sample), frame_020 @ 109.977s (body sample), frame_021 @ 115.567s (recap readable), frame_023 @ 124.367s (closing_practice readable), frame_024 @ 131.577s (closing_practice hold end), frame_025 @ 133.167s (closing readable), frame_027 @ 136.843s (last frame)

### 09 — attempt_03

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 12.510s (body sample), frame_005 @ 20.177s (body sample), frame_006 @ 23.443s (body sample), frame_007 @ 26.310s (body sample), frame_008 @ 32.967s (chapter readable), frame_010 @ 40.577s (body sample), frame_011 @ 48.377s (body sample), frame_012 @ 51.510s (body sample), frame_013 @ 53.643s (body sample), frame_014 @ 55.233s (chapter readable), frame_016 @ 62.310s (body sample), frame_017 @ 63.310s (body sample), frame_018 @ 69.777s (body sample), frame_019 @ 71.367s (chapter readable), frame_021 @ 81.177s (body sample), frame_022 @ 82.767s (recap readable), frame_024 @ 91.567s (closing_practice readable), frame_025 @ 98.777s (closing_practice hold end), frame_026 @ 100.367s (closing readable), frame_027 @ 102.577s (last frame)

### 10 — attempt_03

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 14.043s (body sample), frame_005 @ 16.577s (body sample), frame_006 @ 18.167s (chapter readable), frame_008 @ 23.910s (body sample), frame_009 @ 29.110s (body sample), frame_010 @ 31.043s (body sample), frame_011 @ 37.910s (body sample), frame_012 @ 40.643s (body sample), frame_013 @ 43.977s (body sample), frame_014 @ 45.567s (chapter readable), frame_016 @ 52.510s (body sample), frame_017 @ 54.100s (chapter readable), frame_019 @ 63.643s (body sample), frame_020 @ 66.577s (body sample), frame_021 @ 69.510s (body sample), frame_022 @ 71.100s (recap readable), frame_024 @ 79.900s (closing_practice readable), frame_025 @ 87.110s (closing_practice hold end), frame_026 @ 88.700s (closing readable), frame_027 @ 90.910s (last frame)

### 11 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 11.977s (body sample), frame_005 @ 16.310s (body sample), frame_006 @ 20.577s (body sample), frame_007 @ 27.843s (body sample), frame_008 @ 29.433s (chapter readable), frame_010 @ 38.110s (body sample), frame_011 @ 42.910s (body sample), frame_012 @ 44.500s (chapter readable), frame_014 @ 52.110s (body sample), frame_015 @ 56.110s (body sample), frame_016 @ 61.710s (body sample), frame_017 @ 63.300s (chapter readable), frame_019 @ 72.243s (body sample), frame_020 @ 74.843s (body sample), frame_021 @ 79.577s (body sample), frame_022 @ 81.167s (recap readable), frame_024 @ 89.967s (closing_practice readable), frame_025 @ 97.177s (closing_practice hold end), frame_026 @ 98.767s (closing readable), frame_027 @ 100.977s (last frame)

### 12 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 17.843s (body sample), frame_005 @ 19.510s (body sample), frame_006 @ 21.977s (body sample), frame_007 @ 23.310s (body sample), frame_008 @ 26.567s (chapter readable), frame_010 @ 32.310s (body sample), frame_011 @ 33.843s (body sample), frame_012 @ 36.500s (chapter readable), frame_014 @ 41.443s (body sample), frame_015 @ 42.910s (body sample), frame_016 @ 46.377s (body sample), frame_017 @ 47.910s (body sample), frame_018 @ 50.500s (recap readable), frame_020 @ 59.300s (closing_practice readable), frame_021 @ 66.510s (closing_practice hold end), frame_022 @ 68.100s (closing readable), frame_023 @ 70.310s (last frame)

### 13 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 14.377s (body sample), frame_005 @ 21.043s (body sample), frame_006 @ 27.300s (chapter readable), frame_008 @ 33.843s (body sample), frame_009 @ 36.177s (body sample), frame_010 @ 40.633s (chapter readable), frame_012 @ 50.500s (chapter readable), frame_014 @ 55.443s (body sample), frame_015 @ 56.643s (body sample), frame_016 @ 64.710s (body sample), frame_017 @ 66.300s (recap readable), frame_019 @ 75.100s (closing_practice readable), frame_020 @ 82.310s (closing_practice hold end), frame_021 @ 83.900s (closing readable), frame_022 @ 86.110s (last frame)

### 14 — attempt_02

frame_000 @ 1.100s (opening readable), frame_002 @ 6.300s (chapter readable), frame_004 @ 19.243s (body sample), frame_005 @ 27.710s (body sample), frame_006 @ 29.243s (body sample), frame_007 @ 32.910s (body sample), frame_008 @ 40.577s (body sample), frame_009 @ 43.633s (chapter readable), frame_011 @ 53.177s (body sample), frame_012 @ 56.510s (body sample), frame_013 @ 63.633s (chapter readable), frame_015 @ 71.777s (body sample), frame_016 @ 80.100s (chapter readable), frame_018 @ 86.710s (body sample), frame_019 @ 90.577s (body sample), frame_020 @ 92.510s (body sample), frame_021 @ 101.043s (body sample), frame_022 @ 102.633s (recap readable), frame_024 @ 111.433s (closing_practice readable), frame_025 @ 118.643s (closing_practice hold end), frame_026 @ 120.233s (closing readable), frame_027 @ 122.443s (last frame)

Additional native-size inspection: preserved evidence files `mechanical_024177.png` and `mechanical_046710.png` in 01; `mechanical_061800.png` and `mechanical_087300.png` in 02; `mechanical_077843.png` in 03; `mechanical_080110.png` in 05; `mechanical_028777.png`, `mechanical_171500.png`, `mechanical_187300.png`, `mechanical_205500.png`, `mechanical_210500.png` in 07; the indexed 52.510 s frame in 10; `mechanical_079577.png` in 11; `mechanical_047500.png` in 13; and `mechanical_019243.png` in 14. The native 01 frame at 21.177 s and 05 semicircle frame at 74.510 s were also opened during selection. Files named `mechanical_*` preserve their timestamps independently of extractor reindexing.

No existing completed manual sample-review record was overwritten. The extractor’s generated `sample-review.json` remains a sampling record with inspection pending; this Markdown file is the reviewer’s evidence and judgment.

## Limits

Only the named video hashes and viewed frames are covered. Animation correctness between samples, narration wording and pronunciation, audio timing, listening quality, institutional logo approval and release approval are not covered. Native inspection was targeted; most body states were read from 427×240 thumbnails within contact sheets. This review does not establish the correctness of every unseen frame or guarantee learner comprehension. No lesson source was edited during the review.

## Fresh-render verification

The following entries verify fresh encoded outputs. The initial findings and hashes above are preserved. Fresh verification covers corrected lessons 01/05/07/14 and the revised inverse-function warning in 11.

Artifact root for all relative evidence paths: `/Users/xiaxiao/Desktop/video/math_video_project_clean/review_artifacts/course_coherence/2026-10-15/`.

### Verified 01 — attempt_03

Actual MP4 SHA-256: `2f3bd5dea64c7ae926e3ff55700a732c3ba97fce257cd60ff32c6496f94d314d`.

At **23.977 s** (`frame_005.png`, native inspection), only the numerals `2` and `1` are boxed under “constantes fixées”; `x` remains distinct. Finding 1 is resolved. Every structural readable card and all 12 stable body samples were reviewed from `cards_00.png`/`body_00.png`; the practice hold-end and last frame were also opened at native size. No new mathematical, orientation or readability issue was found in these samples.

Exact indexed samples inspected: frame_000.png @ 1.100s (opening readable), frame_002.png @ 6.300s (chapter readable), frame_004.png @ 12.510s (body sample), frame_005.png @ 23.977s (body sample), frame_006.png @ 28.177s (body sample), frame_007.png @ 30.967s (chapter readable), frame_009.png @ 37.577s (body sample), frame_010.png @ 39.443s (body sample), frame_011.png @ 43.177s (body sample), frame_012.png @ 46.510s (body sample), frame_013.png @ 49.300s (chapter readable), frame_015.png @ 55.843s (body sample), frame_016.png @ 58.777s (body sample), frame_017.png @ 64.310s (body sample), frame_018.png @ 68.043s (body sample), frame_019.png @ 73.967s (chapter readable), frame_021.png @ 84.043s (body sample), frame_022.png @ 87.433s (recap readable), frame_024.png @ 96.233s (closing_practice readable), frame_025.png @ 103.443s (closing_practice hold end), frame_026.png @ 105.033s (closing readable), frame_027.png @ 107.243s (last frame).

### Verified 05 — attempt_03

Actual MP4 SHA-256: `5468bb88ea378ed9c32595dfeb5bfd592e1d8d9da319c2c2e2914b129d18712d`.

At **80.110 s** (`frame_021.png`, native inspection), the conclusion is above the graph and no longer crosses the circle or test line. Finding 2 is resolved. Every structural readable card and all 12 stable body samples were reviewed from `cards_00.png`/`body_00.png`; the practice hold-end and last frame were also opened at native size. No new mathematical, orientation or readability issue was found in these samples.

Exact indexed samples inspected: frame_000.png @ 1.100s (opening readable), frame_002.png @ 6.300s (chapter readable), frame_004.png @ 12.843s (body sample), frame_005.png @ 19.443s (body sample), frame_006.png @ 22.510s (body sample), frame_007.png @ 26.233s (chapter readable), frame_009.png @ 30.910s (body sample), frame_010.png @ 36.577s (body sample), frame_011.png @ 39.777s (body sample), frame_012.png @ 44.433s (chapter readable), frame_014.png @ 50.443s (body sample), frame_015.png @ 56.710s (body sample), frame_016.png @ 59.243s (body sample), frame_017.png @ 64.100s (chapter readable), frame_019.png @ 69.777s (body sample), frame_020.png @ 74.510s (body sample), frame_021.png @ 80.110s (body sample), frame_022.png @ 82.367s (recap readable), frame_024.png @ 91.167s (closing_practice readable), frame_025.png @ 98.377s (closing_practice hold end), frame_026.png @ 99.967s (closing readable), frame_027.png @ 102.177s (last frame).

### Verified 11 — attempt_04

Actual MP4 SHA-256: `65e03aabf34e27bbd08b15e5f6c30ea92296362528348f375bb8f2f9b9ba2e96`.

The standalone warning at **85.977 s** (`frame_021.png`, native inspection) clearly states that the inverse-function notation does not mean `1/f`. It appears before the recap. The full stable reading hold is delimited by checkpoint times **81.067–86.067 s**; no listening claim is made. All structural readable cards and all 12 stable body samples were reviewed again, as were the practice-end and last frame at native size. The inverse-function formula, domain restriction and final task remain correct in the samples. No new sampled issue found.

Exact indexed samples inspected: frame_000.png @ 1.100s (opening readable), frame_002.png @ 6.300s (chapter readable), frame_004.png @ 11.977s (body sample), frame_005.png @ 16.310s (body sample), frame_006.png @ 19.577s (body sample), frame_007.png @ 27.843s (body sample), frame_008.png @ 29.433s (chapter readable), frame_010.png @ 38.110s (body sample), frame_011.png @ 41.910s (body sample), frame_012.png @ 44.500s (chapter readable), frame_014.png @ 55.243s (body sample), frame_015.png @ 60.710s (body sample), frame_016.png @ 63.300s (chapter readable), frame_018.png @ 72.243s (body sample), frame_019.png @ 74.843s (body sample), frame_020.png @ 79.577s (body sample), frame_021.png @ 85.977s (body sample), frame_022.png @ 87.567s (recap readable), frame_024.png @ 96.367s (closing_practice readable), frame_025.png @ 103.577s (closing_practice hold end), frame_026.png @ 105.167s (closing readable), frame_027.png @ 107.377s (last frame).

### Verified 07 — attempt_03

Actual MP4 SHA-256: `0b6cf756a45bc5f0846919da0c994906918c29902051d4c1a14f58bbc4aa92b0`.

Findings 3–5 are resolved in the actual encoded output. Native **28.777 s** (`mechanical_028777.png`) shows clearly readable axes and ticks over the lighter intersection. Native **205.500 s** (`mechanical_205500.png`) shows only the intended parabola and its vertex `(2,3)`. Native **210.500 s** (`mechanical_210500.png`) explicitly states `k > 0` for the horizontal scaling rule. All structural readable cards and all 11 stable body samples were reviewed again; the practice hold-end and final encoded sample were opened natively. No new sampled mathematical, orientation or readability defect was found.

Exact indexed samples inspected: frame_000.png @ 1.100s (opening readable), frame_002.png @ 6.300s (chapter readable), frame_004.png @ 13.910s (body sample), frame_005.png @ 28.777s (body sample), frame_006.png @ 36.300s (chapter readable), frame_008.png @ 59.377s (body sample), frame_009.png @ 75.977s (body sample), frame_010.png @ 95.500s (chapter readable), frame_012.png @ 104.110s (body sample), frame_013.png @ 115.577s (body sample), frame_014.png @ 126.510s (body sample), frame_015.png @ 133.633s (chapter readable), frame_017.png @ 148.243s (body sample), frame_018.png @ 171.243s (body sample), frame_019.png @ 193.243s (body sample), frame_020.png @ 203.710s (body sample), frame_021.png @ 213.767s (recap readable), frame_023.png @ 222.567s (closing_practice readable), frame_024.png @ 229.777s (closing_practice hold end), frame_025.png @ 231.367s (closing readable), frame_027.png @ 234.577s (last frame).

### Verified 14 — attempt_03

Actual MP4 SHA-256: `a5fa2823397d0cd401e8b38bc029aac9bd7a41aeb6cd29ad2470eaab72ddc978`.

Finding 6 is resolved. The opening formula and question appear above the plotted area at **17.510 s** (`frame_004.png`) and at the original finding timestamp **19.243 s** (`mechanical_019243.png`, native inspection); the graph no longer crosses the text. All structural readable cards and all 12 stable body samples were reviewed from `cards_00.png`/`body_00.png`. Native endpoint checks at **118.643 s** and **122.443 s** show the unanswered practice prompt and held final card. The sampled square completion, vertex and quadratic-formula conditions remain correct. No new sampled mathematical, orientation or readability defect was found.

Exact indexed samples inspected: frame_000.png @ 1.100s (opening readable), frame_002.png @ 6.300s (chapter readable), frame_004.png @ 17.510s (body sample), frame_005.png @ 27.710s (body sample), frame_006.png @ 29.243s (body sample), frame_007.png @ 32.910s (body sample), frame_008.png @ 40.577s (body sample), frame_009.png @ 43.633s (chapter readable), frame_011.png @ 53.177s (body sample), frame_012.png @ 56.510s (body sample), frame_013.png @ 63.633s (chapter readable), frame_015.png @ 71.777s (body sample), frame_016.png @ 80.100s (chapter readable), frame_018.png @ 86.710s (body sample), frame_019.png @ 90.577s (body sample), frame_020.png @ 92.510s (body sample), frame_021.png @ 101.043s (body sample), frame_022.png @ 102.633s (recap readable), frame_024.png @ 111.433s (closing_practice readable), frame_025.png @ 118.643s (closing_practice hold end), frame_026.png @ 120.233s (closing readable), frame_027.png @ 122.443s (last frame).

## Final disposition

All six confirmed initial findings are closed against the actual fresh MP4 hashes recorded above. Lesson 11’s restored inverse-versus-reciprocal warning was also verified in its fresh encoded output. The latest reviewed versions are attempt_03 for 01/05/07/09/10/14, attempt_04 for 11, and attempt_02 for 02/03/04/06/08/12/13. No remaining actionable defect was found in this sampled review of lessons 01–14. The full-motion, listening, institutional-approval and release limits stated above still apply.
