# Latest maths delivery — 4 October 2026, 20:20:33

This update supersedes the 12:07 delivery described in `REPORT.md`; that
report and its files remain as history. No sciences or long-film files changed.

## Delivered to local Drive

`/Users/xiaxiao/My Drive/UQAM-apercu-programme/02 - Promotion du bac en mathématiques/versions/2026-10-04/20261004_202033`

- HD: `uqam_math_birds_20261004_202033.mp4`, 1920 × 1080, 60 fps,
  66.083333 seconds. SHA-256:
  `475033cf02fa16a0ed52ead51de42fe56a9fa32f3188ccfc46d1bd05858442bf`.
- Instagram: `uqam_math_birds_instagram_20261004_202033.mp4`,
  1080 × 1920, 30 fps, 66.083 seconds. SHA-256:
  `3db2d51db1cc9b94315d0b1701bc8258018ffee064e620e07e7272baca76247d`.
- Narration TXT, subtitles, full credits, source metadata, review reports,
  LaCIM voice/mix listening excerpts, six active photos and two retouch originals.

Thirty-two files were copied and their SHA-256 values compared with the production
files. `versions.json` and the collection's `INDEX.md` now point to this stamp.
The noon and October 3 versions remain intact. The other two project directories
were compared before and after copying and are unchanged. Detailed copy evidence:
`dist/uqam_revision_20261004/final_clean/DRIVE_COPY_REPORT.json`.

## Final photo refinement

Close-crop imagegen edits removed small vehicle remnants at both street edges.
Original pixels protect the foreground poles, cyclist and pedestrians. The
final campus PNG is pinned in the fetcher and source registry:
`2f1ac03611e32bf7e58433a027cb653d6697923601284ff0f8a64772001d59da`.
The library derivative is unchanged from the earlier review. Both derivatives
have zero changed decoded RGB values outside their bounded object masks.
The two final mask PNGs accompany the photos; their hashes, feather parameters
and protected regions are recorded in `PHOTO_EDIT_QA.json`.
Prompts and composition recipe are preserved in `PHOTO_EDITS.md` and
`export_retouches.cjs`; generated photographs remain outside Git.

## Verification of this latest render

- **49 targeted tests passed** after the final campus asset update: promo,
  two-film safeguards, derivative lineage, music mixing and Instagram packaging.
- **Real render:** Manim/Azure voice master rebuilt; Birds mix and portrait
  packaging completed. MAI-Voice-2 and uniform +6% rate retained.
- **Visual review:** all 48 current raw QA frames, 12 final HD frames and six
  Instagram frames inspected. Retouch edges also inspected at close range.
  Text and faces remain separated; credits are absent from the image and
  supplied in sidecars and metadata. The requested ending appears in narration,
  screen text and subtitles.
- Five encoded photo holds passed stability checks; mean channel differences
  are below 0.543/255. Both final videos fully decode. HD video packets are
  unchanged by music mixing.
- Final mix: −19.37 LUFS integrated, −3.86 dBTP. Instagram PCM correlation
  with the HD mix is 0.998551, RMS ratio 0.996497.
- Fresh LaCIM source/master correlation is 0.999554; reconstructed voice/Birds
  mix correlation is 0.999756. No clipped/nonfinite samples or AAC gaps over
  1 ms were found in the reviewed excerpts. The alias synthesis is 2.904 s,
  compared with 3.096 s for the original October 3 take.

**Actual listening has not been performed.** Numerical checks do not establish
that the reported LaCIM sound defect is audibly resolved. The delivered excerpts
remain available for listening; full headphone/phone listening and institutional
approval are pending. Existing distribution conditions are retained in
`CREDITS.txt`, without inferring new clearance.

Only inspected source, provenance and report files are included in Git.
Rendered videos, audio, generated images, caches and local credentials are
excluded. The temporary rendering-runtime symlink was removed.
