# Maths capsule revision — 4 October 2026

## Delivered

- `uqam_math_birds_20261004_120750.mp4`: 1920 × 1080, 60 fps, 66.116667 s.
- `uqam_math_birds_instagram_20261004_120750.mp4`: 1080 × 1920, 30 fps, 66.116 s.
- Narration TXT matched exactly against delivered source subtitles; credits,
  music provenance, photo retouches, voice/mix excerpts and review manifests accompany both.
- 30 delivery files copied to the local Drive collection's maths project under
  `versions/2026-10-04/20261004_120750`, with SHA-256 verification. Its history and
  collection index were updated. Older versions remain; the other two projects
  were verified unchanged.

## Changes

Opening: the supplied Président-Kennedy/formula photograph. Library: locally
retouched red bag. Campus: locally retouched trucks/cars. Community: selected
smiling students on steps, within a bounded panel. The nighttime 256 × 144 image
was omitted. Original photos remain intact; original decoded pixels outside
object masks remain identical. See [photo prompts and recipe](PHOTO_EDITS.md).

The conclusion now says **« De multiples accès à la recherche. Au cœur de
Montréal ! »**. Screen text was shortened and all credit overlays obey the
disabled-credit setting, including the previous unconditional upper-right
overlay. Full attribution remains in sidecars and source metadata. Birds and
MAI-Voice-2 at uniform +6% are retained.

LaCIM was newly synthesized using a French pronunciation alias, preserving the
written acronym and the existing voice/rate. Cache audio differs from the prior
version; duration changed from 3.096 to 2.904 seconds. Old cache/master and
reconstructed mix correlations did not localize a separate numerical mixing
fault. The new source/master and mix reconstruction correlate above 0.999.
Checks found no clipping, nonfinite samples or AAC packet gap above 1 ms in the
review excerpt. These measurements do **not** establish that the reported
audible defect is resolved; actual listening remains pending. Before/after
artifacts are retained under `dist/uqam_revision_20261004/audio_review/`.

## Verification performed

- **49 targeted tests passed**: promo, two-film safeguards, edited-asset lineage,
  music mixer and Instagram packaging. Syntax and diff-whitespace checks passed.
- **Real Azure/Manim HD render** completed using Manim 0.19.0 and Azure SDK
  1.51.2; reviewed frames preceded the explicit builder visual gate.
- **Visual review:** all 48 raw QA frames, 12 final landscape frames and six
  Instagram frames inspected. Text and pictures are separated; no credit
  overlays or problematic sampled white transitions remain.
- Five encoded photo holds passed the stability comparison. Mean channel
  differences were below 0.55/255; minor codec variation is not camera movement.
- Both final exports fully decode. The landscape mix retains video packet
  identity. Mix true peak is −4.34 dBTP, integrated loudness −19.37 LUFS.
- Instagram PCM comparison: equal decoded sample count, correlation 0.998525,
  RMS ratio 0.996440, with the same narration/music timing.

An initial broad test collection in the short-film runtime lacked MoviePy.
An optional collection attempt in the separate main runtime was interrupted
after stalling during imports. These were not counted as passing, and no checks
were disabled. The first render attempt lacked PyYAML; its existing installed
package was reused through a task-local dependency path, without changing the
Manim/Azure versions. The temporary runtime symlink was removed after rendering.

## Remaining review boundaries

Full listening on headphones/phone and institutional approval are pending.
Previously recorded music/photo distribution conditions are retained without
inventing new clearance. An individual photographer for the FSPD steps photo
was not identified; its source institution and exact image URL are supplied.

Generated media were excluded from the Git checkpoint. Fresh-checkout rendering
needs the separately delivered reviewed derivative PNGs; the fetcher refuses
to replace them with unedited originals or overwrite them with `--force`.
