"""Code-rendered, raster-derived Faculty of Science signature.

The SVG contains native path geometry, including letter counters; no bitmap or
installed font is used during rendering. This is an approximate reconstruction,
not an official vector master. See the adjacent asset provenance document.
"""
from __future__ import annotations

import math
from pathlib import Path
from tempfile import TemporaryDirectory

from manim import SVGMobject

SIGNATURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "assets/branding/faculty_science_approx.svg"
)
REFERENCE_URL = (
    "https://coeurdessciences.uqam.ca/wp-content/uploads/"
    "lg_Faculte-sciences-interne-COUL-1.jpg"
)
REFERENCE_SHA256 = "366534a5091eeb2729afcc443d93f49dbe6c7b08277211ba58fe49ce810e865b"
REFERENCE_BLUE = "#0168AB"
REFERENCE_GREEN = "#3DA939"
SIGNATURE_ASPECT_RATIO = 2084 / 167


def faculty_signature(width: float = 3.6) -> SVGMobject:
    """Return the centered faculty signature as a native Manim vector group.

    ``width`` is in Manim scene units. Position and animation belong to the
    caller. The tight bounds exclude the source JPG's white margin, so callers
    must reserve their own clear space. Colors are sampled from that reference;
    they are not independently certified institutional color specifications.
    """
    if isinstance(width, bool) or not isinstance(width, (int, float)):
        raise ValueError("Faculty signature width must be a positive finite number.")
    if not math.isfinite(width) or width <= 0:
        raise ValueError("Faculty signature width must be a positive finite number.")
    if not SIGNATURE_PATH.is_file():
        raise FileNotFoundError(f"Faculty signature vector is missing: {SIGNATURE_PATH}")
    # Manim writes and removes an adjacent "*_" SVG during parsing. A private
    # copy keeps concurrent lesson renders from racing over that temporary file
    # and permits source assets to live in a read-only checkout.
    with TemporaryDirectory(prefix='faculty-signature-') as temporary:
        source = Path(temporary) / 'signature.svg'
        source.write_bytes(SIGNATURE_PATH.read_bytes())
        signature = SVGMobject(
            source,
            height=None,
            width=float(width),
            fill_opacity=1,
            stroke_width=0,
        )
    signature.set_stroke(width=0)
    return signature
