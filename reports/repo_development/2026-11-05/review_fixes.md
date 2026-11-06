# Follow-up to the eight-commit review

5 November 2026. Starting HEAD: `905665d4d4a20a3440a86b070f37cf47e0a9917a`.
Reviewed unpublished range: `f84fda6..905665d` (eight commits). This record covers
the four engineering corrections identified by that review. The
[roadmap](../../../docs/DEVELOPMENT_ROADMAP.md) retains subsequent work and the
separate, unresolved MAT0339 editorial feedback.

## Corrections

1. **Source snapshots.** The audit archives tracked eligible sources with their
   working-tree edits. Unrelated untracked files are excluded; required untracked
   inputs, private paths and symlink components block the audit. A shared guard
   runs before catalogue parsing, scene hashing and dependency reads. Failures
   record a blocked status before tests or rendering. Exclusive archive creation
   preserves an existing attempt. Source archives still exclude rendered media
   and fonts; they are not complete runtime bundles.
2. **Secret-detector provenance matches.** The public audit distinguishes raw
   matches, source fingerprints proven from bytes and remaining findings. Only
   exact hashes in recognized JSON provenance maps qualify. Historical checks
   use the finding's exact commit. Mismatches, missing files, symlinks, other
   detector rules and external GitHub surfaces remain blocking. Real-detector
   tests retain a synthetic credential in the same report and in deleted history.
3. **Finding closure.** `acceptance_passed` must be the Boolean `true`. Strings,
   numbers, missing/null values and containers cannot close a finding. Existing
   reviewer, replacement-media and input-freshness requirements remain enforced.
4. **Book verification.** Ordinary MAT0339 checks use the standard library and
   book sources. Live video-catalogue checks remain mandatory for relevant map
   changes through the explicit `make verify-video-map` target. All four existing
   live-catalogue tests remain present; an additional subprocess test rejects
   teaching-runtime imports from the ordinary suite.

## Validation

The final combined regression command used the existing review environment:

```sh
GITLEAKS_BIN=/path/to/verified/gitleaks .venv-review/bin/python -B -m pytest -p no:cacheprovider \
  tests/test_public_audit.py tests/test_public_audit_gitleaks.py \
  tests/test_public_fingerprints.py tests/test_public_workflow_policy.py \
  tests/test_course_source_snapshot.py tests/test_private_data_guard.py \
  tests/test_course_review.py tests/test_course_catalog.py \
  tests/test_course_workflow_syntax.py -q
```

Result: **116 passed, 55 subtests passed**. This includes the real pinned
Gitleaks 8.30.1 integration tests, rather than their optional skip path.

| Check | Result |
| --- | --- |
| Source snapshot regressions | Dirty tracked files retained; untracked/private files excluded or blocked; file and parent symlinks rejected; existing archive preserved. Real catalogue loading cannot read unsafe source/manifest fixtures before preflight. |
| Current catalogue | Guarded catalogue/dependency reads accepted all 43 lessons; generated indexes are current without regeneration. |
| Book-only checks | 60 tests passed with site packages disabled. `make verify` also passed in a disposable environment without pip or PyYAML: archives intact, 17 chapters and 126 aligned sections. |
| Book integration | Explicit map verification passed for 17 chapters and 43 videos; all 5 integration tests passed. |
| Syntax and lint | All 11 changed Python files parsed. Full scoped Ruff passed for catalogue, scanner and new tests; E/F/W checks passed for legacy audit/review modules with the repository's E501 exclusion. |
| Privacy prevention | Current-index path guard passed. This is a narrow filename check, not history or content clearance. |
| Independent review | Scanner proof and closure behavior reviewed separately; independent snapshot review exposed an early catalogue read, which received the shared pre-read guard and real-loader regressions. Reproduction then showed zero unsafe reads; the expanded catalogue/review suite passed 149 tests and 859 subtests. |

An ad-hoc E/F/W lint invocation re-enabled E501 and reported long lines. The
follow-up retained the repository's existing E501 exclusion; no lint policy or
unrelated baseline check was disabled. Repository-wide lint was not repeated.

## Git-history detector results

The cached Gitleaks 8.30.1 macOS ARM64 archive was checked against its official
release checksum, and the executable was checked against that archive. Default
detector rules were used. Raw reports stayed in temporary directories and were
removed; no matched values are retained here.

A scan of all **765 regular files in the prepared Git index** also passed:
242 raw matches, 242 verified source fingerprints and zero remaining findings.
The first local run exposed a macOS temporary-path alias mismatch. Canonicalizing
the scan target aligned the detector and verifier roots; a new real-detector test
confirms that scanning through a root alias still preserves credential findings.
Checks against symlinks within the scanned tree remain unchanged.

| History scope at starting HEAD | Raw matches | Automatically verified source fingerprints | Remaining |
| --- | ---: | ---: | ---: |
| Eight unpublished commits, `f84fda6..HEAD` | 242 | 242 | 0 |
| All commits reachable from `HEAD` | 242 | 242 | 0 |
| All locally available Git refs | 858 | 856 | 2 |

The two remaining all-ref matches are in
`reports/error_capsules/2026-11-02/verification.json`, lines 817–818, at commit
`08b0a4b64f8a93f47378dbbb6b656dfa45acd2d9`. That commit is reachable from
`origin/main` but is not an ancestor of this branch's starting HEAD. Independent
inspection proved that both entries equal the hashes of their named regular
tracked Python sources. Their map is named `current_input_sha256`; this change
recognizes only `inputs` and `input_sha256`, so the automated all-ref scan
continues to report them. No historical file or allowlist was rewritten to clear
these separate findings.

## Scope and remaining limits

The expanded regression suite exercised selected real geometry helpers and
animation ownership without encoding video. No full lesson construction audit,
encoded render, paid narration, listening, complete playback, new book PDF
compilation or graphical inspection was performed. Book mathematics
and chapter order were inspected for the user's question but were not changed;
the October sources do not fully address that feedback. Technical test success
does not establish pedagogical or institutional approval.

This batch did not inspect GitHub discussions, workflow logs, downloadable
artifact payloads, binary-media rights, external forks, unreachable history or
repository administration settings. Existing unrelated UQAM working files and
photos remain outside the checkpoint. No Drive copy, release, history rewrite
or remote publication was performed.
