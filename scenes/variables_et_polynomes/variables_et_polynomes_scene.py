"""
variables_et_polynomes_scene.py
================================
SINGLE SOURCE OF TRUTH
  All values that appear both on screen AND in narration are defined
  as module-level constants below.  The SSML strings are built from
  those constants with f-strings so they CANNOT drift from the visuals.

VOICE SELECTION
  Set env var  MANIM_VOICE=fr-CA-SylvieNeural  (or any of the four)
  before rendering.  Default: fr-CA-SylvieNeural.

CONSISTENCY RULE
  If you change a constant, run:
      python tools/ssml_sync_check.py variables_et_polynomes/variables_et_polynomes_scene.py
  before re-rendering.
"""

from manim import *
import numpy as np
import os
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

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D

# ══════════════════════════════════════════════════════════════════════
#  SINGLE SOURCE OF TRUTH — edit only here; SSML is derived below
# ══════════════════════════════════════════════════════════════════════

# Act 2: expression  EXPR_A * x + EXPR_B
EXPR_A: int = 2        # coefficient displayed, narrated, and computed
EXPR_B: int = 1        # constant displayed, narrated, and computed
# x values shown on the slider + their computed outputs
EVAL_POINTS: list[tuple[int, int]] = [
    (0, EXPR_A * 0 + EXPR_B),   # (0, 1)
    (1, EXPR_A * 1 + EXPR_B),   # (1, 3)
    (2, EXPR_A * 2 + EXPR_B),   # (2, 5)
]

# Act 3: polynomial curve  P(x) = POLY_A*x^2 + POLY_B*x + POLY_C
POLY_A: int = 1
POLY_B: int = 2
POLY_C: int = 3


def POLY_FUNC(x: float) -> float:
    """Curve function — single definition used by both plot and label."""
    return POLY_A * x**2 + POLY_B * x + POLY_C


# LaTeX label derived from the coefficients (no manual transcription)
POLY_LABEL_TEX: str = (
    rf"P(x) = {f'{POLY_A}' if POLY_A != 1 else ''}x^2"
    rf" + {POLY_B}x + {POLY_C}"
)

from tools.tts import VOICE_CONFIGS, VOICE_ID, VOICE_RATE, ssml, char, X, P

# ── French number words (used to keep SSML and visuals in sync) ───────
_FR_NUM: dict[int, str] = {
    0: "zéro", 1: "un", 2: "deux", 3: "trois",
    4: "quatre", 5: "cinq", 6: "six", 7: "sept",
    8: "huit", 9: "neuf", 10: "dix",
}


def _fr(n: int) -> str:
    """Return the Québec French word for integer n."""
    return _FR_NUM.get(n, str(n))


# ══════════════════════════════════════════════════════════════════════
#  DERIVED SSML STRINGS  (generated from constants — do NOT edit manually)
# ══════════════════════════════════════════════════════════════════════

SSML_1A = ssml(
    f"Une variable comme {X} peut prendre différentes valeurs."
    "<break time='120ms'/>"
    f"Elle peut changer."
)

SSML_1B = ssml(
    "Dans une formule, on choisit d'abord ce qui reste fixe."
    "<break time='140ms'/>"
    f"Ici, {_fr(EXPR_A)} et {_fr(EXPR_B)} sont tenus constants."
)

SSML_1C = ssml(
    "La variable, c'est la quantité qu'on autorise à changer."
    "<break time='130ms'/>"
    f"Donc, si {_fr(EXPR_A)} et {_fr(EXPR_B)} sont fixés, {X} est la variable."
)

# Beat 2a: built from EXPR_A, EXPR_B, and EVAL_POINTS
_eval_lines = "".join(
    f"si {X} vaut {_fr(xv)}, le résultat est {_fr(yv)}."
    "<break time='100ms'/>"
    for xv, yv in EVAL_POINTS
)
SSML_2A = ssml(
    f"Dans l'expression {_fr(EXPR_A)} {X} plus {_fr(EXPR_B)},"
    "<break time='120ms'/>"
    + _eval_lines
    + f"Changer {X} change le résultat."
)

