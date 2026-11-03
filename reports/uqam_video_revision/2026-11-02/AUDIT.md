# UQAM recent-video audit — 2 November 2026

Three export safeguards were repaired on top of the October 29 full-photo
branch, `b6b8a27`, which includes the October 22 narration and portrait updates.
The existing films, selected photos, voice profiles, narration and delivery
copies are preserved.

## Verified problems and fixes

1. Both the music mixer and portrait packager accepted a synthetic input with
   0.6 seconds of picture and 1.2 seconds of audio, silently cut the audio to
   0.6 seconds, and reported success. They now compare measured stream endpoints
   before export and reject an audio overrun exceeding 50 ms. This tolerance
   permits container/AAC padding; it is not speech-activity detection. Existing
   final exports have at most 33.3 ms difference and pass the check.
2. Adding music replaced source-comment attribution and omitted photo-credit
   sidecars. The mixer now retains those credits alongside the music credit.
   Both downstream packagers prefer a video-specific `.credits.txt`, with a
   fallback to sibling `CREDITS.txt`, the format used by the full-photo builder.
   The selected source-credit path and SHA-256 are recorded. Synthetic integration
   tests cover credit preservation, fallback and precedence.
3. The full-photo verifier trusted the first video and audio streams without
   rejecting additional tracks or a changed frame rate. It now requires exactly
   one video stream at 60 fps and exactly one AAC soundtrack, before the retained
   dimensions, frame-count, duration, decoding and PCM-identity checks.

An independent `export_checks` job now runs these regressions using synthetic
media and the repository's existing font. Its path filters include both
packaging scripts and all three export test modules. It requires no cloud
credentials or production photos. The pre-existing revision job and manual-main
paid-narration gate are unchanged.

## Actual validation

- Final integrated run: **154 tests and 5 subtests passed**. This includes
  55 full-photo tests, 21 packaging tests, 70 short-film contracts and the
  workflow policy/syntax tests. Scoped Ruff, syntax and whitespace checks pass.
- Six full-photo regression cases failed with the original verifier. Real
  synthetic-media tests reproduced both audio truncations and the lost-credit
  case; three additional fallback regressions also failed before repair.
- All four final October 22 math/sciences landscape/portrait MP4s match their
  recorded output hashes and fully decode. Two portrait samples were inspected.
  The superseded `history_initial_science_mix` files were not treated as current.
- Both existing October 29 full-photo v2 exports fully decode: **3,965 frames,
  60 fps, 66.083 seconds**, in 1920×1080 and 1080×1920. Their encoded AAC payloads
  and decoded PCM match the pinned October 22 soundtrack exactly.
- Seven source-photo hashes and their recorded credits were checked. Thirty
  layout images were regenerated without encoding a complete film. They show
  small sparse raster differences from historical JPEGs; byte identity is not
  claimed. Twelve encoded samples across both formats were visually inspected,
  including photo and copy transitions. The workshop and campus-conversation
  portrait crops retain the intended people.
- Three already-local sciences photos were restored into the isolated test
  checkout only after matching their declared hashes. These copies are excluded
  from the commit; no new asset download or substitution occurred.

Exact source, media, frame and log hashes and the inspection limits are in
[verification.json](verification.json). An independent review checked the
audio/credit/stream changes and found the standard-sidecar case, which was then
fixed and included in the final rerun.

## Boundaries

These are code/verification repairs. No production film was regenerated,
remixed, overwritten, sent to Drive or published. Fresh video encodes in the
tests use synthetic media only. The earlier photo-context exceptions, exact
credits, soundtrack choice and voice rates remain unchanged.

Selected-frame review and audio identity do not establish continuous playback,
listening quality, institutional approval or media-rights clearance.
`release_ready` remains false. Existing repository-wide lint and other baseline
CI limitations are not disabled or repaired by this change. Only inspected
task text is staged; generated media, photos and raw local logs remain outside
Git. A successful export test is not complete public-repository clearance.
