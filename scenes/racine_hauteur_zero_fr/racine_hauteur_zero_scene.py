import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import *

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


SCRIPT = [
    {
        "caption": "Une racine, c'est une hauteur zéro.",
        "ssml": tts.ssml(
            "<bookmark mark='open_title'/>"
            "Dans cette vidéo, on va clarifier une idée très simple : "
            "une racine, c'est une valeur de "
            f"{tts.char('x')} "
            "où la hauteur du graphe est zéro. "
            "<break time='250ms'/>"
            "<bookmark mark='open_formula'/>"
            "Autrement dit, "
            f"{tts.char('x')} égale {tts.char('a')} "
            "est une racine si "
            f"{tts.char('f')} de {tts.char('a')} "
            "égale zéro."
        ),
    },
    {
        "caption": "La hauteur d'un point est f(x).",
        "ssml": tts.ssml(
            "<bookmark mark='show_graph'/>"
            "Regardons d'abord une fonction très simple. "
            "<bookmark mark='show_height'/>"
            "Pour chaque valeur de "
            f"{tts.char('x')}, "
            "le point du graphe a une hauteur : "
            f"{tts.char('f')} de {tts.char('x')}. "
            "<bookmark mark='move_to_root'/>"
            "Quand cette hauteur devient zéro, "
            "le point arrive sur l'axe horizontal. "
            "<bookmark mark='name_root'/>"
            "La valeur de "
            f"{tts.char('x')} "
            "à ce moment-là s'appelle une racine."
        ),
    },
    {
        "caption": "La racine est une valeur de x.",
        "ssml": tts.ssml(
            "<bookmark mark='root_value'/>"
            "Attention à une petite confusion fréquente. "
            "La racine est la valeur de "
            f"{tts.char('x')}. "
            "<break time='200ms'/>"
            "<bookmark mark='graph_point'/>"
            "Sur le graphe, cette racine correspond au point "
            "dont la hauteur est zéro. "
            "<break time='200ms'/>"
            "<bookmark mark='not_same'/>"
            "Donc ici, la racine est "
            f"{tts.char('x')} égale deux, "
            "et le point sur le graphe est le point deux, zéro."
        ),
    },
    {
        "caption": "Le facteur x-a crée une racine.",
        "ssml": tts.ssml(
            "<bookmark mark='factor_intro'/>"
            "Pourquoi le facteur "
            f"{tts.char('x')} moins deux "
            "donne-t-il une racine en deux ? "
            "<bookmark mark='substitute_two'/>"
            "Parce que si on remplace "
            f"{tts.char('x')} "
            "par deux, on obtient deux moins deux, donc zéro. "
            "<break time='250ms'/>"
            "<bookmark mark='general_factor'/>"
            "Plus généralement, le facteur "
            f"{tts.char('x')} moins {tts.char('a')} "
            "devient zéro quand "
            f"{tts.char('x')} égale {tts.char('a')}."
        ),
    },
    {
        "caption": "Un produit peut avoir plusieurs racines.",
        "ssml": tts.ssml(
            "<bookmark mark='product_formula'/>"
            "Maintenant, regardons un produit de deux facteurs. "
            "<bookmark mark='root_two'/>"
            "Si "
            f"{tts.char('x')} "
            "vaut deux, le premier facteur devient zéro. "
            "Donc tout le produit vaut zéro. "
            "<bookmark mark='root_minus_one'/>"
            "Si "
            f"{tts.char('x')} "
            "vaut moins un, le deuxième facteur devient zéro. "
            "Donc le produit vaut encore zéro. "
            "<bookmark mark='product_graph'/>"
            "Sur le graphe, on voit donc deux racines : "
            "deux endroits où la courbe rencontre l'axe horizontal."
        ),
    },
    {
        "caption": "Une racine indique où f(x)=0.",
        "ssml": tts.ssml(
            "<bookmark mark='final_roots'/>"
            "À retenir : une racine est une valeur de "
            f"{tts.char('x')} "
            "qui rend la fonction égale à zéro. "
            "<bookmark mark='final_points'/>"
            "Sur le graphe, cela donne un point de la forme "
            f"{tts.char('x')}, zéro. "
            "<bookmark mark='final_warning'/>"
            "Dans une prochaine vidéo, on verra pourquoi certaines racines font traverser l'axe, "
            "alors que d'autres font seulement toucher l'axe."
        ),
    },
]


