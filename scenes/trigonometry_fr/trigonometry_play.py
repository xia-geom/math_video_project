from manim import *
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

import tools.tts as tts
from tools.branding import play_uqam_intro

# Short aliases — used throughout the SCRIPT dict below.
A, B, C, Y, ET = tts.A, tts.B, tts.C, tts.Y, tts.ET

@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


# ---------------------------------------------------------------------------
# SCRIPT  (full French narration, split by scene phase)
# ---------------------------------------------------------------------------

SCRIPT = {
    # P0 — Introduction statique
    "P0_intro": (
        "Dans cette vidéo, on va comprendre ce qu'est la fonction sinus. "
        "On part d'un cercle de rayon un, appelé cercle trigonométrique. "
        "Un point se déplace sur ce cercle, et l'angle thêta mesure sa position "
        "depuis l'axe horizontal, en tournant dans le sens anti-horaire."
    ),

    # P1 — Le cercle trigonométrique et le rayon
    "P1_circle": (
        "À gauche, on voit un cercle de rayon 1 : c'est le cercle trigonométrique. "
        "Le point jaune se déplace dessus de façon régulière. "
        "À chaque instant, ce point correspond à un angle thêta, "
        "mesuré depuis le point de départ sur le cercle, en tournant dans le sens anti-horaire. "
        "La droite bleue relie le centre du cercle au point : "
        "elle matérialise le rayon, donc un vecteur de norme 1."
    ),

    # P2 — Définition du sinus comme coordonnée verticale
    "P2_sinus": (
        "L'idée clé, c'est que ce mouvement circulaire contient déjà la fonction sinus. "
        f"Quand le point tourne sur le cercle unité, sa coordonnée verticale varie entre moins un{ET}un. "
        "Et par définition, pour un angle thêta, on appelle sinus de thêta "
        f"la hauteur du point sur le cercle, autrement dit sa coordonnée {Y}. "
        "Donc, tant que le point tourne, la valeur de sinus de thêta n'est rien d'autre que "
        "à quelle hauteur se trouve le point jaune."
    ),

    # P3 — L'arc et la ligne verte : déroulement de l'angle
    "P3_arc": (
        "Maintenant, on veut transformer cette variation de hauteur en une courbe : la courbe du sinus. "
        "Pour ça, on fait correspondre l'angle thêta à une position horizontale sur l'axe du bas. "
        "L'arc vert sur le cercle représente l'angle parcouru, "
        "et la ligne verte sur l'axe horizontal représente ce même avancement, "
        "mais reporté en ligne droite : "
        "à mesure que l'angle augmente, on avance vers la droite."
    ),

    # P4 — Le pont jaune entre le cercle et le graphique
    "P4_bridge": (
        "À chaque instant, on prend alors la hauteur du point sur le cercle, "
        "et on la transporte sur le repère de droite : "
        "la petite ligne jaune joue le rôle de pont entre le point en mouvement "
        "et le point correspondant sur le graphique. "
        "Quand le point est au-dessus de l'axe, sinus de thêta est positif ; "
        "quand il est en dessous, sinus de thêta est négatif ; "
        "et quand il coupe l'axe horizontal, sinus de thêta est égal à zéro."
    ),

    # P5 — La courbe s'allonge et la périodicité apparaît
    "P5_curve": (
        "Et c'est là que la courbe apparaît : "
        "le tracé jaune foncé s'allonge en enregistrant, pour chaque angle thêta, la valeur sinus de thêta. "
        "On retrouve les repères classiques : à thêta égal pi la courbe revient à zéro, "
        "à thêta égal deux pi elle revient encore à zéro après un tour complet, "
        "puis le motif recommence. "
        "Cette répétition n'est pas un truc de dessin : "
        "c'est une propriété du mouvement circulaire lui-même. "
        "Un tour de plus, c'est le même cycle, "
        "donc la fonction est périodique de période deux pi."
    ),

    # P6 — Résumé
    "P6_summary": (
        "En résumé : le sinus, c'est la hauteur d'un point qui tourne sur le cercle unité. "
        "Et la courbe du sinus, c'est l'enregistrement de cette hauteur au fil de l'angle thêta, "
        "comme si on déroulait le cercle dans le temps "
        "et qu'on notait, instant après instant, la valeur obtenue."
    ),
}


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class SineCurveUnitCircle(VoiceoverScene if VoiceoverScene is not None else Scene):
    """
    Refactored version using ValueTracker + self.play instead of dt-updaters.

    All positions are derived analytically from the angle ValueTracker `theta`.
    The dot, blue radius, red sin-projection, green arc/travel-line, and yellow
    bridge line are all always_redraw objects driven by `theta.get_value()`.
    The sine curve itself is a ParametricFunction revealed via Create().
    """

    # ------------------------------------------------------------------
    # Layout constants
    # ------------------------------------------------------------------
    ORIGIN_POINT  = np.array([-5, 0, 0])   # circle center; right edge tangent to y-axis at x=-4
    CURVE_START   = np.array([-4, 0, 0])   # sine curve starts at the y-axis
    CIRCLE_RADIUS = 1.0
    # Horizontal scale: one full period (2π radians) maps to 2π screen units
    X_SCALE       = 1.0   # screen units per radian  (so 2π rad → 2π units)

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
            print("[voiceover] Missing Azure Speech credentials. Rendering without narration.")
            return
        self.set_speech_service(AzureService(voice=tts.VOICE_ID, global_speed=0.80))
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text: str, fallback_wait: float = 4.0):
        """Context manager: plays voiceover if enabled, otherwise waits fallback_wait seconds."""
        if self._voiceover_enabled:
            with self.voiceover(text=tts.ssml(text, "0%"), subcaption=tts.strip_ssml(text)) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker(duration=fallback_wait)
            self.wait(fallback_wait)

    # ------------------------------------------------------------------
    # Analytical helpers  (pure functions of theta value)
    # ------------------------------------------------------------------

    def _dot_pos(self, theta: float) -> np.ndarray:
        """Position of the dot on the circle for angle theta (radians)."""
        cx, cy, _ = self.ORIGIN_POINT
        return np.array([
            cx + self.CIRCLE_RADIUS * np.cos(theta),
            cy + self.CIRCLE_RADIUS * np.sin(theta),
            0,
        ])

    def _curve_x(self, theta: float) -> float:
        """Horizontal position on the sine curve for angle theta."""
        return self.CURVE_START[0] + theta * self.X_SCALE

    # ------------------------------------------------------------------
    # construct
    # ------------------------------------------------------------------

    def construct(self):
        self._setup_voiceover()
        play_uqam_intro(self)
        self.show_intro_static()
        self._build_main_scene()
        self.wait()

    # ------------------------------------------------------------------
    # Static intro (P0)
    # ------------------------------------------------------------------

    def show_intro_static(self):
        """P0 — Static intro: frozen circle with θ arc label and title."""
        title = Text("Qu'est-ce que le sinus ?", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.4)

        intro_center = np.array([0, 0, 0])
        intro_circle = Circle(radius=1.5, color=WHITE)
        intro_circle.move_to(intro_center)

        theta_val = 35 * DEGREES
        dot_pos   = intro_center + 1.5 * np.array([np.cos(theta_val), np.sin(theta_val), 0])
        intro_dot = Dot(dot_pos, radius=0.08, color=YELLOW)

        radius_line = Line(intro_center, dot_pos, color=BLUE, stroke_width=3)
        x_ref       = Line(intro_center, intro_center + RIGHT * 1.5, color=WHITE, stroke_width=2)
        start_dot   = Dot(intro_center + RIGHT * 1.5, radius=0.06, color=WHITE)

        theta_arc = Arc(
            radius=0.55,
            start_angle=0,
            angle=theta_val,
            arc_center=intro_center,
            color=GREEN,
            stroke_width=3,
        )

        arc_mid_angle = theta_val / 2
        theta_label   = MathTex(r"\theta", color=GREEN).scale(0.9)
        theta_label.move_to(
            intro_center + 0.85 * np.array([np.cos(arc_mid_angle), np.sin(arc_mid_angle), 0])
        )

        intro_group = VGroup(
            intro_circle, radius_line, x_ref, start_dot,
            theta_arc, theta_label, intro_dot,
        )

        with self.narrated(SCRIPT["P0_intro"], fallback_wait=7.0):
            self.play(FadeIn(title), run_time=0.8)
            self.play(Create(intro_circle), Create(x_ref), FadeIn(start_dot), run_time=1.0)
            self.play(Create(radius_line), FadeIn(intro_dot), run_time=0.8)
            self.play(Create(theta_arc), FadeIn(theta_label), run_time=0.7)
            self.wait(4.0)

        self.play(FadeOut(VGroup(title, intro_group)), run_time=0.8)

    # ------------------------------------------------------------------
    # Main scene  (P1 – P6)
    # ------------------------------------------------------------------

    def _build_main_scene(self):
        # ---- Static layout ------------------------------------------------
        x_start = np.array([-6, 0, 0])
        x_end   = np.array([ 6, 0, 0])
        y_start = np.array([-4, -2, 0])
        y_end   = np.array([-4,  2, 0])

        x_axis = Line(x_start, x_end)
        y_axis = Line(y_start, y_end)
        self.add(x_axis, y_axis)
        self._add_x_labels()

        circle = Circle(radius=self.CIRCLE_RADIUS)
        circle.move_to(self.ORIGIN_POINT)
        self.add(circle)

        # ---- Angle tracker ------------------------------------------------
        # theta goes from 0 upward (counterclockwise).
        # We animate theta from 0 → 4π (two full rotations).
        theta = ValueTracker(0.0)

        # ---- Dot ----------------------------------------------------------
        dot = always_redraw(
            lambda: Dot(self._dot_pos(theta.get_value()), radius=0.08, color=YELLOW)
        )

        # ---- Blue radius line (center → dot) ------------------------------
        radius_line = always_redraw(
            lambda: Line(
                self.ORIGIN_POINT,
                self._dot_pos(theta.get_value()),
                color=BLUE,
            )
        )

        # ---- Red vertical sin-projection (dot → x-axis) -------------------
        def _make_sin_projection():
            dp   = self._dot_pos(theta.get_value())
            foot = np.array([dp[0], 0, 0])
            # Avoid zero-length line at θ=0 and θ=π
            if abs(dp[1]) < 1e-6:
                return VGroup()   # invisible placeholder
            return DashedLine(foot, dp, color=RED, stroke_width=2)

        sin_projection = always_redraw(_make_sin_projection)

        sin_label = always_redraw(
            lambda: MathTex(r"\sin(\theta)", color=RED).scale(0.7).next_to(
                np.array([
                    self._dot_pos(theta.get_value())[0],
                    self._dot_pos(theta.get_value())[1] / 2,
                    0,
                ]),
                LEFT, buff=0.1,
            )
        )

        # ---- Green travel arc (swept angle on circle) ---------------------
        def _make_travel_arc():
            t = theta.get_value()
            if t < 1e-6:
                return VGroup()
            return Arc(
                radius=self.CIRCLE_RADIUS,
                start_angle=0,
                angle=t % TAU if (t % TAU) > 1e-6 else TAU,
                arc_center=self.ORIGIN_POINT,
                color=GREEN,
                stroke_width=6,
            )

        travel_arc = always_redraw(_make_travel_arc)

        # ---- Green travel line (x-axis progress) --------------------------
        travel_line = always_redraw(
            lambda: Line(
                self.CURVE_START,
                np.array([self._curve_x(theta.get_value()), 0, 0]),
                color=GREEN,
                stroke_width=6,
            )
        )

        # ---- Yellow bridge line (dot → curve point) -----------------------
        bridge_line = always_redraw(
            lambda: Line(
                self._dot_pos(theta.get_value()),
                np.array([
                    self._curve_x(theta.get_value()),
                    self._dot_pos(theta.get_value())[1],
                    0,
                ]),
                color=YELLOW_A, stroke_width=2,
            )
        )

        # ---- Sine curve as two ParametricFunctions (one per rotation) -----
        # Each segment spans exactly one full rotation [0, 2π] / [2π, 4π],
        # so Create(segment) takes the same time as theta crossing that range.
        def _make_sine_segment(t_start: float) -> ParametricFunction:
            return ParametricFunction(
                lambda t: np.array([self._curve_x(t_start + t), np.sin(t_start + t), 0]),
                t_range=[0, TAU],
                color=YELLOW_D,
                stroke_width=3,
            )

        sine_curve_1 = _make_sine_segment(0)       # first rotation:  θ ∈ [0,   2π]
        sine_curve_2 = _make_sine_segment(TAU)     # second rotation: θ ∈ [2π,  4π]

        # ==================================================================
        # Phase 1 — Circle + dot + blue radius (P1_circle)
        # ==================================================================
        self.add(dot, radius_line)

        # Animate one full rotation during the narration
        with self.narrated(SCRIPT["P1_circle"], fallback_wait=8.0):
            self.play(
                theta.animate.set_value(TAU),
                run_time=8.0,
                rate_func=linear,
            )

        # ==================================================================
        # Phase 2 — Sin projection (P2_sinus)
        # ==================================================================
        self.add(sin_projection, sin_label)

        with self.narrated(SCRIPT["P2_sinus"], fallback_wait=8.0):
            self.play(
                theta.animate.set_value(2 * TAU),
                run_time=8.0,
                rate_func=linear,
            )

        # ==================================================================
        # Phase 3 — Green arc + travel line (P3_arc)
        # ==================================================================
        # Reset theta to 0 so arc/line start fresh from the beginning
        theta.set_value(0.0)
        self.add(travel_arc, travel_line)

        with self.narrated(SCRIPT["P3_arc"], fallback_wait=7.0):
            self.play(
                theta.animate.set_value(TAU),
                run_time=7.0,
                rate_func=linear,
            )

        # ==================================================================
        # Phase 4 — Yellow bridge + curve starts drawing (P4_bridge)
        # ==================================================================
        # Reset to 0 so curve and bridge are anchored to curve_start
        theta.set_value(0.0)
        self.add(bridge_line)

        with self.narrated(SCRIPT["P4_bridge"], fallback_wait=8.0):
            self.play(
                Create(sine_curve_1),
                theta.animate.set_value(TAU),
                run_time=8.0,
                rate_func=linear,
            )

        # ==================================================================
        # Phase 5 — Curve completes 2nd rotation (P5_curve)
        # ==================================================================
        # Reset theta to 0 so the dot/bridge/arc still track correctly,
        # while sine_curve_2 is positioned at the 2π offset via _make_sine_segment.
# Phase 5 — keep theta at TAU and animate to 2*TAU
        with self.narrated(SCRIPT["P5_curve"], fallback_wait=16.0):
            self.play(
                Create(sine_curve_2),
                theta.animate.set_value(2 * TAU),
                run_time=16.0,
                rate_func=linear,
            )

        # ==================================================================
        # Phase 6 — Summary (P6_summary)
        # ==================================================================
        summary = Text(
            "Le sinus = hauteur d'un point\nsur le cercle unité.",
            font_size=24,
            color=WHITE,
        ).to_edge(DOWN, buff=0.3)

        with self.narrated(SCRIPT["P6_summary"], fallback_wait=9.0):
            self.play(FadeIn(summary))
            self.wait(8.0)

        self.play(FadeOut(summary))

    # ------------------------------------------------------------------
    # X-axis labels
    # ------------------------------------------------------------------

    def _add_x_labels(self):
        x_labels = [MathTex(r"\pi"), MathTex(r"2\pi"), MathTex(r"3\pi")]
        for i, label in enumerate(x_labels):
            label.next_to(np.array([-4 + (i + 1) * np.pi, 0, 0]), DOWN)
            self.add(label)
