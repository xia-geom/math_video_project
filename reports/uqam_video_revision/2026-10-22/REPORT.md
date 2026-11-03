# Instagram mathematics draft — 22 October 2026

## Identified source

The supplied `uqam_math_birds_instagram_20261004_202033.mp4` matches the
repository and local Drive archive byte for byte (SHA-256
`3db2d51db1cc9b94315d0b1701bc8258018ffee064e620e07e7272baca76247d`).
The matching clean landscape master is
`dist/uqam_revision_20261004/final_clean/uqam_math_birds_20261004_202033.mp4`
(SHA-256 `475033cf02fa16a0ed52ead51de42fe56a9fa32f3188ccfc46d1bd05858442bf`).
Historical files and the other UQAM projects were preserved.

## Changes and remaining request

- Repackaged the clean landscape master without narration subtitles. The
  incorrect lower caption “Au Cirgé” disappears; the original CIRGET card,
  scene titles, photographs, portrait title and website remain.
- Applied a localized fade/mute to the isolated narration before LaCIM. The
  original CIRGET take contains a loud terminal low-frequency artifact, after
  its speech-like spectral tail has decayed. The correction is a candidate
  audible repair; listening has not established phonetic completeness or
  perceived improvement.
- “Au cœur de Montréal !” retains its original recording. No alternate exact
  take was found in the inspected voice cache, and Azure Speech credentials
  were unavailable in the local runtime. No voice substitution, word splicing,
  pitch adjustment or new synthesis was performed. The naturalness request
  remains open.

The caption packager now requires either `--subtitles PATH` or `--no-captions`.
Existing captioned calls remain compatible. Caption-free exports have no ASS
or SRT sidecars and record null timing fields and empty cue arrays.

## Audio reconstruction

The source narration WAV is the existing normalized export from
`dist/bac_math_uqam_fr/releases/20261004_202033/`:
`uqam_bac_mathematiques_promo_fr_20261004_202033_narration.wav`, SHA-256
`e05f39ce1e0c54cf0b8aaae6eb1efda67110c04c7fde57504fd99d5b1e481882`.
Its 3,170,304 mono signed-16-bit samples at 48 kHz were retained in place.

| Boundary | Time (s) | Sample index at 48 kHz |
| --- | ---: | ---: |
| Start fade | 22.273333333 | 1,069,120 |
| End fade, start silence | 22.303333333 | 1,070,560 |
| Resume unmodified next take | 22.591333333 | 1,084,384 |

For samples `i` in `[start, end)`, the gain is
`0.5 * (1 + cos(pi * (i - start) / (end - start - 1)))`, with the product rounded
to an integer. Samples `[end, resume)` are zero. All other samples are identical,
including Montréal and the LaCIM take. The repaired WAV SHA-256 is
`ee7e48d05ce43f99365322b03096d1f76f23fa8d92f27b209036fdad26a777a8`.

The original already-ducked Birds music stem was reused unchanged, SHA-256
`131de2ee2aa9aad390a954b05e118b0c06135245b827e6c7d6551c255aff72bc`.
The voice was converted to stereo with FFmpeg's existing conversion and gained
by −0.5 dB, then mixed with that stem using `amix normalize=0` and the original
`alimiter limit=0.841395:level=false:latency=true`. Both streams were padded to
66.083333 s. A PCM-24 MOV intermediate avoids an additional lossy audio encode;
its video packets are copied from the landscape master.

Final packaging uses `scripts/package_uqam_instagram.py --no-captions`, the
original Roboto font, and title `Mathématiques à l’UQAM`. The packager's unchanged
portrait layout fits the complete landscape picture at (0, 430), 1080 × 608.
Attribution sidecars and metadata were retained locally. Narration remains the
existing MAI-Voice-2 recording at its original +6% rate.

## Verification performed

- **Automated source checks:** 8 targeted Instagram tests passed, including two
  real 0.6-second FFmpeg exports. Tests check mutually exclusive modes, encoded
  caption pixels, retained title/CTA, streams, duration and caption metadata.
  Python syntax and `git diff --check` passed. An earlier pytest startup was
  interrupted before collection; the completed run disabled unrelated plugin
  autoload. No failing test was excluded.
- **Real media export:** full 66.083 s portrait export and complete FFmpeg decode
  passed; 1080 × 1920, 30 fps, H.264, stereo AAC at 48 kHz. All 3,965 landscape
  video packet hashes match the clean source in the PCM intermediate.
- **Audio measurements:** PCM samples outside the edit are identical; the muted
  interval is zero in the isolated voice. Its prior RMS was −19.87 dBFS.
  Final mix measures −19.40 LUFS integrated and −3.77 dBTP, with no peak clipping
  indicated. These measurements do not constitute listening.
- **Visual inspection:** inspected encoded frames at 1, 9, 19.2, 23.5, 28.5,
  40, 56.8 and 63 seconds, including CIRGET at full resolution. The lower
  narration captions are absent; the retained graphics and website are visible.
  This was sampled frame inspection, not continuous playback review.
- **Listening / institutional approval:** not performed / not inferred.

Generated evidence is under `dist/uqam_revision_20261022/`, including
`audio_repair_manifest.json`, `review/cirget_tail_numeric.json`, the final
packaging manifest, loudness log, frames, contact sheet and LaCIM excerpt.
No generated media, fonts or private configuration are included in Git.

## Draft delivery

`uqam_math_birds_instagram_sans_sous_titres_20261022.mp4` — 5,533,662 bytes,
SHA-256 `d839734903299d2b06531052d36965a53f0889706336340e4929312b402bed5a`.

A byte-verified copy was placed in the existing local Drive collection:
`UQAM-apercu-programme/02 - Promotion du bac en mathématiques/versions/2026-10-22/`.
That new folder contains only the MP4. The older version was not replaced.
This verifies the local Drive copy, not remote synchronization or a replacement
of the original shared file ID. Publication and listening approval remain pending.
