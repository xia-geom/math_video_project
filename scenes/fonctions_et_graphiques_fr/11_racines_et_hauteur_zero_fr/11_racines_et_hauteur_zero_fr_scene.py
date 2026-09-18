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
    from tools.teaching_voiceover import TeachingAzureService as AzureService
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
        "caption": "Où une fonction atteint-elle la hauteur zéro ?",
        "ssml": tts.ssml(
            "<bookmark mark='open_title'/>"
            "Voici la question centrale : comment reconnaître une racine sur un graphe ? "
            "<bookmark mark='open_question'/>"
            "Une racine apparaît exactement au moment où la hauteur du graphe devient zéro. "
            "C'est le lien entre résoudre une équation et lire un graphique."
        ),
    },
    {
        "caption": "La hauteur du point est f(x).",
        "ssml": tts.ssml(
            "<bookmark mark='show_graph'/>"
            "Regardons une fonction très simple. "
            "<bookmark mark='show_height'/>"
            "Pour une valeur de "
            f"{tts.char('x')}, "
            "le point du graphe a pour hauteur "
            f"{tts.char('f')} de {tts.char('x')}. "
            "<bookmark mark='move_to_root'/>"
            "Faisons maintenant glisser le point jusqu'à ce que cette hauteur devienne zéro. "
            "<bookmark mark='name_root'/>"
            "Le point arrive sur l'axe horizontal. La valeur de "
            f"{tts.char('x')} "
            "à cet endroit s'appelle une racine."
        ),
    },
    {
        "caption": "La racine est x=2; le point est (2,0).",
        "ssml": tts.ssml(
            "<bookmark mark='root_value'/>"
            "Attention à une confusion fréquente : la racine est une valeur de "
            f"{tts.char('x')}. "
            "Ici, la racine est deux. "
            "<bookmark mark='graph_point'/>"
            "Le point correspondant sur le graphe possède deux coordonnées : deux, zéro. "
            "<bookmark mark='not_same'/>"
            "La racine et le point sont donc liés, mais ce ne sont pas le même objet."
        ),
    },
    {
        "caption": "Le facteur x−a s'annule en x=a.",
        "ssml": tts.ssml(
            "<bookmark mark='factor_intro'/>"
            "Pourquoi le facteur "
            f"{tts.char('x')} moins deux "
            "donne-t-il une racine en deux ? "
            "<bookmark mark='substitute_two'/>"
            "Parce qu'en remplaçant "
            f"{tts.char('x')} "
            "par deux, on obtient deux moins deux, donc zéro. "
            "<bookmark mark='general_factor'/>"
            "Plus généralement, le facteur "
            f"{tts.char('x')} moins {tts.char('a')} "
            "s'annule quand "
            f"{tts.char('x')} égale {tts.char('a')}."
        ),
    },
    {
        "caption": "Chaque facteur nul donne une racine du produit.",
        "ssml": tts.ssml(
            "<bookmark mark='product_formula'/>"
            "Regardons maintenant un produit de deux facteurs. "
            "<bookmark mark='root_two'/>"
            "Si "
            f"{tts.char('x')} "
            "vaut deux, le premier facteur devient zéro, donc le produit vaut zéro. "
            "<bookmark mark='root_minus_one'/>"
            "Si "
            f"{tts.char('x')} "
            "vaut moins un, le deuxième facteur devient zéro, donc le produit vaut encore zéro. "
            "<bookmark mark='product_graph'/>"
            "Sur le graphe, ces deux valeurs donnent deux rencontres avec l'axe horizontal."
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
            "Sur le graphe, elle correspond à un point de la forme "
            f"{tts.char('x')}, zéro. "
            "<bookmark mark='final_warning'/>"
            "Dans la prochaine vidéo, on distinguera une courbe qui traverse l'axe d'une courbe qui le touche seulement."
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

        title = Text("Une racine, c'est une hauteur zéro", font_size=42)
        title.to_edge(UP, buff=0.25)

        # ------------------------------------------------------------------
        # Opening: begin with the question, not the formal notation.
        # ------------------------------------------------------------------
        question = Text("Comment reconnaître une racine sur un graphe ?", font_size=34)
        question.move_to(UP * 0.35)

        clue = VGroup(
            Text("Observer la hauteur", font_size=29),
            MathTex(r"f(x)").scale(1.15).set_color(accent),
        ).arrange(RIGHT, buff=0.25)
        clue.move_to(DOWN * 0.55)

        with self.narrated(SCRIPT[0]):
            self.wait_until_bookmark("open_title")
            self.play(FadeIn(title), run_time=0.6)

            self.wait_until_bookmark("open_question")
            self.play(Write(question), run_time=0.8)
            self.play(FadeIn(clue, shift=UP * 0.12), run_time=0.65)
            self.wait(0.5)

        self.play(FadeOut(question), FadeOut(clue), run_time=0.55)

        # ------------------------------------------------------------------
        # Act 1: a point's height shrinks to zero.
        # ------------------------------------------------------------------
        axes = proportional_axes(
            x_range=[-1, 4, 1],
            y_range=[-3, 3, 1],
            unit_size=0.76,
            font_size=21,
        ).shift(DOWN * 0.55)
        axis_labels = axes.get_axis_labels(MathTex("x"), MathTex("y"))

        def f(x):
            return x - 2

        graph = axes.plot(f, x_range=[-0.5, 3.5], color=ink, stroke_width=4)
        graph_label = MathTex(r"f(x)=x-2").scale(0.88)
        graph_label.next_to(title, DOWN, buff=0.14)

        x_tracker = ValueTracker(3.25)

        moving_dot = always_redraw(
            lambda: Dot(
                axes.c2p(x_tracker.get_value(), f(x_tracker.get_value())),
                color=accent,
                radius=0.075,
            )
        )
        base_dot = always_redraw(
            lambda: Dot(
                axes.c2p(x_tracker.get_value(), 0),
                color=accent,
                radius=0.045,
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
            lambda: MathTex(r"f(x)").scale(0.7).set_color(accent).next_to(
                height, RIGHT, buff=0.13
            )
        )
        point_label = always_redraw(
            lambda: MathTex(r"(x,f(x))").scale(0.62).next_to(
                moving_dot, UR, buff=0.12
            )
        )

        root_dot = Dot(axes.c2p(2, 0), color=accent, radius=0.09)
        root_label = MathTex(r"x=2").scale(0.76).next_to(root_dot, DOWN, buff=0.18)
        zero_height_label = MathTex(r"f(2)=0").scale(0.82).set_color(accent)
        zero_height_label.next_to(root_dot, UP, buff=0.28)

        with self.narrated(SCRIPT[1]):
            self.wait_until_bookmark("show_graph")
            self.play(Create(axes), FadeIn(axis_labels), run_time=0.8)
            self.play(FadeIn(graph_label), Create(graph), run_time=0.9)

            self.wait_until_bookmark("show_height")
            self.play(
                FadeIn(moving_dot),
                FadeIn(base_dot),
                Create(height),
                FadeIn(point_label),
                run_time=0.6,
            )
            self.play(FadeIn(height_label), run_time=0.45)

            self.wait_until_bookmark("move_to_root")
            self.play(x_tracker.animate.set_value(2.0), run_time=2.0)
            self.wait(0.25)

            self.wait_until_bookmark("name_root")
            self.play(
                FadeOut(moving_dot),
                FadeOut(base_dot),
                FadeOut(point_label),
                FadeOut(height),
                FadeOut(height_label),
                FadeIn(root_dot),
                FadeIn(root_label),
                FadeIn(zero_height_label),
                run_time=0.65,
            )
            self.play(Circumscribe(root_dot, color=accent), run_time=0.8)
            self.wait(0.35)

        # ------------------------------------------------------------------
        # Act 2: keep the graph on the left and the language on the right.
        # This replaces the former bottom overlay that covered the axes.
        # ------------------------------------------------------------------
        graph_core = VGroup(
            axes,
            axis_labels,
            graph,
            root_dot,
            root_label,
            zero_height_label,
        )
        graph_target = graph_core.copy().scale(0.78)
        graph_target.to_edge(LEFT, buff=0.45).shift(DOWN * 0.3)


        root_value_box = VGroup(
            Text("La racine", font_size=29, color=accent),
            MathTex(r"x=2").scale(1.05),
        ).arrange(DOWN, buff=0.16)
        root_value_rect = SurroundingRectangle(
            root_value_box, color=accent, buff=0.22, stroke_width=3
        )
        root_value_group = VGroup(root_value_rect, root_value_box)

        point_box = VGroup(
            Text("Le point correspondant", font_size=27),
            MathTex(r"(2,0)").scale(1.05),
        ).arrange(DOWN, buff=0.16)
        point_rect = SurroundingRectangle(
            point_box, color=BLACK, buff=0.22, stroke_width=2
        )
        point_group = VGroup(point_rect, point_box)

        comparison = VGroup(root_value_group, point_group).arrange(DOWN, buff=0.52)
        comparison.to_edge(RIGHT, buff=0.65).shift(DOWN * 0.25)

        with self.narrated(SCRIPT[2]):
            self.play(
                Transform(graph_core, graph_target),
                FadeOut(graph_label),
                run_time=0.75,
            )

            self.wait_until_bookmark("root_value")
            self.play(FadeIn(root_value_group, shift=LEFT * 0.12), run_time=0.55)
            self.play(Circumscribe(root_value_box[1], color=accent), run_time=0.7)

            self.wait_until_bookmark("graph_point")
            self.play(FadeIn(point_group, shift=LEFT * 0.12), run_time=0.55)
            self.play(Circumscribe(point_box[1], color=BLACK), run_time=0.7)

            self.wait_until_bookmark("not_same")
            distinction = MathTex(r"x=2\quad\neq\quad(2,0)").scale(0.82)
            distinction.next_to(comparison, DOWN, buff=0.28)
            distinction[0].set_color(accent)
            self.play(FadeIn(distinction), run_time=0.55)
            self.wait(0.45)

        self.play(
            FadeOut(graph_core),
            FadeOut(comparison),
            FadeOut(distinction),
            run_time=0.65,
        )

        # ------------------------------------------------------------------
        # Act 3: algebra now has its own uncluttered screen.
        # ------------------------------------------------------------------
        factor_title = Text("Pourquoi x − 2 donne-t-il une racine en 2 ?", font_size=31)
        factor_title.next_to(title, DOWN, buff=0.28)

        factor_formula = MathTex(r"f(x)=x-2").scale(1.12)
        substitution = MathTex(r"f(2)=2-2=0").scale(1.12).set_color(accent)
        algebra_row = VGroup(factor_formula, substitution).arrange(RIGHT, buff=1.25)
        algebra_row.move_to(UP * 0.05)

        arrow_factor = Arrow(
            factor_formula.get_right(),
            substitution.get_left(),
            buff=0.22,
            color=accent,
            stroke_width=4,
        )

        general_factor = MathTex(
            r"x-a=0",
            r"\quad\Longleftrightarrow\quad",
            r"x=a",
        ).scale(1.08)
        general_factor[0].set_color(accent)
        general_factor[2].set_color(accent)
        general_rect = SurroundingRectangle(
            general_factor, color=accent, buff=0.28, stroke_width=3
        )
        general_group = VGroup(general_rect, general_factor)
        general_group.move_to(DOWN * 1.55)

        with self.narrated(SCRIPT[3]):
            self.wait_until_bookmark("factor_intro")
            self.play(FadeIn(factor_title), run_time=0.5)
            self.play(Write(factor_formula), run_time=0.65)

            self.wait_until_bookmark("substitute_two")
            self.play(Create(arrow_factor), Write(substitution), run_time=0.8)
            self.play(Circumscribe(substitution, color=accent), run_time=0.7)

            self.wait_until_bookmark("general_factor")
            self.play(FadeIn(general_group, shift=UP * 0.12), run_time=0.75)
            self.play(Circumscribe(general_factor[2], color=accent), run_time=0.7)
            self.wait(0.4)

        self.play(
            FadeOut(factor_title),
            FadeOut(factor_formula),
            FadeOut(substitution),
            FadeOut(arrow_factor),
            FadeOut(general_group),
            run_time=0.65,
        )

        # ------------------------------------------------------------------
        # Act 4: calculations first, graph second. Nothing sits on the graph.
        # ------------------------------------------------------------------
        product_formula = MathTex(r"g(x)=(x-2)(x+1)").scale(1.08)
        product_formula.next_to(title, DOWN, buff=0.18)

        calc_two = VGroup(
            MathTex(r"x=2").scale(1.0),
            MathTex(r"(2-2)(2+1)=0\cdot 3=0").scale(0.9),
            MathTex(r"\therefore\ g(2)=0").scale(0.92).set_color(accent),
        ).arrange(DOWN, buff=0.28)
        calc_two.move_to(DOWN * 0.45)

        calc_minus = VGroup(
            MathTex(r"x=-1").scale(1.0),
            MathTex(r"(-1-2)(-1+1)=(-3)\cdot 0=0").scale(0.82),
            MathTex(r"\therefore\ g(-1)=0").scale(0.92).set_color(accent),
        ).arrange(DOWN, buff=0.28)
        calc_minus.move_to(DOWN * 0.45)

        roots_summary = MathTex(r"\text{Racines : }x=-1\quad\text{et}\quad x=2")
        roots_summary.scale(0.95).set_color(accent)
        roots_summary.move_to(DOWN * 1.95)

        with self.narrated(SCRIPT[4]):
            self.wait_until_bookmark("product_formula")
            self.play(FadeIn(product_formula), run_time=0.5)

            self.wait_until_bookmark("root_two")
            self.play(FadeIn(calc_two, shift=UP * 0.12), run_time=0.7)
            self.play(Circumscribe(calc_two[-1], color=accent), run_time=0.65)

            self.wait_until_bookmark("root_minus_one")
            self.play(FadeOut(calc_two), FadeIn(calc_minus, shift=UP * 0.08), run_time=0.75)
            self.play(Circumscribe(calc_minus[-1], color=accent), run_time=0.65)
            self.play(FadeIn(roots_summary), run_time=0.55)
            self.wait(0.35)

            self.wait_until_bookmark("product_graph")
            self.play(FadeOut(calc_minus), FadeOut(roots_summary), run_time=0.55)

            axes2 = proportional_axes(
                x_range=[-3, 4, 1],
                y_range=[-4, 5, 1],
                unit_size=0.55,
                font_size=19,
            ).shift(DOWN * 0.62)
            labels2 = axes2.get_axis_labels(MathTex("x"), MathTex("y"))

            def g(x):
                return (x - 2) * (x + 1)

            graph2 = axes2.plot(g, x_range=[-2.65, 3.25], color=ink, stroke_width=4)
            root_two_dot = Dot(axes2.c2p(2, 0), color=accent, radius=0.085)
            root_minus_dot = Dot(axes2.c2p(-1, 0), color=accent, radius=0.085)
            two_callout = MathTex(r"x=2").scale(0.68).set_color(accent)
            two_callout.next_to(root_two_dot, UR, buff=0.12)
            minus_callout = MathTex(r"x=-1").scale(0.68).set_color(accent)
            minus_callout.next_to(root_minus_dot, UL, buff=0.12)

            self.play(Create(axes2), FadeIn(labels2), run_time=0.75)
            self.play(Create(graph2), run_time=1.1)
            self.play(
                FadeIn(root_minus_dot),
                FadeIn(root_two_dot),
                FadeIn(minus_callout),
                FadeIn(two_callout),
                run_time=0.55,
            )
            self.play(
                Circumscribe(root_minus_dot, color=accent),
                Circumscribe(root_two_dot, color=accent),
                run_time=0.9,
            )
            self.wait(0.4)

        self.play(
            FadeOut(axes2),
            FadeOut(labels2),
            FadeOut(graph2),
            FadeOut(root_two_dot),
            FadeOut(root_minus_dot),
            FadeOut(two_callout),
            FadeOut(minus_callout),
            run_time=0.6,
        )

        # ------------------------------------------------------------------
        # Act 5: stable final summary.
        # ------------------------------------------------------------------
        final_slogan = MathTex(
            r"\boxed{\text{Racine}=\text{valeur de }x\text{ où }f(x)=0}"
        ).scale(0.9).set_color(accent)
        final_slogan.next_to(title, DOWN, buff=0.2)

        final_roots = VGroup(
            Text("Racines", font_size=30, color=accent),
            MathTex(r"x=-1,\quad x=2").scale(0.95),
        ).arrange(DOWN, buff=0.2)

        final_points = VGroup(
            Text("Points correspondants", font_size=29),
            MathTex(r"(-1,0),\quad (2,0)").scale(0.95),
        ).arrange(DOWN, buff=0.2)

        final_group = VGroup(final_roots, final_points).arrange(RIGHT, buff=1.15)
        final_group.move_to(DOWN * 0.8)

        next_video = Text(
            "Prochaine idée : traverser ou toucher l'axe ?",
            font_size=27,
        )
        next_video.to_edge(DOWN, buff=0.42)

        with self.narrated(SCRIPT[5]):
            self.wait_until_bookmark("final_roots")
            self.play(FadeOut(product_formula), FadeIn(final_slogan), run_time=0.7)
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
