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
        "caption": "Une racine peut traverser ou toucher l’axe.",
        "ssml": tts.ssml(
            "<bookmark mark='intro_recall'/>"
            "Dans la première vidéo, nous avons vu qu’une racine est une valeur de "
            f"{tts.char('x')} où la hauteur de la fonction vaut zéro. "
            "<break time='250ms'/>"
            "<bookmark mark='intro_question'/>"
            "Mais lorsque la courbe arrive sur l’axe horizontal, deux comportements sont possibles. "
            "Elle peut traverser l’axe, ou simplement le toucher avant de repartir."
        ),
    },
    {
        "caption": "Avec x, le signe change.",
        "ssml": tts.ssml(
            "<bookmark mark='linear_graph'/>"
            "Commençons par la fonction la plus simple : "
            f"{tts.char('f')} de {tts.char('x')} égale {tts.char('x')}. "
            "<bookmark mark='linear_left'/>"
            "À gauche de zéro, la hauteur est négative. "
            "<bookmark mark='linear_zero'/>"
            "À zéro, la hauteur vaut zéro. "
            "<bookmark mark='linear_right'/>"
            "À droite de zéro, la hauteur est positive. "
            "<bookmark mark='linear_conclusion'/>"
            "Le signe passe donc de moins à plus. La courbe doit traverser l’axe."
        ),
    },
    {
        "caption": "Avec x², le signe ne change pas.",
        "ssml": tts.ssml(
            "<bookmark mark='square_graph'/>"
            "Comparons maintenant avec "
            f"{tts.char('g')} de {tts.char('x')} égale {tts.char('x')} au carré. "
            "<bookmark mark='square_left'/>"
            "À gauche de zéro, le carré est positif. "
            "<bookmark mark='square_zero'/>"
            "À zéro, la hauteur vaut zéro. "
            "<bookmark mark='square_right'/>"
            "À droite de zéro, le carré est encore positif. "
            "<bookmark mark='square_conclusion'/>"
            "Le signe ne change pas. La courbe touche l’axe, puis repart du même côté."
        ),
    },
    {
        "caption": "L’exposant compte les facteurs répétés.",
        "ssml": tts.ssml(
            "<bookmark mark='repeat_factor'/>"
            f"{tts.char('x')} au carré signifie {tts.char('x')} multiplié par {tts.char('x')}. "
            "Le même facteur apparaît deux fois. "
            "<bookmark mark='name_multiplicity'/>"
            "On dit alors que zéro est une racine de multiplicité deux, ou une racine double. "
            f"{tts.char('x')} tout seul correspond à une multiplicité un."
        ),
    },
    {
        "caption": "Une racine triple traverse plus doucement.",
        "ssml": tts.ssml(
            "<bookmark mark='cube_graph'/>"
            "Regardons maintenant "
            f"{tts.char('h')} de {tts.char('x')} égale {tts.char('x')} au cube. "
            "<bookmark mark='cube_signs'/>"
            "À gauche, le résultat est négatif. À droite, il est positif. "
            "Le signe change encore, donc la courbe traverse l’axe. "
            "<bookmark mark='cube_flat'/>"
            "Mais près de la racine, elle reste plus longtemps près de l’axe. "
            "Elle paraît plus plate que la droite."
        ),
    },
    {
        "caption": "Remplacer x par x−2 déplace la racine.",
        "ssml": tts.ssml(
            "<bookmark mark='shift_start'/>"
            "Jusqu’ici, la racine était toujours zéro. "
            "<bookmark mark='shift_formula'/>"
            f"Remplaçons maintenant {tts.char('x')} par {tts.char('x')} moins deux. "
            "<bookmark mark='shift_graph'/>"
            "La courbe se déplace vers la droite. "
            "<bookmark mark='shift_root'/>"
            "La racine passe de zéro à deux, mais le comportement ne change pas. "
            "Comme l’exposant vaut deux, la courbe touche encore l’axe."
        ),
    },
    {
        "caption": "Un polynôme peut avoir plusieurs comportements.",
        "ssml": tts.ssml(
            "<bookmark mark='product_intro'/>"
            "Appliquons maintenant cette idée à un polynôme plus complet. "
            "<bookmark mark='simple_root'/>"
            f"Le facteur {tts.char('x')} plus deux apparaît une seule fois. "
            "Près de moins deux, le signe change : la courbe traverse l’axe. "
            "<bookmark mark='double_root'/>"
            f"Le facteur {tts.char('x')} moins un apparaît deux fois. "
            "Près de un, le signe reste positif des deux côtés. La courbe touche l’axe et repart."
        ),
    },
    {
        "caption": "Impair traverse, pair touche.",
        "ssml": tts.ssml(
            "<bookmark mark='general_form'/>"
            "Nous pouvons maintenant formuler la règle générale. "
            "<bookmark mark='odd_rule'/>"
            "Si la multiplicité est impaire, le signe change et la courbe traverse l’axe. "
            "<bookmark mark='even_rule'/>"
            "Si la multiplicité est paire, le signe ne change pas et la courbe touche l’axe. "
            "<bookmark mark='flat_rule'/>"
            "Et lorsque la multiplicité augmente, la courbe devient plus plate près de la racine. "
            "<bookmark mark='final_warning'/>"
            "Attention : une racine double reste une seule valeur de "
            f"{tts.char('x')}. Elle n’est pas constituée de deux racines différentes."
        ),
    },
]


