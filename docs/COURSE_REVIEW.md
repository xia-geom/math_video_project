# Repeatable course production review

The catalogue owns the lesson list and stable identities. The review tools track
evidence for that list; they do not define a second curriculum or publish videos.
Use `docs/TEACHING_STANDARD.md` for the teaching and narration contracts.

## Parallel ownership and safe execution

Assign disjoint stable lesson IDs to three workers. A coordinator owns shared
helpers, runners, catalogue, workflows, aggregate evidence and Git operations.
Review three lessons per worker per batch. A different worker verifies each fix.
Workers send shared-code proposals to the coordinator instead of editing those
files concurrently. Freeze scene/data inputs during rendering; shared changes
wait until the render batch finishes. The runners reject changed render inputs.

Only the coordinator launches render commands. At most two Manim subprocesses
may run across the entire team, not two per worker. The isolated runners accept
`--jobs 1` or `--jobs 2` (default 2); do not run several queues at once. Each
attempt requires a new output directory. Run scene construction in subprocesses
because the endpoint inspector temporarily modifies Manim methods globally.
Do not use `render.sh` for this review: it has production/Drive routing effects.

## Commands

Use the project's reviewed Manim environment and put its executables on `PATH`.
The examples below use the ignored `.venv-review` established for the October 10
review, with Manim 0.19.0 and manim-voiceover 0.3.7. Record `pip freeze` beside
the output. Silent review does not need credentials.

```sh
export PATH="$PWD/.venv-review/bin:$PATH"
export PYTHONPATH="$PWD"
export MANIM_DISABLE_VOICEOVER=1
python tools/course_catalog.py check

# Shared checks once, then selected lesson construction and fresh silent videos.
python scripts/course_audit.py --numbers fonctions_rationnelles,operations_sur_les_matrices \
  --jobs 2 --output review_artifacts/course_review/run-001

# Subsequent batches may reference the separately saved test results.
# --skip-tests does not mark those tests passed in this batch.
python scripts/course_audit.py --numbers du_cercle_unite_a_la_fonction_sinus \
  --skip-tests --quality qh --jobs 1 --all-construction-states \
  --output review_artifacts/course_review/run-002

# Build/update the current record; include every retained evidence root.
python scripts/course_review.py --artifact-root review_artifacts/course_review/run-001 \
  --artifact-root review_artifacts/course_review/run-002 \
  --worker-report reports/course_review/2026-10-10/worker_a.json \
  --worker-report reports/course_review/2026-10-10/worker_b.json \
  --worker-report reports/course_review/2026-10-10/worker_c.json \
  --worker-report reports/course_review/2026-10-10/worker_root.json \
  --output review_artifacts/course_review/current
```

`--no-render` only measures construction. `selected_render_checks_passed` and
`automated_course_checks_passed` are automated results, never audiovisual approval.
The ten-addition containment runner keeps its specific authored-depth checks;
they are not imposed on older lessons. Existing CLI defaults and scene classes
remain usable.

## Evidence records

`review.json` is the machine-readable ledger; `review.csv` and `REVIEW.md` are
generated views. Keep generated media in ignored output directories and commit
only inspected, concise dated reports. Old reports remain unchanged.

Each worker report identifies its author, lesson IDs, exact scene and input
hashes, source-review result, evidence and findings. A finding has an ID,
severity, source location or timestamp, description, expected behavior,
correction and status. A source fix is `awaiting_verification`, not closed.
Use `affected_checks` to distinguish a strictly audio finding from a visual
defect; unclassified findings conservatively block both kinds of completion.

The checks are `source_math`, `technical`, `displayed_math`, `readability`,
`motion`, `narration`, `timing` and `final_resolution`. States are `not_checked`,
`blocked`, `failed`, `passed` and `stale`. The source-mathematics check cannot
certify the displayed/spoken explanation. Historical artifacts with matching
recorded hashes but incomplete dependency coverage remain useful inspection
evidence, labelled `recorded_inputs_match`; they cannot certify current source.

Encoded reuse also requires the recorded versions of Manim, manim-voiceover,
NumPy, SciPy and Pillow to match the review runtime. The ledger retains a hash
of that version map alongside the local dependency-file hashes. Missing or
different runtime records cannot become current technical evidence. Run the
reconciler in the recorded review environment; this version fingerprint does
not claim to hash every operating-system library or installed package byte.

