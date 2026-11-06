# Faculty of Science signature — approximate vector reconstruction

Prepared 15 October 2026 for the teaching-video title cards. The user explicitly
requested a code-drawn reconstruction from the official faculty reference.
`faculty_science_approx.svg` is **not an official vector master** or a claim of
institutional approval. It preserves the reference composition and letterforms
through traced path geometry rather than substituting a font.

## Source and identity

- Reference image: <https://coeurdessciences.uqam.ca/wp-content/uploads/lg_Faculte-sciences-interne-COUL-1.jpg>
- Current official use: <https://coeurdessciences.uqam.ca/espace-scolaire/megaseisme-anticiper-linevitable/>
- Reference dimensions: 2306 × 337 pixels.
- Reference SHA-256: `366534a5091eeb2729afcc443d93f49dbe6c7b08277211ba58fe49ce810e865b`.
- Variant: horizontal internal-color signature, blue UQAM mark, black separator,
  green “Faculté des sciences”; no university-name subtitle.
- The complete official identity guide is at <https://www.guide.uqam.ca/>.
  The public [Service des communications page](https://servicecom.uqam.ca/normes-et-directives/logo-uqam-et-normes-graphiques.html)
  says access requires an institutional code MS. An official faculty vector
  master was not obtained during this work.

The reference JPG was inspected in temporary local review storage. It is not
embedded in the SVG, the rendering module, or a delivered video. The official
2026 faculty PowerPoint template contains PNG/JPG media, not a vector master.

## Reconstruction

Each pixel was assigned to the closest white-to-reference-color mixture, with
foreground alpha at least 0.5 and an RGB residual below 35. Isolated components
smaller than 12 pixels were discarded. Directed exposed pixel edges were traced
into closed contours, preserving the opposite winding of letter counters.
Douglas–Peucker simplification used a 0.35-source-pixel tolerance. No font
replacement, bitmap embedding, independent letter repositioning or aspect-ratio
change was applied.

The source's white outer margin was removed: the tight source rectangle is
`[112, 82, 2196, 249)` and the SVG viewBox is `0 0 2084 167`. Callers must reserve
clear space around this tight bounding box. The mark contains 7 blue contours,
26 green contours and one separator contour (4708 total retained vertices).

The dominant interior JPG colors were blue `#0168AB` and green `#3DA939`.
These are **sampled reference colors**, not independently verified official
brand swatches. The separator is solid black. Small JPEG compression artifacts,
antialiasing and thresholding mean this vector reconstruction is approximate.

SVG SHA-256: `d58a1e3feffc64c6810a8f9089bd46f5eadb3b2d41d3c5bec1538e54ecd5d24e`.

## Rendering and review

`tools.faculty_branding.faculty_signature(width=3.6)` returns a centered Manim
`SVGMobject`, with native filled paths and no stroke, bitmap or font dependency.
Placement and animation are owned by the title-card caller. The SVG is source
geometry; rendered review images stay outside source Git.
Parsing uses a private temporary copy because Manim creates an adjacent
intermediate SVG. Concurrent renders must never write beside this source asset.

Review performed on 15 October 2026:

- Nine focused tests passed in `/tmp/math-final-review-venv`: native-vector
  geometry, aspect ratio, colors, no bitmap/font dependency, width validation and
  independent positioning of instances.
- A real Manim Cairo camera rasterized the vector paths at the source crop's
  exact 2084 × 167 dimensions. The reference and rasterized vector were inspected
  side by side. Letterforms, accent, separator and transparent counters were
  retained; the traced edges remain slightly stepped at full source size.
- Foreground intersection-over-union was **0.9885766834**, using the independent
  threshold `min(R, G, B) < 180` on both images. Mean absolute RGB channel error
  was **1.2460 / 255** across the full crop. These measures include JPEG edge
  artifacts and the deliberate solid-black separator.
- At width 3.6 in a standard 1920 × 1080 scene, the tight signature is about
  486 × 39 pixels. The title-card composition and its motion require their own
  scene-level visual review; this check covered the signature image only.

Review images remained in temporary local storage, outside source Git. This was
a real static rendering and image-fidelity review, not a video render, listening
check or institutional approval.

## Rights boundary

UQAM retains its institutional identity rights. This record establishes source
provenance and the reconstruction method; it does not claim a redistribution
license, endorsement or publication permission. Preserve the repository's
existing institutional release review.
