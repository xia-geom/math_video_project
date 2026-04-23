from contextlib import contextmanager
from dataclasses import dataclass
import os

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

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class LegendreTangentIntercept(VoiceoverScene if VoiceoverScene is not None else Scene):
    def _setup_voiceover(self):
        self._voiceover_enabled = False

        if load_dotenv is not None:
            load_dotenv()
            load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)

        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover not installed. Rendering without narration.")
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print(
                "[voiceover] Missing Azure Speech credentials. Set AZURE_SUBSCRIPTION_KEY/AZURE_SERVICE_REGION "
                "or SPEECH_KEY/SPEECH_REGION. Rendering without narration."
            )
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)

        self.set_speech_service(
            AzureService(
                voice=tts.VOICE_ID,
                prosody={"rate": "-10%"},
            )
        )
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, caption: str, ssml: str = None, fallback_duration: float = 2.5):
        if self._voiceover_enabled:
            voice_text = ssml if ssml is not None else caption
            with self.voiceover(text=voice_text, subcaption=caption) as tracker:
                yield tracker
        else:
            try:
                self.add_subcaption(caption, duration=fallback_duration)
            except Exception:
                pass
            yield _NoVoiceTracker(duration=fallback_duration)

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()

        accent = BLUE_D

        def f(x):
            return 0.25 * x**4 + 0.5 * x**2

        def fp(x):
            return x**3 + x

        def b_value(x):
            p = fp(x)
            return f(x) - x * p

        def q_value(x):
            return -b_value(x)

        x0 = ValueTracker(-1.5)

        left_axes = Axes(
            x_range=[-2.4, 2.4, 1],
            y_range=[-5.5, 7, 2],
            x_length=5.7,
            y_length=4.8,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
        )
        right_axes = Axes(
            x_range=[-5.5, 5.5, 2],
            y_range=[-0.5, 5.5, 1],
            x_length=5.7,
            y_length=4.8,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
        )

        axes_group = VGroup(left_axes, right_axes).arrange(RIGHT, buff=0.9).to_edge(DOWN, buff=0.7)

        left_labels = left_axes.get_axis_labels(MathTex("x"), MathTex("y"))
        right_labels = right_axes.get_axis_labels(MathTex("p"), MathTex("q"))

        left_title = Text("Plan (x, y)", font_size=28, color=BLACK).next_to(left_axes, UP, buff=0.12)
        right_title = Text("Plan (p, q)", font_size=28, color=BLACK).next_to(right_axes, UP, buff=0.12)

        graph_f = left_axes.plot(f, x_range=[-2.0, 2.0], color=BLACK, stroke_width=4)

        formula_f = MathTex(r"f(x)=\frac{1}{4}x^4+\frac{1}{2}x^2").scale(0.62).next_to(left_axes, UP, buff=0.52)
        formula_tangent = MathTex(
            r"y=p(x-x_0)+f(x_0)=px+b,\ b=f(x_0)-x_0p"
        ).scale(0.62).next_to(formula_f, DOWN, buff=0.12)
        key_identity = MathTex(r"f^*(p)=x_0p-f(x_0)=-b", color=accent).scale(0.95).to_edge(UP, buff=0.2)

        curve_point = always_redraw(
            lambda: Dot(left_axes.c2p(x0.get_value(), f(x0.get_value())), radius=0.07, color=accent)
        )

        tangent_line = always_redraw(
            lambda: Line(
                left_axes.c2p(
                    max(left_axes.x_range[0], x0.get_value() - 0.9),
                    fp(x0.get_value()) * (max(left_axes.x_range[0], x0.get_value() - 0.9) - x0.get_value())
                    + f(x0.get_value()),
                ),
                left_axes.c2p(
                    min(left_axes.x_range[1], x0.get_value() + 0.9),
                    fp(x0.get_value()) * (min(left_axes.x_range[1], x0.get_value() + 0.9) - x0.get_value())
                    + f(x0.get_value()),
                ),
                color=accent,
                stroke_width=3,
            )
        )

        intercept_dot = always_redraw(
            lambda: Dot(left_axes.c2p(0, b_value(x0.get_value())), radius=0.07, color=accent)
        )

        p_label = always_redraw(
            lambda: MathTex(r"p=f'(x_0)").scale(0.58).next_to(tangent_line, UR, buff=0.08)
        )
        b_label = always_redraw(
            lambda: MathTex("b").scale(0.7).next_to(intercept_dot, LEFT, buff=0.08)
        )

        b_segment = always_redraw(
            lambda: DashedLine(
                left_axes.c2p(0, 0),
                left_axes.c2p(0, b_value(x0.get_value())),
                color=BLACK,
                dash_length=0.08,
                stroke_opacity=0.6,
                stroke_width=2,
            )
        )

        dual_dot = always_redraw(
            lambda: Dot(right_axes.c2p(fp(x0.get_value()), q_value(x0.get_value())), radius=0.07, color=accent)
        )

        q_segment = always_redraw(
            lambda: DashedLine(
                right_axes.c2p(fp(x0.get_value()), 0),
                right_axes.c2p(fp(x0.get_value()), q_value(x0.get_value())),
                color=BLACK,
                dash_length=0.08,
                stroke_opacity=0.6,
                stroke_width=2,
            )
        )

        dual_trace = TracedPath(dual_dot.get_center, stroke_color=accent, stroke_width=4)

        dual_label = always_redraw(
            lambda: MathTex(r"(p,f^*(p))").scale(0.56).next_to(dual_dot, UR, buff=0.07)
        )

        relation_hint = always_redraw(
            lambda: MathTex(r"q=f^*(p)=-b", color=accent).scale(0.7).next_to(right_axes, DOWN, buff=0.22)
        )

        with self.narrated(
            "On considere une fonction convexe f de x. A gauche, son graphe. A droite, le plan p q.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "On considere une fonction convexe f de x. "
                "A gauche, son graphe. "
                "A droite, le plan p q."
                "</lang>"
            ),
            fallback_duration=5.0,
        ) as _:
            self.play(Create(left_axes), Create(right_axes), run_time=1.8)
            self.play(Write(left_labels), Write(right_labels), FadeIn(left_title), FadeIn(right_title), run_time=1.2)
            self.play(Create(graph_f), Write(formula_f), run_time=1.4)

        with self.narrated(
            "Au point x zero, la tangente a pour pente p egale f prime de x zero, "
            "et son ordonnee a l origine vaut b.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "Au point x zéro, la tangente a pour pente "
                "<say-as interpret-as='characters'>p</say-as> "
                "égale f prime de x zéro, "
                "et son ordonnée à l'origine vaut "
                "<say-as interpret-as='characters'>b</say-as>."
                "</lang>"
            ),
            fallback_duration=5.5,
        ) as _:
            self.play(Write(formula_tangent), run_time=1.0)
            self.play(
                Create(tangent_line),
                FadeIn(curve_point),
                Create(b_segment),
                FadeIn(intercept_dot),
                FadeIn(p_label),
                FadeIn(b_label),
                run_time=1.5,
            )
            self.play(Write(key_identity), run_time=1.2)

        with self.narrated(
            "On calcule alors q egal moins b, donc q egal f etoile de p. "
            "Le point p q se deplace dans le plan dual.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "On calcule alors q égal moins b, "
                "donc q égal f étoile de p. "
                "Le point p q se déplace dans le plan dual."
                "</lang>"
            ),
            fallback_duration=5.5,
        ) as _:
            self.play(Create(q_segment), FadeIn(dual_dot), FadeIn(dual_label), FadeIn(relation_hint), run_time=1.2)

        self.add(dual_trace)

        with self.narrated(
            "Quand x zero va de moins un virgule cinq a plus un virgule cinq, "
            "la trace dessine la transformee de Legendre: q egal f etoile de p.",
            ssml=(
                "<lang xml:lang='fr-CA'>"
                "Quand x zéro va de moins un virgule cinq à plus un virgule cinq, "
                "la trace dessine la transformée de Legendre, "
                "q égal f étoile de p."
                "</lang>"
            ),
            fallback_duration=7.5,
        ) as _:
            self.play(x0.animate.set_value(1.5), run_time=7.0, rate_func=linear)

        self.wait(1.6)
