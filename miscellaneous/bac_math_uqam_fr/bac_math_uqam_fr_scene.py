"""
Baccalauréat en mathématiques à l'UQAM — vidéo promotionnelle courte.

Repository path:
    miscellaneous/bac_math_uqam_fr/bac_math_uqam_fr_scene.py

Scene class:
    BacMathUQAMFR

Intent
------
Create a 60–90 second recruitment video for prospective mathematics students.

V2 audit goals:
- begin with a strong real UQAM visual before title typography;
- reduce the "animated PowerPoint" feeling;
- reserve the lower frame for subtitles;
- distinguish faculty-wide claims from mathematics-program claims;
- avoid implying that event participants are ordinary bachelor students;
- end with an explicit programme call-to-action before the approved logo.

The positioning is deliberately not "UQAM is the only university with small
groups / research opportunities", because comparable claims are also made by
other universities. The differentiating story is the combination of:

    rigorous mathematics
    + accessible teaching / collaborative learning
    + undergraduate access to research networks
    + peer mentoring / student support
    + downtown Montréal / direct Place-des-Arts metro access

This scene follows the Xia_video conventions:
- Manim Community + manim-voiceover
- Azure voice selected centrally through tools/tts.py
- narration controls pacing
- white background, black ink, restrained accent
- no decorative motion
- plain-French subcaptions, SSML only in spoken text

UQAM visual standards reflected here:
- Roboto typography
- UQAM blue: RGB 0/121/190
- faculty colours are not used as the main palette
- an official UQAM logo, if supplied, appears only on the final card

Real-photo integration
----------------------
The scene is fully renderable with vector fallbacks. If approved UQAM photos
are available, place them in:

    assets/uqam_promo/

with these optional names:
    campus_central_uqam.jpg     # official UQAM press-bank campus image
    francois_bergeron.jpg
    lisa_berger.jpg
    research_math.jpg
    support_students.jpg        # UQAM welcome/support student-life photo
    bibliotheque_sciences_2026.jpg  # current UQAM Bibliothèque des sciences
    sciences_biologiques_uqam.jpg   # science-complex location image
    international_students.jpg
    allo_pk.jpg

The companion script `fetch_uqam_promo_assets.py` downloads the curated
official UQAM images once and records source pages / photographer credits.
The Manim scene itself never downloads anything at render time.

The release manifest records the user-provided authorization basis together
with source pages, photographer credits, dimensions, and hashes.

Voice test
----------
The scene does not hard-code the Azure voice. To test the current MAI profile:

    SPEECH_REGION=canadacentral \
    UQAM_PROMO_VOICE='MAI-Voice-2' \
    UQAM_PROMO_RATE='+2%' \
    ./scripts/render.sh \
      miscellaneous/bac_math_uqam_fr/bac_math_uqam_fr_scene.py \
      BacMathUQAMFR ql

Music is intentionally absent. The canonical and stamped masters contain one
narration track only.
"""

from __future__ import annotations

# Manim's public scene API is intentionally imported as a star.
# ruff: noqa: F403, F405
import hashlib
import json
import os
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService
from manimpango import register_font
from PIL import Image, ImageDraw, ImageFont
from tools.uqam_video_review import cover_image
from miscellaneous.bac_math_uqam_fr.promo_beats import NARRATION_BEATS

from tools.tts import (
    VOICE_LOCALES,
    azure_service_kwargs,
    configure_azure_speech_environment,
    resolve_voice,
    ssml,
    strip_ssml,
)

# ---------------------------------------------------------------------------
# Project / UQAM visual defaults
# ---------------------------------------------------------------------------

config.background_color = WHITE

REPO_ROOT = Path(__file__).resolve().parents[2]
FONT = os.getenv("UQAM_VIDEO_FONT", "Roboto")
PROMO_RATE = os.getenv("UQAM_PROMO_RATE", "+2%")
HOOK_RATE = os.getenv("UQAM_HOOK_RATE", "0%")
PROMO_VOICE = resolve_voice(
    os.getenv("UQAM_PROMO_VOICE", os.getenv("MANIM_VOICE", "MAI-Voice-2"))
)
ASSET_DIR = Path(
    os.getenv("UQAM_PROMO_ASSET_DIR", str(REPO_ROOT / "assets" / "uqam_promo"))
)
FONT_PATH = Path(
    os.getenv(
        "UQAM_VIDEO_FONT_PATH",
        str(ASSET_DIR / "fonts" / "Roboto-VariableFont_wdth,wght.ttf"),
    )
)
TEXT_CACHE_DIR = ASSET_DIR / "_text_cache"
TEXT_RASTER_SCALE = int(os.getenv("UQAM_TEXT_RASTER_SCALE", "4"))
TEXT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOGO_PATH = Path(
    os.getenv(
        "UQAM_PROMO_LOGO_PATH",
        str(REPO_ROOT / "assets" / "branding" / "uqam_logo.png"),
    )
)
USE_OFFICIAL_LOGO = os.getenv("UQAM_USE_OFFICIAL_LOGO", "0") == "1"
SHOW_PHOTO_CREDITS = os.getenv("UQAM_SHOW_PHOTO_CREDITS", "0") == "1"
USE_REAL_PHOTOS = os.getenv("UQAM_USE_REAL_PHOTOS", "1") != "0"
CTA_URL = os.getenv(
    "UQAM_PROMO_CTA_URL",
    "https://etudier.uqam.ca/programme/baccalaureat-mathematiques",
)
CTA_DISPLAY = os.getenv("UQAM_PROMO_CTA_DISPLAY", "etudier.uqam.ca")
# Setting this to 1 should mean the final video has received the required
# internal approval to use the official UQAM logo.
LOGO_APPROVED = os.getenv("UQAM_LOGO_APPROVED", "0") == "1"
TEACHING_PORTRAIT_HOLD = float(
    os.getenv("UQAM_TEACHING_PORTRAIT_HOLD", "3.20")
)
RESEARCH_GRAPH_HOLD = float(os.getenv("UQAM_RESEARCH_GRAPH_HOLD", "1.35"))
FINAL_MESSAGE_HOLD = float(os.getenv("UQAM_FINAL_MESSAGE_HOLD", "1.65"))
FINAL_CARD_HOLD = float(os.getenv("UQAM_FINAL_CARD_HOLD", "2.80"))
SUPPORT_HUMAN_HOLD = float(os.getenv("UQAM_SUPPORT_HUMAN_HOLD", "2.25"))
SUPPORT_LIBRARY_HOLD = float(os.getenv("UQAM_SUPPORT_LIBRARY_HOLD", "2.30"))
SUPPORT_PAGE_HOLD = float(os.getenv("UQAM_SUPPORT_PAGE_HOLD", "1.15"))
MONTREAL_BUILDING_HOLD = float(
    os.getenv("UQAM_MONTREAL_BUILDING_HOLD", "2.00")
)
MONTREAL_PHOTO_HOLD = float(os.getenv("UQAM_MONTREAL_PHOTO_HOLD", "1.70"))

