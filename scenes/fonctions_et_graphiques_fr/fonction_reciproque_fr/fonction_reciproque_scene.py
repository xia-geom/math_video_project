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
X_SSML = tts.X
Y_SSML = tts.Y


def proportional_axes(x_range, y_range, unit_size=0.6, **kwargs):
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
            "font_size": 22,
        },
        **kwargs,
    )


SCRIPT = [
    {
        "caption": "Une fonction réciproque défait une fonction.",
        "body": (
            "Dans la vidéo précédente, on a vu qu'une composition signifie : "
            "appliquer une fonction, puis une autre. "
            "Maintenant, on regarde un cas très particulier : "
            "la fonction réciproque."
        ),
    },
    {
        "caption": "f transforme x en f(x).",
        "body": (
            f"La fonction {F_SSML} transforme une valeur de départ {X_SSML} "
            f"en une nouvelle valeur : {F_SSML} de {X_SSML}."
        ),
    },
    {
        "caption": "On choisit une valeur de x.",
        "body": f"Choisissons une valeur de {X_SSML} sur le premier graphique.",
    },
    {
        "caption": "On lit f(x) sur le graphe de f.",
        "body": (
            f"On monte jusqu'au graphe de {F_SSML}. "
            f"La hauteur obtenue est {F_SSML} de {X_SSML}."
        ),
    },
    {
        "caption": "f(x) devient l'entrée de la fonction réciproque.",
        "body": (
            f"Maintenant, cette sortie devient l'entrée de la fonction réciproque. "
            f"On transporte donc {F_SSML} de {X_SSML} "
            "sur l'axe horizontal du deuxième graphique."
        ),
    },
    {
        "caption": "La réciproque renvoie cette valeur vers x.",
        "body": (
            "La fonction réciproque fait le chemin inverse. "
            f"Elle prend {F_SSML} de {X_SSML}, "
            f"et elle redonne la valeur de départ : {X_SSML}."
        ),
    },
    {
        "caption": "Donc f^{-1}(f(x)) = x.",
        "body": (
            f"On écrit donc : {F_SSML} exposant moins un, "
            f"de {F_SSML} de {X_SSML}, égale {X_SSML}. "
            "Cela veut dire : la réciproque défait la fonction."
        ),
    },
    {
        "caption": "Graphiquement, on échange x et y.",
        "body": (
            f"Graphiquement, cela revient à échanger les rôles de {X_SSML} "
            f"et de {Y_SSML}."
        ),
    },
    {
        "caption": "Le graphe de f^{-1} est le miroir du graphe de f.",
        "body": (
            "Le graphe de la fonction réciproque est donc le miroir "
            f"du graphe de {F_SSML}, "
            f"par rapport à la droite {Y_SSML} égale {X_SSML}."
        ),
    },
    {
        "caption": "La sortie de f redevient l'entrée initiale.",
        "body": (
            "L'idée essentielle est simple : "
            f"si {F_SSML} envoie {X_SSML} vers {Y_SSML}, "
            f"alors la réciproque envoie {Y_SSML} vers {X_SSML}."
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class FonctionReciproqueFR(VoiceoverScene if VoiceoverScene is not None else Scene):
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
    def narrated(self, item):
        text = tts.ssml(item["body"])
        if self._voiceover_enabled:
            with self.voiceover(text=text, subcaption=item["caption"]) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_for_narration(self, tracker, animation_time, fallback=0.4):
        if self._voiceover_enabled:
            self.wait(max(tracker.duration - animation_time, 0.2))
        else:
            self.wait(fallback)

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        accent = BLUE_D
        mirror_color = GREEN_D

        def f(x):
            return 0.8 * x + 1.5

        def finv(u):
            return (u - 1.5) / 0.8

        x_tracker = ValueTracker(-2.0)

        def x0():
            return x_tracker.get_value()

        def fx():
            return f(x0())

        title = Text("Fonction réciproque", font_size=44)
        formula = MathTex(r"f^{-1}(f(x))=x", font_size=42)
        header = VGroup(title, formula).arrange(DOWN, buff=0.12)
        header.to_edge(UP, buff=0.25)

        axes_f = proportional_axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 5, 1],
            unit_size=0.55,
        )

        axes_inv = proportional_axes(
            x_range=[-1, 5, 1],
            y_range=[-3, 3, 1],
            unit_size=0.55,
        )

        axes_f.shift(LEFT * 3.45 + DOWN * 1.1)
        axes_inv.shift(RIGHT * 3.45 + DOWN * 1.1)

        axes_f_labels = axes_f.get_axis_labels(MathTex("x"), MathTex("y"))
        axes_inv_labels = axes_inv.get_axis_labels(MathTex("x"), MathTex("y"))

        f_graph = axes_f.plot(f, x_range=[-3, 3], color=BLACK, stroke_width=4)
        inv_graph = axes_inv.plot(finv, x_range=[-1, 5], color=BLACK, stroke_width=4)

        f_title = Text("1) Fonction f", font_size=26).next_to(axes_f, UP, buff=0.38)
        inv_title = Text("2) Réciproque f^-1", font_size=26).next_to(
            axes_inv, UP, buff=0.38
        )

        f_label = axes_f.get_graph_label(
            f_graph,
            label=MathTex(r"y=f(x)", font_size=30),
            x_val=1.8,
            direction=UP,
        )

        inv_label = axes_inv.get_graph_label(
            inv_graph,
            label=MathTex(r"y=f^{-1}(x)", font_size=30),
            x_val=3.7,
            direction=UP,
        )

        left_x_dot = always_redraw(
            lambda: Dot(axes_f.c2p(x0(), 0), color=accent, radius=0.06)
        )
        left_graph_dot = always_redraw(
            lambda: Dot(axes_f.c2p(x0(), fx()), color=accent, radius=0.06)
        )
        left_vline = always_redraw(
            lambda: DashedLine(
                axes_f.c2p(x0(), 0),
                axes_f.c2p(x0(), fx()),
                color=GRAY,
                dash_length=0.08,
            )
        )
        left_hline = always_redraw(
            lambda: DashedLine(
                axes_f.c2p(0, fx()),
                axes_f.c2p(x0(), fx()),
                color=GRAY,
                dash_length=0.08,
            )
        )

        transfer_arrow = always_redraw(
            lambda: Arrow(
                axes_f.c2p(0, fx()),
                axes_inv.c2p(fx(), 0),
                buff=0.08,
                stroke_width=3,
                color=accent,
                max_tip_length_to_length_ratio=0.12,
            )
        )

        right_x_dot = always_redraw(
            lambda: Dot(axes_inv.c2p(fx(), 0), color=accent, radius=0.06)
        )
        right_graph_dot = always_redraw(
            lambda: Dot(axes_inv.c2p(fx(), x0()), color=accent, radius=0.06)
        )
        right_vline = always_redraw(
            lambda: DashedLine(
                axes_inv.c2p(fx(), 0),
                axes_inv.c2p(fx(), x0()),
                color=GRAY,
                dash_length=0.08,
            )
        )
        right_hline = always_redraw(
            lambda: DashedLine(
                axes_inv.c2p(0, x0()),
                axes_inv.c2p(fx(), x0()),
                color=GRAY,
                dash_length=0.08,
            )
        )

        x_label = always_redraw(
            lambda: DecimalNumber(x0(), num_decimal_places=2, color=accent)
            .scale(0.55)
            .next_to(axes_f.c2p(x0(), 0), DOWN, buff=0.1)
        )
        fx_left_label = always_redraw(
            lambda: DecimalNumber(fx(), num_decimal_places=2, color=accent)
            .scale(0.55)
            .next_to(axes_f.c2p(0, fx()), LEFT, buff=0.1)
        )
        fx_right_label = always_redraw(
            lambda: DecimalNumber(fx(), num_decimal_places=2, color=accent)
            .scale(0.55)
            .next_to(axes_inv.c2p(fx(), 0), DOWN, buff=0.1)
        )
        x_return_label = always_redraw(
            lambda: DecimalNumber(x0(), num_decimal_places=2, color=accent)
            .scale(0.55)
            .next_to(axes_inv.c2p(0, x0()), LEFT, buff=0.1)
        )

        chain = always_redraw(
            lambda: VGroup(
                MathTex("x=", font_size=31),
                DecimalNumber(x0(), num_decimal_places=2, color=accent).scale(0.7),
                MathTex(r"\xrightarrow{\ f\ }", font_size=31),
                MathTex("f(x)=", font_size=31),
                DecimalNumber(fx(), num_decimal_places=2, color=accent).scale(0.7),
                MathTex(r"\xrightarrow{\ f^{-1}\ }", font_size=31),
                MathTex("x=", font_size=31),
                DecimalNumber(x0(), num_decimal_places=2, color=accent).scale(0.7),
            )
            .arrange(RIGHT, buff=0.1)
            .next_to(header, DOWN, buff=0.2)
        )

        big_axes = proportional_axes(
            x_range=[-3, 5, 1],
            y_range=[-3, 5, 1],
            unit_size=0.68,
        ).shift(DOWN * 0.35)

        big_labels = big_axes.get_axis_labels(MathTex("x"), MathTex("y"))
        big_labels[1].shift(DOWN * 0.35)
        big_f_graph = big_axes.plot(f, x_range=[-3, 4.3], color=BLACK, stroke_width=4)
        big_inv_graph = big_axes.plot(
            finv, x_range=[-0.9, 5], color=mirror_color, stroke_width=4
        )
        mirror_line = big_axes.plot(
            lambda x: x, x_range=[-3, 5], color=accent, stroke_width=3
        )

        big_f_label = big_axes.get_graph_label(
            big_f_graph,
            label=MathTex(r"y=f(x)", font_size=31),
            x_val=2.0,
            direction=UP,
        )
        big_inv_label = big_axes.get_graph_label(
            big_inv_graph,
            label=MathTex(r"y=f^{-1}(x)", font_size=31),
            x_val=4.0,
            direction=DOWN,
        ).shift(RIGHT * 0.15)

        mirror_label = MathTex("y=x", color=accent, font_size=32)
        mirror_label.next_to(big_axes.c2p(3.7, 3.7), UP, buff=0.1)

        p_dot = Dot(big_axes.c2p(1.0, f(1.0)), color=BLACK, radius=0.065)
        q_dot = Dot(big_axes.c2p(f(1.0), 1.0), color=mirror_color, radius=0.065)
        p_label = MathTex(r"(x,f(x))", font_size=30).next_to(p_dot, LEFT, buff=0.12)
        q_label = MathTex(r"(f(x),x)", font_size=30).next_to(q_dot, RIGHT, buff=0.12)
        reflection_arrow = CurvedArrow(
            big_axes.c2p(1.0, f(1.0)),
            big_axes.c2p(f(1.0), 1.0),
            angle=-TAU / 5,
            color=accent,
            stroke_width=3,
        )

        conclusion = Text(
            "La réciproque échange les rôles de x et y.",
            font_size=30,
            color=accent,
        ).to_edge(DOWN, buff=0.35)

        with self.narrated(SCRIPT[0]) as tracker:
            self.play(FadeIn(header), run_time=1.2)
            self.wait_for_narration(tracker, 1.2)

        with self.narrated(SCRIPT[1]) as tracker:
            self.play(
                Create(axes_f),
                FadeIn(axes_f_labels),
                FadeIn(f_title),
                run_time=1.4,
            )
            self.play(Create(f_graph), FadeIn(f_label), run_time=1.2)
            self.play(
                Create(axes_inv),
                FadeIn(axes_inv_labels),
                FadeIn(inv_title),
                run_time=1.4,
            )
            self.play(Create(inv_graph), FadeIn(inv_label), FadeIn(chain), run_time=1.2)
            self.wait_for_narration(tracker, 5.2)

        with self.narrated(SCRIPT[2]) as tracker:
            self.play(FadeIn(left_x_dot), FadeIn(x_label), run_time=1.0)
            self.wait_for_narration(tracker, 1.0)

        with self.narrated(SCRIPT[3]) as tracker:
            self.play(Create(left_vline), FadeIn(left_graph_dot), run_time=1.3)
            self.play(Create(left_hline), FadeIn(fx_left_label), run_time=1.0)
            self.wait_for_narration(tracker, 2.3)

        with self.narrated(SCRIPT[4]) as tracker:
            self.play(
                Create(transfer_arrow),
                FadeIn(right_x_dot),
                FadeIn(fx_right_label),
                run_time=2.2,
            )
            self.wait_for_narration(tracker, 2.2)

        with self.narrated(SCRIPT[5]) as tracker:
            self.play(Create(right_vline), FadeIn(right_graph_dot), run_time=1.4)
            self.play(Create(right_hline), FadeIn(x_return_label), run_time=1.0)
            self.wait_for_narration(tracker, 2.4)

        with self.narrated(SCRIPT[6]) as tracker:
            self.play(Circumscribe(formula, color=accent), run_time=1.4)
            self.play(Circumscribe(chain, color=accent), run_time=1.4)
            self.wait_for_narration(tracker, 2.8)

        for new_x in [1.4, 2.5]:
            self.play(x_tracker.animate.set_value(new_x), run_time=2.0)
            self.wait(0.3)

        two_axis_group = VGroup(
            axes_f,
            axes_inv,
            axes_f_labels,
            axes_inv_labels,
            f_graph,
            inv_graph,
            f_title,
            inv_title,
            f_label,
            inv_label,
            left_x_dot,
            left_graph_dot,
            left_vline,
            left_hline,
            right_x_dot,
            right_graph_dot,
            right_vline,
            right_hline,
            transfer_arrow,
            x_label,
            fx_left_label,
            fx_right_label,
            x_return_label,
            chain,
        )

        with self.narrated(SCRIPT[7]) as tracker:
            self.play(FadeOut(two_axis_group), run_time=1.0)
            self.play(
                Create(big_axes),
                FadeIn(big_labels),
                Create(big_f_graph),
                FadeIn(big_f_label),
                run_time=2.0,
            )
            self.wait_for_narration(tracker, 3.0)

        with self.narrated(SCRIPT[8]) as tracker:
            self.play(Create(mirror_line), FadeIn(mirror_label), run_time=1.5)
            self.play(Create(big_inv_graph), FadeIn(big_inv_label), run_time=1.6)
            self.play(FadeIn(p_dot), FadeIn(p_label), run_time=0.8)
            self.play(Create(reflection_arrow), run_time=1.1)
            self.play(FadeIn(q_dot), FadeIn(q_label), run_time=0.8)
            self.wait_for_narration(tracker, 5.8)

        with self.narrated(SCRIPT[9]) as tracker:
            self.play(FadeIn(conclusion), run_time=1.0)
            self.wait_for_narration(tracker, 1.0)

        self.wait(1)
