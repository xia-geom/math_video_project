import os
from contextlib import contextmanager
from dataclasses import dataclass

import numpy as np
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

F_SSML = tts.char("f")
G_SSML = tts.char("g")
X_SSML = tts.X


SCRIPT = {
    "question": (
        "Comment la sortie d'une fonction peut-elle devenir l'entrée d'une autre ?"
    ),
    "first_graph": (
        f"Commençons avec la fonction {F_SSML}. Pour une entrée {X_SSML}, "
        f"on monte jusqu'à son graphe. La hauteur lue est {F_SSML} de {X_SSML}."
    ),
    "second_graph": (
        f"Ajoutons maintenant la fonction {G_SSML}. Son entrée ne sera pas directement "
        f"la valeur de départ. Ce sera la sortie produite par {F_SSML}."
    ),
    "transfer": (
        f"Partons de trois. La fonction {F_SSML} donne quatre. Regardez maintenant : "
        f"la valeur quatre quitte le premier graphe et devient l'entrée de {G_SSML}."
    ),
    "final_reading": (
        f"À partir de cette nouvelle entrée, on lit {G_SSML} de quatre, qui vaut deux. "
        "Une même valeur vient donc de subir deux transformations successives."
    ),
    "movement": (
        "Faisons varier l'entrée avec des valeurs simples. Trois donne quatre puis deux. "
        "Zéro donne un puis un. Enfin, moins un donne zéro puis zéro. "
        "À chaque fois, la sortie du premier graphe devient l'entrée du second."
    ),
    "notation": (
        f"On note cet enchaînement {G_SSML} composée avec {F_SSML}. "
        f"Dans {G_SSML} de {F_SSML} de {X_SSML}, {F_SSML} agit d'abord, "
        "car elle se trouve à l'intérieur."
    ),
    "substitution": (
        f"La formule raconte exactement le même trajet. {F_SSML} de {X_SSML} vaut "
        f"{X_SSML} plus un. Cette sortie remplace toute l'entrée de {G_SSML}. "
        f"Comme {G_SSML} prend une racine carrée, on obtient la racine de {X_SSML} plus un."
    ),
    "domain": (
        "Le dessin révèle aussi une limite. Le second graphe ne commence qu'à zéro, "
        "car une racine carrée réelle n'accepte pas une entrée négative. "
        f"Il faut donc que la sortie {F_SSML} de {X_SSML}, c'est-à-dire {X_SSML} plus un, "
        "soit positive ou nulle."
    ),
    "boundary": (
        f"À la frontière, {X_SSML} vaut moins un. {F_SSML} produit zéro, "
        f"qui est encore une entrée permise pour {G_SSML}."
    ),
    "invalid_example": (
        f"Mais si {X_SSML} vaut moins deux, {F_SSML} produit moins un. "
        f"Le point arrive dans une zone où le graphe de {G_SSML} n'existe pas. "
        "La composition n'est donc pas définie pour cette entrée."
    ),
    "closing": (
        "À retenir : composer, c'est faire circuler une valeur. "
        "La sortie de la première fonction devient l'entrée de la deuxième, "
        "et cette nouvelle entrée doit être permise."
    ),
}


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


def proportional_axes(x_range, y_range, unit_size=0.46, **kwargs):
    """Create axes with the same visual unit on both coordinates."""
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
            "font_size": 20,
            "stroke_width": 2,
        },
        **kwargs,
    )


class CompositionFonctionsFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    def _setup_voiceover(self):
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
        self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text):
        ssml_text = tts.ssml(text)
        if self._voiceover_enabled:
            with self.voiceover(
                text=ssml_text,
                subcaption=tts.strip_ssml(ssml_text),
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_for_narration(self, tracker, animation_time, fallback=0.55):
        if self._voiceover_enabled:
            self.wait(max(tracker.duration - animation_time, 0.2))
        else:
            self.wait(fallback)

    @staticmethod
    def _decimal(value, color, places=1):
        return DecimalNumber(
            value,
            num_decimal_places=places,
            include_sign=False,
            color=color,
        ).scale(0.6)

    @staticmethod
    def _panel(content, color=BLUE_D, buff=0.18):
        background = SurroundingRectangle(
            content,
            color=color,
            buff=buff,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=0.96,
        )
        return VGroup(background, content)

    @staticmethod
    def _value_token(tex, color):
        circle = Circle(radius=0.28, color=color, stroke_width=3)
        circle.set_fill(WHITE, opacity=1)
        value = MathTex(tex, font_size=30, color=color)
        value.move_to(circle)
        return VGroup(circle, value)

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        accent = BLUE_D
        warning = RED_D

        def f(x):
            return x + 1

        def g(t):
            return np.sqrt(t)

        # ------------------------------------------------------------------
        # Act 1 — Central question, then one graph at a time.
        # ------------------------------------------------------------------
        title = Text(
            "Comment une sortie devient-elle une nouvelle entrée ?",
            font_size=42,
        )
        title.scale_to_fit_width(12.2)
        title.to_edge(UP, buff=0.26)

        with self.narrated(SCRIPT["question"]) as tracker:
            self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.9)
            self.wait_for_narration(tracker, 0.9, fallback=1.0)

        common_x_range = [-3, 5, 1]
        common_y_range = [-2, 5, 1]
        unit_size = 0.46

        axes_f = proportional_axes(
            common_x_range,
            common_y_range,
            unit_size=unit_size,
        )
        axes_g = proportional_axes(
            common_x_range,
            common_y_range,
            unit_size=unit_size,
        )
        axes_f.shift(LEFT * 3.55 + DOWN * 0.65)
        axes_g.shift(RIGHT * 3.55 + DOWN * 0.65)

        axes_f_labels = axes_f.get_axis_labels(
            MathTex("x", font_size=25),
            MathTex("f(x)", font_size=25),
        )
        axes_g_labels = axes_g.get_axis_labels(
            MathTex("t", font_size=25),
            MathTex("g(t)", font_size=25),
        )

        f_graph = axes_f.plot(f, x_range=[-3, 4], color=BLACK, stroke_width=4)
        g_graph = axes_g.plot(g, x_range=[0, 5, 0.05], color=BLACK, stroke_width=4)

        f_label = MathTex(r"f(x)=x+1", font_size=29, color=accent)
        g_label = MathTex(r"g(t)=\sqrt{t}", font_size=29, color=accent)
        f_label.next_to(axes_f, UP, buff=0.24)
        g_label.next_to(axes_g, UP, buff=0.24)

        x_tracker = ValueTracker(3.0)

        def x_value():
            return x_tracker.get_value()

        def f_value():
            return f(x_value())

        def g_value():
            return g(f_value())

        left_input_dot = always_redraw(
            lambda: Dot(axes_f.c2p(x_value(), 0), color=accent, radius=0.06)
        )
        left_graph_dot = always_redraw(
            lambda: Dot(
                axes_f.c2p(x_value(), f_value()),
                color=accent,
                radius=0.072,
            )
        )
        left_vertical = always_redraw(
            lambda: DashedLine(
                axes_f.c2p(x_value(), 0),
                axes_f.c2p(x_value(), f_value()),
                color=GRAY,
                dash_length=0.08,
                stroke_width=2,
            )
        )
        left_horizontal = always_redraw(
            lambda: DashedLine(
                axes_f.c2p(0, f_value()),
                axes_f.c2p(x_value(), f_value()),
                color=GRAY,
                dash_length=0.08,
                stroke_width=2,
            )
        )
        x_number = always_redraw(
            lambda: self._decimal(x_value(), accent)
            .next_to(axes_f.c2p(x_value(), 0), DOWN, buff=0.08)
        )
        fx_number_left = always_redraw(
            lambda: self._decimal(f_value(), accent)
            .next_to(axes_f.c2p(0, f_value()), LEFT, buff=0.08)
        )

        with self.narrated(SCRIPT["first_graph"]) as tracker:
            self.play(
                Create(axes_f),
                FadeIn(axes_f_labels),
                FadeIn(f_label),
                run_time=1.2,
            )
            self.play(Create(f_graph), run_time=1.0)
            self.play(FadeIn(left_input_dot), FadeIn(x_number), run_time=0.55)
            self.play(
                Create(left_vertical),
                Create(left_horizontal),
                FadeIn(left_graph_dot),
                FadeIn(fx_number_left),
                run_time=1.35,
            )
            self.wait_for_narration(tracker, 4.1)

        # ------------------------------------------------------------------
        # Act 2 — Add g and physically transport the intermediate value.
        # ------------------------------------------------------------------
        with self.narrated(SCRIPT["second_graph"]) as tracker:
            self.play(
                Create(axes_g),
                FadeIn(axes_g_labels),
                FadeIn(g_label),
                run_time=1.2,
            )
            self.play(Create(g_graph), run_time=1.0)
            self.wait_for_narration(tracker, 2.2)

        transfer_arrow = always_redraw(
            lambda: Arrow(
                axes_f.c2p(0, f_value()),
                axes_g.c2p(f_value(), 0),
                buff=0.12,
                stroke_width=3,
                color=accent,
                max_tip_length_to_length_ratio=0.12,
            )
        )

        transfer_text = Text(
            "la sortie devient l'entrée",
            font_size=21,
            color=accent,
        )
        transfer_text.move_to(UP * 0.05)
        transfer_background = BackgroundRectangle(
            transfer_text,
            color=WHITE,
            fill_opacity=0.96,
            buff=0.08,
        )
        transfer_label = VGroup(transfer_background, transfer_text)

        right_input_dot = always_redraw(
            lambda: Dot(
                axes_g.c2p(f_value(), 0),
                color=accent,
                radius=0.06,
            )
        )
        right_graph_dot = always_redraw(
            lambda: Dot(
                axes_g.c2p(f_value(), g_value()),
                color=accent,
                radius=0.072,
            )
        )
        right_vertical = always_redraw(
            lambda: DashedLine(
                axes_g.c2p(f_value(), 0),
                axes_g.c2p(f_value(), g_value()),
                color=GRAY,
                dash_length=0.08,
                stroke_width=2,
            )
        )
        right_horizontal = always_redraw(
            lambda: DashedLine(
                axes_g.c2p(0, g_value()),
                axes_g.c2p(f_value(), g_value()),
                color=GRAY,
                dash_length=0.08,
                stroke_width=2,
            )
        )
        fx_number_right = always_redraw(
            lambda: self._decimal(f_value(), accent)
            .next_to(axes_g.c2p(f_value(), 0), DOWN, buff=0.08)
        )
        gfx_number = always_redraw(
            lambda: self._decimal(g_value(), accent)
            .next_to(axes_g.c2p(0, g_value()), LEFT, buff=0.08)
        )

        token = self._value_token("4", accent)
        token.move_to(axes_f.c2p(0, 4))
        token_path = ArcBetweenPoints(
            axes_f.c2p(0, 4),
            axes_g.c2p(4, 0),
            angle=-PI / 7,
        )

        with self.narrated(SCRIPT["transfer"]) as tracker:
            self.play(FadeIn(token), run_time=0.45)
            self.wait(0.35)
            self.play(MoveAlongPath(token, token_path), run_time=1.65, rate_func=smooth)
            self.wait(0.5)
            self.play(
                FadeOut(token),
                FadeIn(right_input_dot),
                FadeIn(fx_number_right),
                Create(transfer_arrow),
                FadeIn(transfer_label),
                run_time=0.9,
            )
            self.wait_for_narration(tracker, 3.85)

        with self.narrated(SCRIPT["final_reading"]) as tracker:
            self.play(
                Create(right_vertical),
                run_time=0.75,
            )
            self.wait(0.45)
            self.play(
                Create(right_horizontal),
                FadeIn(right_graph_dot),
                FadeIn(gfx_number),
                run_time=0.95,
            )
            self.wait_for_narration(tracker, 2.15)

        top_chain = always_redraw(
            lambda: VGroup(
                MathTex("x=", font_size=29),
                self._decimal(x_value(), accent),
                MathTex(r"\longrightarrow", font_size=29),
                MathTex("f(x)=", font_size=29),
                self._decimal(f_value(), accent),
                MathTex(r"\longrightarrow", font_size=29),
                MathTex("g(f(x))=", font_size=29),
                self._decimal(g_value(), accent),
            )
            .arrange(RIGHT, buff=0.1)
            .next_to(title, DOWN, buff=0.16)
        )

        with self.narrated(SCRIPT["movement"]) as tracker:
            self.play(FadeIn(top_chain), run_time=0.6)
            self.wait(0.6)
            self.play(x_tracker.animate.set_value(0.0), run_time=1.9)
            self.wait(0.8)
            self.play(x_tracker.animate.set_value(-1.0), run_time=1.9)
            self.wait(1.0)
            self.play(x_tracker.animate.set_value(3.0), run_time=1.9)
            self.wait_for_narration(tracker, 7.2, fallback=0.8)

        notation = MathTex(
            r"(g\circ f)(x)=",
            r"g(",
            r"f(x)",
            r")",
            font_size=39,
            color=accent,
        )
        notation.next_to(title, DOWN, buff=0.16)

        with self.narrated(SCRIPT["notation"]) as tracker:
            self.play(FadeOut(top_chain), Write(notation), run_time=0.9)
            self.play(Circumscribe(notation[2], color=accent), run_time=0.9)
            self.play(Indicate(transfer_arrow, color=accent), run_time=0.9)
            self.wait_for_narration(tracker, 2.7)

        # ------------------------------------------------------------------
        # Act 3 — Keep the graph visible while formalizing the same journey.
        # ------------------------------------------------------------------
        substitution_steps = VGroup(
            MathTex(r"(g\circ f)(x)=g(f(x))", font_size=31),
            MathTex(r"=g(x+1)", font_size=31),
            MathTex(r"=\sqrt{x+1}", font_size=34, color=accent),
        ).arrange(RIGHT, buff=0.38)
        substitution_steps.scale_to_fit_width(10.8)
        substitution_steps.move_to(DOWN * 3.25)
        substitution_panel = self._panel(substitution_steps, color=accent, buff=0.16)

        with self.narrated(SCRIPT["substitution"]) as tracker:
            self.play(FadeIn(substitution_panel[0]), run_time=0.45)
            self.play(Write(substitution_steps[0]), run_time=0.65)
            self.play(Write(substitution_steps[1]), run_time=0.65)
            self.play(Write(substitution_steps[2]), run_time=0.75)
            self.play(Circumscribe(substitution_steps[2], color=accent), run_time=0.8)
            self.wait_for_narration(tracker, 3.3)

        # ------------------------------------------------------------------
        # Act 4 — Discover the domain on the same coordinate picture.
        # ------------------------------------------------------------------
        domain_lines = VGroup(
            MathTex(
                r"g(t)=\sqrt{t}\text{ exige }t\geq0",
                font_size=29,
            ),
            MathTex(
                r"t=f(x)=x+1\quad\Longrightarrow\quad x\geq-1",
                font_size=31,
                color=accent,
            ),
        ).arrange(DOWN, buff=0.14)
        domain_lines.move_to(DOWN * 3.23)
        domain_panel = self._panel(domain_lines, color=accent, buff=0.15)

        with self.narrated(SCRIPT["domain"]) as tracker:
            self.play(ReplacementTransform(substitution_panel, domain_panel), run_time=0.8)
            self.play(Indicate(g_graph, color=accent), run_time=0.9)
            self.play(Circumscribe(domain_lines[1], color=accent), run_time=0.8)
            self.wait_for_narration(tracker, 2.5)

        with self.narrated(SCRIPT["boundary"]) as tracker:
            self.play(x_tracker.animate.set_value(-1.0), run_time=2.0)
            self.play(
                Indicate(right_input_dot, color=accent),
                Indicate(right_graph_dot, color=accent),
                run_time=0.9,
            )
            self.wait_for_narration(tracker, 2.9)

        # Remove only objects that require a nonnegative input before testing x=-2.
        self.play(
            FadeOut(right_graph_dot),
            FadeOut(right_vertical),
            FadeOut(right_horizontal),
            FadeOut(gfx_number),
            run_time=0.55,
        )

        invalid_mark = MathTex(r"\times", font_size=44, color=warning)
        invalid_mark.move_to(axes_g.c2p(-1, 0) + UP * 0.32)
        invalid_note = MathTex(
            r"-1\notin\operatorname{Dom}(g)",
            font_size=28,
            color=warning,
        )
        invalid_note.next_to(invalid_mark, UP, buff=0.14)

        invalid_formula = MathTex(
            r"g(f(-2))\text{ n'est pas défini}",
            font_size=31,
            color=warning,
        )
        invalid_formula.move_to(domain_lines[1])

        with self.narrated(SCRIPT["invalid_example"]) as tracker:
            self.play(x_tracker.animate.set_value(-2.0), run_time=1.8)
            self.wait(0.55)
            self.play(FadeIn(invalid_mark), FadeIn(invalid_note), run_time=0.75)
            self.play(Transform(domain_lines[1], invalid_formula), run_time=0.8)
            self.wait_for_narration(tracker, 3.9)

        self.wait(0.8)

        # ------------------------------------------------------------------
        # Final stable frame: one idea and one condition.
        # ------------------------------------------------------------------
        closing = VGroup(
            Text("À retenir", font_size=38, color=accent),
            MathTex(
                r"x\xrightarrow{\ f\ }f(x)\xrightarrow{\ g\ }g(f(x))",
                font_size=46,
            ),
            Text(
                "La sortie de f devient l'entrée de g.",
                font_size=30,
                color=accent,
            ),
            MathTex(
                r"\text{Condition : }f(x)\in\operatorname{Dom}(g)",
                font_size=34,
            ),
        ).arrange(DOWN, buff=0.36)
        closing.move_to(ORIGIN)

        with self.narrated(SCRIPT["closing"]) as tracker:
            current_objects = list(self.mobjects)
            self.play(*[FadeOut(mob) for mob in current_objects], run_time=0.85)
            self.play(FadeIn(closing), run_time=0.9)
            self.play(Circumscribe(closing[1], color=accent), run_time=0.9)
            self.wait_for_narration(tracker, 1.8, fallback=1.1)

        self.wait(1.2)
