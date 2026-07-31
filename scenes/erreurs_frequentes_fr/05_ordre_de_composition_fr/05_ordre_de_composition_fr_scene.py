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

F_SSML = tts.char("f")
G_SSML = tts.char("g")
X_SSML = tts.X


SCRIPT = {
    "question": (
        f"Erreur fréquente : peut-on changer l'ordre de {F_SSML} et {G_SSML} "
        "dans une composition ? Prenez un instant pour faire une prédiction."
    ),
    "definitions": (
        f"On garde les mêmes fonctions pendant toute la comparaison. "
        f"{F_SSML} de {X_SSML} égale deux {X_SSML} plus un, et "
        f"{G_SSML} de {X_SSML} égale {X_SSML} au carré."
    ),
    "forward": (
        f"Calculons d'abord {G_SSML} composée avec {F_SSML} en deux. "
        f"On applique {F_SSML} : deux devient cinq. Puis on applique {G_SSML} : "
        "cinq devient vingt-cinq."
    ),
    "reverse": (
        f"Inversons maintenant l'ordre. Pour {F_SSML} composée avec {G_SSML}, "
        f"on applique d'abord {G_SSML} : deux devient quatre. Puis {F_SSML} : "
        "quatre devient neuf."
    ),
    "compare_values": (
        "À partir de la même entrée, les résultats sont différents : vingt-cinq n'est pas neuf."
    ),
    "forward_formula": (
        f"Avec les formules, {G_SSML} composée avec {F_SSML} donne deux "
        f"{X_SSML} plus un, le tout au carré."
    ),
    "reverse_formula": (
        f"Mais {F_SSML} composée avec {G_SSML} donne deux {X_SSML} au carré plus un. "
        "Ce ne sont pas les mêmes expressions."
    ),
    "closing": (
        "La composition n'est donc pas commutative en général. Il existe des cas particuliers "
        "où les deux ordres coïncident, mais on doit toujours le vérifier."
    ),
}


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class CompositionNonCommutativeFR(
    VoiceoverScene if VoiceoverScene is not None else Scene
):
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

    def wait_for_narration(self, tracker, animation_time, fallback=0.6):
        if self._voiceover_enabled:
            self.wait(max(tracker.duration - animation_time, 0.2))
        else:
            self.wait(fallback)

    @staticmethod
    def value_node(label, color):
        circle = Circle(radius=0.34, stroke_color=color, stroke_width=3)
        circle.set_fill(WHITE, opacity=1)
        tex = MathTex(label, font_size=32, color=color)
        tex.move_to(circle)
        return VGroup(circle, tex)

    @staticmethod
    def function_box(label, color):
        box = RoundedRectangle(
            width=1.08,
            height=0.68,
            corner_radius=0.12,
            stroke_color=color,
            stroke_width=3,
        )
        box.set_fill(WHITE, opacity=1)
        tex = MathTex(label, font_size=34, color=color)
        tex.move_to(box)
        return VGroup(box, tex)

    @staticmethod
    def arrow_between(left, right, color):
        return Arrow(
            left.get_right(),
            right.get_left(),
            buff=0.1,
            stroke_width=3,
            color=color,
            max_tip_length_to_length_ratio=0.18,
        )

    def machine_lane(self, title_tex, values, functions, color):
        title = MathTex(title_tex, font_size=34, color=color)
        items = VGroup(
            self.value_node(values[0], color),
            self.function_box(functions[0], color),
            self.value_node(values[1], color),
            self.function_box(functions[1], color),
            self.value_node(values[2], color),
        ).arrange(RIGHT, buff=0.38)
        arrows = VGroup(
            *[
                self.arrow_between(items[index], items[index + 1], color)
                for index in range(4)
            ]
        )
        lane = VGroup(title, VGroup(items, arrows)).arrange(DOWN, buff=0.18)
        return lane, items, arrows

    @staticmethod
    def definition_strip(accent):
        definitions = VGroup(
            MathTex(r"f(x)=2x+1", font_size=34),
            MathTex(r"g(x)=x^2", font_size=34),
        ).arrange(RIGHT, buff=0.85)
        frame = SurroundingRectangle(definitions, color=accent, buff=0.18)
        return VGroup(frame, definitions)

    @staticmethod
    def formula_panel(title, lines, color):
        heading = Text(title, font_size=26, color=color)
        formulas = VGroup(
            *[MathTex(line, font_size=32) for line in lines]
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        content = VGroup(heading, formulas).arrange(DOWN, buff=0.25)
        frame = SurroundingRectangle(content, color=color, buff=0.18)
        return VGroup(frame, content)

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        accent = BLUE_D
        reverse_color = GREEN_D
        warning = RED_D

        title = Text("Erreur fréquente : changer l'ordre", font_size=42)
        title.to_edge(UP, buff=0.28)
        question = MathTex(r"g\circ f\stackrel{?}{=}f\circ g", font_size=52)
        question.move_to(UP * 0.6)
        prediction = Text(
            "Même symbole rond : mêmes fonctions, même résultat ?",
            font_size=29,
        ).next_to(question, DOWN, buff=0.45)

        with self.narrated(SCRIPT["question"]) as tracker:
            self.play(FadeIn(title), run_time=0.7)
            self.play(Write(question), FadeIn(prediction), run_time=1.0)
            self.wait_for_narration(tracker, 1.7, fallback=1.8)

        definitions = self.definition_strip(accent)
        definitions.next_to(title, DOWN, buff=0.22)

        with self.narrated(SCRIPT["definitions"]) as tracker:
            self.play(FadeOut(question), FadeOut(prediction), run_time=0.6)
            self.play(FadeIn(definitions), run_time=0.9)
            self.wait_for_narration(tracker, 1.5)

        forward_lane, forward_items, forward_arrows = self.machine_lane(
            r"(g\circ f)(2)\;:\;f\text{ puis }g",
            [r"2", r"5", r"25"],
            [r"f", r"g"],
            accent,
        )
        forward_lane.move_to(DOWN * 0.15)
        forward_calc = MathTex(
            r"f(2)=5\qquad g(5)=25",
            font_size=32,
            color=accent,
        ).next_to(forward_lane, DOWN, buff=0.32)

        with self.narrated(SCRIPT["forward"]) as tracker:
            self.play(FadeIn(forward_lane[0]), FadeIn(forward_items[0]), run_time=0.7)
            self.play(
                FadeIn(forward_items[1]),
                Create(forward_arrows[0]),
                run_time=0.7,
            )
            self.play(
                Create(forward_arrows[1]),
                FadeIn(forward_items[2]),
                run_time=0.7,
            )
            self.play(
                FadeIn(forward_items[3]),
                Create(forward_arrows[2]),
                run_time=0.7,
            )
            self.play(
                Create(forward_arrows[3]),
                FadeIn(forward_items[4]),
                Write(forward_calc),
                run_time=1.1,
            )
            self.wait_for_narration(tracker, 3.9)

        # Keep the first result visible, then add the reversed order underneath.
        self.play(
            forward_lane.animate.scale(0.82).move_to(UP * 0.65),
            forward_calc.animate.scale(0.86).move_to(DOWN * 0.15),
            run_time=0.8,
        )

        reverse_lane, reverse_items, reverse_arrows = self.machine_lane(
            r"(f\circ g)(2)\;:\;g\text{ puis }f",
            [r"2", r"4", r"9"],
            [r"g", r"f"],
            reverse_color,
        )
        reverse_lane.scale(0.82).move_to(DOWN * 1.6)
        reverse_calc = MathTex(
            r"g(2)=4\qquad f(4)=9",
            font_size=28,
            color=reverse_color,
        ).next_to(reverse_lane, DOWN, buff=0.2)

        with self.narrated(SCRIPT["reverse"]) as tracker:
            self.play(FadeIn(reverse_lane[0]), FadeIn(reverse_items[0]), run_time=0.6)
            self.play(
                FadeIn(reverse_items[1]),
                Create(reverse_arrows[0]),
                run_time=0.6,
            )
            self.play(
                Create(reverse_arrows[1]),
                FadeIn(reverse_items[2]),
                run_time=0.6,
            )
            self.play(
                FadeIn(reverse_items[3]),
                Create(reverse_arrows[2]),
                run_time=0.6,
            )
            self.play(
                Create(reverse_arrows[3]),
                FadeIn(reverse_items[4]),
                Write(reverse_calc),
                run_time=1.0,
            )
            self.wait_for_narration(tracker, 3.4)

        value_comparison = MathTex(r"25\neq 9", font_size=48, color=warning)
        value_comparison.to_edge(DOWN, buff=0.25)

        with self.narrated(SCRIPT["compare_values"]) as tracker:
            self.play(Write(value_comparison), run_time=0.8)
            self.play(
                Indicate(forward_items[4], color=warning),
                Indicate(reverse_items[4], color=warning),
                run_time=1.0,
            )
            self.wait_for_narration(tracker, 1.8)

        lanes_group = VGroup(
            forward_lane,
            forward_calc,
            reverse_lane,
            reverse_calc,
            value_comparison,
        )

        # Formula comparison: the definitions remain pinned at the top.
        forward_panel = self.formula_panel(
            "f puis g",
            [
                r"(g\circ f)(x)=g(f(x))",
                r"=g(2x+1)",
                r"=(2x+1)^2",
            ],
            accent,
        )
        reverse_panel = self.formula_panel(
            "g puis f",
            [
                r"(f\circ g)(x)=f(g(x))",
                r"=f(x^2)",
                r"=2x^2+1",
            ],
            reverse_color,
        )
        panels = VGroup(forward_panel, reverse_panel).arrange(RIGHT, buff=0.55)
        if panels.width > 11.5:
            panels.scale_to_fit_width(11.5)
        panels.move_to(DOWN * 0.25)

        with self.narrated(SCRIPT["forward_formula"]) as tracker:
            self.play(FadeOut(lanes_group), run_time=0.7)
            self.play(FadeIn(forward_panel), run_time=1.0)
            self.wait_for_narration(tracker, 1.7)

        with self.narrated(SCRIPT["reverse_formula"]) as tracker:
            self.play(FadeIn(reverse_panel), run_time=1.0)
            self.play(
                Circumscribe(forward_panel, color=accent),
                Circumscribe(reverse_panel, color=reverse_color),
                run_time=1.1,
            )
            self.wait_for_narration(tracker, 2.1)

        conclusion = VGroup(
            MathTex(
                r"g\circ f\neq f\circ g\quad\text{en général}",
                font_size=46,
                color=warning,
            ),
            Text(
                "L'ordre fait partie de l'opération.",
                font_size=31,
                color=warning,
            ),
            Text(
                "Parfois les deux coïncident, mais il faut le vérifier.",
                font_size=26,
            ),
        ).arrange(DOWN, buff=0.35)
        conclusion.move_to(DOWN * 0.25)

        with self.narrated(SCRIPT["closing"]) as tracker:
            self.play(FadeOut(panels), FadeIn(conclusion), run_time=1.0)
            self.play(Circumscribe(conclusion[0], color=warning), run_time=1.1)
            self.wait_for_narration(tracker, 2.1, fallback=1.3)

        self.wait(1.2)
