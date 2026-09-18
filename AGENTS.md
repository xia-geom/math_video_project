# Agent instructions — Math Video Project

This is the single root instruction file for coding agents. Use [README.md](README.md)
for installation and commands, and [ARCHITECTURE.md](ARCHITECTURE.md) to locate files.
Read the target project's README when it has one; do not load every audit report.

## Work on the requested project

Create rigorous French mathematics videos with Manim Community, not ManimGL.
Reuse the existing environment and helpers; add dependencies only when needed.
Preserve scene class names and existing paths. New lesson sources follow
`scenes/<category_slug>/<topic_slug>/<topic_slug>_scene.py`, with French snake-case
folders and PascalCase scene classes.

Teaching lessons follow [docs/TEACHING_STANDARD.md](docs/TEACHING_STANDARD.md).
Use [curriculum/programme_principal_fr.yaml](curriculum/programme_principal_fr.yaml)
for their order and delivery destinations, not the numbers in folder names.
The domain/image and Pythagorean lessons are existing visual references.

UQAM promotions are separate sibling projects under `miscellaneous/`.
Read [their collection guide](miscellaneous/README.md) and the target README.
Keep each film's renderer, dependencies, narration profile, sources and output
identity separate. Do not apply the teaching style or voice rate indiscriminately
to promotions. Books and reference documents are separate from video sources.

## Default: a focused, fast iteration

Implement the requested change without unrelated refactors or a lengthy plan.
Inspect the target files and directly related helpers. Use a plan for changes
that span projects or alter architecture; resolve consequential ambiguity before
changing scope.

Check Python syntax and the mathematics affected. When layout or runtime changes,
run at most one low-quality preview in fast mode. Do not run medium/high-quality
or whole-series renders, or add narration, captions or render scripts, unless
requested. Existing narrated scenes may need synchronization adjustments.

Use the target project's commands from its README. For a basic syntax check:

```bash
python -m py_compile path/to/changed_scene.py
```

Some render commands also copy outputs or route them to Drive. Choose the command
that matches the requested scope; a source edit is not an instruction to publish.

## Make teaching scenes readable

Use the established whiteboard style: white background, black primary ink, one
restrained blue accent, light fills and no decorative effects. Typical title
sizes are 44–50 points; body text is normally 28–34 points. Leave at least 0.5
scene units around frame edges and a separate area for captions.

Keep one learning objective per scene. Prefer a motivating question, visual
model, mathematical statement, worked example and conclusion. Every animation
should explain something; keep useful context but clear stale objects between
cases. Use selective highlights rather than competing emphasis.

Shorten prose or use symbols with a readable legend. Enlarge a box, move its
contents or split a page before reducing type size. Formulas must remain inside
their intended boxes. Use `tools/teaching_layout.py` where appropriate; its panel
and page guards reject oversized content rather than silently shrinking it.

For geometry and reflections, preserve equal visual units on both axes. Adjust
local animation timing, not every `run_time` through a global multiplier or new
`play_paced()` wrapper. Important actions should normally last at least 0.4 seconds.
Every pause must have a purpose; finish with at least one second of stable content.

## Narration, captions and the opening

Teaching narration uses `TeachingAzureService` from `tools/teaching_voiceover.py`
and the shared settings and SSML helpers in `tools/tts.py`. Keep the current MAI
teaching profile, natural complete thoughts and concept-level synchronization.
Do not hardcode voices, duplicate SSML helpers or add a second audio-speed factor.
Follow the detailed voice and timing contract in `docs/TEACHING_STANDARD.md`.

Use `char`, `chars`, `PLUS` and other shared pronunciation helpers where needed.
Captions are plain French, never SSML. Pass SSML through `voiceover(text=...)`,
not `voiceover(ssml=...)` or `add_voiceover_ssml()`.

Use `tools.branding.play_uqam_intro(self)` once before teaching content. Reuse
the official logo and shared timing; do not add a second scene-local opening.
Keep silent previews clearly distinct from actual Azure narration. Never silently
substitute voices or services. Do not put secrets in code, reports or Git.

## Validate, save and report

Keep changes focused. Preserve assets, historical reports and generated files
unless their removal is requested. Remove dead code introduced by the change;
comment non-obvious mathematical conventions, signs or limits. Put genuinely
reusable helpers in `tools/`, not another copy in each scene.

Fast validation means syntax, affected mathematics and relevant lightweight tests.
For requested production-ready delivery, additionally review the full preview,
geometry, overlaps, all transitions, narration/caption timing and complete audio;
then validate the requested final-quality export. A passing test is not evidence
that listening, visual approval or institutional approval occurred. Do not disable
unrelated failing checks to make a report look successful.

Review the working tree and diff, stage the task's changes, commit and push the
working branch. Respect `.gitignore`; do not add generated MP4/WAV/cache files or
unrelated work. Never force-push or rewrite history. Save unfinished work as a
clearly labelled WIP checkpoint and report failed validation or a failed push.
Do not merge or publish as an incidental part of a source-edit task.

Respond with the result, changed locations, checks actually run and remaining
limits. Link edited files and outputs using verified local paths or real repository
links. Distinguish syntax-checked, rendered, visually reviewed and listened-to.
