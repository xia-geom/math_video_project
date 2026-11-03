# Sciences visual refresh and video-only Drive — 5 October 2026

## Latest exports

Stamp: `20261005_142838` (Toronto). Both exports last **29.000 seconds**, logo
included. Local production files: `dist/uqam_revision_20261005/final/`.

| Export | Dimensions / frame rate | SHA-256 |
| --- | --- | --- |
| `uqam_sciences_birds_20261005_142838.mp4` | 1920 × 1080 / 60 fps | `4ec69f6d96f4695b5f451e6e4be03965e82d65a01f673527127a6b0ad3cdc25a` |
| `uqam_sciences_birds_instagram_20261005_142838.mp4` | 1080 × 1920 / 30 fps | `dd484f9e6ead5c34e8249bd5a11c8215782467ec5b598181dacb206762a388a6` |

Copied and hash-verified in the local Drive collection under:
`03 - Ouvertures interdisciplinaires/versions/2026-10-05/20261005_142838/`.

## Improvements

- The NorthSec opening is replaced by a bright, smiling conversation on the
  Complexe des sciences lawn. Source:
  [Faculté des sciences, Vie étudiante](https://sciences.uqam.ca/vie-etudiante/).
  Original: `vie_etudiante_sciences_uqam.jpg`, 2000 × 1333, SHA-256
  `f78a84a2f355cab5b83130f47ea68073582b0a7ca24bb38ea3d46ab12b0cf6cf`.
  Credit: Faculté des sciences · UQAM; individual photographer unspecified.
  EXIF capture date is September 4, 2024; this is campus life, not a mathematics
  class or an academic teamwork task.
- The posed Métamorphose panel is replaced by a natural gesturing exchange at
  [Avant-première](https://actualites.uqam.ca/2026/avant-premiere-rendez-vous-futurs-etudiants/),
  April 25, 2026, Centre de design. Photo: Clémence Lesné. Local file:
  `avant_premiere_2026.jpg`, 2000 × 1333, SHA-256
  `eb48c3aeb34413e0c98212bf31317ff055e9288d975c96531832393b36943d34`.
  The visitors and representatives are not described as a mathematics class.
- All three photographs use stable, bright right-side panels with copy on the
  white left side. The conclusion is shorter. No credits cover the images.
- The complete approved narration and subtitles remain unchanged in wording.
  MAI-Voice-2 at +2% and Birds — Corbyn Kites are retained. Five takes were
  regenerated with the same SSML/profile; the previous ephemeral cache was
  unavailable. The current cache is persistent in `media/voiceovers`.
- Full photo/music credits are embedded in each MP4's comment metadata, as well
  as retained locally. This copy-only metadata remux preserved both video and
  audio packet hashes. Source photographs were not retouched.

The press photo bank was checked first; it supplied no suitable collaboration
gallery. The two selections come from official UQAM pages. Sources and actual
decoded dimensions/hashes are recorded in the fetcher and shared inventories.
The original photos remain available for historical builds. Editorial selection
does not establish institutional republication clearance.

## Verification performed

- **49 targeted tests passed:** sciences contracts, two-film layout safeguards,
  music mixing, Instagram packaging and previous derivative lineage.
- Real Manim/Azure HD render completed. Its first launch failed to connect to
  Azure from the sandbox; the authorized network retry succeeded. A contact-sheet
  attempt with the system Python lacked Pillow; QA then used the existing
  rendering runtime, without installing or upgrading packages.
- Eleven raw encoded checkpoints (five scenes, four transitions, early opening
  and logo), six final HD frames and six Instagram frames were inspected.
  All 36 frames around the white-card message cut were also inspected: no blank
  frames or overlapping messages. Copy bounds are separate from photo panels;
  no visible credit labels remain.
- Three photo holds measure zero integer displacement. Correlations exceed
  0.9993. Pixel differences up to 1.922/255 are reported separately; an initial
  pixel-identity threshold was inappropriate for assessing movement and was
  replaced by positional comparison. Code applies no photograph motion.
- Both final MP4s fully decode. Narration TXT, scenario, source subtitles and
  portrait subtitles match after whitespace normalization. Both embedded credit
  strings match the complete local `CREDITS.txt`.
- No clipped/nonfinite samples or AAC gaps over 1 ms. HD/Instagram PCM
  correlation is 0.998415, with zero delay. Integrated levels are −19.49 and
  −19.54 LUFS; HD mix true peak is −3.57 dBTP.

Actual listening and institutional approval remain pending. Numeric checks
verify file integrity and mix preservation, not natural pronunciation or the
approval of the academic wording. Detailed audio/visual evidence is retained
under `dist/uqam_revision_20261005/audio_review/` and `visual_review/`.

## Drive cleanup

All three project folders **01, 02 and 03** now contain only videos recursively.
The original 17 video SHA-256 values are unchanged; the two new copies bring the
total to **19 videos**. Fifty-two initial nonvideo files were removed, followed
by eight Finder metadata files recreated during the operation. Empty directories
were pruned. Sources, credits and deleted version histories were retained in the
local workspace. No nonvideo files are delivered alongside the new videos.

The cleanup's final verification/index step initially used a mismatched plan
field name after copying and deletion. Completion was recovered from the actual
Drive files and verified local backups; all 19 videos passed SHA-256 checks.
`INDEX.md`, outside the three project folders, now links only to the latest video
files. The separate root photo archive was outside the cleanup scope.
Detailed inventory and action evidence: `dist/uqam_revision_20261005/drive_cleanup/`.

Git includes only inspected source, provenance and this report. Generated media,
downloaded photographs, audio, caches, credentials and raw local Drive backups
are excluded. Other films' rendering code, narration and exports were unchanged.
