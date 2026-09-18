# Teaching-video revision — implementation and evidence

Date: 18 September 2026 UTC (17 September in Montréal).  
Repository: `xia-geom/math_video_project`. PR: #5.  
Branch: `fix/teaching-layout-voice-intro`.  
Starting main: `111ce8d49930e44444ec654c79a082f19cd95abb`.  
Reviewed teaching implementation after the last graph correction: `ef4f6ce3393d85a85ce4339a846c20b82bef8b70`.

## Result and remaining limits

The requested source revisions are implemented. Two rebuilt common-error lessons have real silent layout previews. The teaching voice and single-logo opening have been standardized in all 33 manifest-listed lessons. Actual Azure narration has **not** been regenerated in this review: the GitHub job has neither a Speech key nor a Speech region. No listening approval, release approval or merge is implied.

The final workflow is read-only, runs against the exact checked-out commit, and no longer applies or pushes migrations. The migration scripts in `scripts/teaching_revision/` are historical change tools, not render-time dependencies. Promotional videos, books, and existing source assets have not been rewritten by this teaching revision.

## User feedback addressed

### 02 — Root of a product

Replaced the prose-heavy sign table with mathematical signs, a zero case, check marks and crosses. A single readable legend defines a check as “defined in the reals”; it does **not** mean that the product identity has been proved. Rows appear sequentially.

Retained the nonnegative-factor conditions, the numerical working example, the negative-factor counterexample, the explicitly labelled complex-principal-root exception, and the proof using nonnegativity and equal squares. The table's mixed-sign and zero/negative rows also apply with exchanged factors, as explained aloud.

### 03 — Equality of functions

Rebuilt the lesson as separate pages: different formulas defining the same function, equal images without equal functions, differing domains, restrictions, differing codomains, and the final criterion. Removed accumulating cards and annotations from previous cases. Function declarations and formulas remain inside expanding panels.

The course's convention that the declared codomain is part of a function is explicitly retained. It has not been silently replaced with a different set-theoretic convention.

### Earlier lessons — targeted layout corrections

| Lesson | Correction |
|---|---|
| 01 Variables and polynomials | Separated the polynomial formula from the graph axis label. |
| 02 Inequalities | Moved annotations below their expressions; shortened and enlarged the conclusion panel. |
| 04 Domain and image | Hid the function-machine formula while the input token passes through it, then restored it. |
| 06 Graph properties | Cleared old vertex/minimum annotations before new point labels; moved a label and enlarged summary panels. |
| 08 Function operations | Separated graph labels, put computed results in their own area, and split/refitted reflection-value annotations. |
| 12 Root multiplicity | Separated the equation, axis label and caption regions. The final correction tightens the product-plot window and guide extents while preserving both roots and equal axis units. |
| 13 Completing the square | Repositioned the area diagram and split a long formula over two lines. |
| 15 Counting principle | Shortened the recap and displayed product/sum conclusions sequentially rather than side by side. |
| 16 Permutations and combinations | Removed stale choice notes; enlarged rule rows; separated definitions, recap and final rule in time. |
| Common-error 04 Extraneous solutions | Separated number-line, output and sign annotations. |
| Geometry 16 Pythagorean theorem | Removed the second, scene-local UQAM opening. |

This is a measured correction pass, not a claim that every earlier lesson has been completely redesigned or that all older small text has been eliminated.

## Shared production contracts

`tools/teaching_layout.py` adds panels with minimum, expandable dimensions. It does not scale down their contents to force a fit. A panel/page too large for the available region raises an error requiring simplification or another page. The two rebuilt lessons use this contract; arbitrary legacy boxes are not automatically certified by it.

`tools/teaching_voiceover.py` uses the repository's existing Azure pipeline and `tools/tts.py`. The existing MAI-Voice-2 profile at the existing -3% teaching rate is now the default. Neutral style and the selected voice locale are preserved; additional post-synthesis `global_speed` multipliers have been removed. Promotion-specific rate overrides and the selectable prerecorded Sigma track remain separate.

