"""
graph_properties_scene.py
=========================
Manim scene for a French math-education video on graph properties.

Topic: restrictions (AND/intersection), graph properties (increasing,
even, odd, periodic), and application to a degree-2 polynomial.

Render (low quality preview):
    manim -pql scenes/fonctions_et_graphiques_fr/graph_properties_fr/graph_properties_scene.py GraphProperties

Render (production):
    manim -pqh scenes/fonctions_et_graphiques_fr/graph_properties_fr/graph_properties_scene.py GraphProperties -r 1920,1080

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
import tools.tts as tts
from tools.branding import play_uqam_intro

# Short aliases matching the existing naming convention in this file.
ET, X_SSML, Y_SSML, T_SSML = tts.ET, tts.X, tts.Y, tts.T

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

    # Section 4 — Graph transformations
    "S4_intro": (
        "Ajoutons maintenant une compétence très utile : transformer un graphe sans tout recalculer. "
        "L'idée est simple : ce qui est à l'extérieur de la fonction agit sur les sorties, "
        "et ce qui est à l'intérieur agit sur les entrées."
    ),
    "S4_base": (
        f"On part d'un graphe quelconque, celui de f de {X_SSML}. "
        "On va garder les axes fixes, puis observer comment la formule déplace tout le graphe."
    ),
    "S4_vertical": (
        "<bookmark mark='v_formula'/>"
        f"Si on écrit f de {X_SSML} plus deux, le plus deux est à l'extérieur. "
        "<bookmark mark='v_point'/>"
        "Chaque point garde la même abscisse, mais sa hauteur augmente de deux. "
        "<bookmark mark='v_graph'/>"
        "Donc tout le graphe monte de deux unités."
    ),
    "S4_horizontal": (
        "<bookmark mark='h_formula'/>"
        f"Si on écrit f de parenthèse {X_SSML} moins deux, le changement est à l'intérieur. "
        "<bookmark mark='h_reason'/>"
        f"Pour obtenir l'ancienne entrée a, il faut que {X_SSML} moins deux égale a. "
        "Donc x égale a plus deux. "
        "<bookmark mark='h_graph'/>"
        "Le graphe se déplace vers la droite, dans le sens opposé au signe moins."
    ),
    "S4_scaling": (
        "<bookmark mark='compress_formula'/>"
        f"Avec f de deux {X_SSML}, on multiplie l'entrée par deux. "
        "<bookmark mark='compress_point'/>"
        f"Pour retrouver l'ancienne entrée a, il faut résoudre deux {X_SSML} égale a. "
        "<bookmark mark='compress_reason'/>"
        "Donc x égale a divisé par deux. "
        "<bookmark mark='compress_graph'/>"
        "Le graphe se rapproche de l'axe des ordonnées : c'est une compression horizontale. "
        "<bookmark mark='stretch_formula'/>"
        f"À l'inverse, f de {X_SSML} sur deux demande d'aller deux fois plus loin. "
        "<bookmark mark='stretch_point'/>"
        f"On résout {X_SSML} sur deux égale a. "
        "<bookmark mark='stretch_reason'/>"
        "Donc x égale deux a. "
        "<bookmark mark='stretch_graph'/>"
        "Le graphe s'éloigne de l'axe des ordonnées : c'est un étirement horizontal."
    ),
    "S4_reflections": (
        "<bookmark mark='reflect_x_formula'/>"
        f"Le signe moins devant f de {X_SSML} change le signe des sorties : "
        "<bookmark mark='reflect_x_point'/>"
        "le point a virgule f de a devient a virgule moins f de a. "
        "<bookmark mark='reflect_x_graph'/>"
        "C'est un miroir par rapport à l'axe des x. "
        "<bookmark mark='reflect_y_formula'/>"
        f"Le signe moins dans f de moins {X_SSML} change le signe des entrées : "
        "<bookmark mark='reflect_y_point'/>"
        "le point a virgule f de a passe à moins a virgule f de a. "
        "<bookmark mark='reflect_y_graph'/>"
        "C'est un miroir par rapport à l'axe des y."
    ),
    "S4_parabola": (
        "<bookmark mark='parabola_start'/>"
        "Sur un exemple classique, on part de y égale x au carré. "
        "<bookmark mark='parabola_shift'/>"
        "Le terme x moins deux déplace la parabole vers la droite. "
        "<bookmark mark='parabola_reflect'/>"
        "Le signe moins devant la formule la retourne vers le bas. "
        "<bookmark mark='parabola_up'/>"
        "Et le plus trois remonte tout le graphe."
    ),
    "S4_transform_summary": (
        "À retenir pour les transformations : extérieur, vertical. "
        "Intérieur, horizontal, souvent dans le sens opposé. "
        "Une transformation de graphe, c'est une transformation coordonnée des points."
    ),

    # Summary
    "S_summary": (
        "En résumé : les restrictions définissent un domaine par intersection de contraintes. "
        "Les propriétés, croissante, paire, impaire, périodique, se lisent directement sur le graphe. "
        "Pour le polynôme du second degré : deux racines, un minimum, décroissante puis croissante. "
        "Et les transformations de graphe se comprennent en distinguant l'extérieur et l'intérieur de la fonction."
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
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            print("[voiceover] MANIM_DISABLE_VOICEOVER set. Rendering without narration.")
            return
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
                voice=tts.VOICE_ID,
                global_speed=1.0 / self.pace_factor,
            )
        )
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text: str):
        if self._voiceover_enabled:
            with self.voiceover(text=tts.ssml(text, "0%"), subcaption=tts.strip_ssml(text)) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def _sync_bookmark(self, mark: str, fallback: float = 0.25):
        if self._voiceover_enabled:
            self.wait_until_bookmark(mark)
        elif fallback > 0:
            self.wait_paced(fallback)

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
        play_uqam_intro(self)

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
    #  SECTION 4 — Graph transformations
    # ════════════════════════════════════════════════════════════════

    def _section_transformations(self):
        c_out = BLUE_D
        c_in = GREEN_D
        c_final = PURPLE_D
        c_ghost = GRAY
        unit = 0.58

        def proportional_axes(x_range, y_range, unit_size=unit):
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
                    "stroke_width": 2,
                    "include_numbers": True,
                    "font_size": 20,
                },
            )

        def colored_formula(parts, color_indices=None, color=BLUE_D, scale=1.0):
            formula = MathTex(*parts).scale(scale)
            if color_indices:
                for i in color_indices:
                    formula[i].set_color(color)
            return formula

        def base_f(x):
            return 0.18 * (x + 2.2) * (x - 0.3) * (x - 1.7) + 0.4

        def point_transition(axes, old_xy, new_xy, old_tex, new_tex, color, reason_tex=None):
            old_dot = Dot(axes.c2p(*old_xy), color=BLACK, radius=0.075)
            new_dot = Dot(axes.c2p(*new_xy), color=color, radius=0.075)
            old_label = MathTex(old_tex, font_size=26).next_to(old_dot, UP, buff=0.1)
            new_label = MathTex(new_tex, font_size=26, color=color).next_to(new_dot, UP, buff=0.1)
            arrow = Arrow(
                axes.c2p(*old_xy),
                axes.c2p(*new_xy),
                buff=0.12,
                color=color,
                stroke_width=3,
                max_tip_length_to_length_ratio=0.18,
            )
            pieces = [old_dot, new_dot, old_label, new_label, arrow]
            reason = None
            if reason_tex:
                reason = MathTex(reason_tex, font_size=28, color=color)
                reason.move_to(axes.c2p(0, -2.45))
                pieces.append(reason)
            return VGroup(*pieces), reason

        with self.narrated(SCRIPT["S4_intro"]):
            title = Text("Transformer un graphe", font_size=42).to_edge(UP)
            outside = VGroup(
                Text("extérieur de f", font_size=30, color=c_out),
                MathTex(r"f(x)+k,\quad -f(x)", font_size=34, color=c_out),
                Text("agit sur les sorties", font_size=26),
                Text("effet vertical", font_size=28, color=c_out),
            ).arrange(DOWN, buff=0.14)
            inside = VGroup(
                Text("intérieur de f", font_size=30, color=c_in),
                MathTex(r"f(x-h),\quad f(kx),\quad f(-x)", font_size=34, color=c_in),
                Text("agit sur les entrées", font_size=26),
                Text("effet horizontal", font_size=28, color=c_in),
            ).arrange(DOWN, buff=0.14)

            for panel, color in [(outside, c_out), (inside, c_in)]:
                box = RoundedRectangle(
                    corner_radius=0.08,
                    width=4.9,
                    height=2.15,
                    stroke_color=color,
                    stroke_width=3,
                )
                panel.move_to(box)
                panel.add_to_back(box)

            panels = VGroup(outside, inside).arrange(RIGHT, buff=0.8).shift(DOWN * 0.2)
            cap = self._show_caption("Transformations : extérieur = sorties, intérieur = entrées.")
            self.play_paced(Write(title), run_time=0.9)
            self.play_paced(FadeIn(panels, shift=UP * 0.12), run_time=1.2)
            self.wait_paced(2.0)
            self._hide_caption(cap)
            self.play_paced(FadeOut(VGroup(title, panels)), run_time=0.8)

        axes = proportional_axes(
            x_range=[-5, 5, 1],
            y_range=[-4, 6, 1],
        ).shift(DOWN * 0.55)
        section_title = Text("Transformations de graphiques", font_size=38).to_edge(UP, buff=0.25)

        base_range = [-2.4, 2.4]
        graph_f = axes.plot(base_f, x_range=base_range, color=BLACK, stroke_width=4)
        formula_base = colored_formula([r"y=", r"f", r"(", r"x", r")"], scale=1.12)
        formula_base.next_to(section_title, DOWN, buff=0.10)
        current_formula = formula_base

        with self.narrated(SCRIPT["S4_base"]):
            cap = self._show_caption("On part du graphe de f.")
            self.play_paced(Create(axes), Write(section_title), run_time=1.6)
            self.play_paced(Create(graph_f), FadeIn(formula_base), run_time=1.7)
            self.wait_paced(1.2)
            self._hide_caption(cap)

        a = 1.2
        fa = base_f(a)

        formula_up = colored_formula(
            [r"y=", r"f", r"(", r"x", r")", r"+2"],
            color_indices=[5],
            color=c_out,
            scale=1.12,
        ).move_to(formula_base)
        tag_out = Text("extérieur : sorties → vertical", font_size=24, color=c_out)
        tag_out.next_to(formula_base, DOWN, buff=0.08)
        graph_up = axes.plot(lambda x: base_f(x) + 2, x_range=base_range, color=c_out, stroke_width=4)
        pts, _ = point_transition(
            axes,
            old_xy=(a, fa),
            new_xy=(a, fa + 2),
            old_tex=r"(a,f(a))",
            new_tex=r"(a,f(a)+2)",
            color=c_out,
        )

        with self.narrated(SCRIPT["S4_vertical"]):
            cap = self._show_caption("f(x)+2 : même x, hauteur +2.")
            self._sync_bookmark("v_formula")
            self.play_paced(ReplacementTransform(current_formula, formula_up), FadeIn(tag_out), run_time=0.7)
            current_formula = formula_up
            self._sync_bookmark("v_point")
            self.play_paced(FadeIn(pts[0]), FadeIn(pts[2]), run_time=0.5)
            self.play_paced(Create(pts[4]), FadeIn(pts[1]), FadeIn(pts[3]), run_time=0.9)
            self._sync_bookmark("v_graph")
            self.play_paced(graph_f.animate.set_stroke(color=c_ghost, width=3, opacity=0.42), run_time=0.4)
            moving = graph_f.copy().set_stroke(color=c_out, width=4, opacity=1)
            self.add(moving)
            self.play_paced(moving.animate.shift(UP * 2 * unit), run_time=1.3)
            self.play_paced(ReplacementTransform(moving, graph_up), run_time=0.35)
            self.wait_paced(0.8)
            self._hide_caption(cap)

        formula_right = colored_formula(
            [r"y=", r"f", r"(", r"x-2", r")"],
            color_indices=[3],
            color=c_in,
            scale=1.12,
        ).move_to(formula_base)
        tag_in = Text("intérieur : entrées → horizontal", font_size=24, color=c_in)
        tag_in.next_to(formula_base, DOWN, buff=0.08)
        graph_right = axes.plot(
            lambda x: base_f(x - 2),
            x_range=[base_range[0] + 2, base_range[1] + 2],
            color=c_in,
            stroke_width=4,
        )
        pts_h, reason_h = point_transition(
            axes,
            old_xy=(a, fa),
            new_xy=(a + 2, fa),
            old_tex=r"(a,f(a))",
            new_tex=r"(a+2,f(a))",
            reason_tex=r"x-2=a \quad\Rightarrow\quad x=a+2",
            color=c_in,
        )

        with self.narrated(SCRIPT["S4_horizontal"]):
            cap = self._show_caption("f(x-2) : déplacement vers la droite.")
            self._sync_bookmark("h_formula")
            self.play_paced(
                FadeOut(pts), FadeOut(graph_up), FadeOut(tag_out),
                graph_f.animate.set_stroke(color=BLACK, width=4, opacity=1),
                ReplacementTransform(current_formula, formula_right),
                FadeIn(tag_in),
                run_time=0.9,
            )
            current_formula = formula_right
            self.play_paced(FadeIn(pts_h[0]), FadeIn(pts_h[2]), run_time=0.5)
            self._sync_bookmark("h_reason")
            self.play_paced(Write(reason_h), run_time=0.7)
            self.play_paced(Create(pts_h[4]), FadeIn(pts_h[1]), FadeIn(pts_h[3]), run_time=0.9)
            self._sync_bookmark("h_graph")
            self.play_paced(graph_f.animate.set_stroke(color=c_ghost, width=3, opacity=0.42), run_time=0.4)
            moving = graph_f.copy().set_stroke(color=c_in, width=4, opacity=1)
            self.add(moving)
            self.play_paced(moving.animate.shift(RIGHT * 2 * unit), run_time=1.3)
            self.play_paced(ReplacementTransform(moving, graph_right), run_time=0.35)
            self.wait_paced(0.8)
            self._hide_caption(cap)

        formula_compress = colored_formula(
            [r"y=", r"f", r"(", r"2x", r")"],
            color_indices=[3],
            color=c_in,
            scale=1.12,
        ).move_to(formula_base)
        formula_stretch = colored_formula(
            [r"y=", r"f", r"(", r"x/2", r")"],
            color_indices=[3],
            color=c_in,
            scale=1.12,
        ).move_to(formula_base)
        graph_compress = axes.plot(
            lambda x: base_f(2 * x),
            x_range=[base_range[0] / 2, base_range[1] / 2],
            color=c_in,
            stroke_width=4,
        )
        graph_stretch = axes.plot(
            lambda x: base_f(x / 2),
            x_range=[base_range[0] * 2, base_range[1] * 2],
            color=c_in,
            stroke_width=4,
        )
        a_scale = -2.0
        fa_scale = base_f(a_scale)
        pts_compress, _ = point_transition(
            axes,
            old_xy=(a_scale, fa_scale),
            new_xy=(a_scale / 2, fa_scale),
            old_tex=r"(a,f(a))",
            new_tex=r"\left(\frac a2,f(a)\right)",
            reason_tex=r"2x=a \quad\Rightarrow\quad x=\frac a2",
            color=c_in,
        )
        pts_compress[2].next_to(pts_compress[0], UP + LEFT, buff=0.08)
        pts_compress[3].scale(0.82)
        pts_compress[3].move_to(axes.c2p(-0.35, 1.45))

        pts_stretch, _ = point_transition(
            axes,
            old_xy=(a_scale, fa_scale),
            new_xy=(2 * a_scale, fa_scale),
            old_tex=r"(a,f(a))",
            new_tex=r"(2a,f(a))",
            reason_tex=r"\frac{x}{2}=a \quad\Rightarrow\quad x=2a",
            color=c_in,
        )

        with self.narrated(SCRIPT["S4_scaling"]):
            cap = self._show_caption("À l'intérieur : les facteurs changent les distances horizontales.")
            self._sync_bookmark("compress_formula")
            self.play_paced(
                FadeOut(pts_h), FadeOut(graph_right), FadeOut(tag_in),
                graph_f.animate.set_stroke(color=BLACK, width=4, opacity=1),
                ReplacementTransform(current_formula, formula_compress),
                run_time=0.9,
            )
            current_formula = formula_compress
            self._sync_bookmark("compress_point")
            self.play_paced(FadeIn(pts_compress[0]), FadeIn(pts_compress[2]), run_time=0.5)
            self._sync_bookmark("compress_reason")
            self.play_paced(Write(pts_compress[5]), run_time=0.7)
            self.play_paced(Create(pts_compress[4]), FadeIn(pts_compress[1]), FadeIn(pts_compress[3]), run_time=0.9)
            self._sync_bookmark("compress_graph")
            self.play_paced(graph_f.animate.set_stroke(color=c_ghost, width=3, opacity=0.42), run_time=0.4)
            moving = graph_f.copy().set_stroke(color=c_in, width=4, opacity=1)
            self.add(moving)
            moving.generate_target()
            moving.target.stretch(0.5, dim=0, about_point=axes.c2p(0, 0))
            self.play_paced(MoveToTarget(moving), run_time=1.2)
            self.play_paced(ReplacementTransform(moving, graph_compress), run_time=0.35)
            self.wait_paced(0.8)
            self._sync_bookmark("stretch_formula")
            self.play_paced(
                FadeOut(pts_compress), FadeOut(graph_compress),
                ReplacementTransform(current_formula, formula_stretch),
                graph_f.animate.set_stroke(color=BLACK, width=4, opacity=1),
                run_time=0.7,
            )
            current_formula = formula_stretch
            self._sync_bookmark("stretch_point")
            self.play_paced(FadeIn(pts_stretch[0]), FadeIn(pts_stretch[2]), run_time=0.5)
            self._sync_bookmark("stretch_reason")
            self.play_paced(Write(pts_stretch[5]), run_time=0.7)
            self.play_paced(Create(pts_stretch[4]), FadeIn(pts_stretch[1]), FadeIn(pts_stretch[3]), run_time=0.9)
            self._sync_bookmark("stretch_graph")
            self.play_paced(graph_f.animate.set_stroke(color=c_ghost, width=3, opacity=0.42), run_time=0.4)
            moving = graph_f.copy().set_stroke(color=c_in, width=4, opacity=1)
            self.add(moving)
            moving.generate_target()
            moving.target.stretch(2.0, dim=0, about_point=axes.c2p(0, 0))
            self.play_paced(MoveToTarget(moving), run_time=1.2)
            self.play_paced(ReplacementTransform(moving, graph_stretch), run_time=0.35)
            self.wait_paced(0.8)
            self._hide_caption(cap)

        formula_reflect_x = colored_formula(
            [r"y=", r"-", r"f", r"(", r"x", r")"],
            color_indices=[1],
            color=c_out,
            scale=1.12,
        ).move_to(formula_base)
        formula_reflect_y = colored_formula(
            [r"y=", r"f", r"(", r"-x", r")"],
            color_indices=[3],
            color=c_in,
            scale=1.12,
        ).move_to(formula_base)
        graph_reflect_x = axes.plot(lambda x: -base_f(x), x_range=base_range, color=c_out, stroke_width=4)
        graph_reflect_y = axes.plot(lambda x: base_f(-x), x_range=base_range, color=c_in, stroke_width=4)
        a_ref = -1.2
        fa_ref = base_f(a_ref)
        pts_reflect_x, _ = point_transition(
            axes,
            old_xy=(a_ref, fa_ref),
            new_xy=(a_ref, -fa_ref),
            old_tex=r"(a,f(a))",
            new_tex=r"(a,-f(a))",
            color=c_out,
        )
        pts_reflect_x[3].next_to(pts_reflect_x[1], DOWN, buff=0.1)

        pts_reflect_y, _ = point_transition(
            axes,
            old_xy=(a_ref, fa_ref),
            new_xy=(-a_ref, fa_ref),
            old_tex=r"(a,f(a))",
            new_tex=r"(-a,f(a))",
            color=c_in,
        )

        with self.narrated(SCRIPT["S4_reflections"]):
            cap = self._show_caption("Deux miroirs : sortie opposée ou entrée opposée.")
            self._sync_bookmark("reflect_x_formula")
            self.play_paced(
                FadeOut(pts_stretch), FadeOut(graph_stretch),
                graph_f.animate.set_stroke(color=BLACK, width=4, opacity=1),
                ReplacementTransform(current_formula, formula_reflect_x),
                run_time=0.8,
            )
            current_formula = formula_reflect_x
            self._sync_bookmark("reflect_x_point")
            self.play_paced(FadeIn(pts_reflect_x[0]), FadeIn(pts_reflect_x[2]), run_time=0.5)
            self.play_paced(Create(pts_reflect_x[4]), FadeIn(pts_reflect_x[1]), FadeIn(pts_reflect_x[3]), run_time=0.9)
            self._sync_bookmark("reflect_x_graph")
            x_axis_hl = Line(
                axes.c2p(-5, 0),
                axes.c2p(5, 0),
                color=c_out,
                stroke_width=6,
                stroke_opacity=0.8,
            )
            self.play_paced(Create(x_axis_hl), run_time=0.45)
            self.play_paced(graph_f.animate.set_stroke(color=c_ghost, width=3, opacity=0.42), run_time=0.35)
            moving = graph_f.copy().set_stroke(color=c_out, width=4, opacity=1)
            self.add(moving)
            moving.generate_target()
            moving.target.stretch(-1.0, dim=1, about_point=axes.c2p(0, 0))
            self.play_paced(MoveToTarget(moving), run_time=1.1)
            self.play_paced(ReplacementTransform(moving, graph_reflect_x), FadeOut(x_axis_hl), run_time=0.35)
            self._sync_bookmark("reflect_y_formula")
            self.play_paced(
                ReplacementTransform(current_formula, formula_reflect_y),
                FadeOut(pts_reflect_x), FadeOut(graph_reflect_x),
                graph_f.animate.set_stroke(color=BLACK, width=4, opacity=1),
                run_time=0.75,
            )
            current_formula = formula_reflect_y
            self._sync_bookmark("reflect_y_point")
            self.play_paced(FadeIn(pts_reflect_y[0]), FadeIn(pts_reflect_y[2]), run_time=0.5)
            self.play_paced(Create(pts_reflect_y[4]), FadeIn(pts_reflect_y[1]), FadeIn(pts_reflect_y[3]), run_time=0.9)
            self._sync_bookmark("reflect_y_graph")
            y_axis_hl = Line(
                axes.c2p(0, -3),
                axes.c2p(0, 6),
                color=c_in,
                stroke_width=6,
                stroke_opacity=0.8,
            )
            self.play_paced(Create(y_axis_hl), run_time=0.45)
            self.play_paced(graph_f.animate.set_stroke(color=c_ghost, width=3, opacity=0.42), run_time=0.35)
            moving = graph_f.copy().set_stroke(color=c_in, width=4, opacity=1)
            self.add(moving)
            moving.generate_target()
            moving.target.stretch(-1.0, dim=0, about_point=axes.c2p(0, 0))
            self.play_paced(MoveToTarget(moving), run_time=1.1)
            self.play_paced(ReplacementTransform(moving, graph_reflect_y), FadeOut(y_axis_hl), run_time=0.35)
            self.wait_paced(0.8)
            self._hide_caption(cap)

        with self.narrated(SCRIPT["S4_parabola"]):
            cap = self._show_caption("Exemple : y = -(x-2)² + 3.")
            self.play_paced(
                FadeOut(pts_reflect_y), FadeOut(graph_reflect_y),
                FadeOut(current_formula),
                graph_f.animate.set_stroke(color=BLACK, width=4, opacity=1),
                run_time=0.7,
            )
            self._sync_bookmark("parabola_start")
            p_formula = MathTex(r"y=x^2", font_size=42).next_to(section_title, DOWN, buff=0.1)
            p_graph = axes.plot(lambda x: x ** 2, x_range=[-2.1, 2.1], color=BLACK, stroke_width=4)
            self.play_paced(FadeIn(p_formula), Create(p_graph), run_time=1.1)

            self._sync_bookmark("parabola_shift")
            p_shift_formula = MathTex(r"y=(x-2)^2", font_size=42, color=c_in).move_to(p_formula)
            p_shift_graph = axes.plot(lambda x: (x - 2) ** 2, x_range=[-0.1, 4.1], color=c_in, stroke_width=4)
            self.play_paced(ReplacementTransform(p_formula, p_shift_formula), run_time=0.5)
            self.play_paced(ReplacementTransform(p_graph, p_shift_graph), run_time=1.0)

            self._sync_bookmark("parabola_reflect")
            p_reflect_formula = MathTex(r"y=-(x-2)^2", font_size=42, color=c_out).move_to(p_shift_formula)
            p_reflect_graph = axes.plot(lambda x: -(x - 2) ** 2, x_range=[-0.1, 4.1], color=c_out, stroke_width=4)
            self.play_paced(ReplacementTransform(p_shift_formula, p_reflect_formula), run_time=0.5)
            self.play_paced(ReplacementTransform(p_shift_graph, p_reflect_graph), run_time=1.0)

            self._sync_bookmark("parabola_up")
            p_final_formula = MathTex(r"y=-(x-2)^2+3", font_size=42, color=c_final).move_to(p_reflect_formula)
            p_final_graph = axes.plot(
                lambda x: -(x - 2) ** 2 + 3,
                x_range=[-0.1, 4.1],
                color=c_final,
                stroke_width=4,
            )
            vertex = Dot(axes.c2p(2, 3), color=c_final, radius=0.085)
            vertex_label = MathTex(r"(2,3)", font_size=28, color=c_final).next_to(vertex, UP, buff=0.1)
            self.play_paced(ReplacementTransform(p_reflect_formula, p_final_formula), run_time=0.5)
            self.play_paced(ReplacementTransform(p_reflect_graph, p_final_graph), run_time=1.0)
            self.play_paced(FadeIn(vertex), FadeIn(vertex_label), run_time=0.6)
            self.wait_paced(1.0)
            self._hide_caption(cap)

        with self.narrated(SCRIPT["S4_transform_summary"]):
            cap = self._show_caption("Règle : extérieur vertical, intérieur horizontal.")
            self.play_paced(
                FadeOut(VGroup(p_final_formula, p_final_graph, vertex, vertex_label, graph_f, axes)),
                run_time=0.8,
            )
            summary = VGroup(
                MathTex(r"f(x)+k", r"\quad\Rightarrow\quad", r"\text{vertical}", font_size=30),
                MathTex(r"f(x-h)", r"\quad\Rightarrow\quad", r"\text{droite de }h", font_size=30),
                MathTex(r"f(kx)", r"\quad\Rightarrow\quad", r"\text{compression/étirement horizontal}", font_size=30),
                MathTex(r"-f(x)", r"\quad\Rightarrow\quad", r"\text{miroir axe }x", font_size=30),
                MathTex(r"f(-x)", r"\quad\Rightarrow\quad", r"\text{miroir axe }y", font_size=30),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
            summary.next_to(section_title, DOWN, buff=0.65)
            box = SurroundingRectangle(summary, color=BLACK, buff=0.16, stroke_width=2)
            self.play_paced(FadeIn(box), FadeIn(summary), run_time=0.9)
            self.wait_paced(2.2)
            self._hide_caption(cap)

        self.play_paced(
            FadeOut(VGroup(
                section_title, summary, box,
            )),
            run_time=1.0,
        )

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
            Text("7.  Transformations : extérieur vertical, intérieur horizontal.", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(s_title, DOWN, buff=0.42)

        with self.narrated(SCRIPT["S_summary"]):
            cap = self._show_caption("Résumé des propriétés.")
            self.play_paced(Write(s_title), run_time=0.8)
            for bullet in bullets:
                self.play_paced(FadeIn(bullet, shift=RIGHT * 0.15), run_time=0.5)
            self.wait_paced(4.0)
            self._hide_caption(cap)

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
        self._section_transformations()
        self._section_summary()

        self.wait(1.0)
