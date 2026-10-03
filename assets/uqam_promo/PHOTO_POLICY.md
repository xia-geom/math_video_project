# UQAM photo sourcing policy

This directory is the shared photographic library for UQAM promotional videos in
`math_video_project`.

## September 30 source research and revision brief

Read [PHOTO_CANDIDATES.md](PHOTO_CANDIDATES.md) for verified source pages,
credits, context restrictions and unverified image/permission checks. These are
candidate sources, not additions to the generated production asset inventory.
The [two-film revision brief](../../reports/uqam_video_revision/2026-09-30/PLAN.md)
records the requested replacements, pacing changes and acceptance checks.
The historical brief describes proposals; the dated implementation reports record
which changes have subsequently been selected and rendered.

## Default source order

1. Start with the official UQAM Salle de presse photo bank:
   https://salledepresse.uqam.ca/banque-de-photos/
2. For pavilion imagery, prefer its pavilion collection:
   https://salledepresse.uqam.ca/banque-de-photos/photos-de-pavillons/
3. When the press bank does not show the activity or interior needed, use a
   recent official UQAM page (for example Actualités UQAM, Faculté des sciences,
   Service des bibliothèques or another UQAM unit) and record the exact source.
4. Do not substitute stock photography for an available UQAM image.

The press bank requires the source wording `Photo : UQAM`. Preserve any more
specific photographer or unit credit stated by an official source.

## Editorial selection

For evergreen recruitment material, prefer current, bright, people-centred or
campus-context images that still read clearly after a 16:9 crop. Avoid
street-dominated building views when a stronger campus or interior image can
carry the same factual point. Avoid pandemic-era masked imagery unless the
historical period itself is relevant. Do not infer that people shown in event,
open-house or support photographs are mathematics students unless the source
states that.

A photograph should have one semantic job in a short film. Reusing the same
image for multiple claims is discouraged unless the repetition is intentional.

Older assets may remain in the shared directory and generated source manifest
when another UQAM film still depends on them. Retention for reproducibility does
not make those files preferred choices for new productions.

## Current short-film refresh

The September 2026 refresh uses:

- `campus_central_uqam.jpg` for the opening UQAM identity shot, from the
  official pavilion photo bank.
- `sciences_biologiques_uqam.jpg` for the Complexe des sciences location shot,
  replacing the street-heavy Président-Kennedy exterior.
- `bibliotheque_sciences_2026.jpg` for the Bibliothèque des sciences, replacing
  the 2021 open-house image with masked visitors.

The October 1 edit replaces that low-resolution library panel in the math film
with `redaction_sciences_2026.jpg`, an official 1500 × 1125 image of the autumn
2026 collective-writing sessions at the Bibliothèque des sciences. Credit:
`Service des bibliothèques · UQAM`. The older file remains for historical builds.

The historical interdisciplinary-opening versions used
`sciences_biologiques_uqam.jpg` for their institutional opening.

The October 3 editorial selection gives each capsule distinct people-centred
photos. Maths uses `ludopolis_2026.jpg`, `math_workshop_2019.jpg` and
`accueil_hiver_2026.jpg`, with its existing library and location shots.
The 29-second sciences version uses `northsec_2026.jpg`,
`metamorphose_2024.jpg` and `bouturage_2026.jpg`. They depict an event team,
project presenters and a campus workshop respectively; none is labelled as a
regular mathematics class. The six selections and complete photographer credits
are recorded in [the October 3 photo review](../../reports/uqam_video_revision/2026-10-03/PHOTOS.md).
User editorial selection does not establish institutional republication clearance.

The canonical URLs, intended uses and credit strings live in
`miscellaneous/bac_math_uqam_fr/fetch_uqam_promo_assets.py`.
`sources.json` and `SOURCES.md` are generated inventories of the downloaded
files.

## Build rule

Rendering does not access the network. Run:

`python miscellaneous/bac_math_uqam_fr/fetch_uqam_promo_assets.py`

before rendering after a fresh clone or photo-source change. The fetcher validates
the image bytes and records dimensions and SHA-256 hashes.
## Review automation

Pull requests that change the shared UQAM photo library, the short-film source or
its tests run the UQAM revision workflow. That workflow refreshes declared photo
assets before tests and visual-only review so a missing or blocked source fails
before publication.
