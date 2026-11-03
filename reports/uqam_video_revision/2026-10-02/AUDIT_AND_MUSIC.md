# Two UQAM films — audit and music reviews

**2 October 2026.** Source checkout: `af03774` on
`codex/uqam-three-film-versioning`. Scope: the latest local 68.483-second maths
film and 29-second interdisciplinary film, plus a limited check of their existing
Instagram wrappers. The long programme presentation is a separate project.

## Findings, in priority order

| Finding | Evidence | Recommended next edit |
| --- | --- | --- |
| Both films briefly go blank between white cards | Maths approximately 19.25–19.35 s; sciences 15.75–15.90 s. Encoded frames show no readable content. Both renderers use sequential copy fades with an empty wait. | Keep a common heading visible or replace the white cards directly. |
| Sciences narration is quieter | Original decoded audio: maths −18.51 LUFS; sciences −23.55 LUFS, a 5.04 LU difference. | Match voice levels across films. **Addressed in the music review variants.** |
| Maths repeats a photo credit phrase | “atelier public, 2019” appears twice at approximately 6.2–14.2 s and 32.7–36.1 s. Both a filename-specific credit and `context=` supply it. | Keep one occurrence, retaining photographer and historical context. |
| Instagram layout underuses the screen | The landscape picture occupies 608 of 1920 vertical pixels. Small research-card details remain small. The “VOIX ET SOUS-TITRES” label and empty caption card persist after speech. | Prepare a native portrait composition and remove the administrative label. |
| Sciences has no visible destination in landscape | Final image is the logo; its Instagram wrapper adds `math.uqam.ca`. | Consider a short URL with the closing message. |
| Sciences documentation is stale | Historical material below the README notice still states 20 seconds, old narration/photos and certificate exclusions. | Clearly archive the obsolete contract and describe the active 29-second version. |

The visual findings remain present in these music variants: their video packets
are deliberately copied from the audited masters. These are music comparisons,
not newly approved picture masters.

## Improvements verified

- No photo shaking indicated in **350 frames sampled at 10 fps across seven
  stable photo holds**. The best alignment displacement was zero within a ±2
  pixel search on 150 × 150 grayscale regions. This is a bounded sample, not a
  check of every transition or every source pixel.
- Separate photo/text layouts have clear spacing in inspected stable frames.
- The discussion image shows people exchanging ideas around a mathematical
  workshop board, credited as a 2019 public workshop. It is intentionally reused
  in the maths film; it is not presented as a newly photographed class.
- The library image is brighter and clearer. Both films end with the official
  blue UQAM logo on white.
- The removed heading is absent and “Plusieurs portes” appears. CIRGET remains
  correctly spelled on screen; its spoken pronunciation requires listening.

Coverage: 55 existing maths checkpoints, 9 sciences checkpoints, 5 Instagram
snapshots and 29 new encoded frames. This was frame inspection and sampled
motion analysis, **not continuous viewing or listening**.

## Audio audit

| Measurement | Maths source | Sciences source |
| --- | ---: | ---: |
| Integrated loudness | −18.51 LUFS | −23.55 LUFS |
| True peak | −1.29 dBTP | −8.93 dBTP |
| Original narration ending | approximately 62.5 s | approximately 25.3 s |
| Remaining picture after narration | approximately 6 s | approximately 3.7 s |

The maths opening (0–5.496 s) passed the existing signal checks: no clipping,
zero first-12-ms peak, longest internal silence 0.36 s, and no sustained deep
pitch run. Both narration sections use the existing +2% rate in source. These
measurements **do not clear the previously reported strange sound or perceived
speed change**, nor do they establish natural pronunciation. Full listening
remains required.

## Music selection

