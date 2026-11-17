# Course format — remaining MAT0339 lessons

## Scope

Continue [PR #37](https://github.com/xia-geom/math_video_project/pull/37) from
commit `c6717b0df8751c3e3a2afe036c7095319ec8b3b1`, after the
[first-batch adaptation](BATCH_01.md).

This continuation covers the 16 remaining MAT0339 lessons, currently numbered
58–73. The tests select their explicit stable identities, independently of
display order. Together with the original 43 lessons and first 14 additions,
all 73 catalogue teaching sources now use the shared format.

## Changes

- Add the shared title/objective opening, three or four chapter cards, and
  closing with three takeaways, a corrected example to retry, and the signature.
- Use black teaching ink, neutral fills, labels, dashed lines, and outlined
  moving markers. Update spoken visual references to match the new diagrams.
  Lesson 63 retains its red/blue probability categories with explicit R/B labels.
- Preserve original body formulas, teaching order, hypotheses, and each
  six-second self-check pause.
- Keep unique material from old endings before the self-checks: the finite
  equiprobability rule in 62, zero-vector case in 68, and bounded-region theorem
  in 71. Other removed ending formulas repeat substantive pages.
- Extend shared opening/closing checks to all 73 lessons and actual-size card
  construction checks to all 30 MAT0339 additions. Update affected lesson notes
  and the course standard.

## Validation

| Check | Result |
| --- | --- |
| Teaching revision, chapters, and timing tests | 231 passed |
| Lesson 62 final recap wording | Both targeted checks passed |
| Changed Python files | 17 syntax-checked; all configured Ruff rules passed |
| Catalogue and generated indexes | 73 lessons validated; indexes current |
| Source preservation review | Body formulas, assumptions, chapter boundaries and self-checks reviewed across all 16 lessons |
| Whitespace and dependencies | `git diff --check` and `pip check` passed |

Repository-wide Ruff still reports 3,150 findings in unchanged files, with none
in the changed Python files. No checks were disabled.

The previous PR commit's teaching workflow passed. Its separate promotional
[UQAM revision job](https://github.com/xia-geom/math_video_project/actions/runs/44152457070/job/134284175657)
failed during photo refresh, before compilation or testing: one download
returned HTTP 429 and two locally retouched assets were missing. That workflow
and its promotional sources are outside this change.

## Preview review

Rendered one complete silent low-quality preview of lesson 71 to inspect the
moving dashed level line, outlined marker on the optimal segment, and retained
bounded-region explanation.

- Video: 854 × 480, 15 fps, 89.60 seconds; no audio stream.
- Reviewed 20 sampled encoded frames covering the opening, chapter cards,
  diagrams at intermediate and final positions, general theorem, self-check,
  answer, recap, practice and final card.
- No clipping or overlapping text was observed in these samples. The dashed
  line remains distinguishable while approaching the solid boundary, and the
  moving marker remains visible along the optimal segment.
- SHA-256: `d9c792dfe49e1cf89347baa4431f57c751701b5cb87f0c2527ed4c8e0972855c`.

Generated media remain ignored local review artifacts. This source adaptation
does not replace old exports. Full motion review, narrated listening,
caption/audio synchronization approval, and final-quality exports remain
pending; no narration was synthesized and no media were published.
