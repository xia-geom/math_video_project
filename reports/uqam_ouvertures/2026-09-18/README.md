# UQAM 20 s — post-merge audit and audio-first revision

**Audited main:** `111ce8d49930e44444ec654c79a082f19cd95abb`  
**Reviewed implementation:** `8ccf6e7250a1461a8bee151f21181c031a4bea06`  
**Draft PR:** [#6](https://github.com/xia-geom/math_video_project/pull/6)  
**Verified workflow:** [35295038727](https://github.com/xia-geom/math_video_project/actions/runs/35295038727)  
**Artifact:** `10527901481`

## Findings

1. The original four nominal beat durations already total 20 seconds. The rule `max(preferred_seconds, speech_seconds + .12)` independently extends long beats but never recovers unused time from other beats. For synthetic durations `[2,7,3,2]`, it produces 22.12 seconds despite only 14 seconds of audio. This is a demonstrated source issue, not a measurement of the user's Mac-local 22–24-second Azure attempts.
2. The committed photographs are 384×216 and 256×144. Their softness was previously attributed incorrectly to the supplied PDF. The PDF embeds images at 1387×640 and 2012×1128, allowing the same photo crops at 903×508 and 1112×625 without intermediate downsampling. A 1080p container does not make thumbnail content high-resolution.
3. Fresh render-time synthesis does not guarantee the same take on later renders. Original captions include visual holds, and voice begins before the new scene settles.
4. Whole-photo fades, four simultaneous destination labels and center placement obscure the strengths of the two-photo concept. Four midpoint frames do not cover transitions, subtitle variants or stale scene objects.

## Implemented

The local project pipeline now measures and preserves Azure clips first, then allocates a global frame budget. Exact audio bytes are cached by SSML/configuration/helper hash and verified on reuse. Rendering does not resynthesize. Impossible budgets fail before graphics and retain their audio plus per-beat diagnostics. There is no automatic take search, tempo filtering, cut-off final sentence or silent fallback.

The current voice selection remains MAI-Voice-2 at +2%, through unchanged `tools/tts.py`. Narration is shorter:

> À l’UQAM, les maths ouvrent des portes. Une majeure en maths ou statistique. Puis un certificat : communication, finance, économique ou informatique. Un bac en sciences. Plusieurs horizons.

The two-year full-time major framing remains on screen. Slides 21–23 remain the source of the major/certificate/B.Sc. Sciences pathway and the four exact domain names, including Économique. The photos still come only from page 1; page 7 supplies math.uqam.ca. There is no new admission, job or postgraduate guarantee.

The student background stays across the middle beats. Communication/Finance appear first, then Économique/Informatique. This is a visual midpoint transition, not certified word alignment. Text sits lower, the preview disclosure stays visible against both photographs, and the ending keeps at least a one-second margin after speech. Subtitles use audio intervals rather than whole visual holds.

The project README documents file responsibilities, image recovery, audio-only preflight and frozen-package reuse. The two other films, lessons, books and shared TTS file are unchanged. Azure CI is explicit/manual-only and failed requests cannot remain misleadingly marked ready.

## Native photos: recovered, not yet committed

The extraction tool was run twice on the original PDF and the recovered pixels matched the pinned hashes. The PDF SHA-256 is `9898b52281f5c6c1d2e1f5c18e7b6ad5e12dcb0cc84f4e992e6812a98de8d30a`.

| Photo | Old thumbnail | Recovered crop | Enlargement at 1920 px width |
|---|---:|---:|---:|
| Group at the board | 384×216 | 903×508 | 2.126× instead of 5× |
| UQAM building | 256×144 | 1112×625 | 1.727× instead of 7.5× |

Recovery crops native source pixels, without resizing, sharpening, generated details or face retouching. These crops still are not natively 1920×1080.

**Native PNG bytes are delivered in a separate repository-relative ZIP; they are not yet committed in PR #6.** Install the pack or run `restore_slide_photos.py --pdf ORIGINAL.pdf`, then explicitly stage `miscellaneous/bac_sciences_ouvertures_fr/assets/native/` on the review branch. Full narrated rendering requires these native assets; a silent CI composition preview may use the old thumbnails only with an explicit warning. Do not treat that CI output as approval of the recovered-photo rendering.

PNG SHA-256:
- students: `9ad17d7228ffb477dbc26ef219785c9c72e4e7295620d7084eabd19118020355`
- building: `f1e5f93c5393ff4e9d7156bbc84d53ae340f65378c4e7e238ad956afbd15ffab`

## What visual review caught

The first revision, `cfc1887`, passed 39 tests and its initial render checks, but inspection found an old certificate header retained on the end card after a subgroup animation. That preview is superseded.

Commit `8ccf6e7` explicitly cleans the outgoing scene family, reuses the original header during the pair switch, and asserts the identity of live text objects after each transition. A contrasting preview-label backing also fixes legibility over the whiteboard photograph. This correction was rendered again, not merely syntax-checked.

## Verified corrected result

- **39 tests passed**, zero failures/errors/skips; focused Ruff passed.
- Real Manim render: **1920×1080, 60 fps, exactly 20.000 seconds**; no audio stream.
- **24 encoded frames inspected**: settled scenes, both destination pairs, scene boundaries and ending, in clean and subtitled variants. No retained or overlapping text observed in the corrected samples; runtime live-scene assertions also passed.
- CI image tier: **legacy_thumbnail_preview_only**. Native extraction is verified separately; no native-photo Manim render was performed here.
- Azure workflow state: **not_requested**. No new real Azure synthesis or listening review was performed in this session. The user's Mac exports and rejected local takes were not accessible or modified.
- Separate smoke run `35295038615`: repository compilation passed, global lint failed, global render skipped. No check was disabled.

Clean preview SHA-256: `1b749811e4a0974272c125998499ae9d62b9d673d1095a1f45a7f3c3f4bb9f3d`  
Subtitled preview SHA-256: `db1e0c35b867c889068f46bbbd03f14a81cad3176c7d318f1341891915bd16ab`

## Local finishing sequence

Use the existing environment in a separate Git worktree to preserve unrelated local edits. Install/recover the native images first. Do not reset or clean the user's original working tree.

```bash
python -m pip install -r miscellaneous/bac_sciences_ouvertures_fr/requirements-assets.txt
python miscellaneous/bac_sciences_ouvertures_fr/restore_slide_photos.py \
  --pdf "/actual/path/Accueil Nouveaux-2026-Septembre.pdf"

python miscellaneous/bac_sciences_ouvertures_fr/build.py \
  --mode azure --quality qh --audio-only --output dist/uqam-audio-review

python miscellaneous/bac_sciences_ouvertures_fr/build.py \
  --mode azure --quality qh \
  --audio-package dist/uqam-audio-review/audio/audio.json
```

The extraction step is unnecessary when the supplied native-photo ZIP has already been installed. Existing nonempty output directories are refused. Keys stay in the environment. If the audio budget fails, inspect the retained take and timing_plan.json; shorten the particular text or explicitly approve a longer format, rather than repeatedly regenerating.

Full listening, field-pair synchronization, complete native-photo playback and editorial/institutional approval remain pending. PR #6 remains draft and unmerged; `release_ready` is false.
