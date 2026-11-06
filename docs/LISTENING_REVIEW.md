# Review historical narration flags

The October 15 offline screen found 86 quiet intervals in 64 utterances across
31 lessons. These are listening candidates, not confirmed defects. The report
hash is recorded in
[the offline revision record](../reports/narration_quality/2026-10-15/offline_revision.json).
Its historical audio predates later wording changes.

[The queue command](../scripts/review_narration_flags.py) verifies that report,
copies selected original audio and complete videos unchanged, and creates a
self-contained local HTML page. It synthesizes nothing and publishes nothing.
Prepare a new package under ignored `review_artifacts/`:

```sh
python scripts/review_narration_flags.py prepare \
  --report /path/to/original/course_screen_v2/report.json \
  --lessons variables_et_polynomes,fonction_reciproque,annulation_dans_les_fractions \
  --output review_artifacts/listening_review/selected-historical-lessons
```

The selected batch contains 12 flags in 9 unchanged utterance clips and three
complete historical videos. Open its `index.html` locally. Each flag has its
utterance player, transcript, interval and a button to seek the complete video
to the corresponding context. No playback begins automatically. Package files
are made read-only and an existing queue is never overwritten.

## Record actual review

Enter your reviewer name. Listen to the utterance and its flagged interval, use
the full video for context, then enter a reason and choose `intentional_pause`,
`audio_defect` or `needs_more_review`. Confirm listening yourself. Leave untouched
flags blank; partial batches are allowed and remain visibly incomplete.

The optional complete-video section has its own disposition, reason, complete
listening confirmation and complete viewing confirmation. Flag decisions cannot
fill it. A complete review still concerns the exact historical file; it does not
approve current source, later replacement audio or institutional publication.

Export the entered decisions as JSON and save them inside the queue's ignored
artifact area. The page does not send data anywhere or save decisions automatically.
Validate the export before relying on it:

```sh
python scripts/review_narration_flags.py validate \
  --queue review_artifacts/listening_review/selected-historical-lessons \
  --decisions review_artifacts/listening_review/selected-historical-lessons/listening-decisions.json
```

## Identity and limits

Stable flag IDs bind the report digest, stable lesson ID, video/audio digests,
voiceover index, utterance interval and video interval. The validator rejects
unknown or duplicate IDs, changed bindings, missing reasons and nonboolean
listening confirmations. It rechecks both original and copied media, both report
copies and the generated HTML. Missing or replaced evidence makes the decisions
unusable; prepare a new queue for replacement media instead of editing old hashes.

`validated_bindings` means the records match the unchanged historical evidence.
It does not authenticate a reviewer, prove that someone listened, or update any
course-ledger acceptance check. Those human attestations remain separate. The
validator never manufactures full playback, listening or release approval.

The local package contains original source locations needed for revalidation.
Keep the package, exported reviewer decisions and media under ignored
`review_artifacts/`; do not commit or upload them. Committed code/tests use
synthetic fixtures. Moving or deleting original media intentionally blocks
validation even if the copied playback file remains available.