Explicit audiovisual review records can be supplied with `--reviews path.json`.
That file has a `reviews` list; each item contains `lesson_id`, a `checks` mapping
and optional `closures`. Passed checks require `reviewer`, `checked_at`,
`evidence`, the current `input_signature` and (for media checks) `video_sha256`.
Whole-video checks require `coverage: complete`; use `full_playback` for motion,
`full_listening` for narration, `full_av_review` for timing and
`display_size_review` for final legibility. These fields record work actually
performed; do not generate them merely because a render or frame sample passed.

A closure also names `finding_id` and `acceptance_passed: true`. Its reviewer
must differ from the author, and its input/video hashes must match the selected
replacement artifact. Reviewers are responsible for checking that their cited
frames, timestamps and inspection manifests substantiate the claimed correction.
The reconciler verifies the current video bytes and source inputs; it requires
nonempty review evidence but does not independently authenticate every cited
frame file or an optional `evidence_sha256` mapping. Retain those frame hashes
for audit and check them when reusing the review's supporting files.
Changing inputs or selecting another movie invalidates
the corresponding passes and reopens artifact findings. Explicitly deferred
minor cosmetic findings require a named deferrer; major defects remain blocking.
Reimporting an older review retains it in `review_history` as stale; it cannot
reapprove a replacement video or stop reconciliation of the current evidence.
Worker files cannot import `closed` findings directly; only independent review
records can close them. Explicit source states remain distinct during import.

Audio-affected findings additionally require the independent, complete current
`narration`/`timing` checks that their scope names. Their reviewer must differ from
the fixer. A frame-only closure cannot stand in for those checks. Missing or
malformed scopes conservatively require both audio checks. Persisted closures
are revalidated, and insufficient historical audio closures remain rejected
history instead of becoming acceptance.

A dated `finding_scopes` list in a `--reviews` row can classify a legacy finding
without changing its historical report. Each entry names `finding_id`, explicit
`affected_checks`, `reviewer`, `checked_at`, `evidence`, `rationale`, and a
`finding_definition_sha256` calculated by `finding_definition_signature`.
The definition fingerprint covers ID, severity, description, expected behavior,
change summary and closure condition. All scopes are applied before closures,
regardless of file order; they cannot remove existing explicit requirements.
The classification survives reimport of an unchanged worker definition. The
[October 11 overlay](../reports/course_review/2026-10-11/finding_scopes.json)
classifies the previously unscoped findings and retains Sigma's listening
requirement. It creates no playback or listening passes.

## Narration and completion

Complete visual correction before scheduling needed narration. Preserve existing
voices and use the existing explicit manual narration workflow on reviewed
`main`; no credentials go to pull-request tests. A narration-driven visual edit
reopens visual verification. Full playback/listening and final-size inspection
remain pending until actually performed by a reviewer with those capabilities.
The manual teaching-review workflow's `numbers` input defaults to its existing
two rebuilt lessons (39,40); clearing it explicitly selects all 43. Its
`narrated_review` switch remains false by default. The general runner's
`--narration` option never substitutes silent audio when credentials are absent.

The narrated runner preserves a credential-free `narration/provenance.json`,
referenced speech clips and a copy of the encoded audio stream before deleting
successful Manim cache output. It records returned SSML/configuration, cached
aggregate requests, measured bookmarks, tracker timing and executed pacing
calls. These are synthesis and timing evidence, not perceived-voice or listening
approval. Requested voice/pacing overrides, audio dependencies, capture-tool
hashes, source/video identity and retained audio hashes are checked during reuse.
Unrecorded voice/pacing changes after launch are rejected before synthesis.
Old narrated output without that provenance cannot become current evidence.
Legacy silent previews retain the explicit limitation that their environment
was not attested; their recorded source/runtime/video identities can still
support narrow inspection. Do not invent a missing launch environment.

Visual completion requires the source, technical, displayed-mathematics,
readability, motion and final-resolution checks, plus resolved findings.
Narrated completion additionally requires full listening and audiovisual timing.
Publication approval remains separate and `release_ready` stays false.
