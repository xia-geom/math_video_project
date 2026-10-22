# Both formats and spoken-copy update — 22 October 2026

This follow-up supersedes the pending synthesis status in the earlier
[Instagram repair report](REPORT.md). Four local review MP4s were delivered,
with source images, earlier exports and the three UQAM projects kept separate.

## Completed changes

- **General mathematics promotion:** both landscape and Instagram contain the
  earlier localized pre-LaCIM noise repair and a new “Au cœur de Montréal.” take.
  The new take uses the existing MAI-Voice-2 voice at +6%, with a period instead
  of an exclamation mark. Its naturalness remains a listening judgment. The
  landscape picture stream is unchanged, including its printed exclamation
  mark; the updated source uses a period for subsequent fresh renders.
  Instagram narration subtitles are absent; original titles and centre names
  remain. Duration: 66.083333 seconds (portrait container: 66.083).
- **Interdisciplinary openings:** a new same-voice take at +2% says “Ce parcours
  mène à un baccalauréat en sciences par cumul.” Both formats use it, and the
  Instagram captions match. The landscape has its original scene text without
  added narration captions. Pictures and duration remain unchanged at 29 seconds.

The existing local Azure configuration was located and used without exposing
or copying its credentials. Two short takes were synthesized through the Azure
Speech SDK using `tools/tts.py` for the voice, configuration, output format and
SSML envelope. A first attempt importing the Manim adapter stalled before any
synthesis and was interrupted; it did not generate an extra take.

## Timing and audio checks

Montréal occupies 56.399333–57.932333 seconds. Only its last 0.315 seconds of
near-silence were removed (−84.78 dBFS RMS, −59.20 dBFS peak after gain matching).
There is about 0.563 seconds between the measured speech activity end and the
cut. The original following CTA samples and timing are unchanged, as is all
other narration PCM relative to the earlier LaCIM-repaired WAV.

The degree phrase occupies 18.171333–22.55 seconds. Its final 0.205333 seconds
of near-silence were removed (−85.52 dBFS RMS, −70.47 dBFS peak). No speed change
or voiced-sample truncation was indicated by the numeric checks. All other
narration PCM, picture timestamps and the music stem remain unchanged.
These silence measurements support the edit boundaries; they are not listening.

An initial science reconstruction revealed a 3.0103 dB routing loss. The source
voice master is stereo with the mono-WAV level in each channel; default mono
upmixing attenuated each channel. Explicit unit-gain channel duplication restores
the original routing before the existing +3.7 dB voice gain. Outside the edited
phrase, fitted mix gain differs by +0.01524 dB, with correlation 0.999774; remaining
residual reflects original AAC and PCM extraction. The initial lower-level
exports were archived locally and were not copied to Drive.

| Final format | Integrated loudness | True peak |
| --- | ---: | ---: |
| Mathematics landscape | −19.52 LUFS | −3.85 dBTP |
| Mathematics Instagram | −19.54 LUFS | −3.77 dBTP |
| Openings landscape | −19.58 LUFS | −4.71 dBTP |
| Openings Instagram | −19.60 LUFS | −4.76 dBTP |

Original music timing, gains and attribution are retained. Numeric peaks do not
indicate clipping. No complete listening or institutional approval is claimed.

## Verification

- **Source:** 36 tests passed (`test_uqam_ouvertures.py` and
  `test_uqam_instagram.py`); changed Python source and test syntax checked;
  `git diff --check` passed. The broader run including `test_uqam_promo.py`
  stalled during dependency import and was interrupted after 425.72 seconds,
  before any tests ran. It is not counted as passed. No test was disabled.
- **Actual media:** all four MP4s exported and fully decoded. Landscape is
  1920×1080 at 60 fps; Instagram is 1080×1920 at 30 fps; AAC stereo at 48 kHz.
  All 3,965 mathematics picture packets/timestamps and 1,740 openings frames
  are preserved in the landscape intermediates; final landscape streams are
  copied. Portrait pictures are fitted without cropping.
- **Visual:** inspected the final science caption at 19.2 seconds and the
  continuation at 21.4 seconds, the mathematics portrait CIRGET card at 19.2,
  and landscape Montréal card at 56.9. The science video payload is identical
  before/after its audio-level correction; the final corrected file's 19.2-second
  frame was also inspected. This is sampled inspection, not continuous playback.
- **Voice evidence:** `voice_revision/degree_mene.json` and
  `voice_revision/montreal_neutral.json` retain text, voice/rate, exact SSML,
  completion status and hashes. Replacement boundaries and preservation checks
  are in `science_revision/audio_replacement_provenance.json` and
  `math_revision/montreal_replacement_manifest.json`.

All generated evidence remains under `dist/uqam_revision_20261022/`, outside Git.

## Delivered files

Build identifier `20261022_102838` uses America/Toronto time.

| File | Duration (s) | SHA-256 |
| --- | ---: | --- |
| `uqam_math_birds_20261022_102838.mp4` | 66.083333 | `6763f42db0e242fbca4fcac764233bb5d6cc2e6f3703ee5d4c71868f81c40b77` |
| `uqam_math_birds_instagram_20261022_102838.mp4` | 66.083000 | `7c27fe05110fdf859b299b3f891a0c0e47e646805740cfcfe8e4bb3de8b3043b` |
| `uqam_sciences_birds_20261022_102838.mp4` | 29.000000 | `860b4de6399f6b54ab4df9bf5ea666f89b023118bac230988c5062ae20b894ed` |
| `uqam_sciences_birds_instagram_20261022_102838.mp4` | 29.000000 | `d4fbb43e2096f0d0affeaf830dd864a9828320ccc56ca56136ed4bee583e9713` |

Byte-verified copies were placed in each film's own local Drive directory:

- `02 - Promotion du bac en mathématiques/versions/2026-10-22/20261022_102838/`
- `03 - Ouvertures interdisciplinaires/versions/2026-10-22/20261022_102838/`

Each new folder contains only its landscape and Instagram MP4s. The collection's
existing `INDEX.md` now points to all four new files. A prior index copy and the
delivery verification manifest are retained locally outside Drive. Historical
videos remain untouched. Local file equality is verified; remote synchronization
and replacement of any old shared file ID are not claimed. No video was published
as a GitHub release or committed to source control.
