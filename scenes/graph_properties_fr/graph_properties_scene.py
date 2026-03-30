"""
graph_properties_scene.py
=========================
Manim scene for a French math-education video on graph properties.

Topic: restrictions (AND/intersection), graph properties (increasing,
even, odd, periodic), and application to a degree-2 polynomial.

Render (low quality preview):
    manim -pql scenes/graph_properties_fr/graph_properties_scene.py GraphProperties

Render (production):
    manim -pqh scenes/graph_properties_fr/graph_properties_scene.py GraphProperties -r 1920,1080

Azure TTS (optional):
    export SPEECH_KEY=...
    export SPEECH_REGION=...
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

# ── Global style ──────────────────────────────────────────────────────
config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

# ── SSML helpers ──────────────────────────────────────────────────────
# French liaison fix: "et" between vowel sounds gets swallowed by TTS.
ET = "<break time='150ms'/> et <break time='100ms'/>"
X_SSML = "<say-as interpret-as='characters'>x</say-as>"
Y_SSML = "<say-as interpret-as='characters'>y</say-as>"
T_SSML = "<say-as interpret-as='characters'>T</say-as>"

# ── Colour palette ────────────────────────────────────────────────────
ACCENT = BLUE_D
C_INC  = GREEN_D
C_DEC  = RED_D
C_EVEN = PURPLE_D
C_ODD  = ORANGE
C_PER  = TEAL_D

# ── French narration strings ──────────────────────────────────────────
SCRIPT = {
    # Section 0 — Title
    "S0_title": (
        "Dans cette vidéo, on explore les propriétés des graphes de fonctions. "
        "D'abord, les restrictions d'un domaine. "
        "Ensuite, les propriétés visuelles des courbes. "
        "Et enfin, on applique tout cela à un polynôme de degré deux."
    ),

    # Section 1 — Restrictions
    "S1_full_plane": (
        f"On commence avec le plan complet, l'ensemble des paires de réels {X_SSML} virgule {Y_SSML}."
    ),
    "S1_upper": (
        f"On ajoute la contrainte {Y_SSML} supérieur à zéro. "
        "On garde seulement la moitié supérieure du plan."
    ),
    "S1_left": (
        f"Maintenant on ajoute {X_SSML} inférieur à trois. "
        "On garde la bande à gauche de x égal trois."
    ),
    "S1_intersection": (
        "L'intersection, c'est la région qui satisfait les deux contraintes à la fois. "
        f"{Y_SSML} supérieur à zéro, {ET} {X_SSML} inférieur à trois. "
        "C'est le ET logique, comme l'intersection de deux ensembles."
    ),
    "S1_venn": (
        "Un diagramme de Venn illustre ce ET : "
        "chaque cercle représente une contrainte, "
        "et leur intersection, c'est la zone commune."
    ),

    # Section 2 — Properties
    "S2_intro": (
        "Passons aux propriétés des fonctions. "
        "On va voir : croissante, paire, impaire, et périodique."
    ),
    "S2_increasing": (
        f"Une fonction est croissante sur un intervalle si, quand {X_SSML} grandit, "
        f"f de {X_SSML} grandit aussi. "
        "Ici, le point se déplace vers la droite et monte."
    ),
    "S2_even": (
        f"Une fonction est paire si f de moins {X_SSML} égale f de {X_SSML} pour tout {X_SSML}. "
        "Le graphe est symétrique par rapport à l'axe des y. "
        "Ici, le point à x égal a et le point à x égal moins a ont la même hauteur."
    ),
    "S2_odd": (
        f"Une fonction est impaire si f de moins {X_SSML} égale moins f de {X_SSML}. "
        "Le graphe est symétrique par rotation de cent quatre-vingts degrés autour de l'origine. "
        "Si x égal a donne f de a, alors x égal moins a donne moins f de a."
    ),
    "S2_periodic": (
        f"Une fonction est périodique si f de {X_SSML} plus {T_SSML} égale f de {X_SSML} pour tout {X_SSML}. "
        f"La valeur {T_SSML} est la période. "
        "Le graphe se répète exactement tous les T unités. "
        "Ici, la période du sinus est deux pi."
    ),

    # Section 3 — Polynomial
    "S3_intro": (
        "Appliquons maintenant ces propriétés à un polynôme de degré deux : "
        "f de x égal x au carré moins deux x moins trois."
    ),
    "S3_roots": (
        "On factorise : f de x égal x moins trois fois x plus un. "
        "Les racines sont x égal trois, et x égal moins un."
    ),
    "S3_vertex": (
        "Le sommet, c'est le minimum de la parabole. "
        # "La dérivée donne x égal un, et f de un égal moins quatre. "
        "La parabole s'ouvre vers le haut, donc ce sommet est un minimum."
    ),
    "S3_not_even_odd": (
        "Est-ce que f est paire ou impaire ? "
        "On calcule f de un : c'est moins quatre. "
        "Et f de moins un : c'est zéro. "
        "Ils sont différents, donc f n'est pas paire. "
        "Et zéro n'est pas l'opposé de moins quatre, donc f n'est pas impaire non plus."
    ),
    "S3_not_periodic": (
        "Est-ce que f est périodique ? "
        "Non, car un polynôme de degré deux tend vers l'infini. "
        "Il ne peut pas se répéter."
    ),
    "S3_monotone": (
        "Par contre, f est décroissante sur moins l'infini virgule un, "
        "et croissante sur un virgule plus l'infini. "
        "Le sommet à x égal un est le point de transition."
    ),

    # Summary
    "S_summary": (
        "En résumé : les restrictions définissent un domaine par intersection de contraintes. "
        "Les propriétés, croissante, paire, impaire, périodique, se lisent directement sur le graphe. "
        "Et pour ce polynôme du second degré : deux racines, un minimum, décroissante puis croissante."
    ),
}


# ── Boilerplate dataclass ─────────────────────────────────────────────
@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


# ── Scene class ───────────────────────────────────────────────────────
class GraphProperties(VoiceoverScene if VoiceoverScene is not None else Scene):

    # ── Pacing helpers ────────────────────────────────────────────────

    def _setup_pacing(self):
        try:
            self.pace_factor = max(float(os.getenv("PACE_FACTOR", "1.2")), 0.1)
        except ValueError:
            self.pace_factor = 1.2

    def _paced_time(self, seconds: float) -> float:
        return seconds * self.pace_factor

    def play_paced(self, *args, run_time: float | None = None, **kwargs):
        if run_time is not None:
            kwargs["run_time"] = self._paced_time(run_time)
        self.play(*args, **kwargs)

    def wait_paced(self, seconds: float):
        self.wait(self._paced_time(seconds))

    # ── Voiceover setup ───────────────────────────────────────────────

    def _setup_voiceover(self):
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover not installed. Rendering without narration.")
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print(
                "[voiceover] Missing Azure Speech credentials. "
                "Set AZURE_SUBSCRIPTION_KEY/AZURE_SERVICE_REGION "
                "or SPEECH_KEY/SPEECH_REGION. Rendering without narration."
            )
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)

        self.set_speech_service(
            AzureService(
                voice="fr-CA-SylvieNeural",
                global_speed=1.0 / self.pace_factor,
            )
        )
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text: str):
        if self._voiceover_enabled:
            with self.voiceover(text=text) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    # ── Caption helpers ───────────────────────────────────────────────

    def _subtitle_box(self, text: str) -> VGroup:
        cap = Text(text, color=BLACK, font_size=28)
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

    # ── Logo intro ────────────────────────────────────────────────────

    def _logo_intro(self):
        logo = ImageMobject(
            "/Users/xiaxiao/Desktop/math_video_project/assets/branding/uqam_logo.png"
        )
        self.play(FadeIn(logo, shift=0.2 * UP), run_time=0.6)
        self.play(logo.animate.scale(0.5), run_time=1.0)
        self.play(logo.animate.scale(1.0), run_time=1.0)
        self.play(FadeOut(logo, shift=0.2 * UP), run_time=0.6)

    # ════════════════════════════════════════════════════════════════
    #  SECTION 1 — Layer-by-layer restrictions (AND / intersection)
    # ════════════════════════════════════════════════════════════════

    def _section_restrictions(self):
        axes = Axes(
            x_range=[-1, 5, 1],
            y_range=[-1, 4, 1],
            x_length=6.5,
            y_length=4.5,
            tips=True,
            axis_config={"color": BLACK, "stroke_width": 2},
        ).shift(DOWN * 0.3 + LEFT * 0.5)
        ax_labels = axes.get_axis_labels(MathTex("x"), MathTex("y"))

        def ax_rect(x0, x1, y0, y1, color, opacity=0.35):
            corners = [
                axes.c2p(x0, y0), axes.c2p(x1, y0),
                axes.c2p(x1, y1), axes.c2p(x0, y1),
            ]
            return Polygon(*corners, stroke_width=0).set_fill(color, opacity=opacity)

        full_rect  = ax_rect(-1, 5, -1, 4, GRAY_C,  opacity=0.25)
        upper_rect = ax_rect(-1, 5,  0, 4, BLUE,    opacity=0.35)
        left_rect  = ax_rect(-1, 3, -1, 4, GREEN_D, opacity=0.30)
        inter_rect = ax_rect(-1, 3,  0, 4, GOLD,    opacity=0.50)

        y0_line = DashedLine(
            axes.c2p(-1, 0), axes.c2p(5, 0), color=BLUE_D, stroke_width=2.5
        )
        x3_line = DashedLine(
            axes.c2p(3, -1), axes.c2p(3, 4), color=GREEN_D, stroke_width=2.5
        )

        lbl_y0  = MathTex(r"y > 0", font_size=36, color=BLUE_D).to_edge(UP).shift(LEFT * 1.5)
        lbl_x3  = MathTex(r"x < 3", font_size=36, color=GREEN_D).to_edge(UP).shift(RIGHT * 1.5)
        lbl_and = Text(
            "ET logique : y > 0  ET  x < 3", font_size=30, color=DARK_BROWN,
        ).to_edge(UP)

        title_s1 = Text("Restrictions et intersection", font_size=36).to_edge(UP)

        # Beat 1: full plane
        with self.narrated(SCRIPT["S1_full_plane"]):
            cap = self._show_caption("Le plan complet ℝ².")
            self.play_paced(
                Create(axes), Write(ax_labels),
                FadeIn(full_rect), FadeIn(title_s1),
                run_time=2.0,
            )
            self.wait_paced(1.2)
            self._hide_caption(cap)

        # Beat 2: y > 0
        with self.narrated(SCRIPT["S1_upper"]):
            cap = self._show_caption("On ajoute y > 0 : moitié supérieure.")
            self.play_paced(
                FadeIn(upper_rect), Create(y0_line),
                ReplacementTransform(title_s1, lbl_y0),
                run_time=1.8,
            )
            self.wait_paced(1.5)
            self._hide_caption(cap)

        # Beat 3: x < 3
        with self.narrated(SCRIPT["S1_left"]):
            cap = self._show_caption("On ajoute x < 3.")
            self.play_paced(
                FadeIn(left_rect), Create(x3_line),
                FadeIn(lbl_x3),
                run_time=1.8,
            )
            self.wait_paced(1.5)
            self._hide_caption(cap)

        # Beat 4: intersection
        with self.narrated(SCRIPT["S1_intersection"]):
            cap = self._show_caption(
                "L'intersection : les deux conditions à la fois — ET logique."
            )
            self.play_paced(
                FadeOut(lbl_y0), FadeOut(lbl_x3),
                FadeIn(inter_rect),
                Write(lbl_and),
                run_time=1.8,
            )
            inter_box = SurroundingRectangle(
                inter_rect, color=DARK_BROWN, buff=0.05, stroke_width=3
            )
            self.play_paced(Create(inter_box), run_time=1.0)
            self.wait_paced(2.0)
            self._hide_caption(cap)

        # Beat 5: Venn diagram
        venn_group = self._make_venn().scale(0.7).to_corner(UR, buff=0.25)
        with self.narrated(SCRIPT["S1_venn"]):
            cap = self._show_caption("Diagramme de Venn : zone commune = ET.")
            self.play_paced(FadeIn(venn_group), run_time=1.2)
            self.wait_paced(2.0)
            self._hide_caption(cap)

        s1_group = VGroup(
            axes, ax_labels, full_rect, upper_rect, left_rect,
            inter_rect, y0_line, x3_line, lbl_and, inter_box, venn_group,
        )
        self.play_paced(FadeOut(s1_group), run_time=1.2)

    def _make_venn(self) -> VGroup:
        c1 = Circle(radius=1.0, color=BLUE,    fill_opacity=0.25, stroke_width=2).shift(LEFT * 0.5)
        c2 = Circle(radius=1.0, color=GREEN_D, fill_opacity=0.25, stroke_width=2).shift(RIGHT * 0.5)
        lbl1  = MathTex(r"y>0", font_size=26, color=BLUE_D).shift(LEFT * 1.3 + DOWN * 0.1)
        lbl2  = MathTex(r"x<3", font_size=26, color=GREEN_D).shift(RIGHT * 1.3 + DOWN * 0.1)
        lbl_et = Text("ET", font_size=24, color=DARK_BROWN).move_to(ORIGIN)
        return VGroup(c1, c2, lbl1, lbl2, lbl_et)

    # ════════════════════════════════════════════════════════════════
    #  SECTION 2 — Graph properties
    # ════════════════════════════════════════════════════════════════

    def _section_properties(self):
        with self.narrated(SCRIPT["S2_intro"]):
            intro_txt = Text(
                "Propriétés des fonctions :\ncroissante, paire, impaire, périodique",
                font_size=36, line_spacing=0.8,
            )
            self.play_paced(Write(intro_txt), run_time=1.8)
            self.wait_paced(1.5)
            self.play_paced(FadeOut(intro_txt), run_time=0.8)

        self._prop_increasing()
        self._prop_even()
        self._prop_odd()
        self._prop_periodic()

    # ── (a) Increasing ────────────────────────────────────────────────

    def _prop_increasing(self):
        axes = Axes(
            x_range=[0, 3.2, 1],
            y_range=[0, 3.5, 1],
            x_length=5.5,
            y_length=4.5,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
        ).shift(LEFT * 1.0 + DOWN * 0.3)
        ax_labels = axes.get_axis_labels(MathTex("x"), MathTex("f(x)"))

        def f_inc(x):
            return x ** 2 / 4 + 0.5

        curve = axes.plot(f_inc, x_range=[0, 3.1], color=C_INC, stroke_width=4)
        lbl_curve = MathTex(
            r"f(x) = \frac{x^2}{4} + 0.5", font_size=32, color=C_INC,
        ).to_corner(UR).shift(DOWN * 0.5)
        prop_title = Text("Croissante", font_size=40, color=C_INC).to_edge(UP)

        x_tracker = ValueTracker(0.1)

        moving_dot = always_redraw(
            lambda: Dot(
                axes.c2p(x_tracker.get_value(), f_inc(x_tracker.get_value())),
                color=ACCENT, radius=0.1,
            )
        )

        def make_up_arrow():
            pt = axes.c2p(x_tracker.get_value(), f_inc(x_tracker.get_value()))
            return Arrow(
                start=pt, end=pt + UP * 0.55,
                color=ACCENT, buff=0, stroke_width=4,
                max_tip_length_to_length_ratio=0.35,
            )

        up_arrow = always_redraw(make_up_arrow)

        with self.narrated(SCRIPT["S2_increasing"]):
            cap = self._show_caption("f est croissante : quand x grandit, f(x) grandit aussi.")
            self.play_paced(
                Create(axes), Write(ax_labels), Create(curve),
                FadeIn(lbl_curve), Write(prop_title),
                run_time=2.0,
            )
            self.play_paced(FadeIn(moving_dot), FadeIn(up_arrow), run_time=0.6)
            self.play_paced(
                x_tracker.animate.set_value(3.0),
                run_time=4.0, rate_func=linear,
            )
            self.wait_paced(1.0)
            self._hide_caption(cap)

        moving_dot.clear_updaters()
        up_arrow.clear_updaters()
        self.play_paced(
            FadeOut(VGroup(axes, ax_labels, curve, lbl_curve, prop_title,
                           moving_dot, up_arrow)),
            run_time=1.0,
        )

    # ── (b) Even ──────────────────────────────────────────────────────

    def _prop_even(self):
        axes = Axes(
            x_range=[-3.2, 3.2, 1],
            y_range=[-0.5, 9.5, 1],
            x_length=6.0,
            y_length=5.0,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
        ).shift(DOWN * 0.3)
        ax_labels = axes.get_axis_labels(MathTex("x"), MathTex("f(x)"))

        def f_even(x):
            return x ** 2

        curve = axes.plot(f_even, x_range=[-3.0, 3.0], color=C_EVEN, stroke_width=4)
        lbl_curve = MathTex(r"f(x) = x^2", font_size=34, color=C_EVEN).to_corner(UR).shift(DOWN * 0.5)
        prop_title = Text("Paire : f(-x) = f(x)", font_size=36, color=C_EVEN).to_edge(UP)

        y_axis_line = DashedLine(
            axes.c2p(0, -0.5), axes.c2p(0, 9.5),
            color=GRAY_D, stroke_width=2.5,
        )

        a_tracker = ValueTracker(1.5)

        dot_pos = always_redraw(
            lambda: Dot(
                axes.c2p(a_tracker.get_value(), f_even(a_tracker.get_value())),
                color=ACCENT, radius=0.1,
            )
        )
        dot_neg = always_redraw(
            lambda: Dot(
                axes.c2p(-a_tracker.get_value(), f_even(a_tracker.get_value())),
                color=C_EVEN, radius=0.1,
            )
        )
        h_line = always_redraw(
            lambda: DashedLine(
                axes.c2p(-a_tracker.get_value(), f_even(a_tracker.get_value())),
                axes.c2p( a_tracker.get_value(), f_even(a_tracker.get_value())),
                color=GOLD, stroke_width=2,
            )
        )

        sym_lbl = MathTex(r"f(-x) = f(x)", font_size=34, color=C_EVEN).to_corner(UR).shift(DOWN * 1.4)

        with self.narrated(SCRIPT["S2_even"]):
            cap = self._show_caption("f est paire : f(-x) = f(x). Symétrie par rapport à l'axe des y.")
            self.play_paced(
                Create(axes), Write(ax_labels), Create(curve),
                FadeIn(lbl_curve), Write(prop_title),
                run_time=2.0,
            )
            self.play_paced(Create(y_axis_line), run_time=0.8)
            self.play_paced(
                FadeIn(dot_pos), FadeIn(dot_neg), Create(h_line),
                run_time=1.0,
            )
            self.play_paced(FadeIn(sym_lbl), run_time=0.6)
            self.play_paced(a_tracker.animate.set_value(0.5),  run_time=2.0, rate_func=smooth)
            self.play_paced(a_tracker.animate.set_value(2.8),  run_time=2.0, rate_func=smooth)
            self.play_paced(a_tracker.animate.set_value(1.5),  run_time=1.5, rate_func=smooth)
            self.wait_paced(0.8)
            self._hide_caption(cap)

        for mob in [dot_pos, dot_neg, h_line]:
            mob.clear_updaters()
        self.play_paced(
            FadeOut(VGroup(axes, ax_labels, curve, lbl_curve, prop_title,
                           y_axis_line, dot_pos, dot_neg, h_line, sym_lbl)),
            run_time=1.0,
        )

    # ── (c) Odd ───────────────────────────────────────────────────────

    def _prop_odd(self):
        axes = Axes(
            x_range=[-3.2, 3.2, 1],
            y_range=[-6.5, 6.5, 2],
            x_length=6.0,
            y_length=5.0,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
        ).shift(DOWN * 0.3)
        ax_labels = axes.get_axis_labels(MathTex("x"), MathTex("f(x)"))

        def f_odd(x):
            return x ** 3 / 5.0

        curve = axes.plot(f_odd, x_range=[-3.0, 3.0], color=C_ODD, stroke_width=4)
        lbl_curve = MathTex(
            r"f(x) = \frac{x^3}{5}", font_size=34, color=C_ODD,
        ).to_corner(UR).shift(DOWN * 0.5)
        prop_title = Text("Impaire : f(-x) = -f(x)", font_size=36, color=C_ODD).to_edge(UP)

        a_tracker = ValueTracker(2.0)

        dot_a = always_redraw(
            lambda: Dot(
                axes.c2p(a_tracker.get_value(), f_odd(a_tracker.get_value())),
                color=ACCENT, radius=0.1,
            )
        )
        dot_neg_a = always_redraw(
            lambda: Dot(
                axes.c2p(-a_tracker.get_value(), f_odd(-a_tracker.get_value())),
                color=C_ODD, radius=0.1,
            )
        )
        connector = always_redraw(
            lambda: DashedLine(
                axes.c2p( a_tracker.get_value(), f_odd( a_tracker.get_value())),
                axes.c2p(-a_tracker.get_value(), f_odd(-a_tracker.get_value())),
                color=GOLD, stroke_width=2,
            )
        )

        sym_lbl = MathTex(r"f(-x) = -f(x)", font_size=34, color=C_ODD).to_corner(UR).shift(DOWN * 1.4)

        with self.narrated(SCRIPT["S2_odd"]):
            cap = self._show_caption("f est impaire : f(-x) = -f(x). Rotation 180° autour de l'origine.")
            self.play_paced(
                Create(axes), Write(ax_labels), Create(curve),
                FadeIn(lbl_curve), Write(prop_title),
                run_time=2.0,
            )
            self.play_paced(
                FadeIn(dot_a), FadeIn(dot_neg_a), Create(connector),
                run_time=1.0,
            )
            self.play_paced(FadeIn(sym_lbl), run_time=0.6)
            self.play_paced(a_tracker.animate.set_value(0.8), run_time=2.0, rate_func=smooth)
            self.play_paced(a_tracker.animate.set_value(2.8), run_time=2.0, rate_func=smooth)
            self.play_paced(a_tracker.animate.set_value(1.5), run_time=1.5, rate_func=smooth)
            self.wait_paced(0.8)
            self._hide_caption(cap)

        for mob in [dot_a, dot_neg_a, connector]:
            mob.clear_updaters()
        self.play_paced(
            FadeOut(VGroup(axes, ax_labels, curve, lbl_curve, prop_title,
                           dot_a, dot_neg_a, connector, sym_lbl)),
            run_time=1.0,
        )

    # ── (d) Periodic ──────────────────────────────────────────────────

    def _prop_periodic(self):
        axes = Axes(
            x_range=[-0.5, 7.5, 1],
            y_range=[-1.5, 1.8, 1],
            x_length=8.5,
            y_length=3.5,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
        ).shift(DOWN * 0.8)
        ax_labels = axes.get_axis_labels(MathTex("x"), MathTex("f(x)"))

        curve = axes.plot(
            lambda x: np.sin(x),
            x_range=[0, 7.2],
            color=C_PER, stroke_width=4,
        )
        lbl_curve = MathTex(
            r"f(x) = \sin(x)", font_size=34, color=C_PER,
        ).to_corner(UR).shift(DOWN * 0.5)
        prop_title = Text("Périodique : f(x+T) = f(x)", font_size=36, color=C_PER).to_edge(UP)

        p_start = axes.c2p(0, 0)
        p_end   = axes.c2p(2 * np.pi, 0)
        period_brace = BraceBetweenPoints(p_start, p_end, direction=DOWN, color=GOLD)
        period_lbl   = MathTex(r"T = 2\pi", font_size=34, color=GOLD).next_to(period_brace, DOWN, buff=0.1)

        p2_start = axes.c2p(2 * np.pi, 0)
        p2_end   = axes.c2p(min(4 * np.pi, 7.2), 0)
        # period_brace2 = BraceBetweenPoints(p2_start, p2_end, direction=DOWN, color=GOLD)
        # period_lbl2   = MathTex(r"T = 2\pi", font_size=34, color=GOLD).next_to(period_brace2, DOWN, buff=0.1)

        repeat_lbl = MathTex(
            r"f(x + 2\pi) = f(x)", font_size=32, color=C_PER,
        ).to_corner(UR).shift(DOWN * 1.4)

        with self.narrated(SCRIPT["S2_periodic"]):
            cap = self._show_caption("f est périodique : f(x+T) = f(x). Le graphe se répète.")
            self.play_paced(
                Create(axes), Write(ax_labels), Write(prop_title),
                run_time=1.5,
            )
            self.play_paced(Create(curve), FadeIn(lbl_curve), run_time=2.5)
            self.play_paced(GrowFromCenter(period_brace), FadeIn(period_lbl), run_time=1.2)
            self.wait_paced(0.8)
            # self.play_paced(GrowFromCenter(period_brace2), FadeIn(period_lbl2), run_time=1.2)
            self.play_paced(FadeIn(repeat_lbl), run_time=0.7)
            self.wait_paced(1.5)
            self._hide_caption(cap)

        self.play_paced(
            FadeOut(VGroup(
                axes, ax_labels, curve, lbl_curve, prop_title,
                period_brace, period_lbl, repeat_lbl,
            )),
            run_time=1.0,
        )

    # ════════════════════════════════════════════════════════════════
    #  SECTION 3 — Degree-2 polynomial
    # ════════════════════════════════════════════════════════════════

    def _section_polynomial(self):
        def f(x):
            return x ** 2 - 2 * x - 3   # = (x-3)(x+1), roots at -1 and 3, vertex at (1,-4)

        axes = Axes(
            x_range=[-2.5, 4.5, 1],
            y_range=[-5.5, 6.5, 1],
            x_length=6.5,
            y_length=5.5,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2},
            x_axis_config={
                "include_numbers": True,
                "numbers_to_include": np.arange(-2, 5, 1),
                "font_size": 22,
                "decimal_number_config": {"num_decimal_places": 0},
            },
            y_axis_config={
                "include_numbers": True,
                "numbers_to_include": np.arange(-4, 7, 2),
                "font_size": 22,
                "decimal_number_config": {"num_decimal_places": 0},
            },
        ).shift(LEFT * 0.5 + DOWN * 0.2)
        ax_labels = axes.get_axis_labels(MathTex("x"), MathTex("f(x)"))

        curve_full = axes.plot(f, x_range=[-2.2, 4.2], color=BLACK, stroke_width=4)
        lbl_f = MathTex(
            r"f(x) = x^2 - 2x - 3", font_size=32,
        ).to_corner(UR).shift(DOWN * 0.3 + LEFT * 0.1)
        lbl_factor = MathTex(
            r"= (x-3)(x+1)", font_size=30,
        ).next_to(lbl_f, DOWN, buff=0.15, aligned_edge=RIGHT)
        prop_title = Text("Application : polynôme de degré 2", font_size=34).to_edge(UP)

        # Beat 1: intro + plot
        with self.narrated(SCRIPT["S3_intro"]):
            cap = self._show_caption("f(x) = x² - 2x - 3")
            self.play_paced(
                Create(axes), Write(ax_labels), Write(prop_title),
                run_time=1.8,
            )
            self.play_paced(Create(curve_full), FadeIn(lbl_f), run_time=2.0)
            self.wait_paced(1.0)
            self._hide_caption(cap)

        # Beat 2: roots
        root_neg1 = Dot(axes.c2p(-1, 0), color=ACCENT, radius=0.1)
        root_3    = Dot(axes.c2p(3, 0),  color=ACCENT, radius=0.1)
        lbl_rn1   = MathTex(r"x=-1", font_size=28, color=ACCENT).next_to(axes.c2p(-1, 0), UL, buff=0.1)
        lbl_r3    = MathTex(r"x=3",  font_size=28, color=ACCENT).next_to(axes.c2p(3, 0),  UR, buff=0.1)

        with self.narrated(SCRIPT["S3_roots"]):
            cap = self._show_caption("Racines : x = -1 et x = 3.")
            self.play_paced(FadeIn(lbl_factor), run_time=0.8)
            self.play_paced(
                FadeIn(root_neg1), FadeIn(root_3),
                Write(lbl_rn1), Write(lbl_r3),
                run_time=1.4,
            )
            self.wait_paced(1.2)
            self._hide_caption(cap)

        # Beat 3: vertex / minimum
        vertex_dot = Dot(axes.c2p(1, -4), color=RED_D, radius=0.12)
        lbl_vertex = MathTex(r"(1,\,-4)", font_size=28, color=RED_D).next_to(
            axes.c2p(1, -4), RIGHT, buff=0.15
        )
        min_lbl = Text("minimum", font_size=26, color=RED_D).next_to(
            axes.c2p(1, -4), DOWN, buff=0.22
        )

        with self.narrated(SCRIPT["S3_vertex"]):
            cap = self._show_caption("Sommet (1, -4) : minimum. La parabole s'ouvre vers le haut.")
            self.play_paced(FadeIn(vertex_dot), Write(lbl_vertex), run_time=1.2)
            self.play_paced(FadeIn(min_lbl), run_time=0.7)
            self.wait_paced(1.5)
            self._hide_caption(cap)

        # Beat 4: NOT even / NOT odd — drop-lines at x=1 and x=-1
        dot_p1  = Dot(axes.c2p(1,  f(1)),  color=BLUE_D,  radius=0.1)
        dot_m1  = Dot(axes.c2p(-1, f(-1)), color=GREEN_D, radius=0.1)
        # f(1) = -4: normal vertical drop-line
        vline_p1 = DashedLine(axes.c2p(1, 0), axes.c2p(1, f(1)), color=BLUE_D, stroke_width=2)
        # f(-1) = 0: root is ON the x-axis, so a zero-length DashedLine would crash.
        # Use a short horizontal tick to mark the point instead.
        vline_m1 = Line(
            axes.c2p(-1, 0) + LEFT * 0.15,
            axes.c2p(-1, 0) + RIGHT * 0.15,
            color=GREEN_D, stroke_width=3,
        )
        lbl_f1   = MathTex(r"f(1)=-4", font_size=26, color=BLUE_D).next_to(
            axes.c2p(1, f(1)), RIGHT, buff=0.1
        )
        lbl_fm1  = MathTex(r"f(-1)=0", font_size=26, color=GREEN_D).next_to(
            axes.c2p(-1, f(-1)), LEFT, buff=0.1
        )

        not_even_lbl = MathTex(
            r"f(1) \neq f(-1) \Rightarrow \text{non paire}",
            font_size=26, color=RED_D,
        ).to_corner(UR).shift(DOWN * 2.2)
        not_odd_lbl = MathTex(
            r"f(-1) \neq -f(1) \Rightarrow \text{non impaire}",
            font_size=26, color=RED_D,
        ).next_to(not_even_lbl, DOWN, buff=0.15, aligned_edge=RIGHT)

        with self.narrated(SCRIPT["S3_not_even_odd"]):
            cap = self._show_caption("f(1) ≠ f(-1) → non paire.  f(-1) ≠ -f(1) → non impaire.")
            self.play_paced(
                Create(vline_p1), Create(vline_m1),
                FadeIn(dot_p1), FadeIn(dot_m1),
                run_time=1.2,
            )
            self.play_paced(Write(lbl_f1), Write(lbl_fm1), run_time=1.0)
            self.play_paced(Write(not_even_lbl), run_time=0.9)
            self.play_paced(Write(not_odd_lbl),  run_time=0.9)
            self.wait_paced(1.5)
            self._hide_caption(cap)

        # Beat 5: NOT periodic
        not_per_lbl = Text(
            "Non périodique : tend vers ∞.", font_size=28, color=RED_D,
        ).next_to(not_odd_lbl, DOWN, buff=0.2, aligned_edge=RIGHT)

        with self.narrated(SCRIPT["S3_not_periodic"]):
            cap = self._show_caption("Non périodique : le polynôme tend vers l'infini.")
            self.play_paced(FadeIn(not_per_lbl), run_time=0.8)
            self.wait_paced(1.5)
            self._hide_caption(cap)

        # Beat 6: monotone segments (recolour curve)
        curve_dec = axes.plot(f, x_range=[-2.2, 1.0], color=C_DEC, stroke_width=5)
        curve_inc = axes.plot(f, x_range=[1.0,  4.2], color=C_INC, stroke_width=5)

        lbl_dec = MathTex(
            r"\text{décroissante sur } (-\infty,\,1]",
            font_size=24, color=C_DEC,
        ).to_corner(UL).shift(DOWN * 1.5 + RIGHT * 0.2)
        lbl_inc = MathTex(
            r"\text{croissante sur } [1,\,+\infty)",
            font_size=24, color=C_INC,
        ).next_to(lbl_dec, DOWN, buff=0.18, aligned_edge=LEFT)

        with self.narrated(SCRIPT["S3_monotone"]):
            cap = self._show_caption("Décroissante sur (-∞, 1], croissante sur [1, +∞).")
            self.play_paced(
                FadeOut(curve_full),
                Create(curve_dec), Create(curve_inc),
                run_time=1.8,
            )
            self.play_paced(Write(lbl_dec), Write(lbl_inc), run_time=1.2)
            self.wait_paced(2.0)
            self._hide_caption(cap)

        s3_group = VGroup(
            axes, ax_labels, curve_dec, curve_inc,
            lbl_f, lbl_factor, prop_title,
            root_neg1, root_3, lbl_rn1, lbl_r3,
            vertex_dot, lbl_vertex, min_lbl,
            dot_p1, dot_m1, vline_p1, vline_m1, lbl_f1, lbl_fm1,
            not_even_lbl, not_odd_lbl, not_per_lbl,
            lbl_dec, lbl_inc,
        )
        self.play_paced(FadeOut(s3_group), run_time=1.2)

    # ════════════════════════════════════════════════════════════════
    #  SUMMARY SLIDE
    # ════════════════════════════════════════════════════════════════

    def _section_summary(self):
        s_title = Text("Résumé", font_size=48).to_edge(UP)

        bullets = VGroup(
            Text("1.  Restrictions ET = intersection de contraintes.", font_size=28),
            Text("2.  Croissante : quand x ↑, f(x) ↑.", font_size=28),
            Text("3.  Paire : f(-x) = f(x)   — symétrie axe des y.", font_size=28),
            Text("4.  Impaire : f(-x) = -f(x) — symétrie par l'origine.", font_size=28),
            Text("5.  Périodique : f(x+T) = f(x) — graphe répété.", font_size=28),
            Text("6.  x²-2x-3 : racines -1 et 3, minimum (1,-4),", font_size=28),
            Text("     décroissante sur (-∞,1], croissante sur [1,∞).", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).next_to(s_title, DOWN, buff=0.5)

        with self.narrated(SCRIPT["S_summary"]):
            cap = self._show_caption("Résumé des propriétés.")
            self.play_paced(Write(s_title), run_time=0.8)
            for bullet in bullets:
                self.play_paced(FadeIn(bullet, shift=RIGHT * 0.15), run_time=0.5)
            self.wait_paced(4.0)
            self._hide_caption(cap)

        self.play_paced(FadeOut(VGroup(s_title, bullets)), run_time=1.2)

    # ════════════════════════════════════════════════════════════════
    #  CONSTRUCT
    # ════════════════════════════════════════════════════════════════

    def construct(self):
        self.camera.background_color = WHITE
        self._setup_pacing()
        self._setup_voiceover()

        self._logo_intro()

        title    = Text("Propriétés des graphes de fonctions", font_size=42)
        subtitle = Text(
            "Restrictions, monotonie, parité, périodicité", font_size=30,
        ).next_to(title, DOWN, buff=0.3)

        with self.narrated(SCRIPT["S0_title"]):
            self.play_paced(
                FadeIn(title, shift=0.2 * DOWN),
                FadeIn(subtitle, shift=0.2 * DOWN),
                run_time=2.0,
            )
            self.wait_paced(2.0)
            self.play_paced(FadeOut(title), FadeOut(subtitle), run_time=1.0)

        self._section_restrictions()
        self._section_properties()
        self._section_polynomial()
        self._section_summary()

        self.wait(1.0)
