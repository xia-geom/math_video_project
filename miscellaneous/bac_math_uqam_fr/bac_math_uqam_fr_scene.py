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
    classroom_math.jpg
    francois_bergeron.jpg
    lisa_berger.jpg
    research_math.jpg
    support_students.jpg        # optional; approved UQAM student-life photo
    bibliotheque_sciences.jpg   # optional; UQAM Bibliothèque des sciences
    president_kennedy.jpg
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
import os
from pathlib import Path

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService
from manimpango import register_font

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
MONTREAL_BUILDING_HOLD = float(
    os.getenv("UQAM_MONTREAL_BUILDING_HOLD", "2.00")
)
MONTREAL_PHOTO_HOLD = float(os.getenv("UQAM_MONTREAL_PHOTO_HOLD", "1.70"))

if FONT_PATH.exists():
    register_font(str(FONT_PATH))

UQAM_BLUE = "#0079BE"      # official UQAM blue: RGB 0/121/190
INK = "#312F2D"            # close to UQAM's dark grey band colour
SOFT_GREY = "#F1F3F5"
MID_GREY = "#8A8F94"
METRO_GREEN = "#00A651"    # semantic use only: Montréal green line

NARRATION_SEGMENTS = {
    "hook": (
        "À l'UQAM, on peut faire des mathématiques exigeantes "
        "<break time='220ms'/> sans se perdre dans la foule."
    ),
    "human_scale": (
        "Les groupes sont à taille humaine, les enseignants accessibles, "
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
        "Tout cela au pavillon Président-Kennedy, en plein Quartier des spectacles, "
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

Text.set_default(font=FONT, color=INK)
Tex.set_default(color=INK)
MathTex.set_default(color=INK)


# ---------------------------------------------------------------------------
# Small reusable visual helpers
# ---------------------------------------------------------------------------

def title_text(text: str, size: int = 48, color=INK) -> Text:
    return Text(text, font=FONT, font_size=size, weight="BOLD", color=color)


def body_text(text: str, size: int = 30, color=INK) -> Text:
    return Text(text, font=FONT, font_size=size, color=color)


def promo_label(
    text: str,
    size: int = 30,
    color=INK,
    *,
    weight: str = "MEDIUM",
) -> Text:
    """A compact sentence-case label that preserves Roboto's native kerning."""
    return Text(
        text,
        font=FONT,
        font_size=size,
        weight=weight,
        color=color,
    )


def editorial_overlay(
    title: str,
    lines: list[str],
    *,
    width: float = 5.4,
) -> VGroup:
    """Quiet editorial copy for full-bleed photography, above the subtitle zone."""
    heading = Text(
        title,
        font=FONT,
        font_size=39,
        weight="MEDIUM",
        color=WHITE,
    )
    rule = Line(ORIGIN, 1.15 * RIGHT, color=UQAM_BLUE, stroke_width=4)
    body = VGroup(
        *[
            Text(
                line,
                font=FONT,
                font_size=25,
                weight="NORMAL",
                color=WHITE,
            )
            for line in lines
        ]
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    copy = VGroup(heading, rule, body).arrange(
        DOWN,
        aligned_edge=LEFT,
        buff=0.28,
    )
    if copy.width > width - 0.55:
        copy.scale_to_fit_width(width - 0.55)

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
    return VGroup(panel, copy)


def photo_credit(text: str) -> Text:
    """Place mandatory full-bleed photo credits outside the subtitle safe zone."""
    credit = Text(text, font=FONT, font_size=14, color=WHITE)
    credit.to_corner(UR, buff=0.28)
    return credit


def pill(text: str, width: float | None = None, accent=UQAM_BLUE) -> VGroup:
    label = Text(text, font=FONT, font_size=27, weight="MEDIUM", color=INK)
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
    return VGroup(box, label)


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


def research_network_fallback() -> VGroup:
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
    stage = VGroup(stage_box, stage_text).move_to(1.45 * UP)

    def mini_chip(label: str) -> VGroup:
        text = Text(label, font=FONT, font_size=18, color=INK)
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
        return VGroup(box, text)

    cirget_box = RoundedRectangle(
        width=5.45,
        height=2.25,
        corner_radius=0.18,
        stroke_color=UQAM_BLUE,
        stroke_width=2.5,
        fill_color=UQAM_BLUE,
        fill_opacity=0.055,
    )
    cirget_copy = VGroup(
        promo_label("CIRGET", size=34, color=UQAM_BLUE),
        Text(
            "centre interuniversitaire",
            font=FONT,
            font_size=20,
            color=INK,
        ),
        Text(
            "notamment :",
            font=FONT,
            font_size=15,
            color=MID_GREY,
        ),
        VGroup(
            mini_chip("UQAM"),
            mini_chip("McGill"),
            mini_chip("UdeM"),
            mini_chip("Sherbrooke"),
        ).arrange(RIGHT, buff=0.13),
    ).arrange(DOWN, buff=0.18)
    cirget_copy.move_to(cirget_box)
    cirget = VGroup(cirget_box, cirget_copy).move_to(2.95 * LEFT + 0.35 * DOWN)

    lacim_box = RoundedRectangle(
        width=4.65,
        height=2.25,
        corner_radius=0.18,
        stroke_color=INK,
        stroke_width=2.0,
        fill_color=SOFT_GREY,
        fill_opacity=0.38,
    )
    lacim_copy = VGroup(
        promo_label("LaCIM", size=34, color=INK),
        Text(
            "centre de recherche de l'UQAM",
            font=FONT,
            font_size=20,
            color=INK,
        ),
        Text(
            "recherche • communauté scientifique",
            font=FONT,
            font_size=17,
            color=MID_GREY,
        ),
    ).arrange(DOWN, buff=0.19)
    lacim_copy.move_to(lacim_box)
    lacim = VGroup(lacim_box, lacim_copy).move_to(3.15 * RIGHT + 0.35 * DOWN)

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

    footer = Text(
        "Deux portes d'entrée vers un réseau scientifique qui dépasse le campus",
        font=FONT,
        font_size=21,
        color=INK,
    ).move_to(2.15 * DOWN)
    accent = Line(
        3.65 * LEFT,
        3.65 * RIGHT,
        color=UQAM_BLUE,
        stroke_width=2.0,
    ).next_to(footer, UP, buff=0.18)

    return VGroup(stage, branches, cirget, lacim, accent, footer)


def metro_fallback() -> VGroup:
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

    building_label = Text(
        "Pavillon\nPrésident-Kennedy",
        font=FONT,
        font_size=24,
        color=INK,
        line_spacing=0.9,
    ).next_to(building, DOWN, buff=0.25)

    arrow = Arrow(
        ring.get_right() + 0.18 * RIGHT,
        building.get_left() + 0.15 * LEFT,
        buff=0.15,
        color=UQAM_BLUE,
        stroke_width=4,
        tip_length=0.18,
    )

    return VGroup(line, station, ring, station_label, building, building_label, arrow)


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
        credit_text = Text(
            credit,
            font=FONT,
            font_size=14,
            color=MID_GREY,
        ).next_to(frame, DOWN, buff=0.08, aligned_edge=RIGHT)
        group.add(credit_text)

    return group



def full_bleed_photo(filename: str, fallback: Mobject | None = None) -> Group:
    """Return a photo filling the 16:9 frame, cropped naturally by the camera."""
    path = ASSET_DIR / filename
    if USE_REAL_PHOTOS and path.exists():
        image = ImageMobject(str(path))
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


def clean_fact(text: str, detail: str | None = None, width: float = 4.7) -> VGroup:
    """A restrained fact row: no coloured pill and no decorative effects."""
    dot = Dot(radius=0.065, color=UQAM_BLUE)
    main = Text(text, font=FONT, font_size=25, weight="MEDIUM", color=INK)
    row = VGroup(dot, main).arrange(RIGHT, buff=0.18)
    if detail:
        sub = Text(detail, font=FONT, font_size=18, color=MID_GREY)
        block = VGroup(row, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
    else:
        block = VGroup(row)
    if block.width > width:
        block.scale_to_fit_width(width)
    return block


def named_person_label(name: str, role: str, width: float = 4.0) -> VGroup:
    """Neutral UQAM-style identity super, kept above the subtitle safe zone."""
    name_mob = Text(name, font=FONT, font_size=22, weight="MEDIUM", color=INK)
    role_mob = Text(role, font=FONT, font_size=16, color=MID_GREY)
    copy = VGroup(name_mob, role_mob).arrange(
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
    return VGroup(panel, copy)


def portrait_fallback(label: str) -> VGroup:
    person = simple_person(1.65, UQAM_BLUE)
    text = body_text(label, 22, MID_GREY)
    return VGroup(person, text).arrange(DOWN, buff=0.35)


def section_label(text: str) -> Text:
    return Text(
        text,
        font=FONT,
        font_size=28,
        weight="BOLD",
        color=UQAM_BLUE,
    )


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

        self.act_hook()
        self.act_human_scale()
        self.act_research()
        self.act_support()
        self.act_montreal()
        self.act_close()

        self.wait(1.0)

    # ---- narration --------------------------------------------------------

    def narrate(self, text: str):
        spoken = ssml(
            text,
            rate=PROMO_RATE,
            locale=VOICE_LOCALES.get(PROMO_VOICE, "fr-CA"),
        )
        return self.voiceover(
            text=spoken,
            subcaption=strip_ssml(spoken),
            max_subcaption_len=52,
            subcaption_buff=0.08,
        )

    # ---- act 1: hook ------------------------------------------------------

    def act_hook(self):
        # UQAM's video guide recommends beginning with a visually strong shot,
        # not static title typography. The competition image is used only as
        # "mathematics happening at UQAM", never as evidence of a normal class.
        visual = full_bleed_photo("classroom_math.jpg", classroom_fallback())
        scrim = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=0.34,
        )

        heading = Text(
            "Mathématiques à l'UQAM",
            font=FONT,
            font_size=54,
            weight="MEDIUM",
            color=WHITE,
        ).to_edge(LEFT, buff=0.75).shift(0.45 * DOWN)

        sub = Text(
            "rigueur  •  proximité  •  Montréal",
            font=FONT,
            font_size=25,
            color=WHITE,
        ).next_to(heading, DOWN, buff=0.22, aligned_edge=LEFT)

        narration = NARRATION_SEGMENTS["hook"]

        with self.narrate(narration) as tracker:
            self.play(FadeIn(visual), run_time=min(0.75, tracker.duration * 0.15))
            self.play(
                visual.animate.scale(1.025),
                run_time=min(1.5, tracker.duration * 0.28),
                rate_func=linear,
            )
            self.play(
                FadeIn(scrim),
                FadeIn(heading, shift=0.10 * UP),
                FadeIn(sub, shift=0.08 * UP),
                run_time=min(1.25, tracker.duration * 0.25),
            )

        self.play(
            FadeOut(visual),
            FadeOut(scrim),
            FadeOut(heading),
            FadeOut(sub),
            run_time=0.35,
        )

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
            "baccalauréat en mathématiques • portrait UQAM 2024",
            width=3.65,
        )
        professor_role = named_person_label(
            "François Bergeron",
            "professeur • Département de mathématiques",
            width=3.75,
        )
        student_role.next_to(student, DOWN, buff=0.12)
        professor_role.next_to(professor, DOWN, buff=0.12)

        verbs = VGroup(
            promo_label("Échanger", size=34, color=UQAM_BLUE),
            promo_label("Pratiquer", size=34, color=UQAM_BLUE),
            promo_label("Progresser", size=34, color=UQAM_BLUE),
        ).arrange(RIGHT, buff=0.85)
        verbs.shift(1.05 * UP)

        facts = VGroup(
            clean_fact(
                "petits groupes",
                "formule d'enseignement de la Faculté",
                width=3.65,
            ),
            clean_fact(
                "2 h de TP par semaine",
                "dans les cours du premier niveau",
                width=3.65,
            ),
            clean_fact(
                "travail supervisé",
                "dans les cours de concentration suivants",
                width=3.65,
            ),
        ).arrange(RIGHT, buff=0.50)
        facts.next_to(verbs, DOWN, buff=0.75)

        access = Text(
            "enseignants accessibles • collaboration • questions en classe",
            font=FONT,
            font_size=23,
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
        """Show student support as a calm editorial sequence, never a dashboard."""
        human_photo = full_bleed_photo(
            "support_students.jpg",
            support_classy_fallback(),
        )
        human_scrim = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=0.15,
        )
        human_copy = editorial_overlay(
            "On n'avance pas seul.",
            [
                "Mentorat par les pairs",
                "Soutien à l'apprentissage",
            ],
            width=5.35,
        )
        human_copy.to_edge(LEFT, buff=0.60).shift(0.55 * UP)

        library_photo = full_bleed_photo(
            "bibliotheque_sciences.jpg",
            library_classy_fallback(),
        )
        library_scrim = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=0.12,
        )
        library_copy = editorial_overlay(
            "Bibliothèque des sciences",
            [
                "Des espaces pour travailler",
                "seul ou en équipe",
            ],
            width=5.15,
        )
        library_copy.to_edge(LEFT, buff=0.60).shift(0.55 * UP)

        # The fallbacks are deliberately neutral full-frame fields, so the
        # same short editorial copy remains legible in either rendering path.
        human_beat = Group(human_photo, human_scrim, human_copy)
        library_beat = Group(library_photo, library_scrim, library_copy)

        narration = NARRATION_SEGMENTS["support"]

        with self.narrate(narration) as tracker:
            phase_one = tracker.duration * 0.58
            phase_two = tracker.duration * 0.42

            self.play(
                FadeIn(human_beat),
                run_time=0.75,
            )
            self.wait(max(SUPPORT_HUMAN_HOLD, phase_one - 1.30))
            self.play(
                FadeOut(human_beat),
                FadeIn(library_beat),
                run_time=0.55,
            )
            self.wait(max(SUPPORT_LIBRARY_HOLD, phase_two - 0.95))

        self.play(
            FadeOut(library_beat),
            run_time=0.38,
        )

    # ---- act 4: research --------------------------------------------------

    def act_research(self):
        heading = title_text("La recherche, dès le bac", 44)
        heading.to_edge(UP, buff=0.52).to_edge(LEFT, buff=0.70)

        hub = photo_card(
            "research_math.jpg",
            research_network_fallback(),
            width=6.15,
            height=3.65,
        )
        hub.to_edge(LEFT, buff=0.65).shift(0.05 * DOWN)

        research_facts = VGroup(
            clean_fact("stages d'été en recherche", "possibilités au CIRGET et au LaCIM"),
            clean_fact("CIRGET", "centre interuniversitaire"),
            clean_fact("LaCIM", "centre de recherche de l'UQAM"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        research_facts.to_edge(RIGHT, buff=0.72).shift(0.08 * DOWN)

        pathway = research_network_fallback()
        pathway.shift(0.10 * DOWN)

        narration = NARRATION_SEGMENTS["research"]

        with self.narrate(narration):
            self.play(
                FadeIn(heading),
                FadeIn(hub, shift=0.10 * RIGHT),
                run_time=1.10,
            )
            self.play(
                LaggedStart(
                    *(FadeIn(fact, shift=0.07 * UP) for fact in research_facts),
                    lag_ratio=0.16,
                ),
                run_time=1.45,
            )
            self.play(
                FadeOut(hub),
                FadeOut(research_facts),
                run_time=0.45,
            )
            self.play(
                FadeIn(pathway[0], shift=0.10 * DOWN),
                run_time=0.65,
            )
            self.play(
                GrowArrow(pathway[1][0]),
                GrowArrow(pathway[1][1]),
                run_time=0.70,
            )
            self.play(
                FadeIn(pathway[2], shift=0.08 * UP),
                FadeIn(pathway[3], shift=0.08 * UP),
                run_time=0.95,
            )
            self.play(
                Create(pathway[4]),
                FadeIn(pathway[5], shift=0.06 * UP),
                run_time=0.65,
            )

        self.wait(RESEARCH_GRAPH_HOLD)
        self.play(FadeOut(Group(heading, pathway)), run_time=0.38)

    # ---- act 5: Montréal / international ---------------------------------

    def act_montreal(self):
        # Beat 1 — the actual mathematics building, with the press-room credit.
        building = full_bleed_photo("president_kennedy.jpg", metro_fallback())
        building_scrim = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=0.27,
        )
        building_title = promo_label(
            "Pavillon Président-Kennedy",
            size=41,
            color=WHITE,
        )
        building_title.to_edge(LEFT, buff=0.72).shift(1.45 * UP)
        building_sub = promo_label(
            "au cœur du Quartier des spectacles",
            size=25,
            color=WHITE,
            weight="NORMAL",
        )
        building_sub.next_to(
            building_title,
            DOWN,
            buff=0.18,
            aligned_edge=LEFT,
        )
        metro_sub = promo_label(
            "accès intérieur direct au métro Place-des-Arts",
            size=24,
            color=WHITE,
            weight="NORMAL",
        )
        metro_sub.next_to(
            building_sub,
            DOWN,
            buff=0.14,
            aligned_edge=LEFT,
        )
        building_credit = photo_credit("Photo UQAM")

        # Beat 2 — an immediate arrival / orientation space.
        allo = full_bleed_photo("allo_pk.jpg", international_fallback())
        allo_scrim = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=0.25,
        )
        allo_label = promo_label(
            "Des repères dès l'arrivée",
            size=34,
            color=WHITE,
        )
        allo_label.to_edge(LEFT, buff=0.72).shift(1.45 * UP)

        # Beat 3 — an international student community, not a card layout.
        international = full_bleed_photo(
            "international_students.jpg", international_fallback()
        )
        international_scrim = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=0.24,
        )
        international_label = promo_label(
            "Une communauté ouverte sur le monde",
            size=34,
            color=WHITE,
        )
        international_label.to_edge(LEFT, buff=0.72).shift(1.45 * UP)

        narration = NARRATION_SEGMENTS["montreal"]

        with self.narrate(narration):
            self.play(
                FadeIn(building),
                FadeIn(building_scrim),
                FadeIn(building_title, shift=0.08 * UP),
                FadeIn(building_sub, shift=0.06 * UP),
                FadeIn(metro_sub, shift=0.06 * UP),
                FadeIn(building_credit),
                run_time=0.85,
            )
            self.wait(MONTREAL_BUILDING_HOLD)

            self.play(
                FadeOut(building),
                FadeOut(building_scrim),
                FadeOut(building_title),
                FadeOut(building_sub),
                FadeOut(metro_sub),
                FadeOut(building_credit),
                FadeIn(allo),
                FadeIn(allo_scrim),
                FadeIn(allo_label, shift=0.08 * UP),
                run_time=0.65,
            )
            self.wait(MONTREAL_PHOTO_HOLD)
            self.play(
                FadeOut(allo),
                FadeOut(allo_scrim),
                FadeOut(allo_label),
                FadeIn(international),
                FadeIn(international_scrim),
                FadeIn(international_label, shift=0.08 * UP),
                run_time=0.65,
            )
            self.wait(MONTREAL_PHOTO_HOLD)

        self.play(
            FadeOut(international),
            FadeOut(international_scrim),
            FadeOut(international_label),
            run_time=0.40,
        )

    # ---- act 6: close -----------------------------------------------------

    def act_close(self):
        lines = VGroup(
            Text(
                "Des mathématiques exigeantes.",
                font=FONT,
                font_size=41,
                weight="BOLD",
                color=INK,
            ),
            Text(
                "Un milieu à taille humaine.",
                font=FONT,
                font_size=41,
                weight="BOLD",
                color=UQAM_BLUE,
            ),
            Text(
                "Un réseau de recherche.",
                font=FONT,
                font_size=41,
                weight="BOLD",
                color=INK,
            ),
            Text(
                "Montréal à votre porte.",
                font=FONT,
                font_size=41,
                weight="BOLD",
                color=INK,
            ),
        ).arrange(DOWN, buff=0.27)
        lines.move_to(0.20 * UP)

        narration = NARRATION_SEGMENTS["close"]

        with self.narrate(narration):
            self.play(
                LaggedStart(
                    *(FadeIn(line, shift=0.07 * UP) for line in lines),
                    lag_ratio=0.18,
                ),
                run_time=1.85,
            )
            self.wait(FINAL_MESSAGE_HOLD)
            self.play(FadeOut(lines), run_time=0.42)

            slogan = title_text("Aller loin, sans avancer seul.", 43)
            slogan.move_to(1.02 * UP)
            programme = body_text("Baccalauréat en mathématiques", 28, UQAM_BLUE)
            programme.next_to(slogan, DOWN, buff=0.42)
            cta = VGroup(
                body_text("Découvrir le programme", 23, INK),
                body_text(CTA_DISPLAY, 23, UQAM_BLUE),
            ).arrange(DOWN, buff=0.14)
            cta.next_to(programme, DOWN, buff=0.37)

            self.play(
                FadeIn(slogan, shift=0.08 * UP),
                FadeIn(programme, shift=0.06 * UP),
                FadeIn(cta, shift=0.06 * UP),
                run_time=0.82,
            )

        self.wait(FINAL_CARD_HOLD)

        # The UQAM logo is opt-in. Public release should enable it only after
        # the required Communications approval has actually been obtained.
        if USE_OFFICIAL_LOGO and LOGO_APPROVED and LOGO_PATH.exists():
            self.play(
                FadeOut(slogan),
                FadeOut(programme),
                FadeOut(cta),
                run_time=0.35,
            )
            logo = ImageMobject(str(LOGO_PATH))
            logo.scale_to_fit_width(2.9).move_to(ORIGIN)
            self.play(FadeIn(logo), run_time=0.50)
            self.wait(1.20)
