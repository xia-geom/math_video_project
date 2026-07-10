import os
from contextlib import contextmanager
from dataclasses import dataclass
from math import sqrt

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


script = [
    {
        "caption": "On additionne les sorties.",
        "ssml": tts.ssml(
            "Additionner deux fonctions, c'est additionner leurs sorties. "
            "Pour le même "
            f"{tts.char('x')}, "
            "on lit "
            f"{tts.char('f')} de {tts.char('x')} "
            "et "
            f"{tts.char('g')} de {tts.char('x')}, "
            "puis on les additionne."
        ),
    },
    {
        "caption": "De +2 à +g(x) : le décalage varie.",
        "ssml": tts.ssml(
            "<bookmark mark='const_formula'/>"
            "Dans la vidéo précédente, "
            f"{tts.char('f')} de {tts.char('x')} plus deux "
            "déplaçait tout le graphe vers le haut, toujours de deux unités. "
            "<bookmark mark='const_move'/>"
            "Maintenant, si on remplace deux par "
            f"{tts.char('g')} de {tts.char('x')}, "
            "<bookmark mark='variable_formula'/>"
            "la quantité ajoutée dépend de "
            f"{tts.char('x')}. "
            "Le décalage vertical n'est plus constant."
        ),
    },
    {
        "caption": "On construit f+g point par point.",
        "ssml": tts.ssml(
            "<bookmark mark='scan_start'/>"
            "On utilise une droite verticale comme scanner. "
            "<bookmark mark='sample_neg'/>"
            "Ici, "
            f"{tts.char('g')} de {tts.char('x')} "
            "est négatif : ajouter "
            f"{tts.char('g')} de {tts.char('x')} "
            "fait descendre le point. "
            "<bookmark mark='sample_mid'/>"
            "Pour une autre valeur de "
            f"{tts.char('x')}, "
            "on recommence. "
            "<bookmark mark='sample_pos'/>"
            "Ici, "
            f"{tts.char('g')} de {tts.char('x')} "
            "est positif : le point monte. "
            "<bookmark mark='sum_graph'/>"
            "En faisant cela pour tous les "
            f"{tts.char('x')}, "
            "on obtient le graphe de "
            f"{tts.char('f')} plus {tts.char('g')}."
        ),
    },
    {
        "caption": "f-g mesure une distance verticale.",
        "ssml": tts.ssml(
            "<bookmark mark='split_start'/>"
            "Pour la soustraction, il est plus clair de séparer l'écran. "
            "À gauche, on garde les graphes de "
            f"{tts.char('f')} "
            "et "
            f"{tts.char('g')}. "
            "À droite, on construit "
            f"{tts.char('h')} égale {tts.char('f')} moins {tts.char('g')}. "
            "<bookmark mark='diff_pos'/>"
            "Quand "
            f"{tts.char('f')} "
            "est au-dessus de "
            f"{tts.char('g')}, "
            "la différence est positive. "
            "<bookmark mark='diff_neg'/>"
            "Quand "
            f"{tts.char('f')} "
            "est en-dessous de "
            f"{tts.char('g')}, "
            "la différence est négative. "
            "<bookmark mark='diff_graph'/>"
            "Le graphe de "
            f"{tts.char('h')} "
            "résume cette distance verticale signée."
        ),
    },
    {
        "caption": "Les intersections deviennent des zéros.",
        "ssml": tts.ssml(
            "<bookmark mark='intersections'/>"
            "Aux intersections, les deux graphes ont exactement la même hauteur. "
            "<bookmark mark='equivalence'/>"
            "Donc "
            f"{tts.char('f')} de {tts.char('x')} égale {tts.char('g')} de {tts.char('x')} "
            "revient à dire que "
            f"{tts.char('f')} de {tts.char('x')} moins {tts.char('g')} de {tts.char('x')} "
            "égale zéro. "
            "<bookmark mark='zero_points'/>"
            "Sur le graphe de "
            f"{tts.char('h')}, "
            "ces valeurs deviennent des zéros."
        ),
    },
    {
        "caption": "Additionner n'est pas composer.",
        "ssml": tts.ssml(
            "<bookmark mark='add_side'/>"
            "Attention : additionner des fonctions n'est pas composer des fonctions. "
            "Dans "
            f"{tts.char('f')} plus {tts.char('g')}, "
            "on additionne deux sorties. "
            "<bookmark mark='comp_side'/>"
            "Dans la composition, la sortie de "
            f"{tts.char('g')} "
            "devient l'entrée de "
            f"{tts.char('f')}."
        ),
    },
]