if FONT_PATH.exists():
    register_font(str(FONT_PATH))

UQAM_BLUE = "#0079BE"      # official UQAM blue: RGB 0/121/190
INK = "#312F2D"            # close to UQAM's dark grey band colour
SOFT_GREY = "#F1F3F5"
MID_GREY = "#59616B"
METRO_GREEN = "#00A651"    # semantic use only: Montréal green line

NARRATION_SEGMENTS = {
    "hook": (
        "À l'UQAM, <break time='280ms'/> "
        "on peut faire des mathématiques exigeantes. "
        "<break time='320ms'/> Sans se perdre dans la foule."
    ),
    "human_scale": (
        "La Faculté met en avant des groupes à taille humaine et des enseignants accessibles, "
        "et les cours laissent une vraie place aux questions. "
        "<break time='180ms'/> Des travaux pratiques accompagnent la première année; "
        "plus tard, le travail supervisé développe l'autonomie et prépare aux pratiques de la recherche."
    ),
    "research": (
        "Ce milieu à taille humaine n'est pas isolé. "
        "<break time='220ms'/> Dès le bac, des stages d'été permettent de découvrir le CIRGET et le LACIM. "
        "Le CIRGET est interuniversitaire; le LACIM est un centre de recherche de l'UQAM. "
        "<break time='180ms'/> Une porte d'entrée vers un réseau scientifique qui dépasse le campus."
    ),
    "support": (
        "Et quand on arrive, on n'est pas laissé seul. "
        "<break time='180ms'/> Le mentorat par les pairs aide à prendre ses repères, "
        "et des services de soutien à l'apprentissage sont disponibles quand on en a besoin. "
        "<break time='180ms'/> La Bibliothèque des sciences offre aussi des espaces pour travailler, "
        "seul ou en équipe."
    ),
    "montreal": (
        "Tout cela au Complexe des sciences Pierre-Dansereau, au cœur du Quartier des spectacles, "
        "avec un accès intérieur direct au métro Place-des-Arts. "
        "<break time='220ms'/> Et si vous arrivez de l'étranger, la Faculté propose "
        "des ressources d'accueil et d'intégration."
    ),
    "close": (
        "Des mathématiques exigeantes. <break time='170ms'/> Un milieu à taille humaine. "
        "<break time='170ms'/> Un réseau de recherche. <break time='170ms'/> Montréal à votre porte. "
        "<break time='260ms'/> Découvrez le bac en mathématiques à l'UQAM."
    ),
}

NARRATION_RATES = {
    "hook": HOOK_RATE,
    "human_scale": PROMO_RATE,
    "research": PROMO_RATE,
    "support": PROMO_RATE,
    "montreal": PROMO_RATE,
    "close": PROMO_RATE,
}

for _segment, _beats in NARRATION_BEATS.items():
    NARRATION_SEGMENTS[_segment] = " ".join(_beats)

Text.set_default(font=FONT, color=INK)
Tex.set_default(color=INK)
MathTex.set_default(color=INK)


# ---------------------------------------------------------------------------
# Small reusable visual helpers
# ---------------------------------------------------------------------------

def _font_variation_name(weight: str) -> str:
    """Resolve our Manim weight names to Roboto's named font instances."""
    mapping = {
        "THIN": "Thin",
        "EXTRALIGHT": "ExtraLight",
        "LIGHT": "Light",
        "NORMAL": "Regular",
        "REGULAR": "Regular",
        "MEDIUM": "Medium",
        "SEMIBOLD": "SemiBold",
        "BOLD": "Bold",
        "EXTRABOLD": "ExtraBold",
        "BLACK": "Black",
    }
    return mapping.get(str(weight).strip().upper(), "Regular")


def _load_pillow_font(pixel_size: int, weight: str) -> ImageFont.FreeTypeFont:
    """Load the registered Roboto file through Pillow/FreeType."""
    if not FONT_PATH.is_file():
        raise RuntimeError(
            "Kerning-safe typography requires the configured Roboto font file: "
            f"{FONT_PATH}"
        )

    font = ImageFont.truetype(str(FONT_PATH), pixel_size)
    variation = _font_variation_name(weight)
    if hasattr(font, "set_variation_by_name"):
        try:
            font.set_variation_by_name(variation)
        except Exception:
            try:
                font.set_variation_by_name(variation.encode("utf-8"))
            except Exception:
                # The variable file's regular instance remains deterministic.
                pass
    return font


def _hex_to_rgba(color) -> tuple[int, int, int, int]:
    """Accept both Manim colours and #RRGGBB values for Pillow rendering."""
    value = color.to_hex() if hasattr(color, "to_hex") else str(color)
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    if len(value) != 6:
        raise ValueError(f"Expected #RRGGBB colour, got {color!r}")
    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
        255,
    )


