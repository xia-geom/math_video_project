# Active-course cleanup and lesson 06 review

The resumed roadmap work removes **4,018 Ruff diagnostics**, leaving **3,150**
in the unchanged historical/separate-project scopes listed below. All **73
catalogue scene sources pass Ruff 0.17.0**. The course-numbering workflow now
lints the paths returned by the unified catalogue on every applicable run.
The global smoke lint check remains enabled and blocking.

This batch follows `a07e6915f0b65967de7891285b19eea84296ffc7`. Earlier tests,
renders and reports remain evidence of that source. The shared-helper and SSML
edits invalidate their current-render signatures; successful earlier CI is not
relabelled as validation of this batch. Exact local results and evidence hashes
are recorded in [the companion record](resumed_implementation.json).

## Lint repair and preservation

Seventeen teaching scenes now import their required Manim names explicitly;
NumPy is imported directly where it was previously obtained through Manim.
Import ordering, unused imports and literal-only f-strings were cleaned across
the original 43 course scenes. Six unread local assignments were removed after
checking that their expressions do not alter visible objects, geometry or
timing. Mathematics, narration strings, bookmarks, public scene classes and
catalogue identities are preserved. This follows
[Ruff's explicit-import guidance](https://docs.astral.sh/ruff/rules/undefined-local-with-import-star-usage/).

The independent review covered the 42 scenes outside the separately reviewed
lesson 06 layout change. It verified **1,338 retained import bindings**, **206
builtin lookups**, unchanged mathematical/narration literals and the side
effects of the removed expressions. No dynamic module-namespace dependency or
actionable regression was found in that scope. Unknown external consumers of
incidental scene-module exports are not exhaustively audited.

Ten active teaching-tool/test files had 13 diagnostics repaired. A separate
five-file SSML/consolidation batch repaired eight more. No lint rule, scanner
allowance, production voice or test scope was disabled.

The remaining global diagnostics are explicitly outside these repairs:

| Remaining scope | Diagnostics |
| --- | ---: |
| Retired implementations and experiments | 3,074 |
| Separate promotion sources, scripts and tests | 54 |
| Separate visual-identity scene | 21 |
| Historical-fingerprint-bound tokenizer test | 1 |
| Total | 3,150 |

The last item is an import-order finding in
`tools/ssml/tests/test_tokenizer.py`. Changing its bytes invalidates 169 source
fingerprint proofs in 11 tracked reports under the current directory-scan
contract. Those reports and both tokenizer files remain unchanged. A different
historical-proof design would require its own implementation and security
regressions; no blanket exception was added to conceal the finding.

Actual Gitleaks 8.30.1 directory scans of the current tracked snapshot and the
SSML proposal found 338 detector matches, all proved to be exact source
fingerprints, with zero unresolved findings. The applied bytes were rechecked
against those actual report/line bindings. This is a bounded source scan, not
complete privacy clearance or a new audit of every public GitHub surface.

## Lesson 06: readable square-model changes

Inspection of retained Linux construction images showed that the growing square
model kept the center of its narrow first case. Later labels approached the
left frame edge; the final comparison condition also nearly spanned the frame.
The scene now reserves the width of the widest model, uses one center for all
four cases, and wraps the condition into two coherent lines at its original
font size.

The first fresh encoded preview exposed an additional problem: transforming
entire square models interpolated unrelated letters and scattered cells between
cases. Each replacement now fades the old case out for 0.4 seconds, then fades
the new case in for 0.4 seconds. Each bookmark interval retains its original
0.8-second transition budget. The mathematical values, narration, font sizes
and total preview duration of **84.066667 seconds** are unchanged.

The second preview has 44 construction endpoints with zero overlap candidates.
All ten targeted border-label/condition observations fit. Thirty-three remaining
margin states concern the five unchanged headings; they are not cleared by this
pilot. Eleven encoded samples were inspected, including all three case changes;
an independent reviewer inspected seven of those samples. The new samples show
legible individual cases and the wrapped condition without the observed glyph
interpolation. These checks do not establish complete motion or listening.

The original 916 margin-candidate states were also grouped for review. Samples
of lesson 27 remained visible without observed collision; lesson 36 has visibly
tight left-hand derivation labels and remains a candidate for a later bounded
correction. No course-wide visual approval is inferred from this triage.

## Validation and evidence freshness

These suites overlap and must not be summed into a single test count:

- Independent scene source/math/narration checks: **222 tests and 1,192 subtests**
  passed, with zero failures, errors or skips.
- Teaching-tool and layout contracts: **83 tests** passed.
- SSML, shared TTS and source-fingerprint/detector checks: **61 tests and 18
  subtests** passed, including the real detector integration.
- Workflow syntax, dependency and complete workflow-policy checks: **56 tests**
  passed; all 15 workflows passed the policy validator.
- Lesson 06 geometry and actual transition-call checks: **3 tests and 7
  subtests** passed. The one final low-quality preview and its sampled encoded
  frames are recorded separately from these tests.
- Syntax validation and scoped Ruff passed for all 73 catalogue scene files.

The current ledger is regenerated from the previous ledger so historical
findings and observations remain recoverable. Old source-dependent artifacts
must remain stale after this cleanup. The new silent lesson 06 preview supplies
current technical evidence only; full visual/narrated acceptance is not granted.
New hosted checks are reported on the PR after the source commit, without
repeated report-only pushes that restart the render workflows.

The book sources and verified PDFs are unchanged. Curriculum documentation now
states explicitly that complex numbers are implemented in the book while a
dedicated video remains an optional, unallocated extension. Actual historical
listening decisions, the explicitly gated pronunciation samples and separate
release approval remain pending.
