"""UQAM mathematics recruitment film: photo-led, readable and narration-paced.

Run the shared asset fetcher before rendering. The production scene requires
registered photographs; the legacy photo_card diagnostic helper remains for
compatibility. Historical portraits are retained as files, not used in this film.
All spoken copy lives in promo_beats.py. review.py renders the same scene with
explicit, labelled silent-review clocks; production always uses real Azure speech.

Preserve the shared MAI voice, source credits, final-logo approval gate, and the
60–90 second format. An encoded preview is not listening or release approval.
"""

from __future__ import annotations

# Manim's public scene API is intentionally imported as a star.
# ruff: noqa: F403, F405
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService
from manimpango import register_font
from PIL import Image, ImageDraw, ImageFont

from miscellaneous.bac_math_uqam_fr.promo_beats import NARRATION_BEATS
from tools.tts import (
    VOICE_LOCALES,
    azure_service_kwargs,
    configure_azure_speech_environment,
    resolve_voice,
    ssml,
    strip_ssml,
)
from tools.uqam_promo_layout import check_copy_layout, mark_copy, photo_canvas

config.background_color = WHITE
REPO_ROOT = Path(__file__).resolve().parents[2]
FONT = os.getenv("UQAM_VIDEO_FONT", "Roboto")
PROMO_RATE = os.getenv("UQAM_PROMO_RATE", "+6%")
HOOK_RATE = os.getenv("UQAM_HOOK_RATE", PROMO_RATE)
PROMO_VOICE = resolve_voice(os.getenv("UQAM_PROMO_VOICE", os.getenv("MANIM_VOICE", "MAI-Voice-2")))
ASSET_DIR = Path(os.getenv("UQAM_PROMO_ASSET_DIR", str(REPO_ROOT / "assets" / "uqam_promo")))
FONT_PATH = Path(os.getenv("UQAM_VIDEO_FONT_PATH", str(ASSET_DIR / "fonts" / "Roboto-VariableFont_wdth,wght.ttf")))
TEXT_CACHE_DIR = ASSET_DIR / "_text_cache"
TEXT_RASTER_SCALE = int(os.getenv("UQAM_TEXT_RASTER_SCALE", "4"))
TEXT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOGO_PATH = Path(os.getenv("UQAM_PROMO_LOGO_PATH", str(REPO_ROOT / "assets" / "branding" / "uqam_logo.png")))
USE_OFFICIAL_LOGO = os.getenv("UQAM_USE_OFFICIAL_LOGO", "0") == "1"
SHOW_PHOTO_CREDITS = os.getenv("UQAM_SHOW_PHOTO_CREDITS", "0") == "1"
USE_REAL_PHOTOS = os.getenv("UQAM_USE_REAL_PHOTOS", "1") != "0"
CTA_URL = os.getenv("UQAM_PROMO_CTA_URL", "https://etudier.uqam.ca/programme/baccalaureat-mathematiques")
CTA_DISPLAY = os.getenv("UQAM_PROMO_CTA_DISPLAY", "etudier.uqam.ca")
LOGO_APPROVED = os.getenv("UQAM_LOGO_APPROVED", "0") == "1"
# Legacy knobs remain import-compatible; active timing follows speech units.
TEACHING_PORTRAIT_HOLD = float(os.getenv("UQAM_TEACHING_PORTRAIT_HOLD", "3.20"))
RESEARCH_GRAPH_HOLD = float(os.getenv("UQAM_RESEARCH_GRAPH_HOLD", "1.35"))
FINAL_MESSAGE_HOLD = float(os.getenv("UQAM_FINAL_MESSAGE_HOLD", "1.65"))
FINAL_CARD_HOLD = float(os.getenv("UQAM_FINAL_CARD_HOLD", "2.80"))
SUPPORT_HUMAN_HOLD = float(os.getenv("UQAM_SUPPORT_HUMAN_HOLD", "2.25"))
SUPPORT_LIBRARY_HOLD = float(os.getenv("UQAM_SUPPORT_LIBRARY_HOLD", "2.30"))
SUPPORT_PAGE_HOLD = float(os.getenv("UQAM_SUPPORT_PAGE_HOLD", "1.15"))
MONTREAL_BUILDING_HOLD = float(os.getenv("UQAM_MONTREAL_BUILDING_HOLD", "2.00"))
MONTREAL_PHOTO_HOLD = float(os.getenv("UQAM_MONTREAL_PHOTO_HOLD", "1.70"))
if FONT_PATH.exists():
    register_font(str(FONT_PATH))