def proportional_axes(x_range, y_range, unit_size=0.75, font_size=22):
    x_span = x_range[1] - x_range[0]
    y_span = y_range[1] - y_range[0]
    return Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=x_span * unit_size,
        y_length=y_span * unit_size,
        tips=False,
        axis_config={
            "color": BLACK,
            "include_numbers": True,
            "font_size": font_size,
        },
    )


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class RacineHauteurZeroFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            return
        if VoiceoverScene is None or AzureService is None:
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)
        try:
            self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        except Exception:
            return
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, item: dict[str, str]):
        if self._voiceover_enabled:
            with self.voiceover(text=item["ssml"], subcaption=item["caption"]) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_until_bookmark(self, mark: str) -> None:
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        accent = BLUE_D
        muted = GRAY
        ink = BLACK

        title = Text("Une racine, c'est une hauteur zéro", font_size=44)
        title.to_edge(UP, buff=0.25)

        # ------------------------------------------------------------------
        # Opening: one idea, slowly
        # ------------------------------------------------------------------
        idea = Text("On cherche où la hauteur vaut zéro.", font_size=32)
        idea.move_to(UP * 0.5)

        root_definition = MathTex(
            r"x=a\ \text{ est une racine}",
            r"\quad\Longleftrightarrow\quad",
            r"f(a)=0",
        ).scale(1.05)
        root_definition[0].set_color(accent)
        root_definition[2].set_color(accent)
        root_definition.move_to(DOWN * 0.35)

        with self.narrated(SCRIPT[0]):
            self.wait_until_bookmark("open_title")
            self.play(FadeIn(title), run_time=0.6)
            self.play(Write(idea), run_time=0.8)

            self.wait_until_bookmark("open_formula")
            self.play(FadeIn(root_definition), run_time=0.8)
            self.wait(0.5)

        self.play(FadeOut(idea), FadeOut(root_definition), run_time=0.6)

        # ------------------------------------------------------------------
        # Act 1: height becomes zero on the x-axis
        # ------------------------------------------------------------------
        axes = proportional_axes(
            x_range=[-1, 4, 1],
            y_range=[-3, 3, 1],
            unit_size=0.78,
            font_size=22,
        ).shift(DOWN * 0.35)

        axis_labels = axes.get_axis_labels(MathTex("x"), MathTex("y"))

        def f(x):
            return x - 2

        graph = axes.plot(f, x_range=[-0.5, 3.5], color=ink, stroke_width=4)

        graph_label = MathTex(r"f(x)=x-2").scale(0.9)
        graph_label.next_to(title, DOWN, buff=0.15)

        x_tracker = ValueTracker(0.2)

        moving_dot = always_redraw(
            lambda: Dot(
                axes.c2p(x_tracker.get_value(), f(x_tracker.get_value())),
                color=accent,
                radius=0.07,
            )
        )

        scanner = always_redraw(
            lambda: DashedLine(
                axes.c2p(x_tracker.get_value(), -3),
                axes.c2p(x_tracker.get_value(), 3),
                color=muted,
                stroke_width=3,
                dash_length=0.12,
            )
        )

        height = always_redraw(
            lambda: Line(
                axes.c2p(x_tracker.get_value(), 0),
                axes.c2p(x_tracker.get_value(), f(x_tracker.get_value())),
                color=accent,
                stroke_width=5,
            )
        )

        height_label = always_redraw(
            lambda: Text("hauteur", font_size=24, color=accent).next_to(
                height, RIGHT, buff=0.12
            )
        )

        point_label = always_redraw(
            lambda: MathTex(r"(x,f(x))").scale(0.65).next_to(
                moving_dot,
                UR if f(x_tracker.get_value()) >= 0 else DR,
                buff=0.1,
            )
        )

        root_dot = Dot(axes.c2p(2, 0), color=accent, radius=0.085)
        root_label = MathTex(r"x=2").scale(0.78).next_to(root_dot, DOWN, buff=0.18)

        zero_height_label = MathTex(r"f(2)=0", color=accent).scale(0.85)
        zero_height_label.next_to(root_dot, UP, buff=0.25)

        with self.narrated(SCRIPT[1]):
            self.wait_until_bookmark("show_graph")
            self.play(Create(axes), FadeIn(axis_labels), run_time=0.8)
            self.play(FadeIn(graph_label), Create(graph), run_time=0.9)

            self.wait_until_bookmark("show_height")
            self.play(Create(scanner), FadeIn(moving_dot), FadeIn(point_label), run_time=0.5)
            self.play(Create(height), FadeIn(height_label), run_time=0.6)

            self.wait_until_bookmark("move_to_root")
            self.play(x_tracker.animate.set_value(2.0), run_time=2.0)

            self.wait_until_bookmark("name_root")
            self.play(
                FadeOut(moving_dot),
                FadeOut(point_label),
                FadeOut(height),
                FadeIn(root_dot),
                FadeIn(root_label),
                ReplacementTransform(height_label, zero_height_label),
                run_time=0.7,
            )
            self.play(Circumscribe(root_dot, color=accent), run_time=0.8)

        # ------------------------------------------------------------------
        # Act 2: root value vs graph point
        # ------------------------------------------------------------------
        root_value_box = VGroup(
            Text("Racine", font_size=30, color=accent),
            MathTex(r"x=2").scale(1.05),
        ).arrange(DOWN, buff=0.18)

        point_box = VGroup(
            Text("Point du graphe", font_size=30),
            MathTex(r"(2,0)").scale(1.05),
        ).arrange(DOWN, buff=0.18)

        root_value_rect = SurroundingRectangle(
            root_value_box, color=accent, buff=0.22, stroke_width=3
        )
        point_rect = SurroundingRectangle(
            point_box, color=BLACK, buff=0.22, stroke_width=2
        )

        root_value_group = VGroup(root_value_rect, root_value_box)
        point_group = VGroup(point_rect, point_box)

        comparison = VGroup(root_value_group, point_group).arrange(RIGHT, buff=0.8)
        comparison.to_edge(DOWN, buff=0.35)

        point_marker_label = MathTex(r"(2,0)").scale(0.72)
        point_marker_label.next_to(root_dot, UR, buff=0.12)

        with self.narrated(SCRIPT[2]):
            self.wait_until_bookmark("root_value")
            self.play(FadeIn(root_value_group), run_time=0.55)
            self.play(Circumscribe(root_value_box[1], color=accent), run_time=0.7)

            self.wait_until_bookmark("graph_point")
            self.play(FadeIn(point_marker_label), FadeIn(point_group), run_time=0.55)

            self.wait_until_bookmark("not_same")
            self.play(
                Circumscribe(root_value_group, color=accent),
                Circumscribe(point_group, color=BLACK),
                run_time=0.9,
            )

        self.play(
            FadeOut(comparison),
            FadeOut(point_marker_label),
            FadeOut(scanner),
            FadeOut(zero_height_label),
            run_time=0.6,
        )

        # ------------------------------------------------------------------
        # Act 3: factor x-a creates a root
        # ------------------------------------------------------------------
        factor_title = Text("Pourquoi x - 2 donne une racine en 2 ?", font_size=31)
        factor_title.next_to(graph_label, DOWN, buff=0.18)

        factor_formula = MathTex(r"f(x)=x-2").scale(1.05)
        factor_formula.move_to(LEFT * 2.7 + DOWN * 0.9)

        substitution = MathTex(r"f(2)=2-2=0").scale(1.05)
        substitution.move_to(RIGHT * 2.3 + DOWN * 0.9)
        substitution.set_color(accent)

        arrow_factor = Arrow(
            factor_formula.get_right() + RIGHT * 0.15,
            substitution.get_left() + LEFT * 0.15,
            buff=0.1,
            color=accent,
            stroke_width=4,
        )

        general_factor = MathTex(
            r"x-a=0",
            r"\quad\Longleftrightarrow\quad",
            r"x=a",
        ).scale(1.05)
        general_factor.move_to(DOWN * 2.25)
        general_factor[0].set_color(accent)
        general_factor[2].set_color(accent)

        with self.narrated(SCRIPT[3]):
            self.wait_until_bookmark("factor_intro")
            self.play(FadeIn(factor_title), run_time=0.5)
            self.play(Write(factor_formula), run_time=0.65)

            self.wait_until_bookmark("substitute_two")
            self.play(Create(arrow_factor), Write(substitution), run_time=0.8)
            self.play(Circumscribe(substitution[-1], color=accent), run_time=0.7)

            self.wait_until_bookmark("general_factor")
            self.play(Write(general_factor), run_time=0.8)
            self.play(Circumscribe(general_factor[2], color=accent), run_time=0.7)

        first_scene_group = VGroup(
            axes,
            axis_labels,
            graph,
            graph_label,
            root_dot,
            root_label,
            factor_title,
            factor_formula,
            substitution,
            arrow_factor,
            general_factor,
        )
        self.play(FadeOut(first_scene_group), run_time=0.75)

        # ------------------------------------------------------------------
        # Act 4: product with two roots
        # ------------------------------------------------------------------
        axes2 = proportional_axes(
            x_range=[-3, 4, 1],
            y_range=[-4, 5, 1],
            unit_size=0.62,
            font_size=20,
        ).shift(DOWN * 0.45)

        labels2 = VGroup(MathTex("x").next_to(axes2.x_axis.get_end(), RIGHT, buff=0.12))

        def g(x):
            return (x - 2) * (x + 1)

        product_formula = MathTex(r"g(x)=(x-2)(x+1)").scale(1.05)
        product_formula.next_to(title, DOWN, buff=0.15)

        graph2 = axes2.plot(g, x_range=[-2.7, 3.4], color=ink, stroke_width=4)

        root_two_dot = Dot(axes2.c2p(2, 0), color=accent, radius=0.08)
        root_two_label = MathTex(r"x=2").scale(0.72)
        root_two_label.next_to(root_two_dot, DOWN, buff=0.16)

        root_minus_dot = Dot(axes2.c2p(-1, 0), color=accent, radius=0.08)
        root_minus_label = MathTex(r"x=-1").scale(0.72)
        root_minus_label.next_to(root_minus_dot, DOWN, buff=0.16)

        calc_two = VGroup(
            MathTex(r"g(2)=(2-2)(2+1)").scale(0.74),
            MathTex(r"=0\cdot 3=0").scale(0.74),
        ).arrange(DOWN, buff=0.08)
        calc_two.to_edge(DOWN, buff=0.35)
        calc_two.set_color(accent)

        calc_minus = VGroup(
            MathTex(r"g(-1)=(-1-2)(-1+1)").scale(0.74),
            MathTex(r"=(-3)\cdot 0=0").scale(0.74),
        ).arrange(DOWN, buff=0.08)
        calc_minus.to_edge(DOWN, buff=0.35)
        calc_minus.set_color(accent)

        scanner_two = DashedLine(
            axes2.c2p(2, -4),
            axes2.c2p(2, 5),
            color=muted,
            stroke_width=3,
            dash_length=0.12,
        )

        scanner_minus = DashedLine(
            axes2.c2p(-1, -4),
            axes2.c2p(-1, 5),
            color=muted,
            stroke_width=3,
            dash_length=0.12,
        )

        with self.narrated(SCRIPT[4]):
            self.wait_until_bookmark("product_formula")
            self.play(Create(axes2), FadeIn(labels2), run_time=0.75)
            self.play(FadeIn(product_formula), run_time=0.5)

            self.wait_until_bookmark("root_two")
            self.play(Create(scanner_two), Write(calc_two), run_time=0.7)
            self.play(FadeIn(root_two_dot), FadeIn(root_two_label), run_time=0.45)
            self.play(Circumscribe(root_two_dot, color=accent), run_time=0.65)

            self.wait_until_bookmark("root_minus_one")
            self.play(
                ReplacementTransform(scanner_two, scanner_minus),
                ReplacementTransform(calc_two, calc_minus),
                run_time=0.75,
            )
            self.play(FadeIn(root_minus_dot), FadeIn(root_minus_label), run_time=0.45)
            self.play(Circumscribe(root_minus_dot, color=accent), run_time=0.65)

            self.wait_until_bookmark("product_graph")
            self.play(Create(graph2), run_time=1.15)
            self.play(
                Circumscribe(VGroup(root_minus_dot, root_two_dot), color=accent),
                run_time=0.9,
            )

        self.play(
            FadeOut(calc_minus),
            FadeOut(scanner_minus),
            FadeOut(axes2),
            FadeOut(labels2),
            FadeOut(graph2),
            FadeOut(root_two_dot),
            FadeOut(root_two_label),
            FadeOut(root_minus_dot),
            FadeOut(root_minus_label),
            run_time=0.55,
        )

        # ------------------------------------------------------------------
        # Act 5: final takeaway
        # ------------------------------------------------------------------
        final_roots = VGroup(
            Text("Racines", font_size=31, color=accent),
            MathTex(r"x=-1,\quad x=2").scale(1.0),
        ).arrange(DOWN, buff=0.22)

        final_points = VGroup(
            Text("Points sur l'axe horizontal", font_size=31),
            MathTex(r"(-1,0),\quad (2,0)").scale(1.0),
        ).arrange(DOWN, buff=0.22)

        final_group = VGroup(final_roots, final_points).arrange(RIGHT, buff=0.85)
        final_group.to_edge(DOWN, buff=0.35)

        final_slogan = MathTex(
            r"\boxed{\text{Racine} = \text{valeur de }x\text{ où }f(x)=0}"
        ).scale(0.92)
        final_slogan.next_to(title, DOWN, buff=0.18)
        final_slogan.set_color(accent)

        next_video = Text(
            "Prochaine idée : traverser ou toucher l'axe ?",
            font_size=28,
            color=BLACK,
        )
        next_video.next_to(final_slogan, DOWN, buff=0.25)

        with self.narrated(SCRIPT[5]):
            self.wait_until_bookmark("final_roots")
            self.play(ReplacementTransform(product_formula, final_slogan), run_time=0.7)
            self.play(FadeIn(final_roots), run_time=0.55)

            self.wait_until_bookmark("final_points")
            self.play(FadeIn(final_points), run_time=0.55)
            self.play(
                Circumscribe(final_roots, color=accent),
                Circumscribe(final_points, color=BLACK),
                run_time=0.9,
            )

            self.wait_until_bookmark("final_warning")
            self.play(FadeIn(next_video), run_time=0.6)

        self.wait(1.0)