# Beat 2b: built from EXPR_A, EXPR_B
SSML_2B = ssml(
    f"Le {_fr(EXPR_A)} et le {_fr(EXPR_B)}, eux, sont des constantes."
    "<break time='120ms'/>"
    "Leurs valeurs ne changent jamais."
)

SSML_3A = ssml(
    "Un polynôme se construit en additionnant des termes."
    "<break time='130ms'/>"
    "On commence par une constante,"
    "<break time='100ms'/>"
    f"puis on ajoute {_fr(EXPR_A)} {X}."
)

SSML_3B = ssml(
    f"On peut continuer avec {X} au carré,"
    "<break time='100ms'/>"
    f"{X} au cube,"
    "<break time='100ms'/>"
    "et ainsi de suite."
)

SSML_3C = ssml(
    f"La forme générale d'un polynôme est : {char('P')} de {X}, "
    "égal à a zéro,"
    "<break time='130ms'/>"
    f"plus a un {X},"
    "<break time='130ms'/>"
    f"plus a deux {X} au carré,"
    "<break time='130ms'/>"
    f"jusqu'à a n {X} puissance n."
)

SSML_3D = ssml(
    "Les coefficients a zéro, a un, a deux..."
    "<break time='140ms'/>"
    "sont des constantes."
    "<break time='120ms'/>"
    "Leurs valeurs restent fixées."
)

SSML_3E = ssml(
    f"Mais {X}, lui, reste la variable."
    "<break time='130ms'/>"
    f"C'est lui qui peut changer."
)

# Beat 4: POLY_LABEL_TEX is already derived from constants
SSML_4 = ssml(
    "Sur un graphique, un polynôme décrit une courbe."
    "<break time='130ms'/>"
    f"Chaque valeur de {X} donne un point sur cette courbe."
)