UQAM_BLUE = "#0079BE"
INK = "#312F2D"
SOFT_GREY = "#F1F3F5"
MID_GREY = "#59616B"
METRO_GREEN = "#00A651"
NARRATION_SEGMENTS = {name: " ".join(units) for name, units in NARRATION_BEATS.items()}
NARRATION_RATES = {
    "hook": HOOK_RATE, "human_scale": PROMO_RATE, "research": PROMO_RATE,
    "support": PROMO_RATE, "montreal": PROMO_RATE, "close": PROMO_RATE,
}
Text.set_default(font=FONT, color=INK)
Tex.set_default(color=INK)
MathTex.set_default(color=INK)


def _font_variation_name(weight: str) -> str:
    mapping = {
        "THIN": "Thin", "EXTRALIGHT": "ExtraLight", "LIGHT": "Light",
        "NORMAL": "Regular", "REGULAR": "Regular", "MEDIUM": "Medium",
        "SEMIBOLD": "SemiBold", "BOLD": "Bold", "EXTRABOLD": "ExtraBold", "BLACK": "Black",
    }
    return mapping.get(str(weight).strip().upper(), "Regular")


def _load_pillow_font(pixel_size: int, weight: str) -> ImageFont.FreeTypeFont:
    """Load the registered Roboto file through Pillow/FreeType."""
    if not FONT_PATH.is_file():
        raise RuntimeError(f"Kerning-safe typography requires the configured Roboto font file: {FONT_PATH}")
    font = ImageFont.truetype(str(FONT_PATH), pixel_size)
    variation = _font_variation_name(weight)
    if hasattr(font, "set_variation_by_name"):
        try:
            font.set_variation_by_name(variation)
        except Exception:
            try:
                font.set_variation_by_name(variation.encode("utf-8"))
            except Exception:
                pass
    return font


def _hex_to_rgba(color) -> tuple[int, int, int, int]:
    value = color.to_hex() if hasattr(color, "to_hex") else str(color)
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(char * 2 for char in value)
    if len(value) != 6:
        raise ValueError(f"Expected #RRGGBB colour, got {color!r}")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), 255