def proportional_axes(x_range, y_range, unit_size=0.8, font_size=22):
    """Create axes where one x-unit equals one y-unit on screen."""
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


def sign_row(left_sign, right_sign, root_tex="0", font_size=30):
    label = Text("signe de la fonction", font_size=font_size)
    row = VGroup(
        MathTex(left_sign).scale(0.9),
        MathTex(r"\longrightarrow").scale(0.8),
        MathTex(root_tex).scale(0.9),
        MathTex(r"\longrightarrow").scale(0.8),
        MathTex(right_sign).scale(0.9),
    ).arrange(RIGHT, buff=0.22)
    return VGroup(label, row).arrange(DOWN, buff=0.16)


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class MultipliciteRacinesFR(VoiceoverScene if VoiceoverScene is not None else Scene):
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
    def narrated(self, item):
        if self._voiceover_enabled:
            with self.voiceover(text=item["ssml"], subcaption=item["caption"]) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_until_bookmark(self, mark):
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        accent = BLUE_D
        muted = GRAY
        pale = GRAY_B

        title = Text("Pourquoi une racine traverse ou touche l’axe ?", font_size=39)
        if title.width > config.frame_width - 0.8:
            title.scale_to_fit_width(config.frame_width - 0.8)
        title.to_edge(UP, buff=0.30)

        # ------------------------------------------------------------------
        # Introduction: name the two possible behaviours before formalising.
        # ------------------------------------------------------------------
        recall_formula = MathTex(
            r"x=a\text{ est une racine}",
            r"\quad\Longleftrightarrow\quad",
            r"f(a)=0",
        ).scale(1.02)
        recall_formula[0].set_color(accent)
        recall_formula[2].set_color(accent)
        recall_formula.move_to(UP * 0.3)

        question = Text("Que fait la courbe lorsqu’elle arrive sur l’axe ?", font_size=32)
        question.next_to(recall_formula, DOWN, buff=0.55)
        alternatives = VGroup(
            Text("traverser", font_size=34, color=accent),
            Text("ou", font_size=29),
            Text("toucher", font_size=34, color=accent),
        ).arrange(RIGHT, buff=0.5)
        alternatives.next_to(question, DOWN, buff=0.42)

        with self.narrated(SCRIPT[0]):
            self.wait_until_bookmark("intro_recall")
            self.play(FadeIn(title), Write(recall_formula), run_time=0.8)
            self.wait_until_bookmark("intro_question")
            self.play(FadeIn(question), FadeIn(alternatives), run_time=0.7)

        self.play(FadeOut(recall_formula), FadeOut(question), FadeOut(alternatives), run_time=0.6)

        # ------------------------------------------------------------------
        # Shared coordinate system: y=x demonstrates a sign change.
        # ------------------------------------------------------------------
        axes = proportional_axes(
            x_range=[-2, 2, 1],
            y_range=[-2, 3, 1],
            unit_size=0.88,
            font_size=22,
        ).shift(DOWN * 0.35)
        axis_labels = axes.get_axis_labels(MathTex("x"), MathTex("y"))
        formula_position = title.get_bottom() + DOWN * 0.35

        formula_x = MathTex(r"f(x)=x").scale(1.05).move_to(formula_position)
        graph_x = axes.plot(lambda x: x, x_range=[-1.8, 1.8], color=BLACK, stroke_width=4)
        tracker_x = ValueTracker(-1)
        moving_dot_x = always_redraw(
            lambda: Dot(axes.c2p(tracker_x.get_value(), tracker_x.get_value()), color=accent, radius=0.075)
        )
        scanner_x = always_redraw(
            lambda: DashedLine(
                axes.c2p(tracker_x.get_value(), -2),
                axes.c2p(tracker_x.get_value(), 3),
                color=muted,
                stroke_width=2.5,
                dash_length=0.1,
            )
        )

        def linear_height():
            x_value = tracker_x.get_value()
            if abs(x_value) < 0.025:
                return Dot(axes.c2p(x_value, 0), color=accent, radius=0.075)
            return Line(axes.c2p(x_value, 0), axes.c2p(x_value, x_value), color=accent, stroke_width=5)

        height_x = always_redraw(linear_height)
        value_left_x = MathTex(r"f(-1)=-1<0").scale(0.85).to_edge(DOWN, buff=0.42)
        value_zero_x = MathTex(r"f(0)=0", color=accent).scale(0.9).to_edge(DOWN, buff=0.42)
        value_right_x = MathTex(r"f(1)=1>0").scale(0.85).to_edge(DOWN, buff=0.42)
        signs_x = sign_row("-", "+").to_edge(DOWN, buff=0.25)
        cross_conclusion = Text("Le signe change : la courbe traverse l’axe.", font_size=30, color=accent)
        cross_conclusion.next_to(signs_x, UP, buff=0.24)
        root_dot_0 = Dot(axes.c2p(0, 0), color=accent, radius=0.085)

        with self.narrated(SCRIPT[1]):
            self.wait_until_bookmark("linear_graph")
            self.play(Create(axes), FadeIn(axis_labels), FadeIn(formula_x), run_time=0.8)
            self.play(Create(graph_x), run_time=0.9)
            self.play(Create(scanner_x), FadeIn(moving_dot_x), Create(height_x), run_time=0.55)
            self.wait_until_bookmark("linear_left")
            self.play(FadeIn(value_left_x), run_time=0.45)
            self.wait_until_bookmark("linear_zero")
            self.play(tracker_x.animate.set_value(0), FadeOut(value_left_x), FadeIn(value_zero_x), run_time=1.15)
            self.play(FadeIn(root_dot_0), run_time=0.3)
            self.wait_until_bookmark("linear_right")
            self.play(tracker_x.animate.set_value(1), FadeOut(value_zero_x), FadeIn(value_right_x), run_time=1.15)
            self.wait_until_bookmark("linear_conclusion")
            self.play(FadeOut(value_right_x), FadeIn(signs_x), run_time=0.5)
            self.play(FadeIn(cross_conclusion), Circumscribe(root_dot_0, color=accent), run_time=0.7)

        self.play(
            FadeOut(moving_dot_x), FadeOut(scanner_x), FadeOut(height_x),
            FadeOut(signs_x), FadeOut(cross_conclusion), run_time=0.55,
        )

        # ------------------------------------------------------------------
        # Same axes, y=x²: the sign stays positive on both sides.
        # ------------------------------------------------------------------
        formula_x2 = MathTex(r"g(x)=x^2").scale(1.05).move_to(formula_position)
        graph_x2 = axes.plot(lambda x: x**2, x_range=[-1.7, 1.7], color=BLACK, stroke_width=4)
        tracker_x2 = ValueTracker(-1)
        moving_dot_x2 = always_redraw(
            lambda: Dot(
                axes.c2p(tracker_x2.get_value(), tracker_x2.get_value() ** 2),
                color=accent,
                radius=0.075,
            )
        )
        scanner_x2 = always_redraw(
            lambda: DashedLine(
                axes.c2p(tracker_x2.get_value(), -2),
                axes.c2p(tracker_x2.get_value(), 3),
                color=muted,
                stroke_width=2.5,
                dash_length=0.1,
            )
        )

        def square_height():
            x_value = tracker_x2.get_value()
            y_value = x_value**2
            if y_value < 0.025:
                return Dot(axes.c2p(x_value, 0), color=accent, radius=0.075)
            return Line(axes.c2p(x_value, 0), axes.c2p(x_value, y_value), color=accent, stroke_width=5)

        height_x2 = always_redraw(square_height)
        value_left_x2 = MathTex(r"g(-1)=1>0").scale(0.85).to_edge(DOWN, buff=0.42)
        value_zero_x2 = MathTex(r"g(0)=0", color=accent).scale(0.9).to_edge(DOWN, buff=0.42)
        value_right_x2 = MathTex(r"g(1)=1>0").scale(0.85).to_edge(DOWN, buff=0.42)
        signs_x2 = sign_row("+", "+").to_edge(DOWN, buff=0.25)
        touch_conclusion = Text("Le signe ne change pas : la courbe touche l’axe.", font_size=29, color=accent)
        touch_conclusion.next_to(signs_x2, UP, buff=0.24)

        with self.narrated(SCRIPT[2]):
            self.wait_until_bookmark("square_graph")
            self.play(FadeOut(formula_x), ReplacementTransform(graph_x, graph_x2), run_time=0.5)
            self.play(FadeIn(formula_x2), run_time=0.5)
            self.play(FadeIn(scanner_x2), FadeIn(moving_dot_x2), FadeIn(height_x2), run_time=0.5)
            self.wait_until_bookmark("square_left")
            self.play(FadeIn(value_left_x2), run_time=0.4)
            self.wait_until_bookmark("square_zero")
            self.play(tracker_x2.animate.set_value(0), FadeOut(value_left_x2), FadeIn(value_zero_x2), run_time=1.15)
            self.wait_until_bookmark("square_right")
            self.play(tracker_x2.animate.set_value(1), FadeOut(value_zero_x2), FadeIn(value_right_x2), run_time=1.15)
            self.wait_until_bookmark("square_conclusion")
            self.play(FadeOut(value_right_x2), FadeIn(signs_x2), run_time=0.5)
            self.play(FadeIn(touch_conclusion), Circumscribe(root_dot_0, color=accent), run_time=0.7)

        self.play(
            FadeOut(moving_dot_x2), FadeOut(scanner_x2), FadeOut(height_x2),
            FadeOut(signs_x2), FadeOut(touch_conclusion), run_time=0.55,
        )

        # ------------------------------------------------------------------
        # Multiplicity is a count of repeated factors.
        # ------------------------------------------------------------------
        expanded_square = MathTex(r"x^2", r"=", r"x", r"\cdot", r"x").scale(1.2)
        expanded_square.move_to(DOWN * 0.3)
        expanded_square[0].set_color(accent)
        expanded_square[2].set_color(accent)
        expanded_square[4].set_color(accent)
        factor_brace = Brace(VGroup(expanded_square[2], expanded_square[3], expanded_square[4]), DOWN, color=accent)
        twice_label = Text("le même facteur, deux fois", font_size=28, color=accent)
        twice_label.next_to(factor_brace, DOWN, buff=0.16)
        multiplicity_label = VGroup(Text("multiplicité", font_size=30), MathTex("2", color=accent).scale(1.25)).arrange(RIGHT, buff=0.18)
        multiplicity_label.next_to(twice_label, DOWN, buff=0.32)
        simple_formula = MathTex(r"x=x^1", r"\qquad", r"\text{multiplicité }1").scale(0.95)
        simple_formula.to_edge(DOWN, buff=0.4)
        simple_formula[0].set_color(accent)

        with self.narrated(SCRIPT[3]):
            self.wait_until_bookmark("repeat_factor")
            self.play(FadeOut(VGroup(axes, axis_labels, graph_x2, formula_x2, root_dot_0)), run_time=0.65)
            self.play(Write(expanded_square), run_time=0.8)
            self.play(Create(factor_brace), FadeIn(twice_label), run_time=0.65)
            self.wait_until_bookmark("name_multiplicity")
            self.play(FadeIn(multiplicity_label), FadeIn(simple_formula), run_time=0.55)
            self.play(Circumscribe(multiplicity_label, color=accent), run_time=0.75)

        self.play(
            FadeOut(expanded_square), FadeOut(factor_brace), FadeOut(twice_label),
            FadeOut(multiplicity_label), FadeOut(simple_formula), run_time=0.6,
        )

        # ------------------------------------------------------------------
        # y=x³ still crosses, but its graph is flatter around the root.
        # ------------------------------------------------------------------
        axes3 = proportional_axes(
            x_range=[-2, 2, 1],
            y_range=[-2, 3, 1],
            unit_size=0.88,
            font_size=22,
        ).shift(DOWN * 0.35)
        labels3 = axes3.get_axis_labels(MathTex("x"), MathTex("y"))
        formula_x3 = MathTex(r"h(x)=x^3").scale(1.05).move_to(formula_position)
        graph_x3 = axes3.plot(lambda x: x**3, x_range=[-1.4, 1.4], color=accent, stroke_width=4)
        ghost_line = axes3.plot(lambda x: x, x_range=[-1.4, 1.4], color=pale, stroke_width=3)
        ghost_label = MathTex(r"y=x", color=pale).scale(0.72).move_to(axes3.c2p(1.32, 1.55))
        cube_label = MathTex(r"y=x^3", color=accent).scale(0.72).move_to(axes3.c2p(1.27, 2.2))
        cube_signs = sign_row("-", "+").to_edge(DOWN, buff=0.25)
        root_dot_3 = Dot(axes3.c2p(0, 0), color=accent, radius=0.085)
        neighborhood = VGroup(
            DashedLine(axes3.c2p(-0.65, -2), axes3.c2p(-0.65, 3), color=muted, stroke_width=2),
            DashedLine(axes3.c2p(0.65, -2), axes3.c2p(0.65, 3), color=muted, stroke_width=2),
        )
        flatter_text = Text("x³ reste plus près de l’axe que x.", font_size=29, color=accent)
        flatter_text.to_edge(DOWN, buff=0.35)

        with self.narrated(SCRIPT[4]):
            self.wait_until_bookmark("cube_graph")
            self.play(Create(axes3), FadeIn(labels3), FadeIn(formula_x3), run_time=0.75)
            self.play(Create(graph_x3), FadeIn(root_dot_3), run_time=0.9)
            self.wait_until_bookmark("cube_signs")
            self.play(FadeIn(cube_signs), Circumscribe(root_dot_3, color=accent), run_time=0.7)
            self.wait_until_bookmark("cube_flat")
            self.play(FadeOut(cube_signs), Create(ghost_line), FadeIn(ghost_label), FadeIn(cube_label), run_time=0.75)
            self.play(Create(neighborhood), FadeIn(flatter_text), run_time=0.6)

        self.play(
            FadeOut(VGroup(
                axes3, labels3, formula_x3, graph_x3, root_dot_3, ghost_line,
                ghost_label, cube_label, neighborhood, flatter_text,
            )),
            run_time=0.7,
        )

        # ------------------------------------------------------------------
        # Shifting a repeated factor changes its root, not its parity.
        # ------------------------------------------------------------------
        shift_axes = proportional_axes(
            x_range=[-1, 5, 1],
            y_range=[-1, 4, 1],
            unit_size=0.78,
            font_size=21,
        ).shift(DOWN * 0.4)
        shift_labels = shift_axes.get_axis_labels(MathTex("x"), MathTex("y"))
        base_formula = MathTex(r"y=x^2").scale(1.05).move_to(formula_position)
        shifted_formula = MathTex(r"y=(x-2)^2").scale(1.05).move_to(formula_position)
        shifted_formula.set_color_by_tex("x-2", accent)
        base_graph = shift_axes.plot(lambda x: x**2, x_range=[-1, 2], color=BLACK, stroke_width=4)
        shifted_graph = shift_axes.plot(lambda x: (x - 2) ** 2, x_range=[0, 4], color=BLACK, stroke_width=4)
        root_zero = Dot(shift_axes.c2p(0, 0), color=accent, radius=0.085)
        root_zero_label = MathTex(r"x=0", color=accent).scale(0.75).next_to(root_zero, DOWN, buff=0.16)
        root_two = Dot(shift_axes.c2p(2, 0), color=accent, radius=0.085)
        root_two_label = MathTex(r"x=2", color=accent).scale(0.75).next_to(root_two, DOWN, buff=0.16)
        horizontal_arrow = Arrow(
            shift_axes.c2p(0, 0.55), shift_axes.c2p(2, 0.55), color=accent, stroke_width=4, buff=0.08
        )
        shift_label = MathTex(r"+2", color=accent).scale(0.8).next_to(horizontal_arrow, UP, buff=0.1)
        same_behavior = Text("La racine bouge, mais la courbe touche toujours.", font_size=29, color=accent)
        same_behavior.to_edge(DOWN, buff=0.38)

        with self.narrated(SCRIPT[5]):
            self.wait_until_bookmark("shift_start")
            self.play(Create(shift_axes), FadeIn(shift_labels), FadeIn(base_formula), run_time=0.75)
            self.play(Create(base_graph), FadeIn(root_zero), FadeIn(root_zero_label), run_time=0.8)
            self.wait_until_bookmark("shift_formula")
            self.play(ReplacementTransform(base_formula, shifted_formula), Create(horizontal_arrow), FadeIn(shift_label), run_time=0.75)
            self.wait_until_bookmark("shift_graph")
            self.play(
                Transform(base_graph, shifted_graph), Transform(root_zero, root_two),
                ReplacementTransform(root_zero_label, root_two_label), run_time=1.3,
            )
            self.wait_until_bookmark("shift_root")
            self.play(FadeIn(same_behavior), Circumscribe(root_zero, color=accent), run_time=0.75)

        self.play(
            FadeOut(VGroup(
                shift_axes, shift_labels, shifted_formula, base_graph, root_zero,
                root_two_label, horizontal_arrow, shift_label, same_behavior,
            )),
            run_time=0.7,
        )

        # ------------------------------------------------------------------
        # A single polynomial can combine a simple root and a double root.
        # ------------------------------------------------------------------
        product_axes = proportional_axes(
            x_range=[-3, 3, 1],
            y_range=[-5, 4, 1],
            unit_size=0.62,
            font_size=19,
        ).shift(DOWN * 0.45)
        product_labels = product_axes.get_axis_labels(MathTex("x"), MathTex("y"))
        product_labels[1].next_to(product_axes.y_axis.get_end(), RIGHT, buff=0.22).shift(DOWN * 0.55)

        def polynomial(x):
            return 0.5 * (x + 2) * (x - 1) ** 2

        product_graph = product_axes.plot(polynomial, x_range=[-2.75, 2.35], color=BLACK, stroke_width=4)
        product_formula = MathTex(r"p(x)=", r"\frac12", r"(x+2)", r"(x-1)^2").scale(0.96)
        product_formula.move_to(formula_position)
        root_minus_two = Dot(product_axes.c2p(-2, 0), color=accent, radius=0.085)
        root_one = Dot(product_axes.c2p(1, 0), color=accent, radius=0.085)
        root_minus_label = MathTex(r"x=-2", color=accent).scale(0.72).next_to(root_minus_two, DOWN, buff=0.16)
        root_one_label = MathTex(r"x=1", color=accent).scale(0.72).next_to(root_one, DOWN, buff=0.16)
        simple_signs = VGroup(
            Text("près de −2 :", font_size=27),
            MathTex(r"-\quad\longrightarrow\quad0\quad\longrightarrow\quad+"),
        ).arrange(RIGHT, buff=0.3).to_edge(DOWN, buff=0.4)
        simple_conclusion = Text("multiplicité 1 : la courbe traverse", font_size=28, color=accent)
        simple_conclusion.next_to(simple_signs, UP, buff=0.2)
        double_signs = VGroup(
            Text("près de 1 :", font_size=27),
            MathTex(r"+\quad\longrightarrow\quad0\quad\longrightarrow\quad+"),
        ).arrange(RIGHT, buff=0.3).to_edge(DOWN, buff=0.4)
        double_conclusion = Text("multiplicité 2 : la courbe touche", font_size=28, color=accent)
        double_conclusion.next_to(double_signs, UP, buff=0.2)
        simple_scanner = DashedLine(
            product_axes.c2p(-2, -5), product_axes.c2p(-2, 4), color=muted, stroke_width=2.5, dash_length=0.1
        )
        double_scanner = DashedLine(
            product_axes.c2p(1, -5), product_axes.c2p(1, 4), color=muted, stroke_width=2.5, dash_length=0.1
        )

        with self.narrated(SCRIPT[6]):
            self.wait_until_bookmark("product_intro")
            self.play(Create(product_axes), FadeIn(product_labels), FadeIn(product_formula), run_time=0.75)
            self.play(Create(product_graph), run_time=1.1)
            self.play(
                FadeIn(root_minus_two), FadeIn(root_one), FadeIn(root_minus_label), FadeIn(root_one_label), run_time=0.55
            )
            self.wait_until_bookmark("simple_root")
            self.play(product_formula[2].animate.set_color(accent), Create(simple_scanner), run_time=0.55)
            self.play(FadeIn(simple_signs), FadeIn(simple_conclusion), Circumscribe(root_minus_two, color=accent), run_time=0.7)
            self.wait_until_bookmark("double_root")
            self.play(
                product_formula[2].animate.set_color(BLACK), product_formula[3].animate.set_color(accent),
                ReplacementTransform(simple_scanner, double_scanner), FadeOut(simple_signs), FadeOut(simple_conclusion), run_time=0.65,
            )
            self.play(FadeIn(double_signs), FadeIn(double_conclusion), Circumscribe(root_one, color=accent), run_time=0.7)

        self.play(
            FadeOut(VGroup(
                product_axes, product_labels, product_graph, product_formula, root_minus_two,
                root_one, root_minus_label, root_one_label, double_scanner, double_signs, double_conclusion,
            )),
            run_time=0.7,
        )

        # ------------------------------------------------------------------
        # Final rule and the common misconception about a double root.
        # ------------------------------------------------------------------
        general_formula = MathTex(r"(x-a)^m", color=accent).scale(1.5).move_to(UP * 0.55)
        exponent_brace = Brace(general_formula, UP, color=accent)
        exponent_label = Text("m = multiplicité", font_size=30, color=accent)
        exponent_label.next_to(exponent_brace, UP, buff=0.15)
        odd_rule = VGroup(
            MathTex(r"m=1,3,5,\ldots").scale(1.0),
            Text("multiplicité impaire : la courbe traverse", font_size=30),
        ).arrange(DOWN, buff=0.16).move_to(DOWN * 0.45)
        even_rule = VGroup(
            MathTex(r"m=2,4,6,\ldots").scale(1.0),
            Text("multiplicité paire : la courbe touche", font_size=30),
        ).arrange(DOWN, buff=0.16).move_to(DOWN * 1.65)
        odd_box = SurroundingRectangle(odd_rule, color=accent, stroke_width=3, buff=0.2)
        even_box = SurroundingRectangle(even_rule, color=accent, stroke_width=3, buff=0.2)
        flatter_rule = Text("Une multiplicité plus grande rend la courbe plus plate.", font_size=28)
        flatter_rule.to_edge(DOWN, buff=0.28)
        warning = VGroup(
            Text("Attention", font_size=30, color=accent),
            MathTex(r"(x-1)^2\quad\Rightarrow\quad\text{une seule racine : }x=1").scale(0.88),
        ).arrange(DOWN, buff=0.18)
        warning_box = SurroundingRectangle(warning, color=accent, stroke_width=3, buff=0.25)
        warning_group = VGroup(warning_box, warning).move_to(DOWN * 0.45)

        with self.narrated(SCRIPT[7]):
            self.wait_until_bookmark("general_form")
            self.play(FadeIn(general_formula), Create(exponent_brace), FadeIn(exponent_label), run_time=0.75)
            self.wait_until_bookmark("odd_rule")
            self.play(FadeIn(odd_box), FadeIn(odd_rule), run_time=0.65)
            self.wait_until_bookmark("even_rule")
            self.play(FadeIn(even_box), FadeIn(even_rule), run_time=0.65)
            self.wait_until_bookmark("flat_rule")
            self.play(FadeIn(flatter_rule), run_time=0.55)
            self.wait_until_bookmark("final_warning")
            self.play(
                FadeOut(odd_box), FadeOut(odd_rule), FadeOut(even_box), FadeOut(even_rule),
                FadeOut(flatter_rule), FadeOut(general_formula), FadeOut(exponent_brace), FadeOut(exponent_label),
                run_time=0.65,
            )
            self.play(FadeIn(warning_group), Circumscribe(warning, color=accent), run_time=0.8)

        self.wait(1.0)