# ══════════════════════════════════════════════════════════════════════
#  VOICEOVER BOILERPLATE
# ══════════════════════════════════════════════════════════════════════

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
            print("[voiceover] manim-voiceover not installed — silent render.")
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print("[voiceover] Missing Azure credentials — silent render.")
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)

        print(f"[voiceover] Using voice: {VOICE_ID}  rate: {VOICE_RATE}")
        self.set_speech_service(AzureService(voice=VOICE_ID))
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, caption: str, ssml: str = None):
        if self._voiceover_enabled:
            with self.voiceover(text=ssml or caption, subcaption=caption) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    # ── caption helpers ───────────────────────────────────────────────

    def _subtitle_box(self, text: str) -> VGroup:
        cap = Text(text, color=BLACK, font_size=30)
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

    def _show_caption(self, text: str) -> VGroup:
        box = self._subtitle_box(text)
        self.play(FadeIn(box), run_time=0.2)
        return box

    def _hide_caption(self, box: VGroup) -> None:
        self.play(FadeOut(box), run_time=0.2)

    def _wait_for_voice_end(self, tracker, start_time: float, pad: float = 0.05) -> None:
        """Wait the remaining narration time so audio never overlaps next beat."""
        if not self._voiceover_enabled:
            return
        remaining = float(getattr(tracker, "duration", 0.0)) - (self.time - start_time)
        if remaining > 0:
            self.wait(remaining + pad)

    # ══════════════════════════════════════════════════════════════════
    #  SCENE
    # ══════════════════════════════════════════════════════════════════

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_voiceover()
        accent = ACCENT

        # ==============================================================
        # ACT 1 — Variable as a movable condition
        # ==============================================================

        x_sym = MathTex("x", font_size=110).move_to(UP * 1.8)
        x_box = SurroundingRectangle(x_sym, color=BLACK, buff=0.3, stroke_width=2.5)
        var_tag = Text("variable", font_size=28, color=GRAY_D).next_to(x_box, UP, buff=0.15)

        nl = NumberLine(
            x_range=[-3, 3, 1], length=8.5, color=BLACK,
            include_numbers=True, font_size=24,
        ).shift(DOWN * 0.3)

        x_tracker = ValueTracker(-3.0)
        slider_dot = Dot(nl.n2p(-3.0), color=accent, radius=0.14)
        slider_dot.add_updater(lambda d: d.move_to(nl.n2p(x_tracker.get_value())))

        x_val_label = always_redraw(
            lambda: MathTex(
                rf"x = {x_tracker.get_value():.0f}", font_size=40, color=accent,
            ).next_to(nl, UP, buff=0.55)
        )

        with self.narrated("x peut changer.", ssml=SSML_1A) as tr:
            t0 = self.time
            cap1 = self._show_caption("x peut changer.")
            self.play(Write(x_sym), Create(x_box), FadeIn(var_tag), run_time=1.6)
            self.wait(0.8)
            self.play(Create(nl), FadeIn(slider_dot), run_time=1.2)
            self.play(FadeIn(x_val_label), run_time=0.4)
            self.play(x_tracker.animate.set_value(3),  run_time=2.5, rate_func=smooth)
            self.play(x_tracker.animate.set_value(-1), run_time=2.0, rate_func=smooth)
            self.play(x_tracker.animate.set_value(2),  run_time=1.5, rate_func=smooth)
            self.wait(0.8)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap1)

        rel_expr = MathTex(str(EXPR_A), "x", "+", str(EXPR_B), font_size=72).move_to(DOWN * 1.7)
        rel_const_box = SurroundingRectangle(
            VGroup(rel_expr[0], rel_expr[3]), color=BLACK, buff=0.12, stroke_width=2.3
        )
        rel_const_lbl = Text("constantes fixées", font_size=28, color=BLACK).next_to(
            rel_const_box, DOWN, buff=0.15
        )
        rel_var_box = SurroundingRectangle(rel_expr[1], color=accent, buff=0.12, stroke_width=2.5)
        rel_var_lbl = Text("variable", font_size=28, color=accent).next_to(rel_var_box, UP, buff=0.16)

        with self.narrated("On fixe certaines quantités.", ssml=SSML_1B) as tr:
            t0 = self.time
            cap2 = self._show_caption("On fixe les constantes dans la formule.")
            self.play(FadeIn(rel_expr, shift=UP * 0.1), run_time=0.8)
            self.play(Create(rel_const_box), FadeIn(rel_const_lbl), run_time=0.9)
            self.wait(0.9)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap2)

        key_line = Text(
            "Variable = quantité qui peut changer\nsi les autres termes sont fixés.",
            font_size=34,
            line_spacing=0.9,
        ).move_to(DOWN * 1.7)
        key_rect = SurroundingRectangle(key_line, color=accent, buff=0.2, stroke_width=2.5)

        with self.narrated("La variable est la quantité qui change.", ssml=SSML_1C) as tr:
            t0 = self.time
            cap3 = self._show_caption("Variable = quantité qui change.")
            self.play(Create(rel_var_box), FadeIn(rel_var_lbl), run_time=0.8)
            self.wait(0.4)
            self.play(
                FadeTransform(
                    VGroup(rel_expr, rel_const_box, rel_const_lbl, rel_var_box, rel_var_lbl),
                    key_line,
                ),
                run_time=1.0,
            )
            self.play(Create(key_rect), run_time=0.7)
            self.wait(0.8)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap3)

        slider_dot.clear_updaters()
        x_val_label.clear_updaters()
        self.play(
            FadeOut(VGroup(x_sym, x_box, var_tag, nl, slider_dot,
                           x_val_label, key_line, key_rect)),
            run_time=1.0,
        )

        # ==============================================================
        # ACT 2 — Expression: input → output
        # ==============================================================
        # MathTex built from the same EXPR_A / EXPR_B constants
        expr = MathTex(
            str(EXPR_A), "x", "+", str(EXPR_B), font_size=76,
        ).move_to(UP * 2.2)

        nl2 = NumberLine(
            x_range=[0, len(EVAL_POINTS), 1], length=5, color=BLACK,
            include_numbers=True, font_size=24,
        ).move_to(UP * 0.5 + LEFT * 1.5)

        x_t2 = ValueTracker(0.0)
        dot2 = Dot(nl2.n2p(0.0), color=accent, radius=0.13)
        dot2.add_updater(lambda d: d.move_to(nl2.n2p(x_t2.get_value())))

        rows = VGroup()

        with self.narrated("Changer x change le résultat.", ssml=SSML_2A) as tr:
            t0 = self.time
            cap4 = self._show_caption("Changer x change le résultat.")
            self.play(Write(expr), run_time=1.4)
            self.wait(0.6)
            self.play(Create(nl2), FadeIn(dot2), run_time=1.0)

            for xv, yv in EVAL_POINTS:
                self.play(x_t2.animate.set_value(xv), run_time=0.8, rate_func=smooth)
                # MathTex uses the same computed values — cannot drift from SSML
                row = MathTex(
                    rf"x = {xv} \;\Rightarrow\; {EXPR_A}x+{EXPR_B} = {yv}",
                    font_size=38,
                ).move_to(DOWN * 0.5 + DOWN * xv * 0.7)
                self.play(FadeIn(row, shift=RIGHT * 0.1), run_time=0.6)
                rows.add(row)
                self.wait(0.5)

            self.wait(0.8)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap4)

        box_a = SurroundingRectangle(expr[0], color=accent, buff=0.1, stroke_width=2)
        box_b = SurroundingRectangle(expr[3], color=accent, buff=0.1, stroke_width=2)
        const_lbl = Text("constantes", font_size=26, color=accent).next_to(
            VGroup(box_a, box_b), UP, buff=0.18
        )

        with self.narrated("2 et 1 sont fixes.", ssml=SSML_2B) as tr:
            t0 = self.time
            cap5 = self._show_caption(f"{EXPR_A} et {EXPR_B} sont fixes.")
            self.play(Create(box_a), Create(box_b), FadeIn(const_lbl), run_time=0.9)
            self.wait(2.0)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap5)

        dot2.clear_updaters()
        self.play(
            FadeOut(VGroup(expr, nl2, dot2, rows, box_a, box_b, const_lbl)),
            run_time=1.0,
        )

        # ==============================================================
        # ACT 3 — Polynôme
        # ==============================================================
        p0 = MathTex("3", font_size=64).move_to(UP * 2.0)

        with self.narrated("On additionne des termes.", ssml=SSML_3A) as tr:
            t0 = self.time
            cap6 = self._show_caption("On additionne des termes.")
            self.play(Write(p0), run_time=0.9)
            self.wait(1.0)
            p1 = MathTex("3", "+", f"{EXPR_A}x", font_size=64).move_to(UP * 2.0)
            p1[2].set_color(accent)
            self.play(TransformMatchingTex(p0, p1), run_time=1.1)
            self.wait(0.7)
            self.play(p1[2].animate.set_color(BLACK), run_time=0.4)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap6)

        with self.narrated("x, x², x³…", ssml=SSML_3B) as tr:
            t0 = self.time
            cap7 = self._show_caption("x, x², x³…")
            p2 = MathTex("3", "+", f"{EXPR_A}x", "+", "x^2", font_size=64).move_to(UP * 2.0)
            p2[4].set_color(accent)
            self.play(TransformMatchingTex(p1, p2), run_time=1.1)
            self.wait(1.0)
            self.play(p2[4].animate.set_color(BLACK), run_time=0.4)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap7)

        general = MathTex(
            r"P(x) = ", r"a_0", r" + ", r"a_1", r"x + ",
            r"a_2", r"x^2 + \cdots + ", r"a_n", r"x^n",
            font_size=44,
        ).move_to(DOWN * 0.1)

        with self.narrated("Un polynôme = somme de monômes.", ssml=SSML_3C) as tr:
            t0 = self.time
            cap8 = self._show_caption("Un polynôme = somme de monômes.")
            self.play(p2.animate.shift(UP * 0.5).scale(0.78), run_time=0.7)
            self.play(Write(general), run_time=2.2)
            self.wait(1.8)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap8)

        coeff_parts = VGroup(general[1], general[3], general[5], general[7])
        coeff_box = SurroundingRectangle(coeff_parts, color=accent, buff=0.12, stroke_width=2)
        coeff_lbl = Text("coefficients constants", font_size=26, color=accent).next_to(
            coeff_box, DOWN, buff=0.22
        )

        with self.narrated("Les coefficients sont constants.", ssml=SSML_3D) as tr:
            t0 = self.time
            cap9 = self._show_caption("Les coefficients sont constants.")
            self.play(coeff_parts.animate.set_color(accent), Create(coeff_box), run_time=0.9)
            self.play(FadeIn(coeff_lbl), run_time=0.6)
            self.wait(1.8)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap9)

        x_parts = VGroup(general[4], general[6], general[8])

        with self.narrated("x reste la variable.", ssml=SSML_3E) as tr:
            t0 = self.time
            cap10 = self._show_caption("x reste la variable.")
            self.play(
                FadeOut(coeff_box), FadeOut(coeff_lbl),
                coeff_parts.animate.set_color(BLACK),
                x_parts.animate.set_color(accent),
                run_time=0.9,
            )
            self.wait(1.8)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap10)

        self.play(FadeOut(VGroup(p2, general)), run_time=1.0)

        # ==============================================================
        # ACT 4 — Graph
        # ==============================================================
        axes = Axes(
            x_range=[-3.5, 2.5, 1], y_range=[0, 14, 2],
            x_length=7.5, y_length=4.8, tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
            x_axis_config={
                "include_numbers": True,
                "numbers_to_include": np.arange(-3, 3, 1),
                "font_size": 22,
                "decimal_number_config": {"num_decimal_places": 0},
            },
            y_axis_config={
                "include_numbers": True,
                "numbers_to_include": np.arange(0, 15, 2),
                "font_size": 22,
                "decimal_number_config": {"num_decimal_places": 0},
            },
        ).shift(DOWN * 0.6)

        ax_labels = axes.get_axis_labels(MathTex("x"), MathTex("P(x)"))

        curve = axes.plot(POLY_FUNC, x_range=[-3.2, 2.2], color=BLACK, stroke_width=3)
        # Label derived from POLY_LABEL_TEX — same constants, cannot drift
        curve_label = MathTex(POLY_LABEL_TEX, font_size=32).next_to(axes, UP, buff=0.25)

        x_t3 = ValueTracker(-3.2)
        moving_dot = Dot(axes.c2p(-3.2, POLY_FUNC(-3.2)), color=accent, radius=0.11)
        moving_dot.add_updater(
            lambda d: d.move_to(axes.c2p(x_t3.get_value(), POLY_FUNC(x_t3.get_value())))
        )

        with self.narrated("P(x) décrit une courbe.", ssml=SSML_4) as tr:
            t0 = self.time
            cap11 = self._show_caption("P(x) décrit une courbe.")
            self.play(Create(axes), Write(ax_labels), run_time=1.5)
            self.play(Create(curve), FadeIn(curve_label), run_time=1.8)
            self.play(FadeIn(moving_dot), run_time=0.4)
            self.play(x_t3.animate.set_value(2.2), run_time=3.5, rate_func=linear)
            self.wait(0.6)
            self._wait_for_voice_end(tr, t0)
            self._hide_caption(cap11)

        moving_dot.clear_updaters()
        self.play(FadeOut(VGroup(axes, ax_labels, curve, curve_label, moving_dot)), run_time=1.0)

        # ==============================================================
        # ENDING
        # ==============================================================
        summ1 = Text("Variable : quantité qui change, constantes fixées.", font_size=34).shift(UP * 0.55)
        summ2 = Text("Polynôme : expression en puissances de x.",   font_size=36).shift(DOWN * 0.55)

        self.play(FadeIn(summ1, shift=UP * 0.1), FadeIn(summ2, shift=DOWN * 0.1), run_time=1.5)
        self.wait(2.5)
        self.play(FadeOut(VGroup(summ1, summ2)), run_time=1.2)
        self.wait(0.5)
