"""Vecteurs 1 — déplacement, composantes et norme.

Second-pass production version for the MAT0339 French video series.
The scene introduces one idea at a time: position, displacement, equivalent
representatives, components, norm, and the reversed-subtraction mistake.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    LEFT,
    ORIGIN,
    RED_D,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    LaggedStart,
    MathTex,
    RightAngle,
    Scene,
    SurroundingRectangle,
    Tex,
    Text,
    Transform,
    TransformFromCopy,
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

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
ERROR = RED_D
A = tts.A
B = tts.B
C = tts.C
D_SPOKEN = tts.char("D")

@dataclass
class _NoVoiceTracker:
    duration: float = 0.0

    def wait_until_bookmark(self, _mark: str) -> None:
        return None


BaseScene = VoiceoverScene if VoiceoverScene is not None else Scene


class VecteursDeplacementComposantesFR(BaseScene):
    """Build the vector concept from a visible displacement in the plane."""

    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            return
        if VoiceoverScene is None or AzureService is None:
            return

        key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not key or not region:
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", key)
        os.environ.setdefault("AZURE_SERVICE_REGION", region)
        os.environ.setdefault("SPEECH_KEY", key)
        os.environ.setdefault("SPEECH_REGION", region)
        try:
            self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        except Exception as exc:
            print(f"[voiceover] Azure setup failed: {exc}. Rendering silently.")
            return
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, spoken: str, caption: str):
        if self._voiceover_enabled:
            with self.voiceover(
                text=tts.ssml(spoken),
                subcaption=caption,
            ):
                # Bookmark waiting is a VoiceoverScene method in the current
                # manim-voiceover API, not a VoiceoverTracker method.
                yield self
        else:
            yield _NoVoiceTracker()

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        # ------------------------------------------------------------------
        # 1. Central question
        # ------------------------------------------------------------------
        title = Text("Vecteurs 1", font_size=46, weight="BOLD")
        question = Text(
            "Comment décrire un déplacement\nsans fixer son point de départ ?",
            font_size=34,
            line_spacing=0.92,
        ).next_to(title, DOWN, buff=0.55)
        title_group = VGroup(title, question).move_to(ORIGIN)

        caption = (
            "Comment décrire un déplacement sans fixer son point de départ ? "
            "C'est précisément le rôle d'un vecteur."
        )
        spoken = (
            "Comment décrire un déplacement sans fixer son point de départ ? "
            "<bookmark mark='answer'/>C'est précisément le rôle d'un vecteur."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(Write(title), run_time=0.75)
            self.play(FadeIn(question, shift=UP * 0.12), run_time=0.85)
            tracker.wait_until_bookmark("answer")
            self.play(question.animate.set_color(ACCENT), run_time=0.45)
        self.wait(0.65)
        self.play(FadeOut(title_group), run_time=0.55)

        # ------------------------------------------------------------------
        # 2. A point is a position; a vector is a displacement
        # ------------------------------------------------------------------
        axes = Axes(
            x_range=[-4, 5, 1],
            y_range=[-3, 4, 1],
            x_length=7.2,
            y_length=5.6,
            axis_config={
                "color": BLACK,
                "stroke_width": 2.2,
                "include_ticks": True,
            },
            tips=False,
        ).to_edge(LEFT, buff=0.55).shift(DOWN * 0.12)
        axis_labels = axes.get_axis_labels(
            MathTex("x", font_size=29),
            MathTex("y", font_size=29),
        )

        header = Text("Un point indique une position.", font_size=31)
        header.to_edge(UP, buff=0.42).shift(RIGHT * 1.25)

        a_xy = (-3, -1)
        b_xy = (1, 2)
        a_dot = Dot(axes.c2p(*a_xy), radius=0.075, color=BLACK)
        b_dot = Dot(axes.c2p(*b_xy), radius=0.075, color=BLACK)
        a_label = MathTex(r"A(-3,-1)", font_size=29).next_to(
            a_dot, DOWN + RIGHT, buff=0.12
        )
        b_label = MathTex(r"B(1,2)", font_size=29).next_to(
            b_dot, UP + RIGHT, buff=0.12
        )

        caption = (
            "Un point indique une position. Le point A et le point B sont deux "
            "endroits précis du plan."
        )
        spoken = (
            f"Un point indique une position. <bookmark mark='A'/>Le point {A} est à moins "
            f"trois, moins un. <bookmark mark='B'/>Le point {B} est à un, deux."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(Create(axes), FadeIn(axis_labels), FadeIn(header), run_time=1.05)
            tracker.wait_until_bookmark("A")
            self.play(FadeIn(a_dot), Write(a_label), run_time=0.65)
            tracker.wait_until_bookmark("B")
            self.play(FadeIn(b_dot), Write(b_label), run_time=0.65)
        self.wait(0.45)

        vector_ab = Arrow(
            axes.c2p(*a_xy),
            axes.c2p(*b_xy),
            buff=0.08,
            color=ACCENT,
            stroke_width=5,
            max_tip_length_to_length_ratio=0.14,
        )
        label_ab = MathTex(r"\overrightarrow{AB}", font_size=38, color=ACCENT)
        label_ab.next_to(vector_ab.get_center(), UP + LEFT, buff=0.18)
        vector_header = Text(
            "Un vecteur indique un déplacement.",
            font_size=31,
            color=ACCENT,
        ).move_to(header)

        caption = (
            "Le vecteur de A vers B n'est pas un troisième point. Il décrit le "
            "déplacement qui mène de A jusqu'à B."
        )
        spoken = (
            f"Le vecteur de {A} vers {B} n'est pas un troisième point. "
            "<bookmark mark='arrow'/>Il décrit le déplacement qui mène du départ jusqu'à "
            "l'arrivée."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(Transform(header, vector_header), run_time=0.55)
            tracker.wait_until_bookmark("arrow")
            self.play(GrowArrow(vector_ab), Write(label_ab), run_time=0.95)
        self.wait(0.7)

        # ------------------------------------------------------------------
        # 3. Equivalent representatives remain visible simultaneously
        # ------------------------------------------------------------------
        c_xy = (-2, -2)
        d_xy = (2, 1)
        c_dot = Dot(axes.c2p(*c_xy), radius=0.07, color=BLACK)
        d_dot = Dot(axes.c2p(*d_xy), radius=0.07, color=BLACK)
        c_label = MathTex("C", font_size=28).next_to(c_dot, DOWN, buff=0.11)
        d_label = MathTex("D", font_size=28).next_to(d_dot, UP, buff=0.11)
        vector_cd = Arrow(
            axes.c2p(*c_xy),
            axes.c2p(*d_xy),
            buff=0.08,
            color=ACCENT,
            stroke_width=5,
            max_tip_length_to_length_ratio=0.14,
        )
        label_cd = MathTex(r"\overrightarrow{CD}", font_size=38, color=ACCENT)
        label_cd.next_to(vector_cd.get_center(), DOWN + RIGHT, buff=0.16)

        equality = MathTex(
            r"\overrightarrow{AB}=\overrightarrow{CD}",
            font_size=37,
            color=ACCENT,
        ).to_edge(RIGHT, buff=0.6).shift(UP * 0.65)
        displacement = MathTex(
            r"(+4,+3)",
            font_size=42,
            color=ACCENT,
        ).next_to(equality, DOWN, buff=0.36)
        reason = Text(
            "même direction · même sens · même longueur",
            font_size=21,
        ).next_to(displacement, DOWN, buff=0.28)
        reason_box = SurroundingRectangle(
            VGroup(displacement, reason),
            color=ACCENT,
            buff=0.20,
            stroke_width=2.3,
        )
        VGroup(displacement, reason, reason_box).to_edge(RIGHT, buff=0.45)

        caption = (
            "On peut représenter le même vecteur ailleurs. Les deux flèches restent "
            "visibles : elles ont la même direction, le même sens et la même longueur. "
            "Elles décrivent toutes deux quatre unités vers la droite et trois vers le haut."
        )
        spoken = (
            f"On peut représenter le même vecteur ailleurs. <bookmark mark='copy'/>Depuis le "
            f"point {C}, on reproduit exactement le même déplacement jusqu'au point {D_SPOKEN}. "
            "<bookmark mark='equal'/>Les deux flèches ont la même direction, le même sens et "
            "la même longueur : quatre unités vers la droite et trois vers le haut."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(FadeIn(c_dot, d_dot, c_label, d_label), run_time=0.45)
            tracker.wait_until_bookmark("copy")
            self.play(
                TransformFromCopy(vector_ab, vector_cd),
                TransformFromCopy(label_ab, label_cd),
                run_time=1.15,
            )
            tracker.wait_until_bookmark("equal")
            self.play(
                Write(equality),
                Write(displacement),
                FadeIn(reason),
                Create(reason_box),
                run_time=1.0,
            )
        self.wait(0.85)

        # ------------------------------------------------------------------
        # 4. Components: arrival minus departure
        # ------------------------------------------------------------------
        self.play(
            FadeOut(
                c_dot,
                d_dot,
                c_label,
                d_label,
                vector_cd,
                label_cd,
                equality,
                displacement,
                reason,
                reason_box,
            ),
            run_time=0.55,
        )

        corner = axes.c2p(b_xy[0], a_xy[1])
        horizontal = DashedLine(
            axes.c2p(*a_xy),
            corner,
            color=ACCENT,
            stroke_width=3,
        )
        vertical = DashedLine(
            corner,
            axes.c2p(*b_xy),
            color=ACCENT,
            stroke_width=3,
        )
        right_angle = RightAngle(horizontal, vertical, length=0.22, color=BLACK)

        dx_on_graph = MathTex(r"+4", font_size=31, color=ACCENT)
        dx_on_graph.next_to(horizontal, DOWN, buff=0.12)
        dy_on_graph = MathTex(r"+3", font_size=31, color=ACCENT)
        dy_on_graph.next_to(vertical, RIGHT, buff=0.12)

        dx_formula = MathTex(
            r"\Delta x=x_B-x_A=1-(-3)=4",
            font_size=31,
            color=ACCENT,
        )
        dy_formula = MathTex(
            r"\Delta y=y_B-y_A=2-(-1)=3",
            font_size=31,
            color=ACCENT,
        )
        component_formula = MathTex(
            r"\overrightarrow{AB}=(4,3)",
            font_size=43,
            color=ACCENT,
        )
        component_panel = VGroup(dx_formula, dy_formula, component_formula).arrange(
            DOWN,
            buff=0.34,
        )
        component_panel.to_edge(RIGHT, buff=0.48).shift(DOWN * 0.05)
        rule = Text("arrivée − départ", font_size=28, color=ACCENT)
        rule.next_to(component_panel, DOWN, buff=0.34)
        rule_box = SurroundingRectangle(
            rule,
            color=ACCENT,
            buff=0.16,
            stroke_width=2.4,
        )

        caption = (
            "Les composantes disent comment effectuer le déplacement. Horizontalement, "
            "on fait l'abscisse d'arrivée moins l'abscisse de départ : quatre. "
            "Verticalement, on obtient trois. Le vecteur a donc pour composantes quatre et trois."
        )
        spoken = (
            "Les composantes disent comment effectuer le déplacement. "
            "<bookmark mark='dx'/>Horizontalement, on fait l'abscisse d'arrivée moins "
            "l'abscisse de départ : un moins moins trois, donc quatre. "
            "<bookmark mark='dy'/>Verticalement, deux moins moins un donne trois. "
            f"<bookmark mark='pair'/>Le vecteur {A} {B} a donc pour composantes quatre et trois."
        )
        with self.narrated(spoken, caption) as tracker:
            tracker.wait_until_bookmark("dx")
            self.play(
                Create(horizontal),
                Write(dx_on_graph),
                Write(dx_formula),
                run_time=0.85,
            )
            tracker.wait_until_bookmark("dy")
            self.play(
                Create(vertical),
                Create(right_angle),
                Write(dy_on_graph),
                Write(dy_formula),
                run_time=0.85,
            )
            tracker.wait_until_bookmark("pair")
            self.play(
                Write(component_formula),
                FadeIn(rule),
                Create(rule_box),
                run_time=0.85,
            )
        self.wait(0.85)

        # ------------------------------------------------------------------
        # 5. Norm as the length of the displacement
        # ------------------------------------------------------------------
        norm_formula = MathTex(
            r"\|\overrightarrow{AB}\|=\sqrt{4^2+3^2}=5",
            font_size=41,
            color=ACCENT,
        ).move_to(component_formula)
        norm_caption = Text("La norme est la longueur du vecteur.", font_size=28)
        norm_caption.next_to(norm_formula, DOWN, buff=0.38)

        caption = (
            "Le trajet horizontal et le trajet vertical forment un triangle rectangle. "
            "Par le théorème de Pythagore, la norme, c'est-à-dire la longueur du vecteur, vaut cinq."
        )
        spoken = (
            "Le trajet horizontal et le trajet vertical forment un triangle rectangle. "
            "<bookmark mark='norm'/>Par le théorème de Pythagore, la norme, c'est-à-dire "
            "la longueur du vecteur, vaut cinq."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(FadeOut(dx_formula, dy_formula, rule, rule_box), run_time=0.4)
            tracker.wait_until_bookmark("norm")
            self.play(
                Transform(component_formula, norm_formula),
                FadeIn(norm_caption),
                run_time=0.95,
            )
        self.wait(0.85)

        # ------------------------------------------------------------------
        # 6. Common error: reversed subtraction gives the opposite vector
        # ------------------------------------------------------------------
        vector_ba = Arrow(
            axes.c2p(*b_xy) + UP * 0.11,
            axes.c2p(*a_xy) + UP * 0.11,
            buff=0.08,
            color=ERROR,
            stroke_width=5,
            max_tip_length_to_length_ratio=0.14,
        )
        label_ba = MathTex(r"\overrightarrow{BA}", font_size=37, color=ERROR)
        label_ba.next_to(vector_ba.get_center(), DOWN + RIGHT, buff=0.18)
        reversed_formula = MathTex(
            r"(x_A-x_B,\,y_A-y_B)=(-4,-3)",
            font_size=33,
            color=ERROR,
        ).to_edge(RIGHT, buff=0.46).shift(UP * 0.58)
        opposite_formula = MathTex(
            r"\overrightarrow{BA}=-\overrightarrow{AB}",
            font_size=38,
            color=ERROR,
        ).next_to(reversed_formula, DOWN, buff=0.42)
        correct_rule = MathTex(
            r"\overrightarrow{AB}=(x_B-x_A,\,y_B-y_A)",
            font_size=34,
            color=ACCENT,
        ).next_to(opposite_formula, DOWN, buff=0.62)
        correct_box = SurroundingRectangle(
            correct_rule,
            color=ACCENT,
            buff=0.19,
            stroke_width=2.5,
        )

        caption = (
            "Si l'on soustrait dans l'ordre inverse, on ne calcule pas le même vecteur. "
            "On obtient le vecteur de B vers A, qui pointe dans le sens opposé. "
            "Pour AB, on fait toujours B moins A."
        )
        spoken = (
            "Si l'on soustrait dans l'ordre inverse, on ne calcule pas le même vecteur. "
            f"<bookmark mark='opposite'/>On obtient le vecteur de {B} vers {A}, qui pointe dans "
            f"le sens opposé. <bookmark mark='rule'/>Pour le vecteur {A} {B}, on fait toujours "
            f"les coordonnées de {B} moins celles de {A}."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(
                FadeOut(component_formula, norm_caption),
                vector_ab.animate.set_opacity(0.32),
                label_ab.animate.set_opacity(0.32),
                run_time=0.45,
            )
            tracker.wait_until_bookmark("opposite")
            self.play(
                GrowArrow(vector_ba),
                Write(label_ba),
                Write(reversed_formula),
                Write(opposite_formula),
                run_time=1.0,
            )
            tracker.wait_until_bookmark("rule")
            self.play(Write(correct_rule), Create(correct_box), run_time=0.85)
        self.wait(0.9)

        # ------------------------------------------------------------------
        # 7. Stable summary
        # ------------------------------------------------------------------
        self.play(
            FadeOut(
                axes,
                axis_labels,
                header,
                a_dot,
                b_dot,
                a_label,
                b_label,
                vector_ab,
                label_ab,
                horizontal,
                vertical,
                right_angle,
                dx_on_graph,
                dy_on_graph,
                vector_ba,
                label_ba,
                reversed_formula,
                opposite_formula,
                correct_rule,
                correct_box,
            ),
            run_time=0.65,
        )

        summary_title = Text("À retenir", font_size=42, weight="BOLD", color=ACCENT)
        summary_lines = VGroup(
            Text("Un point indique une position.", font_size=30),
            Text("Un vecteur indique un déplacement.", font_size=30),
            MathTex(
                r"\overrightarrow{AB}=(x_B-x_A,\,y_B-y_A)",
                font_size=37,
            ),
            MathTex(r"\|\vec v\|=\sqrt{v_x^2+v_y^2}", font_size=37),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        summary = VGroup(summary_title, summary_lines).arrange(DOWN, buff=0.52)
        summary.move_to(ORIGIN)
        summary_box = SurroundingRectangle(
            summary,
            color=ACCENT,
            buff=0.34,
            stroke_width=2.5,
        )

        caption = (
            "À retenir : un point indique une position; un vecteur indique un déplacement. "
            "Ses composantes sont arrivée moins départ, et sa norme mesure sa longueur."
        )
        spoken = (
            "À retenir. Un point indique une position; un vecteur indique un déplacement. "
            "Ses composantes sont arrivée moins départ, et sa norme mesure sa longueur."
        )
        with self.narrated(spoken, caption):
            self.play(Write(summary_title), run_time=0.55)
            self.play(
                LaggedStart(
                    *[FadeIn(line, shift=UP * 0.07) for line in summary_lines],
                    lag_ratio=0.18,
                ),
                run_time=1.55,
            )
            self.play(Create(summary_box), run_time=0.45)
        self.wait(1.4)