The two rebuilt scripts use complete spoken thoughts and conversational transitions. This is an authored change, not a verified claim about how ungenerated speech sounds. MAI passages with bookmarks use measured PCM-fragment boundaries and a tracker-compatible MP3. These are explicitly labelled authored anchors, not recognized word timestamps. A unit test exercises the real upstream wrapper and tracker with deterministic audio fixtures; it is not a cloud-synthesis test. Listening across joins remains necessary.

`tools/branding.py` provides one official-logo opening before lesson content: centered logo at width 4.0 on white, 0.4 s fade-in, 0.5 s hold, 0.4 s fade-out and 0.2 s padding. Duplicate calls and missing assets fail explicitly. All 33 manifest entries have one shared intro call; the standalone identity animation is separate.

The maintained reference is [docs/TEACHING_STANDARD.md](../../../docs/TEACHING_STANDARD.md). Root README, AGENT.md and ARCHITECTURE.md point to or describe it.

## Verification actually performed

### Broad review

[Run 35297547718](https://github.com/xia-geom/math_video_project/actions/runs/35297547718) tested implementation commit `3ca1dd08f7c642e376ef18d31f1fdfa33b5e600a`; artifact `10529185673` is `teaching-review-35297547718`.

- 46 unit/contract tests passed. This includes all 33 manifest entries' narration-adapter and single-intro contracts.
- Python compilation and focused correctness lint passed. The focused selection is not a claim that repository-wide style lint passes.
- All 25 selected scenes constructed successfully: curriculum positions 1–17, geometry at curriculum positions 25–26, and all six common-error scenes.
- 1,012 distinct stable play/wait endpoint states were recorded. No text-to-text overlap candidate or physical frame-clipping candidate remained under this detector's thresholds.
- The initial audit had 34 text-overlap candidates across the comparable selection; its first polynomial-scene construction failed before producing states, so it is not a fully identical before/after denominator.
- The rebuilt root-product preview is 47.4 s; function-equality preview is 43.733333 s. Both are real 854 × 480, 15 fps silent layout previews. Their durations are **not** the final narrated lesson durations.

**Important:** 785 repeated safe-margin candidate states remain in the broad audit, primarily in legacy scenes. A stricter preferred inset is different from the physical frame boundary. The two rebuilt error lessons have zero such margin candidates. These warnings were retained rather than hidden. No conclusion about every moving frame, all graph/text contacts, or overall cognitive load follows from zero text-overlap candidates.

### Last graph correction

[Run 35298372757](https://github.com/xia-geom/math_video_project/actions/runs/35298372757) tested `ef4f6ce3393d85a85ce4339a846c20b82bef8b70`; artifact `10528174666` is `teaching-p12-review-35298372757`. All 46 contracts passed again. All 37 stable states of the corrected multiplicity lesson constructed successfully, with zero text-overlap candidates. The product graph/caption frame was visually inspected after the correction; the curve no longer touches the bottom explanatory caption. This supplements the earlier broad review without pretending all 25 scenes changed again.

### Visual inspection and integrity

The retained stable-state images of both rebuilt lessons were inspected, including the complete symbolic table and equality criterion. Encoded opening and lesson checkpoints were also produced. This is checkpoint review, not complete real-time viewing with narration. Output hashes are in [validation.json](validation.json); the two preview files were rehashed when retrieved.

## Release blockers and remaining review

1. Actual Azure generation and complete listening are pending; GitHub Speech credentials are unavailable. A green conditional step that prints “blocked” is not a generated voiceover.
2. Final narrated timing, pronunciation, joins, captions and the complete in-between animation sequences need review before release.
3. Older safe-margin/small-text warnings remain for a broader editorial pass. The panel guard only certifies code paths that use it.
4. The separate repository-wide `smoke` lint failure remains. No lint workflow has been disabled to hide it.

No new rendered media or font files are committed to source Git. Review artifacts have limited retention; the report and evidence identifiers remain in Git. The branch is proposed in PR #5 and is not automatically merged or published.
