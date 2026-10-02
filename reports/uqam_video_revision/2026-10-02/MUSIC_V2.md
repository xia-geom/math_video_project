# Music mix correction — version 2

The user could not hear the music in the first previews. The −37 LUFS bed was
too quiet relative to the −19 LUFS narrator. The selected recording also had
approximately 0.85 seconds of near-silence before its first note.

Both films were remixed from the original voice-only masters. Version 2 starts
the music at 0.85 seconds and targets −25 LUFS before gentle speech-controlled
ducking (ratio 2:1, threshold 0.04, attack 100 ms, release 600 ms). The narrator
retains the same gain and timing. Music returns to its fuller level in pauses
and after narration. These are now the mixer's defaults.

| Actual measurement | Maths, 68.483 s | Sciences, 29 s |
| --- | ---: | ---: |
| Music after ducking | −27.73 LUFS | −27.09 LUFS |
| Increase over first music bed | 9.27 LU | 9.91 LU |
| Complete mix | −19.32 LUFS | −19.82 LUFS |
| Encoded true peak | −4.13 dBTP | −4.02 dBTP |

Files are in `dist/uqam_music_review_20261002/v2/`:

- `uqam_math_68s_music_v2.mp4`
- `uqam_sciences_29s_music_v2.mp4`

Each has its unchanged subtitle sidecar, a provenance manifest, and an isolated
music bed for signal verification. `CREDITS.txt` identifies Scott Buckley,
Resolutions, CC BY 4.0 and the edits. Earlier previews remain available.

Verification: Python syntax check and both actual FFmpeg builds passed; complete
decoding, unchanged compressed video hashes, duration and true-peak checks
passed. The narration is not time-stretched. Full listening remains unperformed;
the earlier visual audit findings and institutional review gates are unchanged.
Generated audio and video are excluded from the Git checkpoint.

To reproduce the first, quiet comparison with the updated utility, explicitly
pass `--music-offset 0 --music-lufs -37 --no-duck-music`. Use the default settings
for the corrected version.
