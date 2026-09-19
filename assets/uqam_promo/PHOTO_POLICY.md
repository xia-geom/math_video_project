# UQAM photo sourcing policy

This directory is the shared photographic library for UQAM promotional videos in
`math_video_project`.

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

## Current short-film refresh

The September 2026 refresh uses:

- `campus_central_uqam.jpg` for the opening UQAM identity shot, from the
  official pavilion photo bank.
- `sciences_biologiques_uqam.jpg` for the Complexe des sciences location shot,
  replacing the street-heavy Président-Kennedy exterior.
- `bibliotheque_sciences_2026.jpg` for the Bibliothèque des sciences, replacing
  the 2021 open-house image with masked visitors.

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

