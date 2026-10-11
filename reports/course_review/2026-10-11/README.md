# October 11 acceptance follow-up

The 43 current lesson sources match the prior review's frozen input maps. The
matching local videos are 1920×1080 at 60 fps and are silent. Source integration
review covered all 43 lessons; this does not establish full playback or listening.

Visual completion remains **0/43**. Narrated completion remains **0/43**.
The prior ledger contains 83 independently closed narrow findings, 44 awaiting
audiovisual verification and two explicitly deferred minor cosmetic findings.
Historical October 10 records remain unchanged.

Current generated evidence: [review table](current/REVIEW.md), [CSV](current/review.csv),
[ledger](current/review.json), [43-artifact revalidation](artifact_revalidation.json),
[scope classifications](finding_scopes.json) and [validation record](validation.json).

## Acceptance fixes

Audio findings now require actual complete current listening/timing records from
an independent reviewer. A dated, definition-bound scope overlay preserves the
83 valid narrow visual closures and explicitly retains the mixed mathematical
and spoken requirements. It does not add any whole-video passes.

The narrated runner preserves observed request, voice, SSML, bookmark, pacing and
audio evidence before cache cleanup. Its capture-tool hashes are rechecked after
rendering and on import. Cached MAI aggregates retain their actual request data;
implicit voice/pacing environment changes are rejected before synthesis. The
older teaching preflight now has a two-process construction limit.

## Integration and prerequisites

The math checkpoint was isolated on top of `main` at
`f2b126980702c0c3c364dc5ae8640559628b6f51`. The isolated checkpoint is
`047cb41287e6446f6eb5199c0fd896871716cfdb`; its 62 changed paths exclude the
unrelated book and UQAM work inherited by the older branch.

The existing local Azure environment file was located in the original sibling
project. Both supported credential aliases are present, consistent and compatible
with the current MAI voice's region requirement. Values were not displayed,
copied, committed or transferred to GitHub. The clean checkout does not discover
this sibling file automatically. A deliberate launcher can load its explicit path
into a child process without copying it into the repository.

GitHub reported no configured repository Actions secrets or environments at this
check. The existing narrated workflow requires explicit manual selection on
reviewed `main`; pull-request checks remain credential-free. No paid narration,
main merge or publication was performed during this follow-up.

## Acceptance capability

An actual audio-input capability probe returned: `audio content omitted because
you do not support audio input`. Available frame inspection and source analysis
cannot establish listening, pronunciation, complete motion or audiovisual timing.
A reviewer able to play and hear the complete artifacts is still required.

## Historical clarification

Lesson 37's current scene does not reference `voix_off_fr.wav`; that route was
already absent on the inspected `main`. The earlier worker note that described
a preserved selectable prerecorded route was not supported by the source.
Existing historical audio lacks matching current provenance and is not approved
as a replacement narrated artifact.

## Validation boundary

Final focused validation passed **92 tests and 64 subtests**, including the actual
offline Azure/TeachingAzure cache and VoiceoverTracker path. Cloud synthesis and
scene encoding were stubbed in that regression; it is not a new narrated video.
Independent reviewers confirmed the closure/import gates, all 83 retained proof
records, cached-speech capture and tooling-fingerprint enforcement. All 43 prior
silent videos were rehashed and probed against unchanged complete input maps.

The initial integration passed 27 review/workflow-policy tests and 19 subtests.
Independent source checks passed focused correctness lint, syntax for all 115
tracked smoke targets and the local runtime's dependency check.

Full repository Ruff remains failing: 7,408 findings on `main`, 7,496 on the
isolated math checkpoint. The difference is 105 added and 15 removed F405 uses
of the established Manim wildcard-import pattern, plus two removed I001 findings.
These results do not constitute a passing overall CI gate. No unrelated checks
were disabled or unrelated projects changed to hide that backlog.

## Public audit follow-up

The first hosted scan flagged 570 historical and 328 current occurrences of two
source SHA-256 values because their JSON keys contain `tokenizer`. Every historical
match was verified against the named source blob at its recorded commit. A narrow
rule-specific allowance now accepts only those exact key/digest lines in eight
reviewed path suffixes, including absolute or nested copies; default secret rules
and adjacent-key detection remain active. Historical reports were not rewritten.

Pinned Gitleaks 8.30.1 rescanned history with zero remaining findings. Nine real
scanner cases verify the exception and retained synthetic-key detection. Integrated
validation passed 14 tests and five subtests, plus focused Ruff. CI runs the scanner
regression after its checksum-verified installation. See the sanitized
[validation record](public_audit_validation.json); this is not full public clearance
or audiovisual acceptance.