def kerning_text(
    text: str,
    *,
    size: int,
    color=INK,
    weight: str = "NORMAL",
) -> ImageMobject:
    """Render visible promotional copy with Pillow/FreeType, not ManimPango.

    The output is a cached transparent image. It keeps normal Manim layout and
    animation behaviour while letting FreeType use Roboto's pair-specific
    kerning. Subtitle rendering and MathTex intentionally remain unchanged.
    """
    scale = max(2, TEXT_RASTER_SCALE)
    pixel_size = int(round(size * scale))
    rgba = _hex_to_rgba(color)
    cache_payload = {
        "renderer_revision": 2,
        "text": text,
        "size": size,
        "weight": weight,
        "rgba": rgba,
        "scale": scale,
        "font": str(FONT_PATH),
        "font_mtime_ns": FONT_PATH.stat().st_mtime_ns if FONT_PATH.exists() else None,
    }
    digest = hashlib.sha256(
        json.dumps(cache_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()[:24]
    png_path = TEXT_CACHE_DIR / f"text_{digest}.png"

    if not png_path.exists():
        font = _load_pillow_font(pixel_size, weight)
        padding = max(12, int(pixel_size * 0.30))
        probe = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        bbox = ImageDraw.Draw(probe).textbbox((0, 0), text, font=font)
        width = max(1, bbox[2] - bbox[0])
        height = max(1, bbox[3] - bbox[1])
        canvas = Image.new(
            "RGBA", (width + 2 * padding, height + 2 * padding), (0, 0, 0, 0)
        )
        ImageDraw.Draw(canvas).text(
            (padding - bbox[0], padding - bbox[1]), text, font=font, fill=rgba
        )
        # Keep a tiny alpha margin after rasterization. The larger working
        # padding protects accents while drawing, but retaining it in the PNG
        # would make Manim align the transparent border rather than the words.
        alpha_bounds = canvas.getchannel("A").getbbox()
        if alpha_bounds is None:
            raise RuntimeError(f"Pillow produced an empty text raster for {text!r}")
        margin = max(2, scale)
        left, top, right, bottom = alpha_bounds
        canvas = canvas.crop(
            (
                max(0, left - margin),
                max(0, top - margin),
                min(canvas.width, right + margin),
                min(canvas.height, bottom + margin),
            )
        )
        canvas.save(png_path)

    mob = ImageMobject(str(png_path))
    # This Pango probe is never displayed. It only preserves the existing
    # Manim point-size-to-scene-size calibration for the FreeType raster.
    probe_height = Text("Ag", font=FONT, font_size=size, weight=weight).height
    mob.scale_to_fit_height(probe_height * 1.08)
    return mob


def title_text(text: str, size: int = 48, color=INK) -> ImageMobject:
    return kerning_text(text, size=size, weight="BOLD", color=color)


def body_text(text: str, size: int = 30, color=INK) -> ImageMobject:
    return kerning_text(text, size=size, weight="NORMAL", color=color)


def promo_label(
    text: str,
    size: int = 30,
    color=INK,
    *,
    weight: str = "MEDIUM",
) -> ImageMobject:
    """A compact sentence-case label that preserves Roboto's native kerning."""
    return kerning_text(text, size=size, weight=weight, color=color)


def editorial_overlay(
    title: str,
    lines: list[str],
    *,
    width: float = 5.4,
    title_size: int = 36,
) -> Group:
    """Quiet editorial copy for full-bleed photography, above the subtitle zone."""
    heading = kerning_text(title, size=title_size, weight="MEDIUM", color=WHITE)
    rule = Line(ORIGIN, 1.15 * RIGHT, color=UQAM_BLUE, stroke_width=4)
    body = Group(
        *[
            kerning_text(line, size=25, weight="NORMAL", color=WHITE)
            for line in lines
        ]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    copy = Group(heading, rule, body).arrange(
        DOWN,
        aligned_edge=LEFT,
        buff=0.28,
    )
    if copy.width > width - 0.55:
        raise ValueError(
            f"Editorial overlay copy is too wide ({copy.width:.2f} > {width - 0.55:.2f}); "
            "shorten the text instead of scaling it."
        )

    panel = Rectangle(
        width=width,
        height=copy.height + 0.85,
        stroke_width=0,
        fill_color=BLACK,
        fill_opacity=0.42,
    )
    copy.move_to(panel)
    copy.align_to(panel, LEFT)
    copy.shift(0.32 * RIGHT)
    return Group(panel, copy)


def photo_credit(text: str) -> Group:
    credit = kerning_text(text, size=18, weight="NORMAL", color=WHITE)
    panel = Rectangle(width=credit.width + 0.30, height=credit.height + 0.20,
                      stroke_width=0, fill_color=INK, fill_opacity=1)
    credit.move_to(panel)
    return Group(panel, credit).to_corner(UR, buff=0.35)


def pill(text: str, width: float | None = None, accent=UQAM_BLUE) -> Group:
    label = kerning_text(text, size=27, weight="MEDIUM", color=INK)
    w = width if width is not None else label.width + 0.65
    box = RoundedRectangle(
        width=max(w, 1.5),
        height=0.72,
        corner_radius=0.22,
        stroke_color=accent,
        stroke_width=2.2,
        fill_color=accent,
        fill_opacity=0.08,
    )
    label.move_to(box)
    return Group(box, label)


def simple_person(scale: float = 1.0, accent=UQAM_BLUE) -> VGroup:
    head = Circle(
        radius=0.18 * scale,
        stroke_color=accent,
        stroke_width=3,
        fill_color=WHITE,
        fill_opacity=1,
    )
    body = Line(
        head.get_bottom(),
        head.get_bottom() + 0.62 * scale * DOWN,
        color=accent,
        stroke_width=3,
    )
    arms = Line(
        body.get_center() + 0.10 * scale * UP + 0.23 * scale * LEFT,
        body.get_center() + 0.10 * scale * UP + 0.23 * scale * RIGHT,
        color=accent,
        stroke_width=3,
    )
    leg_l = Line(
        body.get_end(),
        body.get_end() + 0.28 * scale * DOWN + 0.18 * scale * LEFT,
        color=accent,
        stroke_width=3,
    )
    leg_r = Line(
        body.get_end(),
        body.get_end() + 0.28 * scale * DOWN + 0.18 * scale * RIGHT,
        color=accent,
        stroke_width=3,
    )
    return VGroup(head, body, arms, leg_l, leg_r)


def classroom_fallback() -> VGroup:
    board = RoundedRectangle(
        width=4.5,
        height=2.4,
        corner_radius=0.08,
        stroke_color=INK,
        stroke_width=2.5,
        fill_color=SOFT_GREY,
        fill_opacity=0.35,
    )
    formula = MathTex(
        r"\text{question}\ \longrightarrow\ \text{idée}\ \longrightarrow\ \text{solution}",
        font_size=30,
        color=INK,
    ).move_to(board)

    teacher = simple_person(1.0).next_to(board, LEFT, buff=0.55).shift(0.25 * DOWN)

    students = VGroup()
    for x in (-1.6, -0.55, 0.55, 1.6):
        student = simple_person(0.7, accent=INK)
        student.move_to(np.array([x, -2.05, 0]))
        students.add(student)

    return VGroup(board, formula, teacher, students)


def library_fallback() -> VGroup:
    shelf = RoundedRectangle(
        width=4.7,
        height=2.8,
        corner_radius=0.08,
        stroke_color=INK,
        stroke_width=2.5,
        fill_color=SOFT_GREY,
        fill_opacity=0.35,
    )
    books = VGroup()
    xs = np.linspace(-1.7, 1.7, 7)
    heights = [1.25, 1.7, 1.35, 1.8, 1.45, 1.65, 1.25]
    for x, h in zip(xs, heights):
        b = Rectangle(
            width=0.35,
            height=h,
            stroke_color=UQAM_BLUE if len(books) % 3 == 0 else INK,
            stroke_width=2,
            fill_opacity=0.06,
        )
        b.move_to(shelf.get_center() + x * RIGHT + (-0.45 + h / 2 - 0.8) * UP)
        books.add(b)
    table = Line(
        shelf.get_left() + 0.45 * RIGHT + 0.25 * DOWN,
        shelf.get_right() + 0.45 * LEFT + 0.25 * DOWN,
        color=INK,
        stroke_width=2.5,
    )
    return VGroup(shelf, books, table)


def mentor_fallback() -> VGroup:
    mentor = simple_person(1.05, UQAM_BLUE).shift(1.0 * LEFT)
    newcomer = simple_person(1.05, INK).shift(1.0 * RIGHT)
    link = CurvedArrow(
        mentor.get_right() + 0.08 * RIGHT,
        newcomer.get_left() + 0.08 * LEFT,
        angle=-TAU / 7,
        color=UQAM_BLUE,
        stroke_width=3,
        tip_length=0.16,
    )
    return VGroup(mentor, newcomer, link)


def research_network_fallback() -> Group:
    stage_box = RoundedRectangle(
        width=5.15,
        height=0.90,
        corner_radius=0.20,
        stroke_color=UQAM_BLUE,
        stroke_width=2.6,
        fill_color=UQAM_BLUE,
        fill_opacity=1.0,
    )
    stage_text = promo_label(
        "Stages d'été en recherche",
        size=27,
        color=WHITE,
    ).move_to(stage_box)
    stage = Group(stage_box, stage_text).move_to(1.45 * UP)

    def mini_chip(label: str) -> Group:
        text = kerning_text(label, size=18, color=INK)
        box = RoundedRectangle(
            width=max(1.02, text.width + 0.38),
            height=0.48,
            corner_radius=0.14,
            stroke_color=MID_GREY,
            stroke_width=1.4,
            fill_color=WHITE,
            fill_opacity=1,
        )
        text.move_to(box)
        return Group(box, text)

    cirget_box = RoundedRectangle(
        width=5.45,
        height=2.25,
        corner_radius=0.18,
        stroke_color=UQAM_BLUE,
        stroke_width=2.5,
        fill_color=UQAM_BLUE,
        fill_opacity=0.055,
    )
    cirget_copy = Group(
        promo_label("CIRGET", size=34, color=UQAM_BLUE),
        kerning_text("centre interuniversitaire", size=20, color=INK),
        kerning_text("notamment :", size=15, color=MID_GREY),
        Group(
            mini_chip("UQAM"),
            mini_chip("McGill"),
            mini_chip("UdeM"),
            mini_chip("Sherbrooke"),
        ).arrange(RIGHT, buff=0.13),
    ).arrange(DOWN, buff=0.18)
    cirget_copy.move_to(cirget_box)
    cirget = Group(cirget_box, cirget_copy).move_to(2.95 * LEFT + 0.35 * DOWN)

    lacim_box = RoundedRectangle(
        width=4.65,
        height=2.25,
        corner_radius=0.18,
        stroke_color=INK,
        stroke_width=2.0,
        fill_color=SOFT_GREY,
        fill_opacity=0.38,
    )
    lacim_copy = Group(
        promo_label("LaCIM", size=34, color=INK),
        kerning_text("centre de recherche de l'UQAM", size=20, color=INK),
        kerning_text("recherche • communauté scientifique", size=17, color=MID_GREY),
    ).arrange(DOWN, buff=0.19)
    lacim_copy.move_to(lacim_box)
    lacim = Group(lacim_box, lacim_copy).move_to(3.15 * RIGHT + 0.35 * DOWN)

    branches = VGroup(
        Arrow(
            stage_box.get_bottom() + 0.92 * LEFT,
            cirget_box.get_top() + 0.65 * RIGHT,
            buff=0.10,
            color=UQAM_BLUE,
            stroke_width=2.6,
            tip_length=0.13,
        ),
        Arrow(
            stage_box.get_bottom() + 0.92 * RIGHT,
            lacim_box.get_top() + 0.55 * LEFT,
            buff=0.10,
            color=UQAM_BLUE,
            stroke_width=2.6,
            tip_length=0.13,
        ),
    )

    footer = kerning_text(
        "Deux portes d'entrée vers un réseau scientifique qui dépasse le campus",
        size=21,
        color=INK,
    ).move_to(2.15 * DOWN)
    accent = Line(
        3.65 * LEFT,
        3.65 * RIGHT,
        color=UQAM_BLUE,
        stroke_width=2.0,
    ).next_to(footer, UP, buff=0.18)

    return Group(stage, branches, cirget, lacim, accent, footer)


def metro_fallback() -> Group:
    line = Line(4.7 * LEFT, 2.0 * RIGHT, color=METRO_GREEN, stroke_width=10)
    station = Dot(point=0.8 * LEFT, radius=0.16, color=WHITE)
    ring = Circle(radius=0.23, color=METRO_GREEN, stroke_width=4).move_to(station)
    station_label = body_text("Place-des-Arts", 27).next_to(ring, DOWN, buff=0.25)

    building = VGroup(
        Rectangle(
            width=2.6,
            height=2.0,
            stroke_color=UQAM_BLUE,
            stroke_width=3,
            fill_color=UQAM_BLUE,
            fill_opacity=0.08,
        ),
        *[
            Rectangle(
                width=0.36,
                height=0.36,
                stroke_color=UQAM_BLUE,
                stroke_width=1.7,
                fill_opacity=0.05,
            ).move_to(np.array([x, y, 0]))
            for x in (0.45, 1.15, 1.85)
            for y in (-0.45, 0.25, 0.95)
        ],
    )
    # Normalize the window group around the building centre.
    building[1:].shift(1.15 * LEFT + 0.25 * DOWN)
    building.move_to(3.35 * RIGHT + 0.25 * UP)

    building_label = Group(
        body_text("Pavillon", 24),
        body_text("Président-Kennedy", 24),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(
        building, DOWN, buff=0.25
    )

    arrow = Arrow(
        ring.get_right() + 0.18 * RIGHT,
        building.get_left() + 0.15 * LEFT,
        buff=0.15,
        color=UQAM_BLUE,
        stroke_width=4,
        tip_length=0.18,
    )

    return Group(line, station, ring, station_label, building, building_label, arrow)


def international_fallback() -> VGroup:
    globe = Circle(radius=1.25, color=UQAM_BLUE, stroke_width=3)
    vertical = Ellipse(width=0.9, height=2.5, color=UQAM_BLUE, stroke_width=2)
    h1 = Arc(radius=1.10, start_angle=0.13 * PI, angle=0.74 * PI, color=UQAM_BLUE, stroke_width=2)
    h2 = Arc(radius=1.10, start_angle=1.13 * PI, angle=0.74 * PI, color=UQAM_BLUE, stroke_width=2)
    h1.stretch(0.48, 1)
    h2.stretch(0.48, 1)
    group = VGroup(globe, vertical, h1, h2)
    people = VGroup(
        simple_person(0.55, INK).shift(2.0 * LEFT + 0.3 * DOWN),
        simple_person(0.55, UQAM_BLUE).shift(2.0 * RIGHT + 0.3 * DOWN),
    )
    return VGroup(group, people)


def support_classy_fallback() -> VGroup:
    """A high-key support fallback that does not imitate people or a workflow."""
    background = Rectangle(
        width=config.frame_width,
        height=config.frame_height,
        stroke_width=0,
        fill_color=WHITE,
        fill_opacity=1,
    )
    rule = Line(
        2.25 * RIGHT,
        3.55 * RIGHT,
        color=UQAM_BLUE,
        stroke_width=5,
    ).shift(1.25 * UP)
    return VGroup(background, rule)


def library_classy_fallback() -> VGroup:
    """A similarly restrained fallback when no approved library photo is available."""
    background = Rectangle(
        width=config.frame_width,
        height=config.frame_height,
        stroke_width=0,
        fill_color=SOFT_GREY,
        fill_opacity=1,
    )
    rule = Line(
        2.25 * RIGHT,
        3.55 * RIGHT,
        color=UQAM_BLUE,
        stroke_width=5,
    ).shift(1.25 * UP)
    return VGroup(background, rule)


def editorial_photo(
    filename: str,
    fallback: Mobject,
    *,
    width: float,
    max_height: float,
) -> Group:
    """Return an unframed editorial image while preserving its aspect ratio."""
    path = ASSET_DIR / filename
    if (not USE_REAL_PHOTOS) or (not path.exists()):
        fallback.scale_to_fit_width(min(width, fallback.width))
        if fallback.height > max_height:
            fallback.scale_to_fit_height(max_height)
        return Group(fallback)

    image = ImageMobject(str(path))
    image.scale_to_fit_width(width)
    if image.height > max_height:
        image.scale_to_fit_height(max_height)
    return Group(image)


def editorial_caption(title: str, detail: str, *, width: float) -> Group:
    """Small magazine-style caption block for the editorial support spread."""
    heading = kerning_text(title, size=24, weight="MEDIUM", color=INK)
    sub = kerning_text(detail, size=17, weight="NORMAL", color=MID_GREY)
    copy = Group(heading, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    if copy.width > width - 0.40:
        raise ValueError(f"Editorial caption is too wide ({copy.width:.2f}); shorten copy.")
    panel = RoundedRectangle(
        width=width,
        height=copy.height + 0.32,
        corner_radius=0.05,
        stroke_width=0,
        fill_color=WHITE,
        fill_opacity=0.94,
    )
    copy.move_to(panel).align_to(panel, LEFT).shift(0.20 * RIGHT)
    return Group(panel, copy)


def photo_card(
    filename: str,
    fallback: Mobject,
    width: float = 5.4,
    height: float = 3.5,
    credit: str | None = None,
) -> Group:
    """
    Prefer a local curated UQAM photo; otherwise return the supplied vector
    fallback. No network access is attempted by the scene.
    """
    path = ASSET_DIR / filename
    if (not USE_REAL_PHOTOS) or (not path.exists()):
        fallback.scale_to_fit_width(width)
        if fallback.height > height:
            fallback.scale_to_fit_height(height)
        return Group(fallback)

    image = ImageMobject(str(path))
    image.scale_to_fit_width(width)
    if image.height > height:
        image.scale_to_fit_height(height)

    frame = RoundedRectangle(
        width=image.width + 0.14,
        height=image.height + 0.14,
        corner_radius=0.10,
        stroke_color=MID_GREY,
        stroke_width=1.5,
    ).move_to(image)

    group = Group(image, frame)

    if SHOW_PHOTO_CREDITS and credit:
        credit_text = kerning_text(credit, size=14, color=MID_GREY).next_to(
            frame, DOWN, buff=0.08, aligned_edge=RIGHT
        )
        group.add(credit_text)

    return group



def full_bleed_photo(filename: str, fallback: Mobject | None = None) -> Group:
    """Return a photo filling the 16:9 frame, cropped naturally by the camera."""
    path = ASSET_DIR / filename
    if USE_REAL_PHOTOS and path.exists():
        focal = (0.5, 0.5) if filename == "president_kennedy.jpg" else (0.5, 0.48)
        pixels = np.asarray(cover_image(path, (config.pixel_width, config.pixel_height), focal))
        image = ImageMobject(pixels)
        factor = max(config.frame_width / image.width, config.frame_height / image.height)
        image.scale(factor).move_to(ORIGIN)
        group = Group(image)
        group.is_real_photo = True
        return group

    if fallback is None:
        fallback = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_opacity=0,
            fill_color=SOFT_GREY,
            fill_opacity=1,
        )
    is_full_frame = (
        abs(fallback.width - config.frame_width) < 0.05
        and abs(fallback.height - config.frame_height) < 0.05
    )
    if not is_full_frame:
        fallback.scale_to_fit_width(min(config.frame_width - 0.5, fallback.width))
    group = Group(fallback)
    group.is_real_photo = False
    return group


def clean_fact(text: str, detail: str | None = None, width: float = 4.7) -> Group:
    """A restrained fact row: no coloured pill and no decorative effects."""
    dot = Dot(radius=0.065, color=UQAM_BLUE)
    main = kerning_text(text, size=25, weight="MEDIUM", color=INK)
    row = Group(dot, main).arrange(RIGHT, buff=0.18)
    if detail:
        sub = kerning_text(detail, size=18, color=MID_GREY)
        block = Group(row, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    else:
        block = Group(row)
    if block.width > width:
        raise ValueError(
            f"Fact copy is too wide ({block.width:.2f} > {width:.2f}); "
            "shorten it instead of scaling typography."
        )
    return block


def named_person_label(name: str, role: str, width: float = 4.0) -> Group:
    """Neutral UQAM-style identity super, kept above the subtitle safe zone."""
    name_mob = kerning_text(name, size=22, weight="MEDIUM", color=INK)
    role_mob = kerning_text(role, size=16, color=MID_GREY)
    copy = Group(name_mob, role_mob).arrange(
        DOWN, aligned_edge=LEFT, buff=0.07
    )
    panel = RoundedRectangle(
        width=max(width, copy.width + 0.38),
        height=copy.height + 0.28,
        corner_radius=0.06,
        stroke_width=0,
        fill_color=WHITE,
        fill_opacity=0.92,
    )
    copy.move_to(panel).align_to(panel, LEFT).shift(0.18 * RIGHT)
    return Group(panel, copy)


def portrait_fallback(label: str) -> Group:
    person = simple_person(1.65, UQAM_BLUE)
    text = body_text(label, 22, MID_GREY)
    return Group(person, text).arrange(DOWN, buff=0.35)


def section_label(text: str) -> ImageMobject:
    return kerning_text(text, size=28, weight="BOLD", color=UQAM_BLUE)


# ---------------------------------------------------------------------------
# Main scene
# ---------------------------------------------------------------------------

class BacMathUQAMFR(VoiceoverScene):
    """
    16:9 promotional master, expected duration about 70–90 seconds with MAI
    Soleil around +2%. The exact duration remains narration-driven.
    """

    def construct(self):
        configure_azure_speech_environment(PROMO_VOICE)
        self.set_speech_service(AzureService(**azure_service_kwargs(PROMO_VOICE)))
        self.semantic_shots = []
        self.semantic_acts = []
        for key in NARRATION_SEGMENTS:
            self._act_start = float(self.renderer.time)
            getattr(self, "act_" + key)()
            self.semantic_acts.append({"act": key, "start": self._act_start, "end": float(self.renderer.time)})
        self.wait(1.0)
        timeline = Path(os.getenv("UQAM_TIMELINE_PATH", str(REPO_ROOT / "dist/bac_math_uqam_fr/semantic_timeline.json")))
        timeline.parent.mkdir(parents=True, exist_ok=True)
        timeline.write_text(json.dumps({"timing_source": "rendered scene clock and separately synthesized speech units", "acts": self.semantic_acts, "shots": self.semantic_shots, "duration": float(self.renderer.time), "listening_review": "pending"}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---- narration --------------------------------------------------------

    def record_photo(self, filename, start, end, displayed_credit=None):
        self.semantic_shots.append({"filename": filename, "start": start, "end": end,
                                    "displayed_credit": displayed_credit,
                                    "placement": "upper-right protected panel" if displayed_credit else "distribution description"})

    def narrate_unit(self, segment, index):
        return self.narrate(NARRATION_BEATS[segment][index], rate=NARRATION_RATES[segment])

    def narrate(self, text: str, *, rate: str | None = None):
        spoken = ssml(
            text,
            rate=rate or PROMO_RATE,
            locale=VOICE_LOCALES.get(PROMO_VOICE, "fr-CA"),
        )
        return self.voiceover(
            text=spoken,
            subcaption=strip_ssml(spoken),
            max_subcaption_len=42,
            subcaption_buff=0.08,
        )

    # ---- act 1: hook ------------------------------------------------------

    def act_hook(self):
        # Give the viewer a short visual arrival before the narration begins.
        visual = full_bleed_photo("campus_central_uqam.jpg", classroom_fallback())
        scrim = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=0.34,
        )

        heading = kerning_text(
            "Mathématiques à l'UQAM", size=54, weight="MEDIUM", color=WHITE
        ).to_edge(LEFT, buff=0.75).shift(0.45 * DOWN)

        sub = kerning_text(
            "rigueur  •  proximité  •  Montréal", size=25, color=WHITE
        ).next_to(heading, DOWN, buff=0.22, aligned_edge=LEFT)

        context_credit = photo_credit("Campus de l’UQAM · Photo : UQAM")
        self.play(FadeIn(visual), FadeIn(context_credit), run_time=0.65)
        self.wait(0.22)

        narration = NARRATION_SEGMENTS["hook"]

        with self.narrate(narration, rate=NARRATION_RATES["hook"]) as tracker:
            zoom_time = min(1.55, tracker.duration * 0.36)
            title_time = min(1.15, tracker.duration * 0.27)
            self.play(
                visual.animate.scale(1.018),
                run_time=zoom_time,
                rate_func=linear,
            )
            self.play(
                FadeIn(scrim),
                FadeIn(heading, shift=0.08 * UP),
                FadeIn(sub, shift=0.06 * UP),
                run_time=title_time,
            )
            remaining = tracker.duration - zoom_time - title_time
            if remaining > 0:
                self.wait(remaining)

        self.play(
            FadeOut(visual),
            FadeOut(scrim),
            FadeOut(heading),
            FadeOut(sub),
            FadeOut(context_credit),
            run_time=0.35,
        )
        self.record_photo("campus_central_uqam.jpg", self._act_start, float(self.renderer.time), "Campus de l’UQAM · Photo : UQAM")

    # ---- act 2: teaching / proximity -------------------------------------

    def act_human_scale(self):
        heading = title_text("Exigeant, mais à taille humaine", 43)
        heading.to_edge(UP, buff=0.52).to_edge(LEFT, buff=0.70)

        # The two portraits establish a human connection, then leave the frame
        # before the longer teaching explanation. Names and roles follow UQAM's
        # recommended super format and avoid an anonymous-stock-photo effect.
        student = photo_card(
            "lisa_berger.jpg",
            portrait_fallback("étudiante en mathématiques"),
            width=3.55,
            height=3.30,
        )
        professor = photo_card(
            "francois_bergeron.jpg",
            portrait_fallback("professeur de mathématiques"),
            width=3.55,
            height=3.30,
        )

        portraits = Group(student, professor).arrange(RIGHT, buff=0.38)
        portraits.move_to(0.18 * UP)

        student_role = named_person_label(
            "Lisa Berger",
            "baccalauréat en mathématiques",
            width=3.65,
        )
        professor_role = named_person_label(
            "François Bergeron",
            "professeur de mathématiques",
            width=3.75,
        )
        student_role.next_to(student, DOWN, buff=0.12)
        professor_role.next_to(professor, DOWN, buff=0.12)

        verbs = Group(
            promo_label("Échanger", size=34, color=UQAM_BLUE),
            promo_label("Pratiquer", size=34, color=UQAM_BLUE),
            promo_label("Progresser", size=34, color=UQAM_BLUE),
        ).arrange(RIGHT, buff=0.85)
        verbs.shift(1.05 * UP)

        facts = Group(
            clean_fact(
                "petits groupes",
                "approche de la Faculté",
                width=3.65,
            ),
            clean_fact(
                "travaux pratiques",
                "accompagner les apprentissages",
                width=3.65,
            ),
            clean_fact(
                "travail supervisé",
                "dans les concentrations",
                width=3.65,
            ),
        ).arrange(RIGHT, buff=0.50)
        facts.next_to(verbs, DOWN, buff=0.75)

        access = kerning_text(
            "enseignants accessibles • collaboration • questions en classe",
            size=23,
            color=INK,
        ).next_to(facts, DOWN, buff=0.55)

        narration = NARRATION_SEGMENTS["human_scale"]

        with self.narrate(narration):
            self.play(
                FadeIn(heading),
                FadeIn(student, shift=0.08 * RIGHT),
                FadeIn(professor, shift=0.08 * LEFT),
                FadeIn(student_role),
                FadeIn(professor_role),
                run_time=1.0,
            )
            self.wait(TEACHING_PORTRAIT_HOLD)
            portrait_end = float(self.renderer.time) + 0.45
            self.record_photo("lisa_berger.jpg", self._act_start, portrait_end)
            self.record_photo("francois_bergeron.jpg", self._act_start, portrait_end)
            self.play(
                FadeOut(student),
                FadeOut(professor),
                FadeOut(student_role),
                FadeOut(professor_role),
                run_time=0.45,
            )
            self.play(
                LaggedStart(
                    *(FadeIn(verb, shift=0.08 * UP) for verb in verbs),
                    lag_ratio=0.16,
                ),
                run_time=1.15,
            )
            self.play(
                LaggedStart(
                    *(FadeIn(fact, shift=0.06 * UP) for fact in facts),
                    lag_ratio=0.16,
                ),
                run_time=1.35,
            )
            self.play(FadeIn(access, shift=0.05 * UP), run_time=0.60)

        self.play(
            FadeOut(Group(heading, verbs, facts, access)),
            run_time=0.35,
        )

    # ---- act 3: support / mentoring --------------------------------------

    def act_support(self):
        """A coherent editorial support page built from real UQAM imagery."""
        heading = title_text("On n'avance pas seul.", 44)
        heading.to_edge(UP, buff=0.48).to_edge(LEFT, buff=0.68)
        accent = Line(
            heading.get_left(),
            heading.get_left() + 1.10 * RIGHT,
            color=UQAM_BLUE,
            stroke_width=4,
        ).next_to(heading, DOWN, buff=0.16, aligned_edge=LEFT)

        support_photo = editorial_photo(
            "support_students.jpg", support_classy_fallback(), width=6.45, max_height=3.80
        )
        support_photo.to_edge(LEFT, buff=0.68).shift(0.48 * DOWN)
        support_caption = editorial_caption(
            "Accueil et accompagnement",
            "prendre ses repères dès l'arrivée",
            width=4.50,
        )
        support_caption.move_to(
            support_photo.get_corner(DL) + 2.04 * RIGHT + 0.48 * UP
        )

        peer = Group(
            promo_label("Mentorat par les pairs", size=27, color=INK),
            kerning_text(
                "un accompagnement pour mieux s'orienter", size=17, color=MID_GREY
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        learning = Group(
            promo_label("Soutien à l'apprentissage", size=27, color=INK),
            kerning_text("des ressources quand on en a besoin", size=17, color=MID_GREY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        support_facts = Group(peer, learning).arrange(DOWN, aligned_edge=LEFT, buff=0.40)
        support_facts.to_edge(RIGHT, buff=0.66).shift(1.05 * UP)

        library_photo = editorial_photo(
            "bibliotheque_sciences_2026.jpg", library_classy_fallback(), width=4.55, max_height=2.30
        )
        library_photo.to_edge(RIGHT, buff=0.66).shift(1.18 * DOWN)
        library_caption = Group(
            promo_label("Bibliothèque des sciences", size=23, color=INK),
            kerning_text("travailler seul ou en équipe", size=17, color=MID_GREY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        library_caption.next_to(library_photo, DOWN, buff=0.16, aligned_edge=LEFT)

        narration = NARRATION_SEGMENTS["support"]
        with self.narrate(narration, rate=NARRATION_RATES["support"]) as tracker:
            self.play(FadeIn(heading), Create(accent), run_time=0.55)
            support_start = float(self.renderer.time)
            self.play(
                FadeIn(support_photo, shift=0.08 * RIGHT),
                FadeIn(support_caption, shift=0.05 * UP),
                run_time=0.80,
            )
            self.play(FadeIn(peer, shift=0.06 * UP), run_time=0.65)
            self.play(FadeIn(learning, shift=0.06 * UP), run_time=0.65)
            library_start = float(self.renderer.time)
            self.play(
                FadeIn(library_photo, shift=0.06 * LEFT),
                FadeIn(library_caption, shift=0.05 * UP),
                run_time=0.80,
            )
            remaining = tracker.duration - (0.55 + 0.80 + 0.65 + 0.65 + 0.80)
            if remaining > 0:
                self.wait(max(SUPPORT_PAGE_HOLD, remaining))

        self.play(
            FadeOut(
                Group(
                    heading,
                    accent,
                    support_photo,
                    support_caption,
                    support_facts,
                    library_photo,
                    library_caption,
                )
            ),
            run_time=0.38,
        )
        self.record_photo("support_students.jpg", support_start, float(self.renderer.time))
        self.record_photo("bibliotheque_sciences_2026.jpg", library_start, float(self.renderer.time))

    # ---- act 4: research --------------------------------------------------

    def act_research(self):
        heading = title_text("La recherche, dès le bac", 44)
        heading.to_edge(UP, buff=0.52).to_edge(LEFT, buff=0.70)
        hub = photo_card("research_math.jpg", research_network_fallback(), width=6.15, height=3.65)
        hub.to_edge(LEFT, buff=0.65).shift(0.05 * DOWN)
        facts = Group(
            clean_fact("stages d'été en recherche", "des possibilités à explorer"),
            clean_fact("CIRGET", "centre interuniversitaire"),
            clean_fact("LaCIM", "centre de recherche de l'UQAM"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        facts.to_edge(RIGHT, buff=0.72)
        start = float(self.renderer.time)
        with self.narrate_unit("research", 0):
            self.play(FadeIn(heading), FadeIn(hub), FadeIn(facts), run_time=0.75)
        # Hold the fully readable photo and facts through a complete second unit.
        with self.narrate_unit("research", 1):
            pass
        self.play(FadeOut(hub), FadeOut(facts), run_time=0.4)
        self.record_photo("research_math.jpg", start, float(self.renderer.time))
        pathway = research_network_fallback().shift(0.10 * DOWN)
        with self.narrate_unit("research", 2):
            self.play(FadeIn(pathway), run_time=0.7)
        self.play(FadeOut(Group(heading, pathway)), run_time=0.38)

    # ---- act 5: Montréal / international ---------------------------------

    def act_montreal(self):
        # Each full-bleed plan remains until its separately synthesized unit ends.
        plans = (
            ("sciences_biologiques_uqam.jpg", "Complexe des sciences Pierre-Dansereau", "Pavillon des Sciences biologiques · métro Place-des-Arts", "Photo : UQAM", metro_fallback),
            ("allo_pk.jpg", "Des repères dès l'arrivée", "Espace d'accueil Allô!", "Photo : programme Allô! · UQAM", international_fallback),
            ("international_students.jpg", "Une communauté ouverte sur le monde", "Ressources de la Faculté des sciences", "Photo : Faculté des sciences · UQAM", international_fallback),
        )
        for index, (filename, title, detail, credit_text, fallback) in enumerate(plans):
            photo = full_bleed_photo(filename, fallback())
            copy = editorial_overlay(title, [detail], width=11.5, title_size=36)
            copy.to_edge(LEFT, buff=0.65).shift(0.65 * UP)
            credit = photo_credit(credit_text)
            start = float(self.renderer.time)
            with self.narrate_unit("montreal", index):
                self.play(FadeIn(photo), FadeIn(copy), FadeIn(credit), run_time=0.65)
            self.play(FadeOut(photo), FadeOut(copy), FadeOut(credit), run_time=0.35)
            self.record_photo(filename, start, float(self.renderer.time), credit_text)

    # ---- act 6: close -----------------------------------------------------

    def act_close(self):
        lines = Group(*[kerning_text(text, size=41, weight="BOLD", color=UQAM_BLUE if index == 1 else INK) for index, text in enumerate(NARRATION_BEATS["close"][:4])]).arrange(DOWN, buff=0.27).move_to(0.20 * UP)
        for index, line in enumerate(lines):
            with self.narrate_unit("close", index):
                self.play(FadeIn(line, shift=0.07 * UP), run_time=0.4)
        # Do not remove the summary while its corresponding words are still spoken.
        self.play(FadeOut(lines), run_time=0.4)
        slogan = title_text("Aller loin, sans avancer seul.", 43).move_to(1.02 * UP)
        programme = body_text("Baccalauréat en mathématiques", 28, UQAM_BLUE).next_to(slogan, DOWN, buff=0.42)
        cta = Group(body_text("Découvrir le programme", 23, INK), body_text(CTA_DISPLAY, 23, UQAM_BLUE)).arrange(DOWN, buff=0.14).next_to(programme, DOWN, buff=0.37)
        with self.narrate_unit("close", 4):
            self.play(FadeIn(slogan), FadeIn(programme), FadeIn(cta), run_time=0.65)
        self.wait(FINAL_CARD_HOLD)
        if USE_OFFICIAL_LOGO and LOGO_APPROVED and LOGO_PATH.exists():
            self.play(FadeOut(slogan), FadeOut(programme), FadeOut(cta), run_time=0.35)
            logo = ImageMobject(str(LOGO_PATH)).scale_to_fit_width(2.9).move_to(ORIGIN)
            self.play(FadeIn(logo), run_time=0.5)
            self.wait(1.2)


class TypographyDiagnostic(Scene):
    """A compact visual comparison used to confirm the kerning renderer."""

    def construct(self):
        tests = [
            "Mathématiques à l'UQAM",
            "Exigeant, mais à taille humaine",
            "enseignants accessibles",
            "prendre ses repères",
            "Bibliothèque des sciences",
            "Complexe des sciences Pierre-Dansereau",
            "Aller loin, sans avancer seul.",
        ]
        rows = Group()
        for text in tests:
            # Red is Pango's diagnostic reference; blue is the production
            # Pillow/FreeType copy. No Pango text is used in the promo itself.
            pango = Text(text, font=FONT, font_size=30, color=RED)
            pillow = kerning_text(text, size=30, weight="NORMAL", color=UQAM_BLUE)
            rows.add(Group(pango, pillow).arrange(DOWN, aligned_edge=LEFT, buff=0.10))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        rows.scale_to_fit_height(6.8)
        self.add(rows)
