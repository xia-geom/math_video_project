# AGENT.md — Math Video Production Guide

Rules for coding agents creating or editing videos in this repository. See `README.md` for installation, environment variables, scene inventory, and detailed TTS utility documentation.

## 1. Goal and technology

Create rigorous, accessible French mathematics videos in a minimalist whiteboard style.

- Use **Manim Community**, not ManimGL.
- Use the existing environment and dependencies.
- Avoid new dependencies unless necessary.
- Reuse shared utilities instead of duplicating them.
- Reference quality: `12_pythagore_par_les_aires_fr` and `04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py`.

## 2. Default working mode

Use **fast iteration mode** unless the user explicitly asks for a final, production-ready, publishable, or fully validated scene.

In fast iteration mode:

- implement the requested change immediately;
- inspect only the target file and directly related shared utilities;
- make reasonable assumptions instead of asking unnecessary questions;
- do not research alternative approaches unless the current approach is blocked;
- do not refactor unrelated code;
- do not add narration, captions, subtitles, or render scripts unless requested;
- run a syntax check after editing;
- run at most one low-quality preview when the change affects layout or runtime behaviour;
- do not run medium- or high-quality renders;
- do not watch or analyze the complete rendered video unless requested.

For straightforward tasks, begin editing without first presenting a detailed plan. Use a plan only when the change spans multiple files, changes architecture, or contains significant ambiguity.

## 3. Repository conventions

- Production-ready scenes: `scenes/<category_slug>/<topic_slug>/`.
- Exploratory work: `experiments/<topic_slug>/`.
- Directories and files: `snake_case_fr`.
- Scene classes: `PascalCaseFR`.
- Preserve existing scene class names unless explicitly asked to rename them.
- Do not commit generated MP4, WAV, or cache files.

Standard path:

```text
scenes/<category_slug>/<topic_slug>/<topic_slug>_scene.py
```

## 4. Visual style

Set defaults at module level:

```python
config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)
```

Use:

- white background and black primary ink;
- one restrained accent color, usually `BLUE_D` or `BLUE`;
- stroke widths around 2–4;
- light fills, normally opacity ≤ 0.15;
- no gradients, drop shadows, or decorative effects.

Typical sizes:

- title: 44–50;
- headings, captions, and body text: 28–34;
- featured mathematics: about 1.4–1.9 times normal scale.

Keep text at least 0.5 units from frame edges. Prevent overlaps, keep captions away from the main diagram, and remove stale objects between acts.

For geometry, inverse functions, or reflection across `y=x`, the two axes must use the same visual unit scale. Equal numerical distances must appear equal on screen.

## 5. Pedagogical design

Each scene should have one clear learning objective. Prefer this structure:

1. motivating question or misconception;
2. visual model;
3. mathematical formulation;
4. worked example or dynamic test;
5. conclusion or common mistake.

Every animation must communicate an idea. Avoid decorative motion. Connect representations whenever useful: formula and graph, input and output, coordinates and position, or symbolic change and visible movement.

Use highlights selectively and preserve enough stable context for students to understand what changed.

## 6. Animation and pacing

Narration is the main pacing reference for narrated scenes.

- Do not introduce global pacing wrappers such as `play_paced()`.
- Do not multiply every `run_time` by a global factor.
- Adjust timing only where the visual action requires it.
- Avoid important animations shorter than about 0.4 seconds; brief transitions may be shorter when readable.
- Every `wait()` must be intentional.
- End with at least `self.wait(1.0)`.

To slow an explanation, prefer a spoken pause, bookmark, or stable visual hold rather than slowing the entire scene.

## 7. Voiceover and captions

Only add or modify voiceover, SSML, captions, bookmarks, or subtitles when requested, or when an existing narrated scene needs synchronization changes.

For narrated scenes, use `VoiceoverScene`, `AzureService`, and the shared helpers in `tools/tts.py`.

```python
from tools.tts import VOICE_ID, ssml, char, chars, strip_ssml, PLUS

self.set_speech_service(AzureService(voice=VOICE_ID))
```

Rules:

- do not hardcode voices or recreate SSML helpers;
- captions contain plain French text, never SSML tags;
- SSML belongs only in spoken text;
- use bookmarks for concept-level synchronization;
- use shared pronunciation helpers such as `char`, `chars`, and `PLUS`;
- do not use `add_voiceover_ssml()` or `voiceover(ssml=...)`.

## 8. Editing rules

- Make focused changes; do not rewrite unrelated code.
- Preserve the established style of the scene being edited.
- Do not delete assets or generated files unless asked.
- Keep helpers small; move them project-wide only when genuinely reusable.
- Remove unused imports and dead code.
- Comment non-obvious formula, sign, limit, or convention checks.
- In fast iteration mode, distinguish between **syntax checked** and **render tested**.
- Do not claim that a scene rendered successfully unless a render was actually run.
- Full visual review is required only for production-ready delivery.

## 9. Essential commands

```bash
# Syntax check
python -m py_compile scenes/<category>/<topic>/<topic>_scene.py

# Fast preview
./scripts/render.sh scenes/<category>/<topic>/<topic>_scene.py <SceneClass>

# Final 1080p render
manim -pqh scenes/<category>/<topic>/<topic>_scene.py <SceneClass> -r 1920,1080
```

Use the syntax check by default. Use the preview only when useful. Use the final render only for production-ready delivery or when explicitly requested.

## 10. Validation levels

### Fast iteration — default

- [ ] Requested change is implemented.
- [ ] Unrelated code was not modified.
- [ ] Python syntax check passes.
- [ ] Mathematics introduced or changed has been checked.
- [ ] A low-quality render was run only when useful.

### Production-ready delivery

In addition to the fast checks:

- [ ] A low-quality preview renders without errors.
- [ ] Axes, geometry, and proportions are correct.
- [ ] Text, captions, and diagrams do not overlap.
- [ ] No stale objects remain unintentionally.
- [ ] Important actions are readable at normal speed.
- [ ] Narration, bookmarks, captions, and visible actions agree.
- [ ] The complete preview has been watched.
- [ ] A final-quality render succeeds when requested.
- [ ] Generated media and cache files are not committed.

## 11. Automatic Git checkpoint policy

At the end of every task that changes files:

1. Run the relevant fast validation.
2. Run `git status --short` and review the diff.
3. Stage all current changes with `git add -A`.
4. Create a commit with a concise description of the task.
5. Push the current branch to the configured remote.

Unfinished work may be committed with a `WIP:` prefix.

Do not commit files excluded by `.gitignore`.
Never force-push or rewrite existing history.
If validation fails, create a WIP checkpoint commit rather than leaving valuable work only in the working directory.
If push fails, keep the local commit and report the failure.

## 12. Response style

After completing a coding task, respond concisely with:

1. files changed;
2. main implementation result;
3. validation actually performed;
4. any remaining limitation.

Do not provide a long implementation narrative unless requested. When the user asks for complete code, prioritize producing or editing the complete file over explaining how it could be written.

Whenever a response mentions an edited or created Python file, render it as a clickable Markdown link with its absolute local path, for example:

```markdown
Updated [operations_fonctions_scene.py](/Users/xiaxiao/Desktop/Projects/math_video_project/scenes/fonctions_et_graphiques_fr/operations_fonctions_fr/operations_fonctions_scene.py).
```

Whenever a response mentions a rendered video output, render the video path as a clickable Markdown link with its absolute local path, for example:

```markdown
[OperationsFonctionsFR.mp4](/Users/xiaxiao/Desktop/Projects/math_video_project/dist/OperationsFonctionsFR/OperationsFonctionsFR.mp4)
```
