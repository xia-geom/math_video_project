# UQAM video revision — execution plan

Baseline: `0c4556ab07e8ae700c1556148374a83c0808cef1`.
Branch: `fix/uqam-video-audit-2026-09-14`.
User instruction: implement the September 14 audit and test on GitHub.

## 1. Content and preservation

Create a V4-only, source-attributed 2026–2027 course dataset, checked against the official guide's four autumn/five-course grids (pages 9, 13, 18, 22). Correct MAT2411 and its geometry association; correct the statistics semester placement. Preserve the shared historical `program_data.py`, V2/V3 sources and all existing masters. Record codes, alternatives, blocks, guide date and pages. Pin the downloaded PDF and derived cover; produce a before/after data report. Public scope remains the baccalaureate, not an exhaustive department presentation.

## 2. Image and narrative

Use the already-inventoried Président-Kennedy photograph in the first part of the long V4 opening, within its existing 15 seconds. Keep the mathematical illustrations, explicit semester labels and 283-second authored timeline. Use explicit crop focus and readable Photo UQAM credit. Show the authentic research-hub photo briefly at the start of the conclusion before the institutional card. Account for photo transitions in the render cache. Keep the chosen fonts and distinct audio/music profiles.

For the short film, split Montréal, research and conclusion into actual speech units so transitions follow speech completion, not guessed word-duration estimates. Extend the useful view of the research photo, clarify first-year practical work and faculty-level support claims, and avoid presenting event photos as ordinary bachelor classes or testimonials.

## 3. Technical corrections

Use one effective parent/child render configuration; inventory every new dependency and per-photo displayed credits. Darken small gray copy and protect credits on photographs. Strengthen subtitle syntax, length and reading-speed reporting. Record actual semantic scene boundaries for review frames. Keep visual inspection, listening, automated validation and institutional authorization as separate statuses; never infer approval from a passing test.

## 4. GitHub execution and evidence

Implement changes on this branch. Run compilation, focused lint, the existing relevant test suites and new regression tests in GitHub Actions. Render native-size V4 review frames and short-film visual-only previews without needing speech credentials. Export shot/transition frames, media metadata, test logs, source hashes and an explicit validation-status JSON as Actions artifacts. Run real speech synthesis/full narrated renders only if the existing authorized Speech credentials are available. A silent or synthetic-clock test is NOT a narration synchronization or listening pass.

No forced pushes, no automatic merge, no publication, no overwrite of historical masters, and no fabricated approval. Finish with a draft PR and the exact CI results, artifacts and remaining review requirements.

## Completion gates

- [ ] Source-attributed V4 data and report committed.
- [ ] Both video implementations revised.
- [ ] Regression tests and Actions workflow committed.
- [ ] Focused automated checks executed successfully on GitHub.
- [ ] Review media and transition evidence produced.
- [ ] Real narrated export tested (or explicitly blocked with reason).
- [ ] Final viewing and listening recorded (otherwise pending).
- [ ] Draft PR opened; main remains unchanged.
