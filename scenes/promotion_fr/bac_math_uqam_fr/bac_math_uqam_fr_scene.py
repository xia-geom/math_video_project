"""
Baccalauréat en mathématiques à l'UQAM — vidéo promotionnelle courte.

Suggested repository path:
    scenes/promotion_fr/bac_math_uqam_fr/bac_math_uqam_fr_scene.py

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
    bibliotheque_sciences.jpg   # optional; no bundled downloader source yet
    research_math.jpg
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
      scenes/promotion_fr/bac_math_uqam_fr/bac_math_uqam_fr_scene.py \
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

REPO_ROOT = Path(__file__).resolve().parents[3]
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
USE_OFFICIAL_LOGO = os.getenv("UQAM_USE_OFFICIAL_LOGO", "1") == "1"
SHOW_PHOTO_CREDITS = os.getenv("UQAM_SHOW_PHOTO_CREDITS", "0") == "1"
USE_REAL_PHOTOS = os.getenv("UQAM_USE_REAL_PHOTOS", "1") != "0"
CTA_URL = os.getenv(
    "UQAM_PROMO_CTA_URL",
    "etudier.uqam.ca/programme/baccalaureat-mathematiques",
)
# Setting this to 1 should mean the final video has received the required
# internal approval to use the official UQAM logo.
LOGO_APPROVED = os.getenv("UQAM_LOGO_APPROVED", "1") == "1"

if FONT_PATH.exists():
    register_font(str(FONT_PATH))

UQAM_BLUE = "#0079BE"      # official UQAM blue: RGB 0/121/190
INK = "#312F2D"            # close to UQAM's dark grey band colour
SOFT_GREY = "#F1F3F5"
MID_GREY = "#8A8F94"
METRO_GREEN = "#00A651"    # semantic use only: Montréal green line

NARRATION_SEGMENTS = {
    "hook": (
        "À l'UQAM, faire des mathématiques, c'est pouvoir aller loin "
        "<break time='220ms'/> sans se perdre dans la foule."
    ),
    "human_scale": (
        "Le programme est solide, théorique et pratique. "
        "<break time='180ms'/> La Faculté mise sur les petits groupes; "
        "le programme, sur la collaboration et la disponibilité des enseignants. "
        "Au premier niveau, les cours de mathématiques comprennent deux heures de travaux pratiques "
        "par semaine. Ensuite, le travail en classe sous supervision prépare à la recherche."
    ),
    "support": (
        "Et quand on arrive, on n'est pas laissé seul. "
        "<break time='180ms'/> Le mentorat par les pairs est offert à toutes les nouvelles personnes "
        "étudiantes en sciences, avec des services de soutien à l'apprentissage et une Bibliothèque "
        "des sciences pour travailler seul ou en équipe."
    ),
    "research": (
        "Dès le bac, plusieurs stages d'été permettent de découvrir la recherche au CIRGET et au LACIM. "
        "<break time='180ms'/> Le CIRGET est interuniversitaire; le LACIM est un centre institutionnel "
        "de l'UQAM. Deux portes d'entrée vers un réseau scientifique qui dépasse largement le campus."
    ),
    "montreal": (
        "Le Département de mathématiques est au pavillon Président-Kennedy, au cœur du Quartier des "
        "spectacles, avec un accès intérieur direct au métro Place-des-Arts. "
        "<break time='180ms'/> Et la Faculté propose des ressources d'accueil et d'intégration aux "
        "personnes étudiantes internationales."
    ),
    "close": (
        "Des mathématiques exigeantes. <break time='140ms'/> Des enseignants accessibles. "
        "<break time='140ms'/> Un vrai réseau de recherche. <break time='140ms'/> Montréal à votre porte. "
        "<break time='220ms'/> Découvrez le bac en mathématiques à l'UQAM."
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
    centre = Circle(
        radius=0.68,
        color=UQAM_BLUE,
        stroke_width=3,
        fill_color=UQAM_BLUE,
        fill_opacity=0.10,
    )
    centre_label = Text(
        "CIRGET",
        font=FONT,
        font_size=27,
        weight="BOLD",
        color=INK,
    ).move_to(centre)

    data = [
        ("UQAM", 2.3 * LEFT + 0.55 * UP),
        ("McGill", 2.3 * RIGHT + 0.75 * UP),
        ("UdeM", 2.15 * LEFT + 1.25 * DOWN),
        ("Sherbrooke", 2.35 * RIGHT + 1.15 * DOWN),
    ]

    nodes = VGroup()
    edges = VGroup()
    for label, pos in data:
        node = RoundedRectangle(
            width=1.55 if label != "Sherbrooke" else 2.0,
            height=0.68,
            corner_radius=0.18,
            stroke_color=INK,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(pos)
        txt = Text(label, font=FONT, font_size=23, color=INK).move_to(node)
        nodes.add(VGroup(node, txt))
        edges.add(Line(centre.get_center(), node.get_center(), color=MID_GREY, stroke_width=2))

    lacim = pill("LaCIM • UQAM", width=2.6).next_to(centre, DOWN, buff=1.55)
    note = body_text("stages d'été en recherche", 27, UQAM_BLUE).next_to(lacim, DOWN, buff=0.35)

    return VGroup(edges, nodes, centre, centre_label, lacim, note)


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
    16:9 promotional master, expected duration about 70–85 seconds with MAI
    Soleil around +2%. The exact duration remains narration-driven.
    """

    def construct(self):
        configure_azure_speech_environment(PROMO_VOICE)
        self.set_speech_service(AzureService(**azure_service_kwargs(PROMO_VOICE)))

        self.act_hook()
        self.act_human_scale()
        self.act_support()
        self.act_research()
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

        student = photo_card(
            "lisa_berger.jpg",
            portrait_fallback("étudiante en mathématiques"),
            width=3.45,
            height=3.25,
        )
        professor = photo_card(
            "francois_bergeron.jpg",
            portrait_fallback("professeur de mathématiques"),
            width=3.45,
            height=3.25,
        )

        portraits = Group(student, professor).arrange(RIGHT, buff=0.28)
        portraits.to_edge(LEFT, buff=0.65).shift(0.10 * DOWN)

        facts = VGroup(
            clean_fact("petits groupes", "formule d'enseignement de la Faculté"),
            clean_fact("enseignants accessibles", "particularité officielle du programme"),
            clean_fact("2 h de TP par semaine", "dans les cours du premier niveau"),
            clean_fact("travail supervisé", "dans les cours de concentration suivants"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        facts.to_edge(RIGHT, buff=0.62).shift(0.15 * DOWN)

        narration = NARRATION_SEGMENTS["human_scale"]

        with self.narrate(narration) as tracker:
            self.play(
                FadeIn(heading),
                FadeIn(student, shift=0.10 * RIGHT),
                FadeIn(professor, shift=0.10 * LEFT),
                run_time=min(1.4, tracker.duration * 0.16),
            )
            self.play(
                LaggedStart(
                    *(FadeIn(f, shift=0.08 * UP) for f in facts),
                    lag_ratio=0.14,
                ),
                run_time=min(2.6, tracker.duration * 0.30),
            )

        self.play(
            FadeOut(
                Group(
                    heading,
                    student,
                    professor,
                    facts,
                )
            ),
            run_time=0.35,
        )

    # ---- act 3: support / mentoring --------------------------------------

    def act_support(self):
        heading = title_text("On n'avance pas seul.", 45).to_edge(UP, buff=0.55)

        mentor = mentor_fallback().scale(0.78)
        mentor.move_to(4.0 * LEFT + 0.15 * UP)

        support_icon = VGroup(
            Circle(radius=0.62, color=UQAM_BLUE, stroke_width=3),
            Text("?", font=FONT, font_size=42, weight="MEDIUM", color=UQAM_BLUE),
        )
        support_icon[1].move_to(support_icon[0])
        support_icon.move_to(ORIGIN + 0.15 * UP)

        library = library_fallback().scale(0.64)
        library.move_to(4.0 * RIGHT + 0.15 * UP)

        labels = VGroup(
            VGroup(
                body_text("mentorat par les pairs", 24),
                Text(
                    "pour toutes les nouvelles personnes\nen sciences",
                    font=FONT,
                    font_size=15,
                    color=MID_GREY,
                    line_spacing=0.85,
                ),
            ).arrange(DOWN, buff=0.08),
            VGroup(
                body_text("soutien à l'apprentissage", 24),
                Text(
                    "ateliers, clinique et\nrencontres individuelles",
                    font=FONT,
                    font_size=15,
                    color=MID_GREY,
                    line_spacing=0.85,
                ),
            ).arrange(DOWN, buff=0.08),
            VGroup(
                body_text("Bibliothèque des sciences", 24),
                Text(
                    "travail individuel\net en équipe",
                    font=FONT,
                    font_size=15,
                    color=MID_GREY,
                    line_spacing=0.85,
                ),
            ).arrange(DOWN, buff=0.08),
        )

        labels[0].next_to(mentor, DOWN, buff=0.32)
        labels[1].next_to(support_icon, DOWN, buff=0.46)
        labels[2].next_to(library, DOWN, buff=0.34)

        # All essential copy stays well above the subtitle safe zone.
        panel = RoundedRectangle(
            width=12.5,
            height=4.55,
            corner_radius=0.12,
            stroke_color="#E2E5E8",
            stroke_width=1.5,
            fill_color=SOFT_GREY,
            fill_opacity=0.28,
        ).shift(0.18 * DOWN)

        narration = NARRATION_SEGMENTS["support"]

        with self.narrate(narration) as tracker:
            self.play(FadeIn(heading), FadeIn(panel), run_time=min(0.8, tracker.duration * 0.10))
            self.play(
                LaggedStart(
                    FadeIn(mentor, shift=0.10 * UP),
                    FadeIn(support_icon, shift=0.10 * UP),
                    FadeIn(library, shift=0.10 * UP),
                    lag_ratio=0.12,
                ),
                run_time=min(1.6, tracker.duration * 0.22),
            )
            self.play(
                LaggedStart(*(FadeIn(x) for x in labels), lag_ratio=0.12),
                run_time=min(1.5, tracker.duration * 0.18),
            )

        self.play(
            FadeOut(Group(heading, panel, mentor, support_icon, library, labels)),
            run_time=0.35,
        )

    # ---- act 4: research --------------------------------------------------

    def act_research(self):
        heading = title_text("La recherche, dès le bac", 44)
        heading.to_edge(UP, buff=0.52).to_edge(LEFT, buff=0.70)

        hub = photo_card(
            "research_math.jpg",
            research_network_fallback(),
            width=6.20,
            height=3.70,
        )
        hub.to_edge(LEFT, buff=0.65).shift(0.15 * DOWN)

        hub_label = VGroup(
            body_text("Pôle en mathématiques", 25),
            body_text("Complexe des sciences Pierre-Dansereau", 18, MID_GREY),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        hub_label.next_to(hub, DOWN, buff=0.18, aligned_edge=LEFT)

        research_facts = VGroup(
            clean_fact("stages d'été en recherche", "possibilités au CIRGET et au LACIM"),
            clean_fact("CIRGET", "centre interuniversitaire"),
            clean_fact("LACIM", "centre institutionnel de l'UQAM"),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        research_facts.to_edge(RIGHT, buff=0.70).shift(0.10 * DOWN)

        network = research_network_fallback().scale(0.84).shift(0.45 * UP)

        narration = NARRATION_SEGMENTS["research"]

        with self.narrate(narration) as tracker:
            self.play(
                FadeIn(heading),
                FadeIn(hub, shift=0.12 * RIGHT),
                FadeIn(hub_label),
                run_time=min(1.4, tracker.duration * 0.18),
            )
            self.play(
                LaggedStart(*(FadeIn(f, shift=0.08 * UP) for f in research_facts), lag_ratio=0.15),
                run_time=min(1.8, tracker.duration * 0.22),
            )
            self.play(
                FadeOut(hub),
                FadeOut(hub_label),
                FadeOut(research_facts),
                run_time=min(0.55, tracker.duration * 0.06),
            )
            self.play(
                Create(network[0]),
                FadeIn(network[1]),
                GrowFromCenter(network[2]),
                FadeIn(network[3]),
                run_time=min(1.9, tracker.duration * 0.22),
            )
            self.play(
                FadeIn(network[4], shift=0.08 * UP),
                FadeIn(network[5], shift=0.08 * UP),
                run_time=min(1.25, tracker.duration * 0.14),
            )

        self.play(FadeOut(Group(heading, network)), run_time=0.35)

    # ---- act 5: Montréal / international ---------------------------------

    def act_montreal(self):
        heading = title_text("Montréal à votre porte", 44)
        heading.to_edge(UP, buff=0.52).to_edge(LEFT, buff=0.70)

        metro = metro_fallback().scale(0.78)
        metro.to_edge(LEFT, buff=0.55).shift(0.10 * DOWN)

        international = photo_card(
            "international_students.jpg",
            international_fallback(),
            width=4.05,
            height=2.70,
        )
        international.to_edge(RIGHT, buff=0.58).shift(0.55 * UP)

        international_super = VGroup(
            body_text("Communauté internationale", 23),
            body_text("accueil et intégration à la Faculté des sciences", 17, MID_GREY),
        ).arrange(DOWN, buff=0.07)
        international_super.next_to(international, DOWN, buff=0.20)

        allo = photo_card(
            "allo_pk.jpg",
            international_fallback(),
            width=4.05,
            height=2.70,
        )
        allo.move_to(international)

        allo_super = VGroup(
            body_text("Programme Allô!", 23),
            body_text("au Complexe des sciences", 17, MID_GREY),
        ).arrange(DOWN, buff=0.07)
        allo_super.next_to(allo, DOWN, buff=0.20)

        narration = NARRATION_SEGMENTS["montreal"]

        with self.narrate(narration) as tracker:
            self.play(FadeIn(heading), run_time=min(0.7, tracker.duration * 0.08))
            self.play(
                Create(metro[0]),
                FadeIn(VGroup(*metro[1:4])),
                run_time=min(1.3, tracker.duration * 0.17),
            )
            self.play(
                GrowArrow(metro[-1]),
                FadeIn(VGroup(*metro[4:6]), shift=0.10 * LEFT),
                run_time=min(1.2, tracker.duration * 0.15),
            )
            self.play(
                FadeIn(international, shift=0.10 * UP),
                FadeIn(international_super),
                run_time=min(1.2, tracker.duration * 0.16),
            )
            self.play(
                FadeOut(international),
                FadeOut(international_super),
                FadeIn(allo),
                FadeIn(allo_super),
                run_time=min(1.0, tracker.duration * 0.12),
            )

        self.play(
            FadeOut(Group(heading, metro, allo, allo_super)),
            run_time=0.35,
        )

    # ---- act 6: close -----------------------------------------------------

    def act_close(self):
        # Short real-photo recap before the clean UQAM call-to-action.
        student = photo_card(
            "lisa_berger.jpg",
            portrait_fallback("étudiante en mathématiques"),
            width=3.55,
            height=2.60,
        )
        professor = photo_card(
            "francois_bergeron.jpg",
            portrait_fallback("professeur de mathématiques"),
            width=3.55,
            height=2.60,
        )
        community = photo_card(
            "international_students.jpg",
            international_fallback(),
            width=3.55,
            height=2.60,
        )
        cards = Group(student, professor, community).arrange(RIGHT, buff=0.25)
        cards.scale_to_fit_width(11.9).shift(0.05 * UP)

        captions = VGroup(
            body_text("mathématiques exigeantes", 22),
            body_text("enseignants accessibles", 22, UQAM_BLUE),
            body_text("communauté ouverte", 22),
        )
        for label, card in zip(captions, cards):
            label.next_to(card, UP, buff=0.22)

        narration = NARRATION_SEGMENTS["close"]

        with self.narrate(narration) as tracker:
            self.play(
                LaggedStart(
                    FadeIn(student, shift=0.08 * UP),
                    FadeIn(professor, shift=0.08 * UP),
                    FadeIn(community, shift=0.08 * UP),
                    lag_ratio=0.14,
                ),
                LaggedStart(*(FadeIn(c) for c in captions), lag_ratio=0.14),
                run_time=min(2.0, tracker.duration * 0.34),
            )
            self.play(
                FadeOut(cards),
                FadeOut(captions),
                run_time=min(0.55, tracker.duration * 0.08),
            )

            slogan = title_text("Aller loin, sans avancer seul.", 43)
            slogan.move_to(0.90 * UP)
            programme = body_text("Baccalauréat en mathématiques", 28, UQAM_BLUE)
            programme.next_to(slogan, DOWN, buff=0.38)
            cta = VGroup(
                body_text("Découvrir le programme", 23, INK),
                body_text(CTA_URL, 22, UQAM_BLUE),
            ).arrange(DOWN, buff=0.16)
            cta.next_to(programme, DOWN, buff=0.35)

            self.play(
                FadeIn(slogan, shift=0.10 * UP),
                FadeIn(programme, shift=0.08 * UP),
                FadeIn(cta, shift=0.08 * UP),
                run_time=min(1.5, tracker.duration * 0.25),
            )

        # UQAM's published video guide says use the logo only at the end and
        # have the content approved by the Service des communications.
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
            self.wait(0.65)
        else:
            approval_note = body_text(
                "Logo officiel à insérer après approbation UQAM",
                17,
                MID_GREY,
            ).next_to(cta, DOWN, buff=0.28)
            self.play(FadeIn(approval_note), run_time=0.35)
            self.wait(0.45)
