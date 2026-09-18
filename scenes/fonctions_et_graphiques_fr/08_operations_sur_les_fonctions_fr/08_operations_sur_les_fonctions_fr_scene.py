import os
from contextlib import contextmanager
from dataclasses import dataclass
from math import isclose

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


opening_item = {
    "caption": "Comment construire f+g et f−g à partir des graphes?",
    "ssml": tts.ssml(
        "Voici la question centrale. "
        "<bookmark mark='question'/>"
        "Si les graphes de "
        f"{tts.char('f')} "
        "et de "
        f"{tts.char('g')} "
        "sont déjà tracés, comment construire leur somme et leur différence? "
        "<break time='260ms'/>"
        "<bookmark mark='same_x'/>"
        "Dans toutes les constructions, on garde la même abscisse. "
        "Seule la hauteur change."
    ),
}


script = [
    {
        "caption": "Même x, deux hauteurs sur le domaine commun.",
        "ssml": tts.ssml(
            "Pour une même valeur de "
            f"{tts.char('x')}, "
            "on lit deux hauteurs : "
            f"{tts.char('f')} de {tts.char('x')} "
            "et "
            f"{tts.char('g')} de {tts.char('x')}. "
            "<bookmark mark='domain'/>"
            "Cette opération est possible seulement lorsque les deux fonctions sont définies."
        ),
    },
    {
        "caption": "Pour f+g, on reporte exactement la longueur signée g(x).",
        "ssml": tts.ssml(
            "Commençons par la somme. "
            "<bookmark mark='add_formula'/>"
            "On part du point de hauteur "
            f"{tts.char('f')} de {tts.char('x')}, "
            "puis on reporte exactement le segment signé qui représente "
            f"{tts.char('g')} de {tts.char('x')}. "
            "<bookmark mark='add_left'/>"
            "À gauche, cette valeur est négative : le segment descend d'une demi-unité. "
            "<bookmark mark='add_zero'/>"
            "Lorsque "
            f"{tts.char('g')} de {tts.char('x')} "
            "vaut zéro, le point ne bouge pas. "
            "<bookmark mark='add_right'/>"
            "À droite, la valeur est positive : le même segment est reporté vers le haut. "
            "<bookmark mark='add_more'/>"
            "On ajoute ensuite plusieurs autres points. "
            "<bookmark mark='add_graph'/>"
            "Leur ensemble dessine le graphe de la somme."
        ),
    },
    {
        "caption": "Pour f−g, on reporte exactement la longueur opposée −g(x).",
        "ssml": tts.ssml(
            "Passons à la différence. "
            "<bookmark mark='sub_formula'/>"
            "Soustraire "
            f"{tts.char('g')} de {tts.char('x')} "
            "revient à ajouter son opposé. "
            "<bookmark mark='sub_left'/>"
            "À gauche, "
            f"{tts.char('g')} "
            "vaut moins un demi. Son opposé vaut plus un demi. "
            "Le segment est d'abord réfléchi, puis reporté sans changer de longueur. "
            "<bookmark mark='sub_zero'/>"
            "Si la hauteur de "
            f"{tts.char('g')} "
            "est nulle, la soustraction ne déplace pas le point. "
            "<bookmark mark='sub_right'/>"
            "À droite, "
            f"{tts.char('g')} "
            "est positif. Son opposé est négatif, donc le point descend. "
            "<bookmark mark='sub_more'/>"
            "En répétant cette opération, on obtient plusieurs points de la différence. "
            "<bookmark mark='sub_graph'/>"
            "Ils déterminent le graphe de "
            f"{tts.char('f')} moins {tts.char('g')}."
        ),
    },
    {
        "caption": "Deuxième méthode : réfléchir tout le graphe de g.",
        "ssml": tts.ssml(
            "Voici maintenant une seconde méthode. "
            "<bookmark mark='reflect_formula'/>"
            "Le graphe de moins "
            f"{tts.char('g')} "
            "est la réflexion du graphe de "
            f"{tts.char('g')} "
            "par rapport à l'axe horizontal. "
            "<bookmark mark='reflect_points'/>"
            "Chaque point garde la même abscisse, mais son ordonnée devient son opposé. "
            "<bookmark mark='reflect_graph'/>"
            "Toute la droite se réfléchit ainsi. "
            "<bookmark mark='alternative_formula'/>"
            "On peut alors construire la différence comme une somme : "
            f"{tts.char('f')} moins {tts.char('g')} "
            "égale "
            f"{tts.char('f')} plus, moins {tts.char('g')}. "
            "<bookmark mark='alternative_points'/>"
            "On applique exactement la construction de la somme à plusieurs abscisses. "
            "<bookmark mark='alternative_graph'/>"
            "On retrouve le même graphe violet."
        ),
    },
    {
        "caption": "Les intersections de f et g deviennent les zéros de f−g.",
        "ssml": tts.ssml(
            "La différence donne aussi une lecture importante. "
            "<bookmark mark='intersections'/>"
            "Les graphes de "
            f"{tts.char('f')} "
            "et de "
            f"{tts.char('g')} "
            "se rencontrent ici, pour "
            f"{tts.char('x')} égal zéro, "
            "et ici, pour "
            f"{tts.char('x')} égal deux. "
            "<bookmark mark='equivalence'/>"
            "À ces abscisses, les deux hauteurs sont égales, donc leur différence est nulle. "
            "<bookmark mark='zeros'/>"
            "Les deux intersections deviennent exactement les deux zéros de "
            f"{tts.char('f')} moins {tts.char('g')}."
        ),
    },
    {
        "caption": "Résumé : deux constructions exactes de f−g.",
        "ssml": tts.ssml(
            "Résumons. "
            "<bookmark mark='summary_add'/>"
            "Pour la somme, on reporte le segment signé "
            f"{tts.char('g')} de {tts.char('x')} "
            "à partir de la hauteur de "
            f"{tts.char('f')}. "
            "<bookmark mark='summary_sub_direct'/>"
            "Pour la différence, on peut reporter directement le segment opposé, moins "
            f"{tts.char('g')} de {tts.char('x')}. "
            "<bookmark mark='summary_sub_reflect'/>"
            "Ou bien réfléchir d'abord tout le graphe de "
            f"{tts.char('g')}, "
            "puis additionner "
            f"{tts.char('f')} "
            "et moins "
            f"{tts.char('g')}. "
            "Dans tous les cas, l'abscisse ne change pas."
        ),
    },
]


