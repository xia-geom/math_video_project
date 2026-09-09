"""Opérations sur les vecteurs — troisième passe approfondie.

Cette capsule relie systématiquement trois représentations :

1. le déplacement dans le plan ;
2. les composantes horizontale et verticale ;
3. la formule algébrique.

La progression reste volontairement lente : une idée nouvelle par acte, résultats
cachés jusqu'au moment du calcul, et pauses de secours lors des aperçus sans voix.

Cette passe impose aussi une vraie grille de mise en page : ouverture en deux
zones, bande basse libre pour les sous-titres, transitions sans objets résiduels
et cartes de synthèse qui ne grossissent jamais leur texte artificiellement.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GRAY_D,
    GRAY_E,
    GREEN_D,
    LEFT,
    RED_D,
    RIGHT,
    SEMIBOLD,
    UP,
    WHITE,
    Arrow,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    MathTex,
    Matrix,
    Mobject,
    NumberPlane,
    ReplacementTransform,
    RoundedRectangle,
    Scene,
    SurroundingRectangle,
    Tex,
    Text,
    Transform,
    VGroup,
    Write,
    config,
)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.azure import AzureService
except ImportError:
    VoiceoverScene = None
    AzureService = None

import tools.tts as tts
from tools.branding import play_uqam_intro


# ---------------------------------------------------------------------------
# Visual defaults
# ---------------------------------------------------------------------------
config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
SECONDARY = GRAY_D
RESULT = GREEN_D
WARN = RED_D
PALE = GRAY_E
VOICE_SPEED = 0.86


# ---------------------------------------------------------------------------
# Narration
# ---------------------------------------------------------------------------
SCRIPT = [
    {
        "caption": "Comment les coordonnées décrivent-elles un déplacement ?",
        "ssml": tts.ssml(
            "Comment les opérations sur les coordonnées deviennent-elles des déplacements visibles ? "
            "<break time='350ms'/>Nous allons partir du mouvement, puis écrire la formule."
        ),
    },
    {
        "caption": "Additionner, c’est enchaîner deux déplacements.",
        "ssml": tts.ssml(
            "Partons de l'origine. "
            f"<bookmark mark='u_move'/>Le vecteur {tts.char('u')} avance de trois unités vers la droite "
            "et d'une unité vers le haut. "
            f"<bookmark mark='v_move'/>Puis le vecteur {tts.char('v')} avance d'une unité vers la gauche "
            "et de deux unités vers le haut. "
            "<bookmark mark='direct_sum'/>Le déplacement total relie directement le départ à l'arrivée. "
            f"<bookmark mark='horizontal_sum'/>Horizontalement, trois {tts.PLUS} moins un donne deux. "
            f"<bookmark mark='vertical_sum'/>Verticalement, un {tts.PLUS} deux donne trois. "
            "<bookmark mark='sum_formula'/>Le vecteur somme est donc deux, trois."
        ),
    },
    {
        "caption": "Deux ordres, le même point d’arrivée.",
        "ssml": tts.ssml(
            "Plaçons maintenant les deux vecteurs au même point de départ. "
            f"<bookmark mark='u_then_v'/>On peut suivre {tts.char('u')} puis {tts.char('v')}. "
            f"<bookmark mark='v_then_u'/>Ou suivre {tts.char('v')} puis {tts.char('u')}. "
            "<bookmark mark='same_endpoint'/>Les deux chemins arrivent au même point. "
            "L'addition des vecteurs est donc commutative."
        ),
    },
    {
        "caption": "Un scalaire étire, réduit ou renverse le sens.",
        "ssml": tts.ssml(
            f"Prenons {tts.char('u')} égal à deux, un. "
            f"<bookmark mark='double'/>Le vecteur deux {tts.char('u')} reste sur la même droite, garde le même sens, "
            "et double la longueur. "
            f"<bookmark mark='negative_half'/>Moins un demi {tts.char('u')} reste parallèle, "
            "réduit la longueur de moitié, et prend le sens opposé. "
            f"<bookmark mark='zero_scalar'/>Zéro fois {tts.char('u')} donne le vecteur nul. "
            "<bookmark mark='scalar_rule'/>Le scalaire multiplie chaque composante."
        ),
    },
    {
        "caption": "Soustraire v, c’est ajouter son opposé.",
        "ssml": tts.ssml(
            f"Pour soustraire {tts.char('v')}, on construit le vecteur opposé. "
            f"<bookmark mark='opposite'/>Moins {tts.char('v')} a la même longueur que {tts.char('v')}, "
            "mais le sens contraire. "
            f"<bookmark mark='subtract_path'/>On l'ajoute ensuite à {tts.char('u')}. "
            "<bookmark mark='subtract_components'/>Coordonnée par coordonnée, soustraire revient à ajouter l'opposé."
        ),
    },
    {
        "caption": "Pour AB : arrivée moins départ.",
        "ssml": tts.ssml(
            "Quand un vecteur relie deux points, l'ordre devient essentiel. "
            f"<bookmark mark='ab_arrow'/>Pour aller de {tts.char('A')} vers {tts.char('B')}, on fait arrivée moins départ : {tts.char('B')} moins {tts.char('A')}. "
            "<bookmark mark='ba_arrow'/>Dans l'autre sens, on obtient le vecteur opposé. "
            "<bookmark mark='ab_warning'/>Il faut donc toujours lire la flèche avant de soustraire."
        ),
    },
    {
        "caption": "Dans R³, la règle reste coordonnée par coordonnée.",
        "ssml": tts.ssml(
            "Le passage à trois dimensions ne change pas la règle. "
            "<bookmark mark='r3_first'/>On additionne les premières coordonnées. "
            "<bookmark mark='r3_second'/>Puis les deuxièmes. "
            "<bookmark mark='r3_third'/>Puis les troisièmes. "
            "<bookmark mark='r3_done'/>Le résultat possède encore trois composantes."
        ),
    },
    {
        "caption": "Mouvement, composantes, formule : trois vues d’une même opération.",
        "ssml": tts.ssml(
            "À retenir. "
            "<bookmark mark='recap_add'/>Additionner, c'est enchaîner les déplacements. "
            "<bookmark mark='recap_sub'/>Soustraire, c'est ajouter le vecteur opposé. "
            "<bookmark mark='recap_scale'/>Multiplier par un scalaire change la longueur, "
            "et parfois le sens. "
            "Les mêmes règles valent dans le plan et dans l'espace."
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


BaseScene = VoiceoverScene if VoiceoverScene is not None else Scene


class OperationsVecteursFR(BaseScene):
    """Addition, soustraction et multiplication scalaire des vecteurs."""

    # ------------------------------------------------------------------
    # Voiceover
    # ------------------------------------------------------------------
    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()

        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            print("[voiceover] MANIM_DISABLE_VOICEOVER set. Rendering without narration.")
            return

        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover not installed. Rendering without narration.")
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print("[voiceover] Missing Azure Speech credentials. Rendering without narration.")
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)

        try:
            self.set_speech_service(
                AzureService(voice=tts.VOICE_ID, global_speed=VOICE_SPEED)
            )
        except Exception as exc:
            print(f"[voiceover] Azure Speech setup failed: {exc}. Rendering without narration.")
            return
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, item: dict[str, str]):
        if self._voiceover_enabled:
            with self.voiceover(text=item["ssml"], subcaption=item["caption"]) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def sync(self, mark: str, silent_wait: float = 0.55) -> None:
        """Wait for a narration bookmark, or pause in silent previews."""
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)
        else:
            self.wait(silent_wait)

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def clear_page(self, *mobjects: Mobject, run_time: float = 0.65) -> None:
        """Close one act cleanly and prevent visual bleed into the next one."""
        requested = [mob for mob in mobjects if mob is not None]
        # self.mobjects is the authoritative list: formula panels are often
        # animated line by line, so their container is not necessarily the
        # object that Manim actually registered in the scene.
        visible = list(self.mobjects) or requested
        if visible:
            self.play(*(FadeOut(mob) for mob in visible), run_time=run_time)
        # ReplacementTransform can leave descendants outside the group passed
        # above.  Clearing the scene after the visible fade makes every act
        # start from a genuinely blank frame.
        self.clear()
        self.wait(0.12)

    def make_heading(self, text: str) -> Text:
        heading = Text(text, font_size=36, weight=SEMIBOLD)
        if heading.width > 12.2:
            heading.scale_to_fit_width(12.2)
        return heading.to_edge(UP, buff=0.35)

    def make_plane(
        self,
        *,
        x_range: tuple[int, int, int] = (-2, 6, 1),
        y_range: tuple[int, int, int] = (-2, 5, 1),
        unit_size: float = 0.72,
        center=LEFT * 3.15 + DOWN * 0.12,
    ) -> NumberPlane:
        """Create a plane with equal visual units on both axes."""
        x_span = x_range[1] - x_range[0]
        y_span = y_range[1] - y_range[0]
        plane = NumberPlane(
            x_range=x_range,
            y_range=y_range,
            x_length=x_span * unit_size,
            y_length=y_span * unit_size,
            background_line_style={
                "stroke_color": PALE,
                "stroke_width": 1.35,
                "stroke_opacity": 0.82,
            },
            axis_config={
                "color": BLACK,
                "stroke_width": 2.2,
                "include_tip": True,
            },
        )
        plane.move_to(center)
        return plane

    def vector_arrow(
        self,
        plane: NumberPlane,
        start: tuple[float, float],
        end: tuple[float, float],
        *,
        color=ACCENT,
        stroke_width: float = 6,
    ) -> Arrow:
        return Arrow(
            plane.c2p(*start),
            plane.c2p(*end),
            buff=0,
            color=color,
            stroke_width=stroke_width,
            max_tip_length_to_length_ratio=0.16,
        )

    def vector_label(
        self,
        plane: NumberPlane,
        start: tuple[float, float],
        end: tuple[float, float],
        tex: str,
        *,
        color=BLACK,
        offset=UP * 0.24,
        font_size: int = 34,
    ) -> MathTex:
        label = MathTex(tex, font_size=font_size, color=color)
        midpoint = (plane.c2p(*start) + plane.c2p(*end)) / 2
        label.move_to(midpoint + offset)
        return label

    def formula_panel(self, *lines: Mobject, width: float = 5.05) -> VGroup:
        content = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        if content.width > width - 0.55:
            content.scale_to_fit_width(width - 0.55)
        box = RoundedRectangle(
            width=width,
            height=max(2.15, content.height + 0.58),
            corner_radius=0.16,
            stroke_color=BLACK,
            stroke_width=2.2,
            fill_color=WHITE,
            fill_opacity=0.97,
        )
        content.move_to(box)
        return VGroup(box, content).move_to(RIGHT * 3.75 + DOWN * 0.1)

    def component_row(self, label: str, calculation: str, color=BLACK) -> VGroup:
        label_mob = Text(label, font_size=27, color=SECONDARY)
        calculation_mob = MathTex(calculation, font_size=39, color=color)
        return VGroup(label_mob, calculation_mob).arrange(RIGHT, buff=0.38)

    def recap_card(self, title: str, formula: str, note: str) -> VGroup:
        box = RoundedRectangle(
            width=3.85,
            height=3.05,
            corner_radius=0.18,
            stroke_color=BLACK,
            stroke_width=2.1,
            fill_color=ACCENT,
            fill_opacity=0.05,
        )
        title_mob = Text(title, font_size=30, weight=SEMIBOLD)
        formula_mob = MathTex(formula, font_size=40, color=ACCENT)
        if formula_mob.width > 3.25:
            formula_mob.scale_to_fit_width(3.25)
        note_mob = Text(note, font_size=23, line_spacing=0.92)
        # scale_to_fit_width also enlarges short text.  The former unconditional
        # call made these two-line notes huge and caused the closing overlap.
        if note_mob.width > 3.15:
            note_mob.scale_to_fit_width(3.15)
        content = VGroup(title_mob, formula_mob, note_mob).arrange(DOWN, buff=0.28)
        if content.height > 2.45:
            content.scale_to_fit_height(2.45)
        content.move_to(box)
        return VGroup(box, content)

    # ------------------------------------------------------------------
    # Scene
    # ------------------------------------------------------------------
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)
        # Some branding helpers retain their final logo as a scene mobject.
        # Start the lesson on a clean frame regardless of the helper version.
        self.clear()
        self.wait(0.18)

        # --------------------------------------------------------------
        # 0. Central question
        # --------------------------------------------------------------
        title = Text("Vecteurs — opérations", font_size=48, weight=SEMIBOLD)
        question = Text(
            "Comment les coordonnées décrivent-elles un déplacement ?",
            font_size=33,
        )
        if question.width > 11.8:
            question.scale_to_fit_width(11.8)
        opening_copy = VGroup(title, question).arrange(DOWN, buff=0.34)
        opening_copy.to_edge(UP, buff=0.58)
        start = LEFT * 2.7 + DOWN * 1.0
        corner = LEFT * 0.4 + DOWN * 0.15
        end = RIGHT * 1.45 + UP * 1.35
        demo_u = Arrow(start, corner, buff=0, color=ACCENT, stroke_width=7)
        demo_v = Arrow(corner, end, buff=0, color=SECONDARY, stroke_width=7)
        demo_sum = Arrow(start, end, buff=0, color=RESULT, stroke_width=7)
        demo = VGroup(demo_u, demo_v, demo_sum)
        demo.move_to(DOWN * 0.95)

        with self.narrated(SCRIPT[0]):
            self.play(FadeIn(title), run_time=0.7)
            self.play(Write(question), run_time=1.0)
            self.play(GrowArrow(demo_u), run_time=0.8)
            self.play(GrowArrow(demo_v), run_time=0.8)
            self.play(GrowArrow(demo_sum), run_time=0.8)
            self.wait(1.1)
        self.clear_page(title, question, demo)

        # --------------------------------------------------------------
        # 1. Addition: motion, components, formula
        # --------------------------------------------------------------
        heading = self.make_heading("Additionner = enchaîner deux déplacements")
        plane = self.make_plane()
        traveler = Dot(plane.c2p(0, 0), radius=0.09, color=BLACK)
        origin_label = MathTex("O", font_size=28).next_to(traveler, DOWN + LEFT, buff=0.08)
        u_arrow = self.vector_arrow(plane, (0, 0), (3, 1), color=ACCENT)
        v_shifted = self.vector_arrow(plane, (3, 1), (2, 3), color=SECONDARY)
        sum_arrow = self.vector_arrow(plane, (0, 0), (2, 3), color=RESULT)
        u_label = self.vector_label(plane, (0, 0), (3, 1), r"\vec u=(3,1)", color=ACCENT)
        v_label = self.vector_label(
            plane,
            (3, 1),
            (2, 3),
            r"\vec v=(-1,2)",
            color=SECONDARY,
            offset=RIGHT * 0.48,
        )
        sum_label = self.vector_label(
            plane,
            (0, 0),
            (2, 3),
            r"\vec u+\vec v",
            color=RESULT,
            offset=LEFT * 0.48,
        )

        horizontal = self.component_row("horizontal", r"3+(-1)=2", color=ACCENT)
        vertical = self.component_row("vertical", r"1+2=3", color=SECONDARY)
        final_sum = MathTex(r"\vec u+\vec v=(2,3)", font_size=46, color=RESULT)
        panel = self.formula_panel(horizontal, vertical, final_sum)

        with self.narrated(SCRIPT[1]):
            self.play(FadeIn(heading), Create(plane), FadeIn(traveler, origin_label), run_time=1.0)
            self.sync("u_move", 0.6)
            self.play(
                GrowArrow(u_arrow),
                traveler.animate.move_to(plane.c2p(3, 1)),
                FadeIn(u_label),
                run_time=1.35,
            )
            self.sync("v_move", 0.65)
            self.play(
                GrowArrow(v_shifted),
                traveler.animate.move_to(plane.c2p(2, 3)),
                FadeIn(v_label),
                run_time=1.35,
            )
            self.sync("direct_sum", 0.55)
            self.play(GrowArrow(sum_arrow), FadeIn(sum_label), run_time=1.05)
            self.sync("horizontal_sum", 0.55)
            self.play(FadeIn(panel[0]), FadeIn(horizontal), run_time=0.9)
            self.sync("vertical_sum", 0.55)
            self.play(FadeIn(vertical), run_time=0.8)
            self.sync("sum_formula", 0.55)
            self.play(Write(final_sum), Indicate(sum_arrow, color=RESULT), run_time=1.0)
            self.wait(1.5)
        self.clear_page(
            heading,
            plane,
            traveler,
            origin_label,
            u_arrow,
            v_shifted,
            sum_arrow,
            u_label,
            v_label,
            sum_label,
            panel,
        )

        # --------------------------------------------------------------
        # 2. Parallelogram and commutativity
        # --------------------------------------------------------------
        heading = self.make_heading("Deux chemins, un même point d’arrivée")
        plane = self.make_plane()
        u0 = self.vector_arrow(plane, (0, 0), (3, 1), color=ACCENT)
        v0 = self.vector_arrow(plane, (0, 0), (-1, 2), color=SECONDARY)
        v_after_u = self.vector_arrow(plane, (3, 1), (2, 3), color=SECONDARY, stroke_width=4.5)
        u_after_v = self.vector_arrow(plane, (-1, 2), (2, 3), color=ACCENT, stroke_width=4.5)
        diagonal = self.vector_arrow(plane, (0, 0), (2, 3), color=RESULT)
        endpoint = Dot(plane.c2p(2, 3), radius=0.1, color=RESULT)
        path_one = Text("u puis v", font_size=27, color=SECONDARY).move_to(RIGHT * 3.7 + UP * 0.9)
        path_two = Text("v puis u", font_size=27, color=SECONDARY).move_to(RIGHT * 3.7 + UP * 0.15)
        commutative = MathTex(
            r"\vec u+\vec v=\vec v+\vec u",
            font_size=48,
            color=RESULT,
        ).move_to(RIGHT * 3.7 + DOWN * 0.75)
        caution = Text(
            "Cette propriété concerne l’addition.",
            font_size=25,
            color=SECONDARY,
        ).next_to(commutative, DOWN, buff=0.42)

        with self.narrated(SCRIPT[2]):
            self.play(FadeIn(heading), Create(plane), GrowArrow(u0), GrowArrow(v0), run_time=1.1)
            self.sync("u_then_v", 0.55)
            self.play(GrowArrow(v_after_u), FadeIn(path_one), run_time=1.0)
            self.sync("v_then_u", 0.55)
            self.play(GrowArrow(u_after_v), FadeIn(path_two), run_time=1.0)
            self.sync("same_endpoint", 0.55)
            self.play(FadeIn(endpoint), GrowArrow(diagonal), run_time=1.0)
            self.play(Write(commutative), FadeIn(caution), run_time=1.0)
            self.wait(1.5)
        self.clear_page(
            heading,
            plane,
            u0,
            v0,
            v_after_u,
            u_after_v,
            diagonal,
            endpoint,
            path_one,
            path_two,
            commutative,
            caution,
        )

        # --------------------------------------------------------------
        # 3. Scalar multiplication
        # --------------------------------------------------------------
        heading = self.make_heading("Multiplier par un scalaire")
        plane = self.make_plane(
            x_range=(-3, 6, 1),
            y_range=(-3, 4, 1),
            unit_size=0.69,
        )
        support_line = DashedLine(
            plane.c2p(-3, -1.5),
            plane.c2p(5, 2.5),
            color=PALE,
            stroke_width=3,
        )
        u_arrow = self.vector_arrow(plane, (0, 0), (2, 1), color=ACCENT)
        double_arrow = self.vector_arrow(
            plane,
            (0, 0),
            (4, 2),
            color=RESULT,
            stroke_width=4.5,
        )
        negative_half_arrow = self.vector_arrow(plane, (0, 0), (-1, -0.5), color=WARN)
        zero_dot = Dot(plane.c2p(0, 0), radius=0.12, color=BLACK)
        u_label = self.vector_label(plane, (0, 0), (2, 1), r"\vec u", color=ACCENT)
        double_label = self.vector_label(
            plane,
            (0, 0),
            (4, 2),
            r"2\vec u",
            color=RESULT,
            offset=UP * 0.45,
        )
        negative_label = self.vector_label(
            plane,
            (0, 0),
            (-1, -0.5),
            r"-\tfrac12\vec u",
            color=WARN,
            offset=DOWN * 0.45,
        )

        positive_rule = VGroup(
            MathTex(r"k>0", font_size=34, color=RESULT),
            Text("même direction et même sens", font_size=25),
        ).arrange(RIGHT, buff=0.28)
        negative_rule = VGroup(
            MathTex(r"k<0", font_size=34, color=WARN),
            Text("même direction, sens opposé", font_size=25),
        ).arrange(RIGHT, buff=0.28)
        zero_rule = VGroup(
            MathTex(r"k=0", font_size=34),
            MathTex(r"0\vec u=\vec 0", font_size=34),
        ).arrange(RIGHT, buff=0.35)
        scalar_formula = MathTex(r"k(x,y)=(kx,ky)", font_size=46, color=ACCENT)
        scalar_panel = self.formula_panel(
            positive_rule,
            negative_rule,
            zero_rule,
            scalar_formula,
        )

        with self.narrated(SCRIPT[3]):
            self.play(FadeIn(heading), Create(plane), Create(support_line), run_time=1.0)
            self.play(GrowArrow(u_arrow), FadeIn(u_label), run_time=0.9)
            self.sync("double", 0.6)
            self.play(GrowArrow(double_arrow), FadeIn(double_label), run_time=1.0)
            self.play(FadeIn(scalar_panel[0]), FadeIn(positive_rule), run_time=0.8)
            self.bring_to_front(u_arrow, u_label)
            self.sync("negative_half", 0.65)
            self.play(GrowArrow(negative_half_arrow), FadeIn(negative_label), run_time=1.0)
            self.play(FadeIn(negative_rule), run_time=0.75)
            self.sync("zero_scalar", 0.55)
            self.play(FadeIn(zero_dot), FadeIn(zero_rule), run_time=0.75)
            self.sync("scalar_rule", 0.55)
            self.play(Write(scalar_formula), run_time=0.9)
            self.wait(1.5)
        self.clear_page(
            heading,
            plane,
            support_line,
            u_arrow,
            double_arrow,
            negative_half_arrow,
            zero_dot,
            u_label,
            double_label,
            negative_label,
            scalar_panel,
        )

        # --------------------------------------------------------------
        # 4. Subtraction as addition of the opposite
        # --------------------------------------------------------------
        heading = self.make_heading("Soustraire = ajouter l’opposé")
        plane = self.make_plane(
            x_range=(-2, 6, 1),
            y_range=(-3, 4, 1),
            unit_size=0.71,
        )
        u_arrow = self.vector_arrow(plane, (0, 0), (3, 1), color=ACCENT)
        v_arrow = self.vector_arrow(plane, (0, 0), (-1, 2), color=SECONDARY)
        neg_v_arrow = self.vector_arrow(plane, (0, 0), (1, -2), color=WARN)
        neg_v_shifted = self.vector_arrow(plane, (3, 1), (4, -1), color=WARN)
        difference = self.vector_arrow(plane, (0, 0), (4, -1), color=RESULT)
        neg_v_label = self.vector_label(
            plane,
            (0, 0),
            (1, -2),
            r"-\vec v=(1,-2)",
            color=WARN,
            offset=RIGHT * 0.5,
        )
        difference_label = self.vector_label(
            plane,
            (0, 0),
            (4, -1),
            r"\vec u-\vec v",
            color=RESULT,
            offset=DOWN * 0.38,
        )
        line_1 = MathTex(r"\vec u-\vec v=\vec u+(-\vec v)", font_size=39)
        line_2 = MathTex(r"(3,1)-(-1,2)", font_size=38)
        line_3 = MathTex(r"=(3+1,\;1-2)=(4,-1)", font_size=37, color=RESULT)
        panel = self.formula_panel(line_1, line_2, line_3)

        with self.narrated(SCRIPT[4]):
            self.play(FadeIn(heading), Create(plane), GrowArrow(u_arrow), GrowArrow(v_arrow), run_time=1.15)
            self.sync("opposite", 0.6)
            self.play(ReplacementTransform(v_arrow.copy(), neg_v_arrow), FadeIn(neg_v_label), run_time=1.15)
            self.sync("subtract_path", 0.6)
            self.play(GrowArrow(neg_v_shifted), run_time=0.9)
            self.play(GrowArrow(difference), FadeIn(difference_label), run_time=0.9)
            self.sync("subtract_components", 0.6)
            self.play(FadeIn(panel[0]), Write(line_1), run_time=0.8)
            self.play(Write(line_2), run_time=0.75)
            self.play(Write(line_3), run_time=0.9)
            self.wait(1.5)
        self.clear_page(
            heading,
            plane,
            u_arrow,
            v_arrow,
            neg_v_arrow,
            neg_v_shifted,
            difference,
            neg_v_label,
            difference_label,
            panel,
        )

        # --------------------------------------------------------------
        # 5. Point-to-point vector: B - A
        # --------------------------------------------------------------
        heading = self.make_heading("Un vecteur entre deux points : arrivée moins départ")
        plane = self.make_plane(
            x_range=(-1, 6, 1),
            y_range=(-3, 4, 1),
            unit_size=0.72,
        )
        point_a = Dot(plane.c2p(1, 2), radius=0.1, color=BLACK)
        point_b = Dot(plane.c2p(4, -1), radius=0.1, color=BLACK)
        label_a = MathTex(r"A(1,2)", font_size=33).next_to(point_a, UP, buff=0.14)
        label_b = MathTex(r"B(4,-1)", font_size=33).next_to(point_b, DOWN, buff=0.14)
        ab_arrow = self.vector_arrow(plane, (1, 2), (4, -1), color=ACCENT)
        ba_arrow = self.vector_arrow(plane, (4, -1), (1, 2), color=WARN, stroke_width=4.4)

        ab_title = MathTex(r"\overrightarrow{AB}=B-A", font_size=43, color=ACCENT)
        ab_calc = MathTex(r"=(4-1,\;-1-2)=(3,-3)", font_size=36)
        ba_title = MathTex(r"\overrightarrow{BA}=A-B", font_size=43, color=WARN)
        ba_calc = MathTex(r"=(-3,3)=-\overrightarrow{AB}", font_size=36)
        warning = Text("Lire la flèche : départ → arrivée", font_size=27, color=WARN)
        panel = self.formula_panel(ab_title, ab_calc, ba_title, ba_calc, warning)

        with self.narrated(SCRIPT[5]):
            self.play(
                FadeIn(heading),
                Create(plane),
                FadeIn(point_a),
                FadeIn(point_b),
                FadeIn(label_a),
                FadeIn(label_b),
                run_time=1.0,
            )
            self.sync("ab_arrow", 0.6)
            self.play(GrowArrow(ab_arrow), FadeIn(panel[0]), Write(ab_title), Write(ab_calc), run_time=1.2)
            self.sync("ba_arrow", 0.6)
            self.play(
                ab_arrow.animate.set_opacity(0.18),
                GrowArrow(ba_arrow),
                Write(ba_title),
                Write(ba_calc),
                run_time=1.15,
            )
            self.sync("ab_warning", 0.55)
            self.play(FadeIn(warning), Indicate(ab_title, color=ACCENT), run_time=0.95)
            self.wait(1.5)
        self.clear_page(
            heading,
            plane,
            point_a,
            point_b,
            label_a,
            label_b,
            ab_arrow,
            ba_arrow,
            panel,
        )

        # --------------------------------------------------------------
        # 6. Extension to R^3 with hidden result entries
        # --------------------------------------------------------------
        heading = self.make_heading("Même règle dans ℝ³")
        vector_u = Matrix([[2], [-1], [3]], element_to_mobject_config={"font_size": 43})
        vector_v = Matrix([[-1], [4], [2]], element_to_mobject_config={"font_size": 43})
        result_vector = Matrix([["?"], ["?"], ["?"]], element_to_mobject_config={"font_size": 43})
        plus = MathTex("+", font_size=52)
        equals = MathTex("=", font_size=52)
        equation = VGroup(vector_u, plus, vector_v, equals, result_vector)
        equation.arrange(RIGHT, buff=0.42).scale_to_fit_width(10.8).move_to(UP * 0.15)

        entries_u = vector_u.get_entries()
        entries_v = vector_v.get_entries()
        result_entries = result_vector.get_entries()
        calculations = [
            (r"2+(-1)=1", "1", "r3_first"),
            (r"-1+4=3", "3", "r3_second"),
            (r"3+2=5", "5", "r3_third"),
        ]
        current_highlight: VGroup | None = None
        current_calc: MathTex | None = None

        with self.narrated(SCRIPT[6]):
            self.play(FadeIn(heading), FadeIn(equation), run_time=1.0)
            for index, (calculation, value, bookmark) in enumerate(calculations):
                self.sync(bookmark, 0.58)
                highlight = VGroup(
                    SurroundingRectangle(entries_u[index], color=ACCENT, buff=0.1, stroke_width=3),
                    SurroundingRectangle(entries_v[index], color=SECONDARY, buff=0.1, stroke_width=3),
                )
                calc = MathTex(calculation, font_size=39, color=RESULT).move_to(DOWN * 2.42)
                new_entry = MathTex(value, font_size=43, color=RESULT).move_to(result_entries[index])
                if current_highlight is None:
                    self.play(Create(highlight), Write(calc), run_time=0.8)
                else:
                    self.play(
                        ReplacementTransform(current_highlight, highlight),
                        ReplacementTransform(current_calc, calc),
                        run_time=0.75,
                    )
                # Transform the entry in place.  Keeping it inside result_vector
                # avoids a stale question mark being redrawn under the number.
                self.play(Transform(result_entries[index], new_entry), run_time=0.55)
                current_highlight = highlight
                current_calc = calc

            self.sync("r3_done", 0.55)
            self.play(FadeOut(current_highlight), FadeOut(current_calc), run_time=0.55)
            result_box = SurroundingRectangle(result_vector, color=RESULT, buff=0.16, stroke_width=3)
            self.play(Create(result_box), run_time=0.8)
            self.wait(1.5)
        self.clear_page(heading, equation, result_box)

        # --------------------------------------------------------------
        # 7. Recap
        # --------------------------------------------------------------
        heading = self.make_heading("Trois opérations, une même logique")
        card_add = self.recap_card(
            "Addition",
            r"(a,b)+(c,d)=(a+c,b+d)",
            "enchaîner les\ndéplacements",
        )
        card_sub = self.recap_card(
            "Soustraction",
            r"\vec u-\vec v=\vec u+(-\vec v)",
            "ajouter le\nvecteur opposé",
        )
        card_scale = self.recap_card(
            "Scalaire",
            r"k(a,b)=(ka,kb)",
            "étirer, réduire\nou inverser le sens",
        )
        cards = VGroup(card_add, card_sub, card_scale).arrange(RIGHT, buff=0.42)
        if cards.width > 12.25:
            cards.scale_to_fit_width(12.25)
        cards.move_to(UP * 0.18)
        r3_note = Text(
            "Les mêmes règles s’appliquent coordonnée par coordonnée dans ℝ² et ℝ³.",
            font_size=27,
            color=SECONDARY,
        ).move_to(DOWN * 2.38)
        if r3_note.width > 11.8:
            r3_note.scale_to_fit_width(11.8)

        with self.narrated(SCRIPT[7]):
            self.play(FadeIn(heading), run_time=0.6)
            self.sync("recap_add", 0.55)
            self.play(FadeIn(card_add, shift=UP * 0.12), run_time=0.8)
            self.sync("recap_sub", 0.55)
            self.play(FadeIn(card_sub, shift=UP * 0.12), run_time=0.8)
            self.sync("recap_scale", 0.55)
            self.play(FadeIn(card_scale, shift=UP * 0.12), run_time=0.8)
            self.play(FadeIn(r3_note), run_time=0.7)
            self.wait(2.0)

        # Leave a clean tail for concatenation with an outro or end card.
        self.clear_page(heading, cards, r3_note, run_time=0.7)
        self.wait(0.35)
