# variables_et_polynomes_scene.py  (simplified / more elementary)

from manim import *
import os
import numpy as np
from contextlib import contextmanager
from dataclasses import dataclass

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


# ──────────────────────────────────────────────────────────────────────
# Visual defaults
# ──────────────────────────────────────────────────────────────────────
config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D


# ──────────────────────────────────────────────────────────────────────
# Constants (single source of truth)
# ──────────────────────────────────────────────────────────────────────
EXPR_A = 2
EXPR_B = 1
EVAL_POINTS = [(0, EXPR_A * 0 + EXPR_B), (1, EXPR_A * 1 + EXPR_B), (2, EXPR_A * 2 + EXPR_B)]

POLY_A, POLY_B, POLY_C = 1, 2, 3


def POLY_FUNC(x: float) -> float:
    return POLY_A * x**2 + POLY_B * x + POLY_C


POLY_LABEL_TEX = rf"P(x) = {'' if POLY_A == 1 else POLY_A}x^2 + {POLY_B}x + {POLY_C}"


# ──────────────────────────────────────────────────────────────────────
# Voice helpers + scripts (put in the front)
# ──────────────────────────────────────────────────────────────────────
from tools.tts import VOICE_CONFIGS, VOICE_ID, VOICE_RATE, ssml, X, P

# Centralized captions + SSML (easy to edit)
SCRIPTS = {
    "1A": ("x peut changer.", ssml(f"Une variable comme {X} peut prendre différentes valeurs. {X} peut changer.")),
    "1B": ("On fixe les constantes.", ssml(f"Dans une formule, on choisit ce qui reste fixe. Ici, {EXPR_A} et {EXPR_B} sont fixés.")),
    "1C": ("Variable = quantité qui change.", ssml(f"Si {EXPR_A} et {EXPR_B} sont fixés, alors {X} est la variable : c'est ce qui peut changer.")),
    "2A": (
        "Changer x change le résultat.",
        ssml(
            f"Regardons {EXPR_A} {X} plus {EXPR_B}. "
            + " ".join([f"Si {X} vaut {xv}, le résultat est {yv}." for xv, yv in EVAL_POINTS])
        ),
    ),
    "2B": (f"{EXPR_A} et {EXPR_B} sont fixes.", ssml(f"Le {EXPR_A} et le {EXPR_B} sont des constantes : leurs valeurs ne changent pas.")),
    "3A": ("Un polynôme est une somme.", ssml("Un polynôme se construit en additionnant des termes : une constante, puis un terme en x.")),
    "3B": ("On ajoute x², x³, ...", ssml(f"On peut ajouter {X} au carré, puis {X} au cube, et ainsi de suite.")),
    "3C": ("Forme générale : somme de monômes.", ssml(f"On note {P} de {X}. C'est a zéro, plus a un x, plus a deux x carré, jusqu'à a n x puissance n.")),
    "3D": ("Les coefficients sont constants.", ssml("a zéro, a un, a deux, etc. sont des constantes : on les fixe.")),
    "3E": ("x reste la variable.", ssml(f"Mais {X} reste la variable : {X} peut changer.")),
    "4":  ("P(x) décrit une courbe.", ssml(f"Sur un graphique, un polynôme {P} de {X} décrit une courbe. Chaque valeur de {X} donne un point.")),
}