def make_axes():
    return Axes(
        x_range=[-2.5, 2.5, 1],
        y_range=[-1.5, 4.75, 1],
        x_length=8.7,
        y_length=5.5,
        tips=False,
        axis_config={
            "color": BLACK,
            "include_numbers": True,
            "font_size": 22,
            "stroke_width": 2.5,
        },
    ).shift(DOWN * 0.55)


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class OperationsFonctionsFR(VoiceoverScene if VoiceoverScene is not None else Scene):
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

    @staticmethod
    def _dot(axes, x, y, color, radius=0.065):
        return Dot(axes.c2p(x, y), color=color, radius=radius)

    @staticmethod
    def _scanner(axes, x):
        return DashedLine(
            axes.c2p(x, -1.35),
            axes.c2p(x, 4.55),
            color=GRAY,
            stroke_width=2.4,
            dash_length=0.11,
        )

    @staticmethod
    def _exact_vertical_segment(axes, x, y0, y1, color, width=5):
        """A measurement segment with endpoints exactly at y0 and y1.

        Unlike Arrow with a nonzero buff, this line is not shortened. Its visible
        displacement therefore matches the represented change in y exactly.
        """
        return Line(
            axes.c2p(x, y0),
            axes.c2p(x, y1),
            color=color,
            stroke_width=width,
            buff=0,
        )

    @staticmethod
    def _x_label(axes, x, tex):
        label = MathTex(tex).scale(0.65)
        label.next_to(axes.c2p(x, -1.35), DOWN, buff=0.08)
        return label

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        C_F = BLACK
        C_G = BLUE_D
        C_SUM = GREEN_D
        C_NEG = PURPLE_B
        C_DIFF = PURPLE_D
        C_GHOST = GRAY

        title = Text("Additionner et soustraire des fonctions", font_size=42)
        title.to_edge(UP, buff=0.22)

        central_question = VGroup(
            Text("Question centrale", font_size=28, color=C_G),
            Text("Comment construire f + g et f − g", font_size=36),
            Text("directement à partir des deux graphes?", font_size=32),
        ).arrange(DOWN, buff=0.18)
        central_question.move_to(DOWN * 0.15)

        same_x = VGroup(
            MathTex(r"x\longrightarrow f(x)", color=C_F).scale(1.15),
            MathTex(r"x\longrightarrow g(x)", color=C_G).scale(1.15),
            Text("Même abscisse, deux hauteurs.", font_size=30),
        ).arrange(DOWN, buff=0.27)
        same_x.move_to(DOWN * 0.1)

        with self.narrated(opening_item):
            self.wait_until_bookmark("question")
            self.play(FadeIn(title), FadeIn(central_question), run_time=0.8)
            self.wait(0.45)

            self.wait_until_bookmark("same_x")
            self.play(ReplacementTransform(central_question, same_x), run_time=0.8)
            self.wait(0.60)

        self.play(FadeOut(same_x), run_time=0.55)

        axes = make_axes()
        axis_labels = axes.get_axis_labels(MathTex("x"), MathTex("y"))

        # The coefficients were chosen to make the important values exact and
        # easy to verify:
        #   f(x) = (x^2 - x + 1)/2,  g(x) = (x + 1)/2
        #   f+g = x^2/2 + 1,         f-g = x(x-2)/2.
        def f(x):
            return 0.5 * x**2 - 0.5 * x + 0.5

        def g(x):
            return 0.5 * x + 0.5

        def neg_g(x):
            return -g(x)

        def sum_fg(x):
            return f(x) + g(x)

        def diff_fg(x):
            return f(x) - g(x)

        sample_xs = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]
        for x in sample_xs:
            assert isclose(sum_fg(x) - f(x), g(x), abs_tol=1e-12)
            assert isclose(diff_fg(x) - f(x), neg_g(x), abs_tol=1e-12)
            assert isclose(neg_g(x), -g(x), abs_tol=1e-12)

        x_plot = [-2.15, 2.15]
        graph_f = axes.plot(f, x_range=x_plot, color=C_F, stroke_width=4)
        graph_g = axes.plot(g, x_range=x_plot, color=C_G, stroke_width=4)
        graph_neg_g = axes.plot(neg_g, x_range=x_plot, color=C_NEG, stroke_width=4)
        graph_sum = axes.plot(sum_fg, x_range=x_plot, color=C_SUM, stroke_width=4.5)
        graph_diff = axes.plot(diff_fg, x_range=x_plot, color=C_DIFF, stroke_width=4.5)

        label_f = MathTex(r"f", color=C_F).scale(0.76)
        label_f.move_to(axes.c2p(-1.95, f(-1.95) + 0.27))

        label_g = MathTex(r"g", color=C_G).scale(0.76)
        label_g.move_to(axes.c2p(2.15, g(2.15)) + RIGHT * 0.55)

        label_neg_g = MathTex(r"-g", color=C_NEG).scale(0.76)
        label_neg_g.move_to(axes.c2p(1.75, neg_g(1.75) - 0.24))

        label_sum = MathTex(r"f+g", color=C_SUM).scale(0.76)
        label_sum.move_to(axes.c2p(1.75, sum_fg(1.75) + 0.28))

        label_diff = MathTex(r"f-g", color=C_DIFF).scale(0.76)
        label_diff.move_to(axes.c2p(-2.15, diff_fg(-2.15)) + LEFT * 0.6)

        formula_inputs = MathTex(r"f(x)", r"\qquad", r"g(x)").scale(1.0)
        formula_inputs[0].set_color(C_F)
        formula_inputs[2].set_color(C_G)
        formula_inputs.next_to(title, DOWN, buff=0.12)

        domain_note = VGroup(
            Text("domaine commun :", font_size=21),
            MathTex(r"x\in\operatorname{Dom}(f)\cap\operatorname{Dom}(g)").scale(0.62),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
        domain_box = SurroundingRectangle(
            domain_note,
            color=C_G,
            buff=0.14,
            stroke_width=2.2,
        )
        domain_group = VGroup(domain_box, domain_note)
        domain_group.to_edge(RIGHT, buff=0.38)
        domain_group.align_to(formula_inputs, UP)

        with self.narrated(script[0]):
            self.play(Create(axes), FadeIn(axis_labels), FadeIn(formula_inputs), run_time=0.8)
            self.play(Create(graph_f), FadeIn(label_f), run_time=0.75)
            self.play(Create(graph_g), FadeIn(label_g), run_time=0.75)

            self.wait_until_bookmark("domain")
            self.play(FadeIn(domain_group), run_time=0.55)
            self.wait(0.60)
            self.play(FadeOut(domain_group), run_time=0.45)

        # ------------------------------------------------------------------
        # Act 1 — f+g: copy the exact signed segment g(x) to start at f(x).
        # ------------------------------------------------------------------
        formula_add = MathTex(
            r"(f+g)(x)", r"=", r"f(x)", r"+", r"g(x)"
        ).scale(1.0)
        formula_add[0].set_color(C_SUM)
        formula_add[2].set_color(C_F)
        formula_add[3].set_color(C_SUM)
        formula_add[4].set_color(C_G)
        formula_add.next_to(title, DOWN, buff=0.12)

        sum_points = VGroup()
        scanner = self._scanner(axes, -2.0)

        def show_addition_sample(x, x_tex, value_tex, result_tex, label_side=RIGHT):
            fx = f(x)
            gx = g(x)
            sx = sum_fg(x)

            dot_f = self._dot(axes, x, fx, C_F)
            dot_g = self._dot(axes, x, gx, C_G)
            dot_result = self._dot(axes, x, sx, C_SUM)
            source_segment = self._exact_vertical_segment(axes, x, 0, gx, C_G)
            target_segment = self._exact_vertical_segment(axes, x, fx, sx, C_SUM)

            source_label = MathTex(value_tex, color=C_G).scale(0.64)
            source_label.next_to(source_segment, label_side, buff=0.12)
            result_label = MathTex(result_tex, color=C_SUM).scale(0.67)
            result_label.move_to([4.1, -2.55, 0])
            x_label = self._x_label(axes, x, x_tex)

            self.play(FadeIn(dot_f), FadeIn(dot_g), FadeIn(x_label), run_time=0.30)
            self.play(Create(source_segment), FadeIn(source_label), run_time=0.50)
            self.wait(0.28)
            self.play(
                TransformFromCopy(source_segment, target_segment),
                run_time=0.70,
            )
            self.wait(0.30)
            self.play(FadeIn(dot_result), FadeIn(result_label), run_time=0.35)
            self.wait(0.50)
            self.play(
                FadeOut(dot_f),
                FadeOut(dot_g),
                FadeOut(source_segment),
                FadeOut(target_segment),
                FadeOut(source_label),
                FadeOut(result_label),
                FadeOut(x_label),
                run_time=0.38,
            )
            return dot_result

        def show_zero_displacement(x, x_tex, result_color):
            fx = f(x)
            point = self._dot(axes, x, fx, result_color, radius=0.075)
            x_label = self._x_label(axes, x, x_tex)
            zero_label = MathTex(r"g(-1)=0", font_size=36, color=result_color)
            zero_label.next_to(point, RIGHT, buff=0.3)
            halo = Circle(radius=0.15, color=result_color, stroke_width=3).move_to(point)

            self.play(FadeIn(x_label), FadeIn(point), Create(halo), FadeIn(zero_label), run_time=0.55)
            self.wait(0.55)
            self.play(FadeOut(x_label), FadeOut(halo), FadeOut(zero_label), run_time=0.35)
            return point

        with self.narrated(script[1]):
            self.wait_until_bookmark("add_formula")
            self.play(ReplacementTransform(formula_inputs, formula_add), run_time=0.65)
            self.play(Create(scanner), run_time=0.45)

            self.wait_until_bookmark("add_left")
            sum_left = show_addition_sample(
                -2.0,
                r"x=-2",
                r"g(-2)=-\frac12",
                r"\frac72+\left(-\frac12\right)=3",
                label_side=LEFT,
            )
            sum_points.add(sum_left)

            self.wait_until_bookmark("add_zero")
            self.play(Transform(scanner, self._scanner(axes, -1.0)), run_time=0.55)
            sum_zero = show_zero_displacement(-1.0, r"x=-1", C_SUM)
            sum_points.add(sum_zero)

            self.wait_until_bookmark("add_right")
            self.play(Transform(scanner, self._scanner(axes, 1.0)), run_time=0.55)
            sum_right = show_addition_sample(
                1.0,
                r"x=1",
                r"g(1)=1",
                r"\frac12+1=\frac32",
                label_side=RIGHT,
            )
            sum_points.add(sum_right)

            self.wait_until_bookmark("add_more")
            extra_sum_points = VGroup(
                *[
                    self._dot(axes, x, sum_fg(x), C_SUM, radius=0.055)
                    for x in [-1.5, -0.5, 0.0, 0.5, 1.5, 2.0]
                ]
            )
            self.play(
                AnimationGroup(
                    *[FadeIn(point, scale=0.65) for point in extra_sum_points],
                    lag_ratio=0.14,
                ),
                Transform(scanner, self._scanner(axes, 2.0)),
                run_time=1.35,
            )
            sum_points.add(*extra_sum_points)

            self.wait_until_bookmark("add_graph")
            self.play(
                graph_f.animate.set_stroke(color=C_GHOST, opacity=0.35, width=3),
                graph_g.animate.set_stroke(color=C_GHOST, opacity=0.35, width=3),
                FadeOut(scanner),
                run_time=0.45,
            )
            self.play(Create(graph_sum), FadeIn(label_sum), run_time=1.05)
            self.wait(0.65)

        # ------------------------------------------------------------------
        # Act 2 — f-g: reflect the local segment g(x), then copy -g(x).
        # ------------------------------------------------------------------
        formula_sub = MathTex(
            r"(f-g)(x)", r"=", r"f(x)", r"+", r"\bigl(-g(x)\bigr)"
        ).scale(1.0)
        formula_sub[0].set_color(C_DIFF)
        formula_sub[2].set_color(C_F)
        formula_sub[3].set_color(C_DIFF)
        formula_sub[4].set_color(C_DIFF)
        formula_sub.next_to(title, DOWN, buff=0.12)

        diff_points = VGroup()
        scanner_sub = self._scanner(axes, -2.0)

        def show_subtraction_sample(x, x_tex, g_tex, opposite_tex, result_tex, label_side=RIGHT):
            fx = f(x)
            gx = g(x)
            ngx = neg_g(x)
            dx = diff_fg(x)

            dot_f = self._dot(axes, x, fx, C_F)
            dot_g = self._dot(axes, x, gx, C_G)
            dot_diff = self._dot(axes, x, dx, C_DIFF)

            g_segment = self._exact_vertical_segment(axes, x, 0, gx, C_G)
            opposite_segment = self._exact_vertical_segment(axes, x, 0, ngx, C_NEG)
            target_segment = self._exact_vertical_segment(axes, x, fx, dx, C_DIFF)

            g_label = MathTex(g_tex, color=C_G).scale(0.62)
            g_label.next_to(g_segment, label_side, buff=0.12)
            opposite_label = MathTex(opposite_tex, color=C_NEG).scale(0.62)
            opposite_label.next_to(opposite_segment, -label_side, buff=0.12)
            result_label = MathTex(result_tex, color=C_DIFF).scale(0.67)
            result_label.next_to(dot_diff, label_side, buff=0.14)
            x_label = self._x_label(axes, x, x_tex)

            self.play(FadeIn(dot_f), FadeIn(dot_g), FadeIn(x_label), run_time=0.30)
            self.play(Create(g_segment), FadeIn(g_label), run_time=0.50)
            self.wait(0.30)
            self.play(
                TransformFromCopy(g_segment, opposite_segment),
                FadeIn(opposite_label),
                run_time=0.78,
            )
            self.wait(0.60)
            self.play(
                TransformFromCopy(opposite_segment, target_segment),
                run_time=0.78,
            )
            self.wait(0.40)
            self.play(FadeIn(dot_diff), FadeIn(result_label), run_time=0.35)
            self.wait(0.55)
            self.play(
                FadeOut(dot_f),
                FadeOut(dot_g),
                FadeOut(g_segment),
                FadeOut(opposite_segment),
                FadeOut(target_segment),
                FadeOut(g_label),
                FadeOut(opposite_label),
                FadeOut(result_label),
                FadeOut(x_label),
                run_time=0.40,
            )
            return dot_diff

        with self.narrated(script[2]):
            self.wait_until_bookmark("sub_formula")
            self.play(
                FadeOut(graph_sum),
                FadeOut(label_sum),
                FadeOut(sum_points),
                ReplacementTransform(formula_add, formula_sub),
                graph_f.animate.set_stroke(color=C_F, opacity=1, width=4),
                graph_g.animate.set_stroke(color=C_G, opacity=1, width=4),
                run_time=0.75,
            )
            self.play(Create(scanner_sub), run_time=0.45)

            self.wait_until_bookmark("sub_left")
            diff_left = show_subtraction_sample(
                -2.0,
                r"x=-2",
                r"g(-2)=-\frac12",
                r"-g(-2)=\frac12",
                r"\frac72-\left(-\frac12\right)=4",
                label_side=LEFT,
            )
            diff_points.add(diff_left)

            self.wait_until_bookmark("sub_zero")
            self.play(Transform(scanner_sub, self._scanner(axes, -1.0)), run_time=0.55)
            diff_zero = show_zero_displacement(-1.0, r"x=-1", C_DIFF)
            diff_points.add(diff_zero)

            self.wait_until_bookmark("sub_right")
            self.play(Transform(scanner_sub, self._scanner(axes, 1.0)), run_time=0.55)
            diff_right = show_subtraction_sample(
                1.0,
                r"x=1",
                r"g(1)=1",
                r"-g(1)=-1",
                r"\frac12-1=-\frac12",
                label_side=RIGHT,
            )
            diff_points.add(diff_right)

            self.wait_until_bookmark("sub_more")
            extra_diff_points = VGroup(
                *[
                    self._dot(axes, x, diff_fg(x), C_DIFF, radius=0.055)
                    for x in [-1.5, -0.5, 0.0, 0.5, 1.5, 2.0]
                ]
            )
            self.play(
                AnimationGroup(
                    *[FadeIn(point, scale=0.65) for point in extra_diff_points],
                    lag_ratio=0.14,
                ),
                Transform(scanner_sub, self._scanner(axes, 2.0)),
                run_time=1.35,
            )
            diff_points.add(*extra_diff_points)

            self.wait_until_bookmark("sub_graph")
            self.play(
                graph_f.animate.set_stroke(color=C_GHOST, opacity=0.35, width=3),
                graph_g.animate.set_stroke(color=C_GHOST, opacity=0.35, width=3),
                FadeOut(scanner_sub),
                run_time=0.45,
            )
            self.play(Create(graph_diff), FadeIn(label_diff), run_time=1.05)
            self.wait(0.65)

        # ------------------------------------------------------------------
        # Act 3 — Reflect the whole graph g, then compute f+(-g).
        # ------------------------------------------------------------------
        reflect_formula = MathTex(
            r"(-g)(x)", r"=", r"-g(x)"
        ).scale(1.05)
        reflect_formula[0].set_color(C_NEG)
        reflect_formula[2].set_color(C_NEG)
        reflect_formula.next_to(title, DOWN, buff=0.12)

        mirror_label = Text("réflexion par rapport à l’axe des x", font_size=25, color=C_NEG)
        mirror_label.next_to(reflect_formula, RIGHT, buff=0.38)

        pair_xs = [-2.0, 1.0]
        g_pair_points = VGroup(*[self._dot(axes, x, g(x), C_G) for x in pair_xs])
        neg_pair_points = VGroup(*[self._dot(axes, x, neg_g(x), C_NEG) for x in pair_xs])
        pair_guides = VGroup(
            *[
                DashedLine(
                    axes.c2p(x, g(x)),
                    axes.c2p(x, neg_g(x)),
                    color=C_GHOST,
                    stroke_width=2.4,
                    dash_length=0.10,
                )
                for x in pair_xs
            ]
        )
        pair_labels = VGroup(
            MathTex(r"g(-2)=-\frac12\;\longleftrightarrow\;-g(-2)=\frac12").scale(0.62),
            MathTex(r"g(1)=1\;\longleftrightarrow\;-g(1)=-1").scale(0.62),
        )
        pair_labels[0].next_to(neg_pair_points[0], LEFT, buff=0.18)
        pair_labels[1].next_to(neg_pair_points[1], RIGHT, buff=0.18)

        with self.narrated(script[3]):
            self.wait_until_bookmark("reflect_formula")
            self.play(
                FadeOut(graph_diff),
                FadeOut(label_diff),
                FadeOut(diff_points),
                ReplacementTransform(formula_sub, reflect_formula),
                graph_f.animate.set_stroke(color=C_GHOST, opacity=0.18, width=2.5),
                graph_g.animate.set_stroke(color=C_G, opacity=1, width=4),
                FadeIn(mirror_label),
                run_time=0.75,
            )

            self.wait_until_bookmark("reflect_points")
            self.play(FadeIn(g_pair_points), Create(pair_guides), run_time=0.55)
            self.play(
                TransformFromCopy(g_pair_points, neg_pair_points),
                FadeIn(pair_labels),
                run_time=0.85,
            )
            self.wait(0.65)

            self.wait_until_bookmark("reflect_graph")
            reflected_copy = graph_g.copy().set_color(C_NEG)
            self.add(reflected_copy)
            self.play(
                reflected_copy.animate.stretch(
                    -1,
                    dim=1,
                    about_point=axes.c2p(0, 0),
                ),
                run_time=1.15,
            )
            self.play(ReplacementTransform(reflected_copy, graph_neg_g), FadeIn(label_neg_g), run_time=0.35)
            self.wait(0.60)

            self.play(
                FadeOut(g_pair_points),
                FadeOut(neg_pair_points),
                FadeOut(pair_guides),
                FadeOut(pair_labels),
                FadeOut(mirror_label),
                run_time=0.45,
            )

            self.wait_until_bookmark("alternative_formula")
            alternative_formula = MathTex(
                r"(f-g)(x)", r"=", r"f(x)", r"+", r"(-g)(x)"
            ).scale(1.0)
            alternative_formula[0].set_color(C_DIFF)
            alternative_formula[2].set_color(C_F)
            alternative_formula[3].set_color(C_SUM)
            alternative_formula[4].set_color(C_NEG)
            alternative_formula.next_to(title, DOWN, buff=0.12)
            self.play(
                ReplacementTransform(reflect_formula, alternative_formula),
                graph_f.animate.set_stroke(color=C_F, opacity=1, width=4),
                run_time=0.65,
            )

            self.wait_until_bookmark("alternative_points")
            alt_xs = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0]
            alt_result_points = VGroup()
            quick_segments = VGroup()
            for x in alt_xs:
                segment = self._exact_vertical_segment(axes, x, f(x), diff_fg(x), C_DIFF, width=3.5)
                result_point = self._dot(axes, x, diff_fg(x), C_DIFF, radius=0.052)
                quick_segments.add(segment)
                alt_result_points.add(result_point)

            self.play(
                AnimationGroup(
                    *[
                        AnimationGroup(Create(segment), FadeIn(point), lag_ratio=0.15)
                        for segment, point in zip(quick_segments, alt_result_points)
                    ],
                    lag_ratio=0.10,
                ),
                run_time=2.0,
            )
            self.wait(0.50)
            self.play(FadeOut(quick_segments), run_time=0.45)

            self.wait_until_bookmark("alternative_graph")
            self.play(Create(graph_diff), FadeIn(label_diff), run_time=1.0)
            self.play(Indicate(graph_diff, color=C_DIFF, scale_factor=1.02), run_time=0.75)
            self.wait(0.60)

        # ------------------------------------------------------------------
        # Act 4 — Intersections of f and g are zeros of f-g.
        # ------------------------------------------------------------------
        roots = [0.0, 2.0]
        intersection_points = VGroup(
            *[self._dot(axes, root, f(root), C_DIFF, radius=0.075) for root in roots]
        )
        zero_points = VGroup(
            *[self._dot(axes, root, 0, C_DIFF, radius=0.075) for root in roots]
        )
        guides = VGroup(
            *[
                DashedLine(
                    axes.c2p(root, f(root)),
                    axes.c2p(root, 0),
                    color=C_DIFF,
                    stroke_width=2.5,
                    dash_length=0.10,
                )
                for root in roots
            ]
        )
        root_labels = VGroup(
            self._x_label(axes, 0, r"x=0"),
            self._x_label(axes, 2, r"x=2"),
        )

        equivalence = MathTex(
            r"f(x)=g(x)",
            r"\quad\Longleftrightarrow\quad",
            r"(f-g)(x)=0",
        ).scale(0.93)
        equivalence[0].set_color(C_DIFF)
        equivalence[2].set_color(C_DIFF)
        equivalence.next_to(title, DOWN, buff=0.12)

        with self.narrated(script[4]):
            self.wait_until_bookmark("intersections")
            self.play(
                FadeOut(graph_neg_g),
                FadeOut(label_neg_g),
                FadeOut(alt_result_points),
                graph_f.animate.set_stroke(color=C_F, opacity=0.9, width=3.6),
                graph_g.animate.set_stroke(color=C_G, opacity=0.9, width=3.6),
                FadeIn(intersection_points),
                FadeIn(root_labels),
                run_time=0.70,
            )
            self.play(
                AnimationGroup(
                    *[Indicate(point, color=C_DIFF, scale_factor=1.4) for point in intersection_points],
                    lag_ratio=0.35,
                ),
                run_time=1.0,
            )

            self.wait_until_bookmark("equivalence")
            self.play(ReplacementTransform(alternative_formula, equivalence), run_time=0.65)
            self.play(Circumscribe(equivalence[0], color=C_DIFF), run_time=0.65)
            self.play(Circumscribe(equivalence[2], color=C_DIFF), run_time=0.65)

            self.wait_until_bookmark("zeros")
            self.play(Create(guides), run_time=0.65)
            self.play(TransformFromCopy(intersection_points, zero_points), run_time=0.80)
            self.play(
                AnimationGroup(
                    *[Indicate(point, color=C_DIFF, scale_factor=1.45) for point in zero_points],
                    lag_ratio=0.30,
                ),
                run_time=1.0,
            )
            self.wait(0.65)

        graph_scene = VGroup(
            axes,
            axis_labels,
            graph_f,
            graph_g,
            graph_diff,
            label_f,
            label_g,
            label_diff,
            intersection_points,
            zero_points,
            guides,
            root_labels,
            equivalence,
        )

        # ------------------------------------------------------------------
        # Final stable summary.
        # ------------------------------------------------------------------
        summary_title = Text("Même x : trois lectures complémentaires", font_size=35)
        summary_title.next_to(title, DOWN, buff=0.34)

        add_formula = MathTex(
            r"(f+g)(x)", r"=", r"f(x)", r"+", r"g(x)"
        ).scale(0.98)
        add_formula[0].set_color(C_SUM)
        add_formula[2].set_color(C_F)
        add_formula[3].set_color(C_SUM)
        add_formula[4].set_color(C_G)
        add_words = Text("reporter exactement le segment signé g(x)", font_size=25)
        add_row = VGroup(add_formula, add_words).arrange(DOWN, buff=0.15)

        direct_formula = MathTex(
            r"(f-g)(x)", r"=", r"f(x)", r"+", r"\bigl(-g(x)\bigr)"
        ).scale(0.98)
        direct_formula[0].set_color(C_DIFF)
        direct_formula[2].set_color(C_F)
        direct_formula[3].set_color(C_DIFF)
        direct_formula[4].set_color(C_NEG)
        direct_words = Text("réfléchir localement g(x), puis reporter −g(x)", font_size=25)
        direct_row = VGroup(direct_formula, direct_words).arrange(DOWN, buff=0.15)

        reflect_formula_final = MathTex(
            r"f-g", r"=", r"f", r"+", r"(-g)"
        ).scale(0.98)
        reflect_formula_final[0].set_color(C_DIFF)
        reflect_formula_final[2].set_color(C_F)
        reflect_formula_final[3].set_color(C_SUM)
        reflect_formula_final[4].set_color(C_NEG)
        reflect_words = Text("réfléchir tout le graphe de g, puis additionner", font_size=25)
        reflect_row = VGroup(reflect_formula_final, reflect_words).arrange(DOWN, buff=0.15)

        add_box = SurroundingRectangle(add_row, color=C_SUM, buff=0.22, stroke_width=2.7)
        direct_box = SurroundingRectangle(direct_row, color=C_DIFF, buff=0.22, stroke_width=2.7)
        reflect_box = SurroundingRectangle(reflect_row, color=C_DIFF, buff=0.22, stroke_width=2.7)

        add_group = VGroup(add_box, add_row)
        direct_group = VGroup(direct_box, direct_row)
        reflect_group = VGroup(reflect_box, reflect_row)
        summary_rows = VGroup(add_group, direct_group, reflect_group).arrange(DOWN, buff=0.33)
        summary_rows.move_to(DOWN * 0.35)

        final_note = Text("Dans toutes les constructions, l’abscisse x reste fixe.", font_size=28)
        final_note.to_edge(DOWN, buff=0.28)

        with self.narrated(script[5]):
            self.play(FadeOut(graph_scene), run_time=0.75)
            self.play(FadeIn(summary_title), run_time=0.55)

            self.wait_until_bookmark("summary_add")
            self.play(FadeIn(add_group), run_time=0.60)

            self.wait_until_bookmark("summary_sub_direct")
            self.play(FadeIn(direct_group), run_time=0.60)

            self.wait_until_bookmark("summary_sub_reflect")
            self.play(FadeIn(reflect_group), FadeIn(final_note), run_time=0.65)

        self.wait(1.3)
