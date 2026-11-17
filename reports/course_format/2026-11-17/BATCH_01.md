# Course format — first MAT0339 batch

## Scope

Adapt the 14 lessons numbered 44–57 in the first batch of the
[MAT0339 plan](../../error_capsules/2026-10-30/PLAN.md).
Reviewed upstream base: `b39584fc79727ae340239f29b889998e4d3e28c5`.

## Changes

- Use the shared title/objective opening, three or four chapter cards, and closing.
- End with three takeaways, a previously corrected example to retry independently,
  and the shared faculty signature.
- Use black teaching ink, with labels, dashed lines, light fills, and filled/open
  markers to preserve distinctions previously carried by color.
- Preserve the worked mathematics, self-checks, and six-second response pauses.
  Keep the general formulas in lessons 53 and 54 before their self-checks.
- Route shared-card narration through the existing lesson SSML profile and plain
  captions; do not change the voice or synthesize new audio.
- Update affected lesson notes, the teaching standard, and regression coverage.

The shared source format now covers the original 43 lessons and these 14
additions. Lessons 58–73 remain outside this migration. Existing media exports
are not replaced or certified by this source change.

## Validation

| Check | Result |
| --- | --- |
| Teaching revision, chapters, and timing tests | 198 passed |
| Changed Python files | 16 syntax-checked; all configured Ruff rules passed |
| Catalogue and generated indexes | 73 lessons validated; indexes current |
| Whitespace check | `git diff --check` passed |
| Dependency consistency | Reviewed Python 3.13 lock installed; `pip check` passed |

The full-repository Ruff check still reports 3,150 findings in unchanged files;
none are in the changed Python files. No unrelated checks were disabled.

## Preview review

Rendered one complete silent low-quality preview of lesson 48, selected because
its population diagram has the largest visual change in this batch.

- Video: 854 × 480, 15 fps, 111.87 seconds; no audio stream.
- Reviewed 17 sampled encoded frames covering the opening, chapter transition,
  population markers, conditional-probability table, self-check, and closing.
- Text, formulas, marker distinctions, and sampled layouts are readable, with no
  clipping or overlap observed in these frames.
- SHA-256: `ebbb437491af8a2cb8bb11f2e3ddc4969104ce6053873d550da3450db190a4b4`.

The preview and intermediate render files remain ignored local review artifacts.
This was a source-format adaptation: full motion review, narrated listening,
caption/audio synchronization approval, and final-quality exports remain pending.