Recommended comparison: **[Resolutions by Scott Buckley](https://www.scottbuckley.com.au/library/resolutions/)**.
The composer describes hopeful piano and strings with a later increase in
energy. This suggests a warm institutional tone; the fit is inferred from the
artist's description, not an audition of the recording. The current previews
use its opening, before the later energetic section.

Alternatives researched from the composer's official pages:

- [Growing Up](https://www.scottbuckley.com.au/library/growing-up/): a quieter,
  reflective solo-piano option.
- [A Kind Of Hope](https://www.scottbuckley.com.au/library/a-kind-of-hope/): piano,
  strings and atmospheric synth, with a more bittersweet character.

All three track pages offer CC BY 4.0 downloads. The [artist's usage terms](https://www.scottbuckley.com.au/library/using-this-music/)
permit commercial use with attribution and require YouTube credits in the
description. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) requires
credit, a license link and an indication of changes. Put the supplied credit
in the Instagram caption or video description. The artist also instructs users
not to register this music with audio fingerprinting services. Sources checked
2 October 2026; no account, purchase or subscription was used.

## Local music review variants

Directory: `dist/uqam_music_review_20261002/`

| Review file | Duration | Decoded loudness | Decoded true peak |
| --- | ---: | ---: | ---: |
| `uqam_math_68s_resolutions_music_review.mp4` | 68.483 s | −19.01 LUFS | −4.50 dBTP |
| `uqam_sciences_29s_resolutions_music_review.mp4` | 29.000 s | −19.01 LUFS | −4.59 dBTP |

Mix settings: narration target −19 LUFS; music excerpt target −37 LUFS;
0.75-second music entrance and 2-second exit fades; fixed gain, no time stretch
and no word-by-word ducking. The quiet music continues beneath the closing
picture. Maths voice gain is −0.49 dB after stereo conversion; sciences voice
gain is +4.39 dB after padding to the video duration. These are new AAC stereo
48 kHz/192 kbps tracks over the original 1920 × 1080, 60 fps H.264 picture.

The two SRT files were copied without timing changes. Each video has a manifest
with input/output hashes and the exact filter graph. `CREDITS.txt` contains the
ready-to-copy music credit; MP4 metadata also contains attribution and changes.
The downloaded MP3, generated videos and inspection images stay outside Git.
Existing voice-only masters and Instagram derivatives remain separate versions.

Reproduction uses `scripts/mix_uqam_music_review.py`, supplying the original
video, the downloaded `Resolutions_Scott_Buckley.mp3`, and a fresh output path.
The utility refuses to overwrite an existing output and validates video packet
identity, duration, encoded true peak and complete decoding. It does not invoke
Azure, the Manim renderer, Drive copying or release publication. The preset
requires the reviewed music file's SHA-256, preventing accidental use of a
different track with the Resolutions attribution.

### Artifact identity

| Artifact | SHA-256 |
| --- | --- |
| Maths input | `f6430c4319c6eadf89fac54402c4f676cb52ca2dde0bbe30671e5ab6b3d03c79` |
| Sciences input | `7e5ec67ce6a636f124e1f8a98c1040c70bb1a84c1028f1bfd3eea822611d5da8` |
| Music download | `d61702c3b378662a3dd07d6207d9ac2cfedd405a4746c273db890afa644c7015` |
| Maths music review | `2ee593309d368d427da2ebc707a0330c0a7c5d01e9e206e7a23233c92d5e4993` |
| Sciences music review | `7ad67b5f09e92a928109696b286aa568f5f08c72ec40910f6d0e6e69ab5d6d32` |

## Validation and remaining gates

- Python syntax check passed for the new mixer.
- Target tests: **60 passed** (`test_uqam_ouvertures.py`, `test_uqam_promo.py`,
  `test_uqam_two_films.py`); one existing `pkg_resources` deprecation warning.
- Both actual FFmpeg mixes completed. Full decoding passed; compressed video
  packet hashes match their inputs; duration and encoded peak checks passed.
- An independent check found all video packet timing and sizes unchanged. Six
  sampled speech waveform comparisons at 8 kHz found zero timing offset, with
  correlations of 0.988–0.998. These samples support preserved synchronization;
  they are not a listening review.
- No new Manim render or speech synthesis was performed for these audio variants.
- Music taste, intelligibility and opening-noise review still need listening.
  Continuous visual review and institutional approval remain separate gates.
- Photo permissions and programme claims were not newly cleared by this audit.
  Neither preview is marked release-ready or published to a platform.

Local evidence: `audit_frames/photo_stability.json`,
`audit_frames/math_research_keyframes.jpg`,
`audit_frames/science_degree_logo.jpg`, and
`analysis/math_hook_signal_audit.json`, under the review directory above.