def kerning_text(text: str, *, size: int, color=INK, weight: str = "NORMAL") -> ImageMobject:
    """Preserve the established FreeType typography and its invisible size calibration."""
    scale = max(2, TEXT_RASTER_SCALE)
    pixel_size = int(round(size * scale))
    rgba = _hex_to_rgba(color)
    cache_payload = {
        "renderer_revision": 2, "text": text, "size": size, "weight": weight,
        "rgba": rgba, "scale": scale, "font": str(FONT_PATH),
        "font_mtime_ns": FONT_PATH.stat().st_mtime_ns if FONT_PATH.exists() else None,
    }
    digest = hashlib.sha256(json.dumps(cache_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:24]
    png_path = TEXT_CACHE_DIR / f"text_{digest}.png"
    if not png_path.exists():
        font = _load_pillow_font(pixel_size, weight)
        padding = max(12, int(pixel_size * 0.30))
        probe = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        bbox = ImageDraw.Draw(probe).textbbox((0, 0), text, font=font)
        width = max(1, bbox[2] - bbox[0])
        height = max(1, bbox[3] - bbox[1])
        canvas = Image.new("RGBA", (width + 2 * padding, height + 2 * padding), (0, 0, 0, 0))
        ImageDraw.Draw(canvas).text((padding - bbox[0], padding - bbox[1]), text, font=font, fill=rgba)
        # Drawing padding protects accents; crop it before scene alignment.
        alpha_bounds = canvas.getchannel("A").getbbox()
        if alpha_bounds is None:
            raise RuntimeError(f"Pillow produced an empty text raster for {text!r}")
        margin = max(2, scale)
        left, top, right, bottom = alpha_bounds
        canvas = canvas.crop((max(0, left - margin), max(0, top - margin),
                              min(canvas.width, right + margin), min(canvas.height, bottom + margin)))
        canvas.save(png_path)
    mob = ImageMobject(str(png_path))
    # Never displayed: keep the original Manim point-size calibration.
    probe_height = Text("Ag", font=FONT, font_size=size, weight=weight).height
    mob.scale_to_fit_height(probe_height * 1.08)
    return mark_copy(mob, text)


def title_text(text: str, size: int = 48, color=INK) -> ImageMobject:
    return kerning_text(text, size=size, weight="BOLD", color=color)


def body_text(text: str, size: int = 30, color=INK) -> ImageMobject:
    return kerning_text(text, size=size, weight="NORMAL", color=color)


def promo_label(text: str, size: int = 30, color=INK, *, weight: str = "MEDIUM") -> ImageMobject:
    return kerning_text(text, size=size, weight=weight, color=color)


def photo_credit(text: str) -> Group:
    credit = kerning_text(text, size=14, weight="NORMAL", color=WHITE)
    credit.uqam_copy_role = "credit"
    panel = Rectangle(width=credit.width + 0.30, height=credit.height + 0.20,
                      stroke_width=0, fill_color=INK, fill_opacity=1)
    credit.move_to(panel)
    return Group(panel, credit).to_corner(UR, buff=0.35)


def research_network_fallback() -> Group:
    """A stable three-centre graphic; its historical public grouping is retained."""
    stage_box = RoundedRectangle(width=5.15, height=0.70, corner_radius=0.12,
                                 stroke_width=0, fill_color=UQAM_BLUE, fill_opacity=1)
    stage_text = promo_label("Stages d'été en recherche", size=25, color=WHITE).move_to(stage_box)
    stage = Group(stage_box, stage_text).move_to([0, 1.63, 0])
    cards = Group()
    for acronym, domain in (("CIRGET", ("Géométrie", "Topologie")),
                            ("LaCIM", ("Combinatoire", "Informatique", "mathématique")),
                            ("STATQAM", ("Statistique", "Science", "des données"))):
        box = RoundedRectangle(width=3.8, height=2.55, corner_radius=0.12,
                               stroke_color=UQAM_BLUE, stroke_width=2,
                               fill_color=WHITE, fill_opacity=1)
        words = [promo_label(acronym, size=34, color=UQAM_BLUE)]
        words.extend(body_text(text, 24) for text in domain)
        copy = Group(*words).arrange(DOWN, buff=0.20).move_to(box)
        for word in words:
            word.uqam_containing_panel = box
        cards.add(Group(box, copy))
    cards.arrange(RIGHT, buff=0.3).move_to([0, -0.18, 0])
    branches = VGroup()
    accent = Line([-4.0, -1.78, 0], [4.0, -1.78, 0], color=UQAM_BLUE, stroke_width=2)
    footer = body_text("Plusieurs portes d'entrée vers la recherche", 25).move_to([0, -2.05, 0])
    return Group(stage, branches, cards, accent, footer)


def photo_card(filename: str, fallback: Mobject, width: float = 5.4,
               height: float = 3.5, credit: str | None = None) -> Group:
    """Legacy diagnostic helper; the revised film uses strictly checked photo canvases."""
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
    frame = RoundedRectangle(width=image.width + 0.14, height=image.height + 0.14,
                             corner_radius=0.10, stroke_color=MID_GREY, stroke_width=1.5).move_to(image)
    group = Group(image, frame)
    if SHOW_PHOTO_CREDITS and credit:
        credit_text = kerning_text(credit, size=14, color=MID_GREY).next_to(
            frame, DOWN, buff=0.08, aligned_edge=RIGHT)
        group.add(credit_text)
    return group


class BacMathUQAMFR(VoiceoverScene):
    """Narration-led photo film; use review.py only for an explicitly silent preview."""

    def construct(self):
        configure_azure_speech_environment(PROMO_VOICE, require_credentials=True)
        self.set_speech_service(AzureService(**azure_service_kwargs(PROMO_VOICE)))
        self.construct_film()

    def construct_film(self):
        self.semantic_shots, self.semantic_acts, self.speech_units = [], [], []
        self.layout_checks, self.visible_states = [], []
        self.current_background = self.current_copy = None
        self.background_start = 0.0
        self.current_state = None
        if getattr(self, "visual_only", False):
            notice = kerning_text("APERÇU MUET — VOIX NON INCLUSE", size=15, color=INK)
            notice.uqam_copy_role = "preview"
            panel = Rectangle(width=notice.width + 0.3, height=notice.height + 0.14,
                              stroke_width=0, fill_color=WHITE, fill_opacity=1)
            Group(panel, notice).move_to([0, 3.64, 0])
            self.add_foreground_mobjects(Group(panel, notice).set_z_index(10000))
        for key in NARRATION_SEGMENTS:
            self._act_start = float(self.renderer.time)
            getattr(self, "act_" + key)()
            self.semantic_acts.append({"act": key, "start": self._act_start, "end": float(self.renderer.time)})
        self.wait(1.0)
        self.finish_background(float(self.renderer.time))
        if self.current_state is not None:
            self.current_state["end"] = float(self.renderer.time)
        timeline = Path(os.getenv("UQAM_TIMELINE_PATH", str(REPO_ROOT / "dist/bac_math_uqam_fr/semantic_timeline.json")))
        timeline.parent.mkdir(parents=True, exist_ok=True)
        timeline.write_text(json.dumps({
            "mode": "visual_only_no_audio" if getattr(self, "visual_only", False) else "azure",
            "timing_source": "explicit_preview_fixtures" if getattr(self, "visual_only", False) else "measured_speech",
            "acts": self.semantic_acts, "shots": self.semantic_shots, "speech_units": self.speech_units,
            "states": self.visible_states, "layout": self.layout_checks,
            "duration": float(self.renderer.time), "listening_review": "pending",
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def record_photo(self, filename, start, end, displayed_credit=None):
        self.semantic_shots.append({"filename": filename, "start": start, "end": end,
                                    "displayed_credit": displayed_credit,
                                    "placement": "protected credit panel" if displayed_credit else "distribution description"})

    def finish_background(self, end):
        if self.current_background is not None:
            for filename, credit in getattr(self.current_background, "photo_records", []):
                self.record_photo(filename, self.background_start, end, credit)

    def audit(self, context):
        result = check_copy_layout(self.mobjects, context)
        result["at"] = float(self.renderer.time)
        self.layout_checks.append(result)

    def show(self, background, copy, state, seconds=0.75):
        """Exchange two editorial shots without a white flash or doubled messages."""
        start = float(self.renderer.time)
        if self.current_state is not None:
            self.current_state["end"] = start
        if hasattr(background, "photo_credit"):
            copy.add(background.photo_credit.copy())
        copy.set_z_index(20)
        if self.current_copy is None:
            self.add(background)
            self.play(FadeIn(copy), run_time=seconds)
        else:
            if background is self.current_background:
                # White-card changes are direct replacements. A sequential
                # fade otherwise leaves an empty white frame between messages.
                # Individually animated lines may also be scene roots. Cairo's
                # remove(group) alone does not remove those separate children.
                self.remove(*self.current_copy.get_family())
                self.add(copy)
                self.wait(seconds)
            else:
                exchange = Succession(FadeOut(self.current_copy, run_time=0.18), Wait(0.16),
                                      FadeIn(copy, run_time=seconds - 0.34))
                self.play(AnimationGroup(FadeIn(background, run_time=seconds), exchange, lag_ratio=0))
                self.remove(*self.current_copy.get_family())
                self.finish_background(float(self.renderer.time))
                self.remove(self.current_background)
        if background is not self.current_background:
            self.background_start = start
        self.current_background, self.current_copy = background, copy
        self.current_state = {"state": state, "start": float(self.renderer.time)}
        self.visible_states.append(self.current_state)
        self.audit(state)

    def photo_background(self, filename, *, panel=False, left=False, white_veil=False, context=""):
        if panel:
            photo = photo_canvas(ASSET_DIR / filename, width=6.6,
                                 height=4.67,
                                 center=(-3.15 if left else 3.15, 0.15))
        else:
            photo = photo_canvas(ASSET_DIR / filename, width=config.frame_width,
                                 height=config.frame_height, focal=(0.5, 0.42),
                                 veil=0.84 if white_veil else 0.56,
                                 veil_color="white" if white_veil else "black")
        background = Group(photo)
        credit_text = "Photo : Quintin Soloviev · CC BY 4.0" if filename == "montreal_skyline_2026.jpg" else (
            "Photo : UQAM" if filename in {"campus_central_uqam.jpg", "sciences_biologiques_uqam.jpg"}
            else "Service des bibliothèques · UQAM" if filename in {"bibliotheque_sciences_2026.jpg", "redaction_sciences_2026.jpg"}
            else "Photo : Nathalie St-Pierre")
        if context:
            credit_text += " · " + context
        credit = photo_credit(credit_text)
        credit.move_to([config.frame_width / 2 - credit.width / 2 - 0.25, 3.24, 0])
        background.photo_credit = credit
        background.photo_records = [(filename, credit_text)]
        return background

    @contextmanager
    def narrate_unit(self, segment, index):
        text = NARRATION_BEATS[segment][index]
        start = float(self.renderer.time)
        with self.narrate(text, rate=NARRATION_RATES[segment]) as tracker:
            yield tracker
        self.speech_units.append({"segment": segment, "index": index, "text": text,
                                  "start": start, "speech_end": start + float(tracker.duration),
                                  "end": float(self.renderer.time)})

    def narrate(self, text: str, *, rate: str | None = None):
        spoken = ssml(text, rate=rate or PROMO_RATE, locale=VOICE_LOCALES.get(PROMO_VOICE, "fr-CA"))
        return self.voiceover(text=spoken, subcaption=strip_ssml(spoken),
                              max_subcaption_len=42, subcaption_buff=0.08)

    def act_hook(self):
        background = self.photo_background("ludopolis_2026.jpg", panel=True, context="vie de campus, 2026")
        copy = Group(title_text("Des maths", 44, UQAM_BLUE),
                     title_text("de haut niveau", 44, UQAM_BLUE),
                     body_text("Une université", 31), body_text("à votre écoute", 31))
        copy.arrange(DOWN, buff=0.25).move_to([-3.55, 0.25, 0])
        with self.narrate_unit("hook", 0):
            self.show(background, copy, "hook")

    def act_human_scale(self):
        background = self.photo_background("math_workshop_2019.jpg", panel=True, context="atelier public, 2019")
        rows = Group()
        for y, verb, fact in ((1.30, "Échanger", "Petits groupes"), (0.0, "Pratiquer", "Travaux pratiques"),
                              (-1.30, "Progresser", "Travail supervisé")):
            row = Group(promo_label(verb, size=32, color=UQAM_BLUE), body_text(fact, 26))
            row.arrange(DOWN, buff=0.20).move_to([-3.6, y, 0])
            rows.add(row)
        with self.narrate_unit("human_scale", 0):
            self.show(background, Group(rows), "human_scale")
        with self.narrate_unit("human_scale", 1):
            pass

    def act_research(self):
        background = Group(Rectangle(width=config.frame_width, height=config.frame_height,
                                     stroke_width=0, fill_color=WHITE, fill_opacity=1))
        heading = title_text("La recherche, dès le bac", 43).move_to([0, 2.62, 0])
        invitation = Group(promo_label("Stages d'été en recherche", size=40, color=UQAM_BLUE),
                           body_text("Une première expérience scientifique", 29))
        invitation.arrange(DOWN, buff=0.45).move_to([0, 0.10, 0])
        with self.narrate_unit("research", 0):
            self.show(background, Group(heading, invitation), "research_intro")
        pathway = research_network_fallback()
        self.show(background, Group(heading.copy(), pathway), "research_cards")
        for index in (1, 2, 3):
            with self.narrate_unit("research", index):
                for card_index, card in enumerate(pathway[2]):
                    card[0].set_stroke(width=4 if card_index == index - 1 else 2)
                self.audit(f"research_description_{index}")
        elapsed = float(self.renderer.time) - self.current_state["start"]
        if elapsed < 12.0:
            self.wait(12.0 - elapsed)

    def act_support(self):
        mentor = Group(promo_label("Échanger", size=36, color=UQAM_BLUE),
                       body_text("autour des maths", 30), body_text("pour avancer", 30))
        mentor.arrange(DOWN, buff=0.25).move_to([3.55, 0.25, 0])
        background = self.photo_background("redaction_sciences_2026.jpg", panel=True, left=True)
        with self.narrate_unit("support", 0):
            self.show(background, Group(mentor), "math_discussion")
        library = Group(promo_label("Bibliothèque", size=34, color=UQAM_BLUE),
                        promo_label("des sciences", size=34, color=UQAM_BLUE),
                        body_text("Seul ou en équipe", 28))
        library.arrange(DOWN, buff=0.23).move_to([3.55, 0.25, 0])
        with self.narrate_unit("support", 1):
            self.show(background, Group(library), "library")

    def act_montreal(self):
        background = self.photo_background("sciences_biologiques_uqam.jpg")
        copy = Group(kerning_text("Au cœur de Montréal", size=48, weight="BOLD", color=WHITE),
                     kerning_text("Complexe des sciences Pierre-Dansereau", size=28, color=WHITE),
                     kerning_text("Métro Place-des-Arts", size=29, color=WHITE))
        copy.arrange(DOWN, aligned_edge=LEFT, buff=0.32).to_edge(LEFT, buff=0.75).shift(0.35 * DOWN)
        with self.narrate_unit("montreal", 0):
            self.show(background, copy, "montreal_campus")
        background = self.photo_background("accueil_hiver_2026.jpg", panel=True, context="accueil de rentrée, 2026")
        copy = Group(title_text("Une communauté", 36, UQAM_BLUE),
                     title_text("accueillante", 36, UQAM_BLUE),
                     body_text("ouverte sur le monde", 28))
        copy.arrange(DOWN, buff=0.3).move_to([-3.55, 0.25, 0])
        with self.narrate_unit("montreal", 1):
            self.show(background, copy, "student_welcome")

    def act_close(self):
        background = self.photo_background("montreal_skyline_2026.jpg", white_veil=True)
        lines = Group(*[kerning_text(text, size=35, weight="BOLD", color=UQAM_BLUE if i == 1 else INK)
                        .move_to([0, 1.4 - i * 0.86, 0]) for i, text in enumerate(NARRATION_BEATS["close"][:4])])
        copy = Group(lines[0])
        with self.narrate_unit("close", 0):
            self.show(background, copy, "closing_summary")
        for index in (1, 2, 3):
            with self.narrate_unit("close", index):
                self.play(FadeIn(lines[index]), run_time=0.4)
                self.current_copy.add(lines[index])
                self.audit(f"closing_summary_{index}")
        slogan = title_text("Aller loin, sans avancer seul.", 43).move_to([0, 1.03, 0])
        programme = body_text("Baccalauréat en mathématiques", 29, UQAM_BLUE).move_to([0, 0.12, 0])
        cta = Group(body_text("Découvrir le programme", 25), body_text(CTA_DISPLAY, 26, UQAM_BLUE))
        cta.arrange(DOWN, buff=0.2).move_to([0, -1.10, 0])
        with self.narrate_unit("close", 4):
            self.show(background, Group(slogan, programme, cta), "closing_cta")
        self.wait(FINAL_CARD_HOLD)
        if USE_OFFICIAL_LOGO and LOGO_APPROVED and LOGO_PATH.exists():
            white_card = Rectangle(width=config.frame_width, height=config.frame_height,
                                   stroke_width=0, fill_color=WHITE, fill_opacity=1)
            self.play(FadeIn(white_card), FadeOut(self.current_copy), run_time=0.4)
            logo = ImageMobject(str(LOGO_PATH)).scale_to_fit_width(4.0).move_to(ORIGIN)
            self.play(FadeIn(logo), run_time=0.5)
            self.wait(1.2)


class TypographyDiagnostic(Scene):
    """A compact visual comparison used to confirm the kerning renderer."""

    def construct(self):
        tests = ["Mathématiques à l'UQAM", "Exigeant, mais à taille humaine",
                 "enseignants accessibles", "prendre ses repères", "Bibliothèque des sciences",
                 "Complexe des sciences Pierre-Dansereau", "Aller loin, sans avancer seul."]
        rows = Group()
        for text in tests:
            pango = Text(text, font=FONT, font_size=30, color=RED)
            pillow = kerning_text(text, size=30, weight="NORMAL", color=UQAM_BLUE)
            rows.add(Group(pango, pillow).arrange(DOWN, aligned_edge=LEFT, buff=0.10))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        rows.scale_to_fit_height(6.8)
        self.add(rows)