def proportional_axes(x_range, y_range, unit_size=0.62, font_size=22):
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

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        C_F = BLACK
        C_G = BLUE_D
        C_SUM = GREEN_D
        C_DIFF = PURPLE_D
        C_WARN = RED_D
        C_GHOST = GRAY

        title = Text("Additionner et soustraire des fonctions", font_size=42)
        title.to_edge(UP, buff=0.25)

        unit = 0.62

        main_axes = proportional_axes(
            x_range=[-3.5, 3.5, 1],
            y_range=[-4, 5, 1],
            unit_size=unit,
            font_size=22,
        ).shift(DOWN * 0.45)

        main_labels = main_axes.get_axis_labels(MathTex("x"), MathTex("y"))

        def f(x):
            return 0.45 * x**2 - 1

        def g(x):
            return 0.6 * x - 0.2

        def sum_fg(x):
            return f(x) + g(x)

        def diff_fg(x):
            return f(x) - g(x)

        x_range = [-3, 3]

        graph_f = main_axes.plot(f, x_range=x_range, color=C_F, stroke_width=4)
        graph_g = main_axes.plot(g, x_range=x_range, color=C_G, stroke_width=4)
        graph_const = main_axes.plot(lambda x: f(x) + 2, x_range=x_range, color=C_SUM, stroke_width=4)
        graph_sum = main_axes.plot(sum_fg, x_range=x_range, color=C_SUM, stroke_width=4)

        label_f = MathTex("y=f(x)", color=C_F).scale(0.78)
        label_f.move_to(main_axes.c2p(-2.65, f(-2.65) + 0.35))

        label_g = MathTex("y=g(x)", color=C_G).scale(0.78)
        label_g.move_to(main_axes.c2p(2.25, g(2.25) + 0.35))

        label_sum = MathTex("y=(f+g)(x)", color=C_SUM).scale(0.78)
        label_sum.move_to(main_axes.c2p(1.8, sum_fg(1.8) + 0.45))

        formula_intro = MathTex(r"(f+g)(x)=f(x)+g(x)").scale(1.05)
        formula_intro.next_to(title, DOWN, buff=0.12)
        formula_intro[0][1].set_color(C_SUM)

        formula_const = MathTex(r"f(x)+2").scale(1.05)
        formula_const.next_to(title, DOWN, buff=0.12)
        formula_const[-1].set_color(C_SUM)

        formula_variable = MathTex(r"f(x)+g(x)").scale(1.05)
        formula_variable.next_to(title, DOWN, buff=0.12)
        formula_variable[-4:].set_color(C_G)

        def scanner_at(axes, x, y_min=-4, y_max=5):
            return DashedLine(
                axes.c2p(x, y_min),
                axes.c2p(x, y_max),
                color=GRAY,
                stroke_width=3,
                dash_length=0.12,
            )

        def dot_at(axes, x, y, color):
            return Dot(axes.c2p(x, y), color=color, radius=0.065)

        def v_arrow(axes, x, y0, y1, color):
            return Arrow(
                axes.c2p(x, y0),
                axes.c2p(x, y1),
                buff=0.08,
                color=color,
                stroke_width=4,
                max_tip_length_to_length_ratio=0.22,
            )

        # ------------------------------------------------------------------
        # Act 1: introduce f and g
        # ------------------------------------------------------------------
        with self.narrated(script[0]):
            self.play(FadeIn(title))
            self.play(Create(main_axes), FadeIn(main_labels))
            self.play(FadeIn(formula_intro))
            self.play(Create(graph_f), FadeIn(label_f))
            self.play(Create(graph_g), FadeIn(label_g))

        # ------------------------------------------------------------------
        # Act 2: connect f(x)+2 to f(x)+g(x)
        # ------------------------------------------------------------------
        a0 = 1.2
        fa0 = f(a0)

        const_dot_old = dot_at(main_axes, a0, fa0, C_F)
        const_dot_new = dot_at(main_axes, a0, fa0 + 2, C_SUM)
        const_arrow = v_arrow(main_axes, a0, fa0, fa0 + 2, C_SUM)

        const_label = MathTex(r"+2", color=C_SUM).scale(0.8)
        const_label.next_to(const_arrow, RIGHT, buff=0.1)

        with self.narrated(script[1]):
            self.wait_until_bookmark("const_formula")
            self.play(ReplacementTransform(formula_intro, formula_const))

            self.wait_until_bookmark("const_move")
            self.play(FadeIn(const_dot_old))
            self.play(Create(const_arrow), FadeIn(const_dot_new), FadeIn(const_label))

            graph_f_ghost = graph_f.copy().set_stroke(color=C_GHOST, width=3, opacity=0.35)
            moving_const = graph_f.copy().set_stroke(color=C_SUM, width=4, opacity=1)
            self.add(graph_f_ghost, moving_const)
            self.play(moving_const.animate.shift(UP * 2 * unit), run_time=1.1)
            self.play(ReplacementTransform(moving_const, graph_const), run_time=0.3)

            self.wait_until_bookmark("variable_formula")
            self.play(
                FadeOut(graph_const),
                FadeOut(graph_f_ghost),
                FadeOut(const_dot_old),
                FadeOut(const_dot_new),
                FadeOut(const_arrow),
                FadeOut(const_label),
                ReplacementTransform(formula_const, formula_variable),
                run_time=0.8,
            )

        # ------------------------------------------------------------------
        # Act 3: scanner sweep for f+g
        # ------------------------------------------------------------------
        scanner = scanner_at(main_axes, -2.0)
        sum_dots = VGroup()

        def show_sum_sample(x, symbol):
            fx = f(x)
            gx = g(x)
            sx = sum_fg(x)

            dot_f = dot_at(main_axes, x, fx, C_F)
            dot_s = dot_at(main_axes, x, sx, C_SUM)
            arrow = v_arrow(main_axes, x, fx, sx, C_SUM)

            sign_text = rf"g({symbol})>0" if gx >= 0 else rf"g({symbol})<0"
            sign_color = C_SUM if gx >= 0 else C_WARN

            label = MathTex(sign_text, color=sign_color).scale(0.72)
            label.next_to(dot_s, RIGHT if gx >= 0 else LEFT, buff=0.12)

            self.play(FadeIn(dot_f), run_time=0.25)
            self.play(Create(arrow), run_time=0.5)
            self.play(FadeIn(dot_s), FadeIn(label), run_time=0.35)
            self.play(FadeOut(dot_f), FadeOut(arrow), FadeOut(label), run_time=0.35)

            return dot_s

        with self.narrated(script[2]):
            self.wait_until_bookmark("scan_start")
            self.play(Create(scanner), run_time=0.6)

            self.wait_until_bookmark("sample_neg")
            dot_s1 = show_sum_sample(-2.0, "a")
            sum_dots.add(dot_s1)

            self.wait_until_bookmark("sample_mid")
            self.play(Transform(scanner, scanner_at(main_axes, 0.4)), run_time=0.6)
            dot_s2 = show_sum_sample(0.4, "b")
            sum_dots.add(dot_s2)

            self.wait_until_bookmark("sample_pos")
            self.play(Transform(scanner, scanner_at(main_axes, 2.0)), run_time=0.6)
            dot_s3 = show_sum_sample(2.0, "c")
            sum_dots.add(dot_s3)

            self.wait_until_bookmark("sum_graph")
            self.play(
                graph_f.animate.set_stroke(color=C_GHOST, opacity=0.35, width=3),
                graph_g.animate.set_stroke(color=C_GHOST, opacity=0.35, width=3),
                run_time=0.45,
            )
            self.play(Create(graph_sum), FadeIn(label_sum), run_time=1.15)

        main_group = VGroup(
            main_axes,
            main_labels,
            graph_f,
            graph_g,
            graph_sum,
            label_f,
            label_g,
            label_sum,
            scanner,
            sum_dots,
            formula_variable,
        )

        # ------------------------------------------------------------------
        # Act 4: split screen for f-g
        # ------------------------------------------------------------------
        left_axes = proportional_axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 5, 1],
            unit_size=0.46,
            font_size=16,
        ).shift(LEFT * 3.45 + DOWN * 0.65)

        right_axes = proportional_axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 5, 1],
            unit_size=0.46,
            font_size=16,
        ).shift(RIGHT * 3.45 + DOWN * 0.65)

        left_title = Text("Graphes de f et g", font_size=26)
        left_title.next_to(left_axes, UP, buff=0.25)

        right_title = Text("Graphe de h = f - g", font_size=26)
        right_title.next_to(right_axes, UP, buff=0.25)

        left_f = left_axes.plot(f, x_range=x_range, color=C_F, stroke_width=4)
        left_g = left_axes.plot(g, x_range=x_range, color=C_G, stroke_width=4)
        right_h = right_axes.plot(diff_fg, x_range=x_range, color=C_DIFF, stroke_width=4)

        left_label_f = MathTex("f", color=C_F).scale(0.7)
        left_label_f.move_to(left_axes.c2p(-2.4, f(-2.4) + 0.35))

        left_label_g = MathTex("g", color=C_G).scale(0.7)
        left_label_g.move_to(left_axes.c2p(2.2, g(2.2) + 0.35))

        right_label_h = MathTex("h=f-g", color=C_DIFF).scale(0.7)
        right_label_h.move_to(right_axes.c2p(1.8, diff_fg(1.8) + 0.45))

        split_formula = MathTex(r"h(x)=f(x)-g(x)").scale(1.0)
        split_formula.next_to(title, DOWN, buff=0.12)
        split_formula.set_color(C_DIFF)

        # Positive difference sample
        x_pos = -2.0
        fp = f(x_pos)
        gp = g(x_pos)
        hp = diff_fg(x_pos)

        scanner_left = scanner_at(left_axes, x_pos, y_min=-2, y_max=5)

        pos_dot_f = dot_at(left_axes, x_pos, fp, C_F)
        pos_dot_g = dot_at(left_axes, x_pos, gp, C_G)
        pos_segment = Line(left_axes.c2p(x_pos, gp), left_axes.c2p(x_pos, fp), color=C_DIFF, stroke_width=5)

        pos_dot_h = dot_at(right_axes, x_pos, hp, C_DIFF)
        pos_segment_h = Line(right_axes.c2p(x_pos, 0), right_axes.c2p(x_pos, hp), color=C_DIFF, stroke_width=5)

        pos_label = MathTex(r"h(a)>0", color=C_DIFF).scale(0.72)
        pos_label.next_to(pos_dot_h, LEFT, buff=0.12)

        # Negative difference sample
        x_neg = 1.2
        fn = f(x_neg)
        gn = g(x_neg)
        hn = diff_fg(x_neg)

        neg_dot_f = dot_at(left_axes, x_neg, fn, C_F)
        neg_dot_g = dot_at(left_axes, x_neg, gn, C_G)
        neg_segment = Line(left_axes.c2p(x_neg, fn), left_axes.c2p(x_neg, gn), color=C_WARN, stroke_width=5)

        neg_dot_h = dot_at(right_axes, x_neg, hn, C_WARN)
        neg_segment_h = Line(right_axes.c2p(x_neg, 0), right_axes.c2p(x_neg, hn), color=C_WARN, stroke_width=5)

        neg_label = MathTex(r"h(b)<0", color=C_WARN).scale(0.72)
        neg_label.next_to(neg_dot_h, RIGHT, buff=0.12)

        with self.narrated(script[3]):
            self.wait_until_bookmark("split_start")
            self.play(FadeOut(main_group), run_time=0.75)
            self.play(
                FadeIn(split_formula),
                Create(left_axes),
                Create(right_axes),
                FadeIn(left_title),
                FadeIn(right_title),
                run_time=0.75,
            )
            self.play(Create(left_f), Create(left_g), FadeIn(left_label_f), FadeIn(left_label_g))

            self.wait_until_bookmark("diff_pos")
            self.play(Create(scanner_left), run_time=0.5)
            self.play(FadeIn(pos_dot_f), FadeIn(pos_dot_g))
            self.play(Create(pos_segment), run_time=0.55)
            self.play(TransformFromCopy(pos_segment, pos_segment_h), run_time=0.65)
            self.play(FadeIn(pos_dot_h), FadeIn(pos_label))

            self.wait_until_bookmark("diff_neg")
            self.play(Transform(scanner_left, scanner_at(left_axes, x_neg, y_min=-2, y_max=5)), run_time=0.55)
            self.play(FadeIn(neg_dot_f), FadeIn(neg_dot_g))
            self.play(Create(neg_segment), run_time=0.55)
            self.play(TransformFromCopy(neg_segment, neg_segment_h), run_time=0.65)
            self.play(FadeIn(neg_dot_h), FadeIn(neg_label))

            self.wait_until_bookmark("diff_graph")
            self.play(Create(right_h), FadeIn(right_label_h), run_time=1.1)

        # ------------------------------------------------------------------
        # Act 5: intersections become zeros of h=f-g
        # ------------------------------------------------------------------
        # f(x)=g(x):
        # 0.45x^2 - 1 = 0.6x - 0.2
        # 0.45x^2 - 0.6x - 0.8 = 0
        A = 0.45
        B = -0.6
        C = -0.8
        delta = B**2 - 4 * A * C
        r1 = (-B - sqrt(delta)) / (2 * A)
        r2 = (-B + sqrt(delta)) / (2 * A)
        roots = [r1, r2]

        left_intersections = VGroup(
            *[dot_at(left_axes, r, f(r), C_WARN) for r in roots]
        )

        right_zeros = VGroup(
            *[dot_at(right_axes, r, 0, C_DIFF) for r in roots]
        )

        left_guides = VGroup(
            *[
                DashedLine(
                    left_axes.c2p(r, f(r)),
                    left_axes.c2p(r, -2),
                    color=C_WARN,
                    stroke_width=3,
                    dash_length=0.10,
                )
                for r in roots
            ]
        )

        right_guides = VGroup(
            *[
                DashedLine(
                    right_axes.c2p(r, 0),
                    right_axes.c2p(r, -2),
                    color=C_DIFF,
                    stroke_width=3,
                    dash_length=0.10,
                )
                for r in roots
            ]
        )

        zero_formula = MathTex(
            r"f(x)=g(x)",
            r"\quad\Longleftrightarrow\quad",
            r"h(x)=f(x)-g(x)=0",
        ).scale(0.88)
        zero_formula.next_to(title, DOWN, buff=0.12)
        zero_formula[0].set_color(C_WARN)
        zero_formula[2].set_color(C_DIFF)

        with self.narrated(script[4]):
            self.wait_until_bookmark("intersections")
            self.play(FadeIn(left_intersections), run_time=0.6)

            self.wait_until_bookmark("equivalence")
            self.play(ReplacementTransform(split_formula, zero_formula))
            self.play(Circumscribe(zero_formula[1], color=C_WARN), run_time=0.8)

            self.wait_until_bookmark("zero_points")
            self.play(Create(left_guides), Create(right_guides), run_time=0.65)
            self.play(FadeIn(right_zeros), run_time=0.6)
            self.play(Circumscribe(right_zeros, color=C_DIFF), run_time=0.8)

        split_group = VGroup(
            left_axes,
            right_axes,
            left_title,
            right_title,
            left_f,
            left_g,
            right_h,
            left_label_f,
            left_label_g,
            right_label_h,
            scanner_left,
            pos_dot_f,
            pos_dot_g,
            pos_segment,
            pos_segment_h,
            pos_dot_h,
            pos_label,
            neg_dot_f,
            neg_dot_g,
            neg_segment,
            neg_segment_h,
            neg_dot_h,
            neg_label,
            left_intersections,
            right_zeros,
            left_guides,
            right_guides,
            zero_formula,
        )

        # ------------------------------------------------------------------
        # Act 6: addition versus composition
        # ------------------------------------------------------------------
        add_title = Text("Addition", font_size=32, color=C_SUM)
        add_formula = MathTex(r"(f+g)(x)=f(x)+g(x)").scale(1.0)
        add_text = Text("on ajoute deux sorties", font_size=27)

        add_box_content = VGroup(add_title, add_formula, add_text).arrange(DOWN, buff=0.25)
        add_box = SurroundingRectangle(add_box_content, color=C_SUM, buff=0.25, stroke_width=3)
        add_group = VGroup(add_box, add_box_content).move_to(LEFT * 3.25 + DOWN * 0.15)

        comp_title = Text("Composition", font_size=32, color=C_G)
        comp_formula = MathTex(r"(f\circ g)(x)=f(g(x))").scale(1.0)
        comp_text = Text("une sortie devient une entrée", font_size=27)

        comp_box_content = VGroup(comp_title, comp_formula, comp_text).arrange(DOWN, buff=0.25)
        comp_box = SurroundingRectangle(comp_box_content, color=C_G, buff=0.25, stroke_width=3)
        comp_group = VGroup(comp_box, comp_box_content).move_to(RIGHT * 3.25 + DOWN * 0.15)

        warning = Text("Même symbole x, mais deux opérations différentes.", font_size=28)
        warning.to_edge(DOWN, buff=0.45)

        with self.narrated(script[5]):
            self.play(FadeOut(split_group), run_time=0.75)

            self.wait_until_bookmark("add_side")
            self.play(FadeIn(add_group), run_time=0.65)

            self.wait_until_bookmark("comp_side")
            self.play(FadeIn(comp_group), run_time=0.65)
            self.play(FadeIn(warning), run_time=0.4)

        self.wait(1.0)
