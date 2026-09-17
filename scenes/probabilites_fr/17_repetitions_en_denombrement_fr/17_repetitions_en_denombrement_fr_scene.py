"""Dénombrement 3 — Réutiliser un choix ou corriger un surcomptage ?

Seconde version, profondément révisée, de la troisième capsule de probabilités
et dénombrement pour MAT0339.

Objectif unique
---------------
Distinguer deux situations souvent confondues parce qu'elles contiennent toutes
les deux le mot « répétition » :

1. on remplit des positions et un choix peut être réutilisé : ``n^p``;
2. on réordonne une collection fixée contenant des objets identiques :
   ``N! / (n_1! ... n_k!)``.

La scène suit les conventions du projet : Manim Community, fond blanc, encre
noire, un accent bleu, narration Azure facultative, synchronisation par
signets et fonctionnement silencieux sans identifiants Azure.

Chemin recommandé dans le dépôt
--------------------------------
``scenes/probabilites_fr/17_repetitions_en_denombrement_fr/``
``17_repetitions_en_denombrement_fr_scene.py``

Classe de rendu
---------------
``RepetitionsDenombrementFR``
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import (
    BLACK,
    BLUE_D,
    BLUE_E,
    DOWN,
    GRAY_B,
    GRAY_D,
    LEFT,
    RED_D,
    RIGHT,
    UP,
    WHITE,
    Circle,
    Circumscribe,
    Create,
    Cross,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    Mobject,
    ReplacementTransform,
    RoundedRectangle,
    Scene,
    Tex,
    Text,
    TransformFromCopy,
    VGroup,
    Write,
    config,
)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dépendance facultative
    load_dotenv = None

try:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.azure import AzureService
except ImportError:  # pragma: no cover - rendu silencieux permis
    VoiceoverScene = None
    AzureService = None

import tools.tts as tts

try:
    from tools.branding import play_uqam_intro
except ImportError:  # pragma: no cover - prévisualisation isolée

    def play_uqam_intro(_scene):
        return None


# ---------------------------------------------------------------------------
# Style global du projet
# ---------------------------------------------------------------------------
config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
ACCENT_LIGHT = BLUE_E
WARNING = RED_D
MUTED = GRAY_D

TITLE_SIZE = 42
SUBTITLE_SIZE = 27
BODY_SIZE = 29
SMALL_SIZE = 23
FORMULA_SIZE = 48


# Les signets servent à synchroniser une idée visuelle précise avec la phrase
# qui l'explique. Ils sont supprimés automatiquement des sous-titres.
SCRIPT = {
    "intro": (
        "Deux problèmes parlent de répétition, mais pas de la même structure. "
        "<bookmark mark='show_code'/> Dans un code, un chiffre peut être réutilisé. "
        "<bookmark mark='show_word'/> Dans BANANE, les lettres sont déjà présentes et "
        "certaines sont identiques. <bookmark mark='central_question'/> Demandons-nous : "
        "remplit-on des positions, ou réordonne-t-on une collection fixée ? "
        "<bookmark mark='end_intro'/>"
    ),
    "code": (
        "Construisons un code de trois positions avec zéro, un, deux et trois. Comme c'est "
        "un code, zéro peut commencer. <bookmark mark='first_choices'/> La première position "
        "offre quatre choix. <bookmark mark='choose_first_zero'/> Choisissons zéro : aucun "
        "chiffre n'est retiré. <bookmark mark='same_zero_again'/> La deuxième position offre "
        "encore quatre choix, même zéro. <bookmark mark='third_choices'/> La troisième aussi. "
        "<bookmark mark='multiply_code'/> Ainsi, quatre fois quatre fois quatre donne quatre "
        "puissance trois, soit soixante-quatre codes. <bookmark mark='order_code'/> L'ordre "
        "compte : zéro zéro trois et zéro trois zéro sont différents. "
        "<bookmark mark='end_code'/>"
    ),
    "code_rule": (
        "<bookmark mark='show_wrong_code'/> Quatre fois trois fois deux serait le calcul sans "
        "réutilisation : les choix diminueraient. <bookmark mark='restore_choices'/> Ici, les "
        "quatre chiffres restent disponibles. <bookmark mark='general_code'/> Avec p positions "
        "et n choix réutilisables à chaque position, on obtient n puissance p. "
        "<bookmark mark='end_code_rule'/>"
    ),
    "banana_setup": (
        "Dans BANANE, les six lettres sont déjà fixées : on les réordonne. "
        "<bookmark mark='tag_letters'/> Étiquetons provisoirement les deux A et les deux N. "
        "<bookmark mark='six_factorial'/> Avec ces étiquettes, les six objets sont distincts : "
        "il y a six factorielle ordres étiquetés. <bookmark mark='end_banana_setup'/>"
    ),
    "banana_overcount": (
        "<bookmark mark='swap_a_tags'/> Échanger les étiquettes des deux A ne change pas le "
        "mot visible : il reste BANANE. Cela donne deux factorielle étiquetages des A. "
        "<bookmark mark='swap_n_tags'/> Les deux N donnent aussi deux factorielle étiquetages. "
        "<bookmark mark='combine_duplicates'/> Chaque mot visible apparaît donc deux "
        "factorielle fois deux factorielle, soit quatre fois, dans le comptage étiqueté. "
        "<bookmark mark='end_banana_overcount'/>"
    ),
    "banana_formula": (
        "On corrige ce surcomptage en divisant six factorielle par deux factorielle pour les A "
        "et deux factorielle pour les N. <bookmark mark='banana_calculation'/> Le résultat est "
        "cent quatre-vingts. <bookmark mark='general_banana'/> En général, si les types "
        "d'objets ont les multiplicités n un jusqu'à n k, on divise N factorielle par le "
        "produit de leurs factorielles. <bookmark mark='end_banana_formula'/>"
    ),
    "transfer": (
        "Vérifions. <bookmark mark='pin_example'/> Quatre positions avec dix chiffres "
        "réutilisables donnent dix puissance quatre. <bookmark mark='maman_example'/> Dans "
        "MAMAN, la collection est fixée, avec deux M et deux A : cinq factorielle sur deux "
        "factorielle fois deux factorielle donne trente. <bookmark mark='end_transfer'/>"
    ),
    "closing": (
        "Ne choisissez pas une formule à partir du seul mot répétition. "
        "<bookmark mark='closing_left'/> Positions à remplir, choix toujours disponibles : "
        "n puissance p. <bookmark mark='closing_right'/> Collection fixée avec objets "
        "identiques : N factorielle, puis division des échanges invisibles. "
        "<bookmark mark='closing_question'/> Positions à remplir, ou collection à réordonner ? "
        "<bookmark mark='end_closing'/>"
    ),
}


@dataclass
class _NoVoiceTracker:
    """Petit substitut utilisé pendant un rendu sans narration."""

    duration: float = 0.0


class RepetitionsDenombrementFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    """Distinguer choix réutilisables et permutations d'objets identiques."""

    # ------------------------------------------------------------------
    # Narration facultative et synchronisation
    # ------------------------------------------------------------------
    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False

        if load_dotenv is not None:
            load_dotenv()

        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            print("[voiceover] Narration désactivée par MANIM_DISABLE_VOICEOVER.")
            return

        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover absent : rendu silencieux.")
            return

        key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not key or not region:
            print("[voiceover] Identifiants Azure absents : rendu silencieux.")
            return

        # manim-voiceover emploie les deux premières variables, tandis que le
        # dépôt accepte aussi les noms SPEECH_KEY / SPEECH_REGION.
        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", key)
        os.environ.setdefault("AZURE_SERVICE_REGION", region)
        os.environ.setdefault("SPEECH_KEY", key)
        os.environ.setdefault("SPEECH_REGION", region)

        try:
            self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        except Exception as exc:
            print(f"[voiceover] Configuration Azure impossible : {exc}. Rendu silencieux.")
            return
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text: str):
        ssml_text = tts.ssml(text)
        if self._voiceover_enabled:
            with self.voiceover(
                text=ssml_text,
                subcaption=tts.strip_ssml(ssml_text),
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def sync(self, bookmark: str, fallback: float = 0.45) -> None:
        """Attendre un signet narratif, ou une courte pause en mode silencieux."""

        if self._voiceover_enabled:
            self.wait_until_bookmark(bookmark)
        else:
            self.wait(fallback)

    # ------------------------------------------------------------------
    # Composants visuels réutilisables
    # ------------------------------------------------------------------
    @staticmethod
    def fit_width(mobject: Mobject, max_width: float) -> Mobject:
        if mobject.width > max_width:
            mobject.scale_to_fit_width(max_width)
        return mobject

    @staticmethod
    def make_slot(width: float = 1.12, height: float = 0.88) -> RoundedRectangle:
        return RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2.6,
            fill_color=WHITE,
            fill_opacity=1,
        )

    @staticmethod
    def make_chip(
        label: str,
        *,
        width: float = 0.48,
        height: float = 0.48,
        font_size: int = 22,
        color=ACCENT,
    ) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.08,
            stroke_color=color,
            stroke_width=2.0,
            fill_color=WHITE,
            fill_opacity=1,
        )
        text = Text(label, font_size=font_size, color=color).move_to(box)
        return VGroup(box, text)

    @staticmethod
    def make_letter_tile(
        letter: str,
        *,
        width: float = 0.78,
        height: float = 0.72,
        font_size: int = 29,
        stroke_color=BLACK,
    ) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.10,
            stroke_color=stroke_color,
            stroke_width=2.4,
            fill_color=WHITE,
            fill_opacity=1,
        )
        text = Text(letter, font_size=font_size).move_to(box)
        return VGroup(box, text)

    @staticmethod
    def make_panel(
        content: Mobject,
        *,
        color=ACCENT,
        buff: float = 0.28,
        fill_opacity: float = 0.035,
    ) -> VGroup:
        frame = RoundedRectangle(
            width=content.width + 2 * buff,
            height=content.height + 2 * buff,
            corner_radius=0.15,
            stroke_color=color,
            stroke_width=2.3,
            fill_color=color,
            fill_opacity=fill_opacity,
        ).move_to(content)
        return VGroup(frame, content)

    def make_choice_column(self, center_x: float, slot_number: int) -> VGroup:
        choices = VGroup(
            *[self.make_chip(str(digit)) for digit in range(4)]
        ).arrange(RIGHT, buff=0.08)
        choice_label = Text("4 choix", font_size=SMALL_SIZE, color=ACCENT)
        choice_label.next_to(choices, UP, buff=0.10)

        slot = self.make_slot()
        slot.move_to([center_x, -0.10, 0])
        choices.next_to(slot, UP, buff=0.36)
        choice_label.next_to(choices, UP, buff=0.10)

        position_label = Text(f"position {slot_number}", font_size=21)
        position_label.next_to(slot, DOWN, buff=0.12)

        return VGroup(choice_label, choices, slot, position_label)

    @staticmethod
    def make_tag(number: str, anchor: Mobject) -> VGroup:
        dot = Circle(
            radius=0.16,
            stroke_color=ACCENT,
            stroke_width=1.8,
            fill_color=WHITE,
            fill_opacity=1,
        )
        text = Text(number, font_size=18, color=ACCENT).move_to(dot)
        tag = VGroup(dot, text)
        tag.next_to(anchor, UP, buff=0.08)
        return tag

    def new_subtitle(self, text: str) -> Text:
        subtitle = Text(text, font_size=SUBTITLE_SIZE, color=ACCENT)
        subtitle.next_to(self.title, DOWN, buff=0.08)
        return subtitle

    def replace_subtitle(self, current: Mobject, text: str) -> Text:
        new = self.new_subtitle(text)
        self.play(FadeOut(current), FadeIn(new), run_time=0.55)
        return new

    # ------------------------------------------------------------------
    # Construction principale
    # ------------------------------------------------------------------
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        self.title = Text("Dénombrement 3", font_size=TITLE_SIZE)
        self.title.to_edge(UP, buff=0.22)
        subtitle = self.new_subtitle("Réutiliser un choix ou corriger un surcomptage ?")
        header_line = Line(
            LEFT * 6.20,
            RIGHT * 6.20,
            stroke_color=GRAY_B,
            stroke_width=1.2,
        )
        header_line.next_to(subtitle, DOWN, buff=0.15)

        # ------------------------------------------------------------------
        # 0. Question centrale
        # ------------------------------------------------------------------
        code_slots_small = VGroup(*[self.make_slot(0.72, 0.58) for _ in range(3)]).arrange(
            RIGHT, buff=0.10
        )
        code_digits_small = VGroup(
            *[
                Text(value, font_size=24, color=ACCENT).move_to(slot)
                for value, slot in zip(("0", "0", "3"), code_slots_small)
            ]
        )
        code_icon = VGroup(code_slots_small, code_digits_small)
        code_content = VGroup(
            Text("Remplir des positions", font_size=30, color=ACCENT),
            code_icon,
            Text("un choix peut revenir", font_size=24),
        ).arrange(DOWN, buff=0.24)
        code_panel = self.make_panel(code_content)

        banana_row_small = VGroup(
            *[self.make_letter_tile(letter, width=0.52, height=0.50, font_size=22) for letter in "BANANE"]
        ).arrange(RIGHT, buff=0.06)
        word_content = VGroup(
            Text("Réordonner une collection", font_size=30, color=ACCENT),
            banana_row_small,
            Text("des objets sont identiques", font_size=24),
        ).arrange(DOWN, buff=0.24)
        word_panel = self.make_panel(word_content)

        intro_panels = VGroup(code_panel, word_panel).arrange(RIGHT, buff=0.70)
        self.fit_width(intro_panels, 11.8)
        intro_panels.next_to(header_line, DOWN, buff=0.55)

        central_question = VGroup(
            Text("La question décisive", font_size=26, color=WARNING),
            Text(
                "Positions à remplir  —  ou  —  collection à réordonner ?",
                font_size=31,
            ),
        ).arrange(DOWN, buff=0.15)
        central_question.to_edge(DOWN, buff=0.48)

        with self.narrated(SCRIPT["intro"]):
            self.play(FadeIn(self.title), FadeIn(subtitle), Create(header_line), run_time=1.0)
            self.sync("show_code", 0.35)
            self.play(FadeIn(code_panel), run_time=0.8)
            self.sync("show_word", 0.45)
            self.play(FadeIn(word_panel), run_time=0.8)
            self.sync("central_question", 0.45)
            self.play(FadeIn(central_question), run_time=0.8)
            self.play(Circumscribe(central_question[1], color=ACCENT), run_time=0.9)
            self.sync("end_intro", 0.55)

        # ------------------------------------------------------------------
        # 1. Positions avec choix réutilisables
        # ------------------------------------------------------------------
        self.play(FadeOut(intro_panels), FadeOut(central_question), run_time=0.65)
        subtitle = self.replace_subtitle(subtitle, "Cas 1 — Chaque position reçoit un choix réutilisable")

        columns = VGroup(
            self.make_choice_column(-3.45, 1),
            self.make_choice_column(0.00, 2),
            self.make_choice_column(3.45, 3),
        )
        columns.next_to(header_line, DOWN, buff=0.55)

        code_note = Text(
            "Code : le zéro initial est permis.",
            font_size=22,
            color=MUTED,
        )
        code_note.next_to(columns, DOWN, buff=0.18)

        chosen_digits = VGroup(
            Text("0", font_size=38, color=ACCENT).move_to(columns[0][2]),
            Text("0", font_size=38, color=ACCENT).move_to(columns[1][2]),
            Text("3", font_size=38, color=ACCENT).move_to(columns[2][2]),
        )

        multiplication = MathTex(
            r"4\times4\times4=4^3=64",
            font_size=FORMULA_SIZE,
        )
        multiplication.set_color_by_tex("4^3", ACCENT)
        multiplication.set_color_by_tex("64", ACCENT)
        multiplication.to_edge(DOWN, buff=0.62)

        order_note = VGroup(
            MathTex(r"003", font_size=36, color=ACCENT),
            MathTex(r"\neq", font_size=34, color=WARNING),
            MathTex(r"030", font_size=36, color=ACCENT),
            Text("l'ordre compte", font_size=23),
        ).arrange(RIGHT, buff=0.20)
        order_note.next_to(multiplication, UP, buff=0.22)

        with self.narrated(SCRIPT["code"]):
            self.play(FadeIn(columns), FadeIn(code_note), run_time=0.9)
            self.sync("first_choices", 0.45)
            self.play(Indicate(columns[0][1], color=ACCENT), run_time=0.8)
            self.sync("choose_first_zero", 0.45)
            self.play(
                TransformFromCopy(columns[0][1][0][1], chosen_digits[0]),
                run_time=0.75,
            )
            self.sync("same_zero_again", 0.55)
            self.play(Indicate(columns[1][1][0], color=ACCENT), run_time=0.75)
            self.play(
                TransformFromCopy(columns[1][1][0][1], chosen_digits[1]),
                run_time=0.70,
            )
            self.sync("third_choices", 0.45)
            self.play(Indicate(columns[2][1], color=ACCENT), run_time=0.75)
            self.play(
                TransformFromCopy(columns[2][1][3][1], chosen_digits[2]),
                run_time=0.70,
            )
            self.sync("multiply_code", 0.55)
            self.play(Write(multiplication), run_time=1.15)
            self.sync("order_code", 0.45)
            self.play(FadeIn(order_note), run_time=0.75)
            self.sync("end_code", 0.55)

        # Erreur et généralisation sur un écran plus léger.
        code_stage = VGroup(columns, code_note, chosen_digits, multiplication, order_note)
        self.play(FadeOut(code_stage), run_time=0.65)
        subtitle = self.replace_subtitle(subtitle, "Pourquoi ce n'est pas 4 × 3 × 2")

        wrong = MathTex(r"4\times3\times2", font_size=56, color=WARNING)
        wrong_cross = Cross(wrong, stroke_color=WARNING, stroke_width=7)
        wrong_group = VGroup(wrong, wrong_cross)
        wrong_explanation = Text(
            "Ce calcul retire un choix après chaque position.",
            font_size=BODY_SIZE,
        )
        wrong_block = VGroup(wrong_group, wrong_explanation).arrange(DOWN, buff=0.35)
        wrong_block.next_to(header_line, DOWN, buff=0.80)

        available_row = VGroup(
            Text("Après chaque choix :", font_size=27),
            VGroup(*[self.make_chip(str(d)) for d in range(4)]).arrange(RIGHT, buff=0.08),
            Text("toujours 4 possibilités", font_size=27, color=ACCENT),
        ).arrange(RIGHT, buff=0.28)
        available_row.next_to(wrong_block, DOWN, buff=0.55)

        code_general = self.make_panel(
            VGroup(
                Text("p positions, n choix à chaque position", font_size=28),
                MathTex(r"\boxed{n^p}", font_size=54, color=ACCENT),
                Text("à condition que chaque choix reste disponible", font_size=24),
            ).arrange(DOWN, buff=0.28)
        )
        code_general.to_edge(DOWN, buff=0.38)

        with self.narrated(SCRIPT["code_rule"]):
            self.sync("show_wrong_code", 0.35)
            self.play(Write(wrong), run_time=0.75)
            self.play(Create(wrong_cross), FadeIn(wrong_explanation), run_time=0.75)
            self.sync("restore_choices", 0.45)
            self.play(FadeIn(available_row), run_time=0.8)
            self.play(Indicate(available_row[1], color=ACCENT), run_time=0.8)
            self.sync("general_code", 0.45)
            self.play(FadeIn(code_general), run_time=0.85)
            self.play(Circumscribe(code_general[1][1], color=ACCENT), run_time=0.9)
            self.sync("end_code_rule", 0.55)

        # ------------------------------------------------------------------
        # 2. Collection fixée avec objets identiques
        # ------------------------------------------------------------------
        self.play(
            FadeOut(wrong_block),
            FadeOut(available_row),
            FadeOut(code_general),
            run_time=0.65,
        )
        subtitle = self.replace_subtitle(subtitle, "Cas 2 — Réordonner une collection déjà fixée")

        banana_tiles = VGroup(
            *[self.make_letter_tile(letter) for letter in "BANANE"]
        ).arrange(RIGHT, buff=0.13)
        banana_tiles.next_to(header_line, DOWN, buff=0.68)

        fixed_collection = Text(
            "Les 6 lettres sont déjà présentes.",
            font_size=BODY_SIZE,
            color=ACCENT,
        )
        fixed_collection.next_to(banana_tiles, DOWN, buff=0.28)

        tags = {
            "a1": self.make_tag("1", banana_tiles[1]),
            "n1": self.make_tag("1", banana_tiles[2]),
            "a2": self.make_tag("2", banana_tiles[3]),
            "n2": self.make_tag("2", banana_tiles[4]),
        }
        tag_group = VGroup(*tags.values())

        labelled_note = Text(
            "Avec les étiquettes : 6 objets distincts",
            font_size=27,
        )
        labelled_note.next_to(fixed_collection, DOWN, buff=0.50)
        six_factorial = MathTex(r"6!=720", font_size=54, color=ACCENT)
        six_factorial.next_to(labelled_note, DOWN, buff=0.25)

        with self.narrated(SCRIPT["banana_setup"]):
            self.play(FadeIn(banana_tiles), FadeIn(fixed_collection), run_time=0.85)
            self.sync("tag_letters", 0.50)
            self.play(LaggedStart(*[FadeIn(tag) for tag in tag_group], lag_ratio=0.12), run_time=1.0)
            self.sync("six_factorial", 0.50)
            self.play(FadeIn(labelled_note), Write(six_factorial), run_time=0.95)
            self.sync("end_banana_setup", 0.55)

        # Le mot reste fixe. Seules les petites étiquettes se déplacent : aucune
        # transformation de groupe ne peut faire sauter la rangée vers l'origine.
        self.play(FadeOut(labelled_note), FadeOut(six_factorial), run_time=0.55)
        subtitle = self.replace_subtitle(subtitle, "Pourquoi 6! compte chaque mot plusieurs fois")

        visible_word_label = Text("mot visible : BANANE", font_size=27, color=ACCENT)
        visible_word_label.next_to(fixed_collection, DOWN, buff=0.42)

        a_counter = VGroup(
            Text("étiquettes des A", font_size=25),
            MathTex(r"2!", font_size=42, color=ACCENT),
        ).arrange(DOWN, buff=0.12)
        n_counter = VGroup(
            Text("étiquettes des N", font_size=25),
            MathTex(r"2!", font_size=42, color=ACCENT),
        ).arrange(DOWN, buff=0.12)
        duplicate_counters = VGroup(a_counter, n_counter).arrange(RIGHT, buff=1.10)
        duplicate_counters.next_to(visible_word_label, DOWN, buff=0.42)

        duplicate_product = VGroup(
            MathTex(r"2!\times2!=4", font_size=50),
            Text("4 étiquetages pour le même mot visible", font_size=27),
        ).arrange(DOWN, buff=0.18)
        duplicate_product.to_edge(DOWN, buff=0.45)

        a1_start = tags["a1"].get_center().copy()
        a2_start = tags["a2"].get_center().copy()
        n1_start = tags["n1"].get_center().copy()
        n2_start = tags["n2"].get_center().copy()

        with self.narrated(SCRIPT["banana_overcount"]):
            self.play(FadeIn(visible_word_label), run_time=0.55)
            self.sync("swap_a_tags", 0.45)
            self.play(
                tags["a1"].animate.move_to(a2_start),
                tags["a2"].animate.move_to(a1_start),
                run_time=0.85,
            )
            self.play(Indicate(banana_tiles, color=ACCENT), FadeIn(a_counter), run_time=0.85)
            self.sync("swap_n_tags", 0.50)
            self.play(
                tags["n1"].animate.move_to(n2_start),
                tags["n2"].animate.move_to(n1_start),
                run_time=0.85,
            )
            self.play(Indicate(banana_tiles, color=ACCENT), FadeIn(n_counter), run_time=0.85)
            self.sync("combine_duplicates", 0.50)
            self.play(FadeIn(duplicate_product), run_time=0.85)
            self.play(Circumscribe(duplicate_product[0], color=ACCENT), run_time=0.9)
            self.sync("end_banana_overcount", 0.60)

        # Formule particulière puis justification générale.
        overcount_stage = VGroup(
            banana_tiles,
            fixed_collection,
            tag_group,
            visible_word_label,
            duplicate_counters,
            duplicate_product,
        )
        self.play(FadeOut(overcount_stage), run_time=0.65)
        subtitle = self.replace_subtitle(subtitle, "Corriger le surcomptage")

        banana_calculation = VGroup(
            MathTex(r"\frac{6!}{2!\,2!}", font_size=58),
            MathTex(r"=\frac{720}{4}", font_size=48),
            MathTex(r"=180", font_size=58, color=ACCENT),
        ).arrange(RIGHT, buff=0.35)
        banana_calculation.next_to(header_line, DOWN, buff=0.75)

        calculation_labels = VGroup(
            Text("6 lettres", font_size=24),
            Text("2 A", font_size=24, color=ACCENT),
            Text("2 N", font_size=24, color=ACCENT),
        ).arrange(RIGHT, buff=1.05)
        calculation_labels.next_to(banana_calculation, DOWN, buff=0.32)

        proof_line = VGroup(
            Text("permutations étiquetées", font_size=24),
            MathTex(r"\div", font_size=34),
            Text("étiquetages invisibles", font_size=24),
            MathTex(r"=", font_size=34),
            Text("permutations distinctes", font_size=24),
        ).arrange(RIGHT, buff=0.18)
        self.fit_width(proof_line, 11.6)
        proof_line.next_to(calculation_labels, DOWN, buff=0.42)

        general_formula = self.make_panel(
            VGroup(
                MathTex(
                    r"\boxed{\frac{N!}{n_1!\,n_2!\cdots n_k!}}",
                    font_size=52,
                    color=ACCENT,
                ),
                MathTex(r"n_1+n_2+\cdots+n_k=N", font_size=34),
                Text(
                    "Chaque facteur du dénominateur corrige des échanges invisibles.",
                    font_size=24,
                ),
            ).arrange(DOWN, buff=0.24)
        )
        general_formula.to_edge(DOWN, buff=0.34)

        with self.narrated(SCRIPT["banana_formula"]):
            self.play(FadeIn(banana_calculation[0]), FadeIn(calculation_labels), run_time=0.8)
            self.sync("banana_calculation", 0.45)
            self.play(FadeIn(banana_calculation[1]), run_time=0.60)
            self.play(FadeIn(banana_calculation[2]), run_time=0.60)
            self.play(FadeIn(proof_line), run_time=0.75)
            self.play(Circumscribe(banana_calculation[2], color=ACCENT), run_time=0.85)
            self.sync("general_banana", 0.55)
            self.play(FadeIn(general_formula), run_time=0.85)
            self.sync("end_banana_formula", 0.60)

        # ------------------------------------------------------------------
        # 3. Deux exemples de transfert
        # ------------------------------------------------------------------
        formula_stage = VGroup(
            banana_calculation,
            calculation_labels,
            proof_line,
            general_formula,
        )
        self.play(FadeOut(formula_stage), run_time=0.65)
        subtitle = self.replace_subtitle(subtitle, "Test rapide — Quelle structure reconnaissez-vous ?")

        pin_visual = VGroup(*[self.make_slot(0.66, 0.55) for _ in range(4)]).arrange(
            RIGHT, buff=0.09
        )
        pin_content = VGroup(
            Text("Code à 4 positions", font_size=28, color=ACCENT),
            pin_visual,
            Text("10 chiffres réutilisables", font_size=23),
            MathTex(r"10^4=10\,000", font_size=43, color=ACCENT),
        ).arrange(DOWN, buff=0.22)
        pin_panel = self.make_panel(pin_content)

        maman_visual = VGroup(
            *[self.make_letter_tile(letter, width=0.52, height=0.50, font_size=22) for letter in "MAMAN"]
        ).arrange(RIGHT, buff=0.07)
        maman_content = VGroup(
            Text("Réordonner MAMAN", font_size=28, color=ACCENT),
            maman_visual,
            Text("2 M et 2 A identiques", font_size=23),
            MathTex(r"\frac{5!}{2!\,2!}=30", font_size=41, color=ACCENT),
        ).arrange(DOWN, buff=0.22)
        maman_panel = self.make_panel(maman_content)

        transfer_panels = VGroup(pin_panel, maman_panel).arrange(RIGHT, buff=0.72)
        self.fit_width(transfer_panels, 11.8)
        transfer_panels.next_to(header_line, DOWN, buff=0.62)

        transfer_cues = VGroup(
            Text("positions à remplir", font_size=25, color=ACCENT),
            Text("collection à réordonner", font_size=25, color=ACCENT),
        ).arrange(RIGHT, buff=2.0)
        transfer_cues.next_to(transfer_panels, DOWN, buff=0.35)

        with self.narrated(SCRIPT["transfer"]):
            self.sync("pin_example", 0.35)
            self.play(FadeIn(pin_panel), run_time=0.85)
            self.play(Indicate(pin_content[3], color=ACCENT), run_time=0.75)
            self.sync("maman_example", 0.50)
            self.play(FadeIn(maman_panel), run_time=0.85)
            self.play(Indicate(maman_content[3], color=ACCENT), run_time=0.75)
            self.play(FadeIn(transfer_cues), run_time=0.65)
            self.sync("end_transfer", 0.55)

        # ------------------------------------------------------------------
        # 4. Synthèse finale
        # ------------------------------------------------------------------
        self.play(FadeOut(transfer_panels), FadeOut(transfer_cues), run_time=0.65)
        subtitle = self.replace_subtitle(subtitle, "La règle de décision")

        left_summary_content = VGroup(
            Text("Positions à remplir", font_size=30, color=ACCENT),
            VGroup(*[self.make_slot(0.68, 0.55) for _ in range(3)]).arrange(RIGHT, buff=0.09),
            Text("chaque choix reste disponible", font_size=23),
            MathTex(r"\boxed{n^p}", font_size=50, color=ACCENT),
        ).arrange(DOWN, buff=0.24)
        left_summary = self.make_panel(left_summary_content)

        right_summary_content = VGroup(
            Text("Collection à réordonner", font_size=30, color=ACCENT),
            VGroup(
                *[self.make_letter_tile(letter, width=0.48, height=0.46, font_size=20) for letter in "BANANE"]
            ).arrange(RIGHT, buff=0.05),
            Text("corriger les échanges invisibles", font_size=23),
            MathTex(
                r"\boxed{\frac{N!}{n_1!\cdots n_k!}}",
                font_size=42,
                color=ACCENT,
            ),
        ).arrange(DOWN, buff=0.24)
        right_summary = self.make_panel(right_summary_content)

        summary_panels = VGroup(left_summary, right_summary).arrange(RIGHT, buff=0.68)
        self.fit_width(summary_panels, 11.8)
        summary_panels.next_to(header_line, DOWN, buff=0.55)

        final_question = VGroup(
            Text("Avant toute formule, demandez :", font_size=25, color=WARNING),
            Text(
                "positions à remplir  —  ou  —  collection à réordonner ?",
                font_size=30,
            ),
        ).arrange(DOWN, buff=0.14)
        final_question.to_edge(DOWN, buff=0.43)

        with self.narrated(SCRIPT["closing"]):
            self.sync("closing_left", 0.35)
            self.play(FadeIn(left_summary), run_time=0.85)
            self.sync("closing_right", 0.50)
            self.play(FadeIn(right_summary), run_time=0.85)
            self.sync("closing_question", 0.50)
            self.play(FadeIn(final_question), run_time=0.75)
            self.play(Circumscribe(final_question[1], color=ACCENT), run_time=0.95)
            self.sync("end_closing", 0.65)

        self.wait(1.2)