# ──────────────────────────────────────────────────────────────────────
# Minimal voiceover glue
# ──────────────────────────────────────────────────────────────────────
@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class VariablesEtPolynomes(VoiceoverScene if VoiceoverScene is not None else Scene):
    def _setup_voiceover(self):
        self._voiceover_enabled = False

        if load_dotenv is not None:
            load_dotenv()
            load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)

        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover missing — silent render.")
            return

        key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not key or not region:
            print("[voiceover] Missing Azure credentials — silent render.")
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", key)
        os.environ.setdefault("AZURE_SERVICE_REGION", region)
        os.environ.setdefault("SPEECH_KEY", key)
        os.environ.setdefault("SPEECH_REGION", region)

        print(f"[voiceover] voice={VOICE_ID} rate={VOICE_RATE}")
        self.set_speech_service(AzureService(voice=VOICE_ID))
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, caption: str, ssml: str):
        if self._voiceover_enabled:
            with self.voiceover(text=ssml, subcaption=caption) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def _caption_box(self, text: str) -> VGroup:
        cap = Text(text, font_size=30, color=BLACK)
        if cap.width > config.frame_width - 1.0:
            cap.scale_to_fit_width(config.frame_width - 1.0)

        panel = RoundedRectangle(
            corner_radius=0.08,
            width=cap.width + 0.45,
            height=cap.height + 0.28,
            stroke_color=GRAY_B,
            stroke_width=1,
        ).set_fill(WHITE, opacity=0.96)

        cap.move_to(panel)
        return VGroup(panel, cap).to_edge(DOWN, buff=0.18)

    def _wait_voice_end(self, tracker, start_time: float, pad: float = 0.05):
        if not self._voiceover_enabled:
            return
        remaining = float(getattr(tracker, "duration", 0.0)) - (self.time - start_time)
        if remaining > 0:
            self.wait(remaining + pad)

    @contextmanager
    def beat(self, key: str):
        caption, ssml = SCRIPTS[key]
        box = self._caption_box(caption)
        self.play(FadeIn(box), run_time=0.2)

        with self.narrated(caption, ssml) as tr:
            t0 = self.time
            yield tr, t0
            self._wait_voice_end(tr, t0)

        self.play(FadeOut(box), run_time=0.2)

    # ──────────────────────────────────────────────────────────────────
    # Scene
    # ──────────────────────────────────────────────────────────────────
    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        accent = ACCENT

        # ACT 1: x as something that moves
        x_sym = MathTex("x", font_size=110).move_to(UP * 1.8)
        x_box = SurroundingRectangle(x_sym, color=BLACK, buff=0.3, stroke_width=2.5)
        var_tag = Text("variable", font_size=28, color=GRAY_D).next_to(x_box, UP, buff=0.15)

        nl = NumberLine(x_range=[-3, 3, 1], length=8.5, color=BLACK, include_numbers=True, font_size=24).shift(DOWN * 0.3)
        x_tracker = ValueTracker(-3.0)
        dot = Dot(nl.n2p(-3.0), color=accent, radius=0.14)
        dot.add_updater(lambda d: d.move_to(nl.n2p(x_tracker.get_value())))
        x_label = always_redraw(lambda: MathTex(rf"x = {x_tracker.get_value():.0f}", font_size=40, color=accent).next_to(nl, UP, buff=0.55))

        with self.beat("1A"):
            self.play(Write(x_sym), Create(x_box), FadeIn(var_tag), run_time=1.2)
            self.play(Create(nl), FadeIn(dot), FadeIn(x_label), run_time=1.0)
            self.play(x_tracker.animate.set_value(3), run_time=2.0, rate_func=smooth)
            self.play(x_tracker.animate.set_value(-1), run_time=1.6, rate_func=smooth)

        expr = MathTex(str(EXPR_A), "x", "+", str(EXPR_B), font_size=72).move_to(DOWN * 1.7)
        const_box = SurroundingRectangle(VGroup(expr[0], expr[3]), color=BLACK, buff=0.12, stroke_width=2.3)
        const_lbl = Text("constantes", font_size=28, color=BLACK).next_to(const_box, DOWN, buff=0.15)
        var_box = SurroundingRectangle(expr[1], color=accent, buff=0.12, stroke_width=2.5)

        with self.beat("1B"):
            self.play(FadeIn(expr, shift=UP * 0.1), run_time=0.6)
            self.play(Create(const_box), FadeIn(const_lbl), run_time=0.8)

        with self.beat("1C"):
            self.play(Create(var_box), run_time=0.7)

        dot.clear_updaters()
        x_label.clear_updaters()
        self.play(FadeOut(VGroup(x_sym, x_box, var_tag, nl, dot, x_label, expr, const_box, const_lbl, var_box)), run_time=0.8)

        # ACT 2: input -> output
        expr2 = MathTex(str(EXPR_A), "x", "+", str(EXPR_B), font_size=76).move_to(UP * 2.2)
        nl2 = NumberLine(
        x_range=[0, len(EVAL_POINTS), 1],
        length=5,
        color=BLACK,
        include_numbers=True,
        font_size=24,
        decimal_number_config={"color": BLACK},
        ).move_to(UP * 0.5 + LEFT * 1.5)
        x_t2 = ValueTracker(0.0)
        dot2 = Dot(nl2.n2p(0.0), color=accent, radius=0.13)
        dot2.add_updater(lambda d: d.move_to(nl2.n2p(x_t2.get_value())))
        rows = VGroup()

        with self.beat("2A"):
            self.play(Write(expr2), run_time=0.9)
            self.play(Create(nl2), FadeIn(dot2), run_time=0.8)
            for xv, yv in EVAL_POINTS:
                self.play(x_t2.animate.set_value(xv), run_time=0.7, rate_func=smooth)
                row = MathTex(rf"x = {xv} \Rightarrow {EXPR_A}x+{EXPR_B} = {yv}", font_size=38).move_to(DOWN * 0.5 + DOWN * xv * 0.7)
                self.play(FadeIn(row, shift=RIGHT * 0.1), run_time=3.0)
                rows.add(row)

        box_a = SurroundingRectangle(expr2[0], color=accent, buff=0.1, stroke_width=2)
        box_b = SurroundingRectangle(expr2[3], color=accent, buff=0.1, stroke_width=2)

        with self.beat("2B"):
            self.play(Create(box_a), Create(box_b), run_time=0.7)

        dot2.clear_updaters()
        self.play(FadeOut(VGroup(expr2, nl2, dot2, rows, box_a, box_b)), run_time=0.8)

        # ACT 3: polynomial idea
        p0 = MathTex(str(POLY_C), font_size=64).move_to(UP * 2.0)

        with self.beat("3A"):
            self.play(Write(p0), run_time=0.6)
            p1 = MathTex(str(POLY_C), "+", f"{POLY_B}x", font_size=64).move_to(UP * 2.0)
            p1[2].set_color(accent)
            self.play(TransformMatchingTex(p0, p1), run_time=0.9)

        with self.beat("3B"):
            p2 = MathTex(str(POLY_C), "+", f"{POLY_B}x", "+", "x^2", font_size=64).move_to(UP * 2.0)
            p2[4].set_color(accent)
            self.play(TransformMatchingTex(p1, p2), run_time=0.9)

        general = MathTex(
            r"P(x) = ", r"a_0", r" + ", r"a_1", r"x + ",
            r"a_2", r"x^2 + \cdots + ", r"a_n", r"x^n",
            font_size=44,
        ).move_to(DOWN * 0.1)

        with self.beat("3C"):
            self.play(p2.animate.shift(UP * 0.5).scale(0.78), run_time=0.6)
            self.play(Write(general), run_time=1.6)

        coeff_parts = VGroup(general[1], general[3], general[5], general[7])
        coeff_box = SurroundingRectangle(coeff_parts, color=accent, buff=0.12, stroke_width=2)

        with self.beat("3D"):
            self.play(coeff_parts.animate.set_color(accent), Create(coeff_box), run_time=0.8)

        x_parts = VGroup(general[4], general[6], general[8])

        with self.beat("3E"):
            self.play(FadeOut(coeff_box), coeff_parts.animate.set_color(BLACK), x_parts.animate.set_color(accent), run_time=0.8)

        self.play(FadeOut(VGroup(p2, general)), run_time=0.8)

        # ACT 4: graph
        axes = Axes(
            x_range=[-3.5, 2.5, 1], y_range=[0, 14, 2],
            x_length=7.5, y_length=4.8, tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
            x_axis_config={"include_numbers": True, "numbers_to_include": np.arange(-3, 3, 1), "font_size": 22},
            y_axis_config={"include_numbers": True, "numbers_to_include": np.arange(0, 15, 2), "font_size": 22},
        ).shift(DOWN * 0.6)

        ax_labels = axes.get_axis_labels(MathTex("x"), MathTex("P(x)"))
        curve = axes.plot(POLY_FUNC, x_range=[-3.2, 2.2], color=BLACK, stroke_width=3)
        curve_label = MathTex(POLY_LABEL_TEX, font_size=32).next_to(axes, UP, buff=0.25)

        x_t3 = ValueTracker(-3.2)
        moving_dot = Dot(axes.c2p(-3.2, POLY_FUNC(-3.2)), color=accent, radius=0.11)
        moving_dot.add_updater(lambda d: d.move_to(axes.c2p(x_t3.get_value(), POLY_FUNC(x_t3.get_value()))))

        with self.beat("4"):
            self.play(Create(axes), Write(ax_labels), run_time=1.2)
            self.play(Create(curve), FadeIn(curve_label), run_time=1.5)
            self.play(FadeIn(moving_dot), run_time=0.3)
            self.play(x_t3.animate.set_value(2.2), run_time=3.0, rate_func=linear)

        moving_dot.clear_updaters()
        self.play(FadeOut(VGroup(axes, ax_labels, curve, curve_label, moving_dot)), run_time=0.8)

        # END
        summ1 = Text("Variable : ce qui change (les autres termes sont fixés).", font_size=34).shift(UP * 0.55)
        summ2 = Text("Polynôme : somme de puissances de x.", font_size=36).shift(DOWN * 0.55)
        self.play(FadeIn(summ1), FadeIn(summ2), run_time=1.0)
        self.wait(2.0)
        self.play(FadeOut(VGroup(summ1, summ2)), run_time=0.8)
