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


# ---------------------------------------------------------------------------
# Project visual defaults: whiteboard style
# ---------------------------------------------------------------------------

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

INK = BLACK
CIRCLE_COLOR = GREY_D
RADIUS_COLOR = BLUE_D
HEIGHT_COLOR = RED_D
ANGLE_COLOR = GREEN_D
CURVE_COLOR = ORANGE
LIGHT_PANEL = BLUE_E

Y, ET = tts.Y, tts.ET


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


# ---------------------------------------------------------------------------
# SCRIPT — narration progressive, from intuition to formal mathematics
# ---------------------------------------------------------------------------

SCRIPT = {
    "P0_intro": (
        "Comment un point qui tourne sur un cercle peut-il produire une courbe en forme de vague ? "
        "C'est cette question qui permet de comprendre la fonction sinus, "
        "et pourquoi elle apparaît dans tant de phénomènes périodiques."
    ),
    "P1_circle": (
        "Commençons seulement avec le cercle unité, c'est-à-dire un cercle de rayon un. "
        "Le point orange part de la droite du cercle et tourne dans le sens inverse des aiguilles d'une montre. "
        "Le rayon bleu indique sa position. "
        "L'angle thêta mesure la rotation depuis la direction horizontale."
    ),
    "P2_sinus": (
        "Regardons maintenant une seule information : la hauteur du point par rapport au centre. "
        f"Elle varie entre moins un{ET}un. "
        "Par définition, le sinus de l'angle thêta est précisément cette hauteur, "
        f"autrement dit la coordonnée {Y} du point. "
        "En haut du cercle, le sinus vaut un. Sur l'axe horizontal, il vaut zéro. "
        "Et en bas du cercle, il vaut moins un."
    ),
    "P3_angle": (
        "Pour construire un graphique, il faut aussi une position horizontale. "
        "On utilise l'angle thêta, mesuré en radians. "
        "La longueur d'un arc vérifie la formule s égale r fois thêta. "
        "Ici, le rayon r vaut un, donc la longueur parcourue s est égale à thêta. "
        "On peut alors dérouler cet arc sur une ligne droite : "
        "plus le point tourne, plus on avance vers la droite."
    ),
    "P4_curve": (
        "À chaque angle thêta, on reporte la hauteur du point sur le graphique. "
        "Le point de droite a donc pour coordonnées thêta et sinus de thêta. "
        "À pi sur deux, la hauteur vaut un. "
        "À pi, elle revient à zéro. "
        "À trois pi sur deux, elle vaut moins un. "
        "Et à deux pi, après un tour complet, elle revient encore à zéro. "
        "L'ensemble de ces points forme le graphique d'équation y égale sinus de thêta."
    ),
    "P5_period": (
        "Que se passe-t-il si le point effectue un deuxième tour ? "
        "Le point bleu montre la position correspondante pendant le premier tour. "
        "Les deux points gardent toujours la même hauteur, avec un écart horizontal de deux pi. "
        "La valeur du sinus à l'angle thêta plus deux pi est donc la même qu'à l'angle thêta. "
        "On dit que le sinus est périodique de période deux pi."
    ),
    "P6_summary": (
        "Retenons les trois étapes. "
        "Premièrement, un point tourne sur le cercle unité. "
        "Deuxièmement, sa hauteur est sinus de thêta. "
        "Troisièmement, on place cette hauteur à l'abscisse thêta. "
        "La courbe du sinus est donc l'enregistrement de la hauteur d'un mouvement circulaire."
    ),
}


class SineCurveUnitCircle(VoiceoverScene if VoiceoverScene is not None else Scene):
    """Build the sine graph progressively from motion on the unit circle."""

    # The visual unit on the circle and on the graph's vertical axis is the same.
    UNIT_SCALE = 1.15
    ORIGIN_POINT = np.array([-5.15, 0.0, 0.0])
    CURVE_START = np.array([-3.55, 0.0, 0.0])

    # Four pi radians fit safely inside the 16:9 frame.
    X_SCALE = 0.74
    GRAPH_RIGHT = 6.05
    ANGLE_RULER_Y = -1.85

    # ------------------------------------------------------------------
    # Voiceover helpers
    # ------------------------------------------------------------------

    def _setup_voiceover(self):
        self._voiceover_enabled = False

        if load_dotenv is not None:
            load_dotenv()

        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            return

        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover not installed. Rendering without narration.")
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print("[voiceover] Missing Azure Speech credentials. Rendering without narration.")
            return

        self.set_speech_service(
            AzureService(voice=tts.VOICE_ID, global_speed=0.80)
        )
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text: str, fallback_duration: float = 5.0):
        """Yield a tracker without adding a second fallback wait after animations."""
        if self._voiceover_enabled:
            with self.voiceover(
                text=tts.ssml(text, "0%"),
                subcaption=tts.strip_ssml(text),
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker(duration=fallback_duration)

    @staticmethod
    def _duration(tracker, minimum: float) -> float:
        return max(minimum, float(getattr(tracker, "duration", minimum)))

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _circle_point(self, theta: float) -> np.ndarray:
        return self.ORIGIN_POINT + self.UNIT_SCALE * np.array(
            [np.cos(theta), np.sin(theta), 0.0]
        )

    def _curve_x(self, theta: float) -> float:
        return self.CURVE_START[0] + self.X_SCALE * theta

    def _graph_point(self, theta: float) -> np.ndarray:
        return np.array(
            [
                self._curve_x(theta),
                self.UNIT_SCALE * np.sin(theta),
                0.0,
            ]
        )

    def _phase_caption(self, text: str) -> Text:
        caption = Text(text, font_size=30, weight="MEDIUM")
        caption.to_edge(UP, buff=0.35)
        return caption

    def _replace_phase_caption(self, current: Text, new: Text) -> Text:
        self.play(FadeOut(current), run_time=0.25)
        self.play(FadeIn(new), run_time=0.35)
        return new

    def _animate_quarter_turns(
        self,
        theta: ValueTracker,
        start: float,
        total_duration: float,
    ):
        """Advance through four quarter-turns with short observation pauses."""
        pause = min(0.45, total_duration * 0.045)
        motion_time = max(0.8, (total_duration - 3 * pause) / 4)

        for index in range(1, 5):
            self.play(
                theta.animate.set_value(start + index * PI / 2),
                run_time=motion_time,
                rate_func=linear,
            )
            if index < 4:
                self.wait(pause)

    # ------------------------------------------------------------------
    # Scene
    # ------------------------------------------------------------------

    def construct(self):
        self._setup_voiceover()
        play_uqam_intro(self)
        self.show_intro_static()
        self._build_main_scene()
        self.wait(1.0)

    # ------------------------------------------------------------------
    # P0 — Central question
    # ------------------------------------------------------------------

    def show_intro_static(self):
        title = Text(
            "Comment un cercle dessine-t-il une vague ?",
            font_size=42,
            weight="BOLD",
        ).to_edge(UP, buff=0.5)

        subtitle = Text(
            "Du cercle unité à la fonction sinus",
            font_size=27,
            color=RADIUS_COLOR,
        ).next_to(title, DOWN, buff=0.22)

        center = DOWN * 0.35
        circle = Circle(radius=1.55, color=CIRCLE_COLOR, stroke_width=3).move_to(center)
        horizontal = Line(center + LEFT * 1.55, center + RIGHT * 1.55, color=INK, stroke_width=2)
        vertical = Line(center + DOWN * 1.55, center + UP * 1.55, color=INK, stroke_width=2)

        theta_value = 40 * DEGREES
        point = center + 1.55 * np.array(
            [np.cos(theta_value), np.sin(theta_value), 0.0]
        )
        radius = Line(center, point, color=RADIUS_COLOR, stroke_width=4)
        dot = Dot(point, radius=0.09, color=CURVE_COLOR)
        arc = Arc(
            radius=0.58,
            start_angle=0,
            angle=theta_value,
            arc_center=center,
            color=ANGLE_COLOR,
            stroke_width=4,
        )
        theta_label = MathTex(r"\theta", color=ANGLE_COLOR).scale(0.85)
        theta_label.move_to(center + 0.88 * np.array([np.cos(theta_value / 2), np.sin(theta_value / 2), 0]))

        diagram = VGroup(circle, horizontal, vertical, radius, dot, arc, theta_label)

        with self.narrated(SCRIPT["P0_intro"], fallback_duration=5.5) as tracker:
            duration = self._duration(tracker, 5.5)
            self.play(FadeIn(title), FadeIn(subtitle), run_time=0.18 * duration)
            self.play(Create(circle), Create(horizontal), Create(vertical), run_time=0.24 * duration)
            self.play(Create(radius), FadeIn(dot), run_time=0.18 * duration)
            self.play(Create(arc), FadeIn(theta_label), run_time=0.14 * duration)
            self.wait(max(0.8, 0.26 * duration))

        self.play(FadeOut(VGroup(title, subtitle, diagram)), run_time=0.8)

    # ------------------------------------------------------------------
    # P1–P6 — Main construction
    # ------------------------------------------------------------------

    def _build_main_scene(self):
        theta = ValueTracker(0.0)

        # Circle reference frame
        circle = Circle(
            radius=self.UNIT_SCALE,
            color=CIRCLE_COLOR,
            stroke_width=3,
        ).move_to(self.ORIGIN_POINT)
        circle_x_axis = Line(
            self.ORIGIN_POINT + LEFT * self.UNIT_SCALE,
            self.ORIGIN_POINT + RIGHT * self.UNIT_SCALE,
            color=INK,
            stroke_width=2,
        )
        circle_y_axis = Line(
            self.ORIGIN_POINT + DOWN * self.UNIT_SCALE,
            self.ORIGIN_POINT + UP * self.UNIT_SCALE,
            color=INK,
            stroke_width=2,
        )
        unit_label = MathTex(r"r=1", color=RADIUS_COLOR).scale(0.62)
        unit_label.next_to(circle, UP, buff=0.12).shift(LEFT * 0.28)

        moving_dot = always_redraw(
            lambda: Dot(
                self._circle_point(theta.get_value()),
                radius=0.085,
                color=CURVE_COLOR,
            ).set_z_index(6)
        )
        radius_line = always_redraw(
            lambda: Line(
                self.ORIGIN_POINT,
                self._circle_point(theta.get_value()),
                color=RADIUS_COLOR,
                stroke_width=4,
            ).set_z_index(4)
        )

        def make_angle_arc():
            remainder = theta.get_value() % TAU
            if np.isclose(remainder, 0.0) and theta.get_value() > 0:
                remainder = TAU
            if remainder < 1e-4:
                return VGroup()
            return Arc(
                radius=0.52,
                start_angle=0,
                angle=remainder,
                arc_center=self.ORIGIN_POINT,
                color=ANGLE_COLOR,
                stroke_width=4,
            ).set_z_index(3)

        def make_theta_label():
            remainder = theta.get_value() % TAU
            if np.isclose(remainder, 0.0) and theta.get_value() > 0:
                remainder = TAU
            if remainder < 0.16:
                return VGroup()
            middle = remainder / 2
            return MathTex(r"\theta", color=ANGLE_COLOR).scale(0.65).move_to(
                self.ORIGIN_POINT
                + 0.78 * np.array([np.cos(middle), np.sin(middle), 0.0])
            )

        angle_arc = always_redraw(make_angle_arc)
        theta_label = always_redraw(make_theta_label)

        # Height on the unit circle
        def make_height_projection():
            point = self._circle_point(theta.get_value())
            foot = np.array([point[0], self.ORIGIN_POINT[1], 0.0])
            if abs(point[1] - self.ORIGIN_POINT[1]) < 1e-4:
                return VGroup()
            return DashedLine(
                foot,
                point,
                color=HEIGHT_COLOR,
                stroke_width=3,
                dash_length=0.09,
            ).set_z_index(3)

        height_projection = always_redraw(make_height_projection)

        height_scale = VGroup(
            MathTex(r"1", color=HEIGHT_COLOR).scale(0.50).next_to(
                circle_y_axis.get_end(), RIGHT, buff=0.10
            ),
            MathTex(r"-1", color=HEIGHT_COLOR).scale(0.50).next_to(
                circle_y_axis.get_start(), RIGHT, buff=0.10
            ),
        )

        # Graph frame, introduced only after the circle is understood.
        graph_x_axis = Arrow(
            self.CURVE_START + LEFT * 0.08,
            np.array([self.GRAPH_RIGHT, 0.0, 0.0]),
            buff=0,
            color=INK,
            stroke_width=2.4,
            max_tip_length_to_length_ratio=0.018,
        )
        graph_y_axis = Arrow(
            self.CURVE_START + DOWN * 1.48,
            self.CURVE_START + UP * 1.55,
            buff=0,
            color=INK,
            stroke_width=2.4,
            max_tip_length_to_length_ratio=0.055,
        )
        x_axis_label = MathTex(r"\theta").scale(0.68)
        x_axis_label.next_to(graph_x_axis.get_end(), RIGHT, buff=0.10).shift(UP * 0.10)
        y_axis_label = MathTex("y").scale(0.68).next_to(graph_y_axis.get_end(), LEFT, buff=0.08)

        x_ticks = VGroup()
        x_labels = VGroup()
        for value, tex in [
            (0, "0"),
            (PI, r"\pi"),
            (TAU, r"2\pi"),
            (3 * PI, r"3\pi"),
            (2 * TAU, r"4\pi"),
        ]:
            x = self._curve_x(value)
            tick = Line(
                np.array([x, -0.08, 0.0]),
                np.array([x, 0.08, 0.0]),
                color=INK,
                stroke_width=2,
            )
            label = MathTex(tex).scale(0.55)
            label.next_to(np.array([x, 0.0, 0.0]), DOWN, buff=0.14)
            x_ticks.add(tick)
            x_labels.add(label)

        y_ticks = VGroup()
        y_labels = VGroup()
        for value, tex in [(1, "1"), (-1, "-1")]:
            y = value * self.UNIT_SCALE
            tick = Line(
                np.array([self.CURVE_START[0] - 0.08, y, 0.0]),
                np.array([self.CURVE_START[0] + 0.08, y, 0.0]),
                color=INK,
                stroke_width=2,
            )
            label = MathTex(tex).scale(0.52)
            label.next_to(np.array([self.CURVE_START[0], y, 0.0]), LEFT, buff=0.13)
            y_ticks.add(tick)
            y_labels.add(label)

        # The unrolled angle is shown on a separate ruler, not on top of the graph axis.
        angle_ruler_base = Line(
            np.array([self.CURVE_START[0], self.ANGLE_RULER_Y, 0.0]),
            np.array([self.GRAPH_RIGHT - 0.1, self.ANGLE_RULER_Y, 0.0]),
            color=GREY_B,
            stroke_width=2,
        )
        angle_progress = always_redraw(
            lambda: Line(
                np.array([self.CURVE_START[0], self.ANGLE_RULER_Y, 0.0]),
                np.array([
                    self._curve_x(theta.get_value()),
                    self.ANGLE_RULER_Y,
                    0.0,
                ]),
                color=ANGLE_COLOR,
                stroke_width=5,
            ).set_z_index(2)
        )
        angle_marker = always_redraw(
            lambda: Dot(
                np.array([
                    self._curve_x(theta.get_value()),
                    self.ANGLE_RULER_Y,
                    0.0,
                ]),
                radius=0.055,
                color=ANGLE_COLOR,
            ).set_z_index(5)
        )
        ruler_label = Text("angle déroulé", font_size=20, color=ANGLE_COLOR)
        ruler_label.next_to(angle_ruler_base, DOWN, buff=0.12).align_to(angle_ruler_base, LEFT)

        graph_dot = always_redraw(
            lambda: Dot(
                self._graph_point(theta.get_value()),
                radius=0.072,
                color=CURVE_COLOR,
            ).set_z_index(7)
        )
        bridge_line = always_redraw(
            lambda: DashedLine(
                self._circle_point(theta.get_value()),
                self._graph_point(theta.get_value()),
                color=HEIGHT_COLOR,
                stroke_width=1.8,
                stroke_opacity=0.34,
                dash_length=0.11,
            ).set_z_index(1)
        )

        # TracedPath synchronizes the curve exactly with the moving graph point.
        sine_trace = TracedPath(
            graph_dot.get_center,
            stroke_color=CURVE_COLOR,
            stroke_width=4,
        ).set_z_index(5)

        # ------------------------------------------------------------------
        # P1 — Motion first
        # ------------------------------------------------------------------
        caption = self._phase_caption("1. Un point tourne sur le cercle unité")

        with self.narrated(SCRIPT["P1_circle"], fallback_duration=9.0) as tracker:
            duration = self._duration(tracker, 9.0)
            self.play(FadeIn(caption), run_time=0.7)
            self.play(
                Create(circle),
                Create(circle_x_axis),
                Create(circle_y_axis),
                FadeIn(unit_label),
                run_time=min(1.6, 0.18 * duration),
            )
            self.add(radius_line, angle_arc, theta_label, moving_dot)
            remaining = max(4.5, duration - 2.3)
            self.play(
                theta.animate.set_value(TAU),
                run_time=remaining,
                rate_func=linear,
            )
            self.wait(0.6)

        # ------------------------------------------------------------------
        # P2 — Height defines sine
        # ------------------------------------------------------------------
        theta.set_value(0.0)  # same visible position as 2π
        next_caption = self._phase_caption("2. Le sinus est la hauteur du point")
        sine_definition = MathTex(r"\sin(\theta)=y", color=HEIGHT_COLOR).scale(1.05)
        sine_definition.move_to(np.array([1.45, 2.55, 0.0]))

        with self.narrated(SCRIPT["P2_sinus"], fallback_duration=12.0) as tracker:
            duration = self._duration(tracker, 12.0)
            caption = self._replace_phase_caption(caption, next_caption)
            self.play(FadeIn(sine_definition), FadeIn(height_scale), run_time=0.7)
            self.add(height_projection)
            self._animate_quarter_turns(
                theta,
                start=0.0,
                total_duration=max(7.0, duration - 1.4),
            )
            self.wait(0.8)

        # ------------------------------------------------------------------
        # P3 — Angle becomes horizontal position
        # ------------------------------------------------------------------
        theta.set_value(0.0)
        next_caption = self._phase_caption("3. L'angle devient la position horizontale")
        arc_formula = MathTex(r"s=r\theta", color=ANGLE_COLOR).scale(0.92)
        arc_formula.move_to(np.array([1.35, 2.48, 0.0]))
        unit_arc_formula = MathTex(
            r"r=1\quad\Longrightarrow\quad s=\theta",
            color=ANGLE_COLOR,
        ).scale(0.82)
        unit_arc_formula.move_to(arc_formula)

        with self.narrated(SCRIPT["P3_angle"], fallback_duration=11.0) as tracker:
            duration = self._duration(tracker, 11.0)
            caption = self._replace_phase_caption(caption, next_caption)
            self.play(
                FadeOut(sine_definition),
                FadeOut(height_projection),
                FadeOut(height_scale),
                run_time=0.7,
            )
            self.play(
                Create(graph_x_axis),
                FadeIn(VGroup(x_axis_label, x_ticks, x_labels)),
                run_time=1.2,
            )
            self.play(
                Create(angle_ruler_base),
                FadeIn(ruler_label),
                FadeIn(arc_formula),
                run_time=0.9,
            )
            self.play(TransformMatchingTex(arc_formula, unit_arc_formula), run_time=0.8)
            self.add(angle_progress, angle_marker)
            self.play(
                theta.animate.set_value(TAU),
                run_time=max(6.5, duration - 3.8),
                rate_func=linear,
            )
            self.wait(0.8)

        # ------------------------------------------------------------------
        # P4 — Record the height and obtain the first period
        # ------------------------------------------------------------------
        theta.set_value(0.0)
        next_caption = self._phase_caption("4. On enregistre la hauteur pour chaque angle")
        graph_point_formula = MathTex(
            r"(\theta,\,\sin(\theta))",
            color=CURVE_COLOR,
        ).scale(0.95)
        graph_point_formula.move_to(np.array([1.35, 2.48, 0.0]))
        sine_equation = MathTex(r"y=\sin(\theta)", color=CURVE_COLOR).scale(1.00)
        sine_equation.move_to(graph_point_formula)

        with self.narrated(SCRIPT["P4_curve"], fallback_duration=14.0) as tracker:
            duration = self._duration(tracker, 14.0)
            caption = self._replace_phase_caption(caption, next_caption)
            self.play(
                FadeOut(unit_arc_formula),
                FadeOut(angle_arc),
                FadeOut(theta_label),
                FadeOut(angle_ruler_base),
                FadeOut(ruler_label),
                FadeOut(angle_progress),
                FadeOut(angle_marker),
                FadeIn(height_scale),
                FadeIn(graph_point_formula),
                run_time=0.9,
            )
            self.play(
                Create(graph_y_axis),
                FadeIn(VGroup(y_axis_label, y_ticks, y_labels)),
                run_time=0.8,
            )
            self.add(height_projection, sine_trace, bridge_line, graph_dot)
            self._animate_quarter_turns(
                theta,
                start=0.0,
                total_duration=max(8.5, duration - 2.6),
            )
            self.play(Transform(graph_point_formula, sine_equation), run_time=0.8)
            self.wait(1.0)

        # ------------------------------------------------------------------
        # P5 — Repeat the motion and formalize periodicity
        # ------------------------------------------------------------------
        next_caption = self._phase_caption("5. Un tour de plus répète le même motif")
        periodic_formula = MathTex(
            r"\sin(\theta+2\pi)=\sin(\theta)",
            color=RADIUS_COLOR,
        ).scale(0.95)
        periodic_formula.move_to(np.array([1.35, 2.48, 0.0]))

        period_reference_dot = Dot(
            self._graph_point(0.0),
            radius=0.062,
            color=RADIUS_COLOR,
        ).set_z_index(7)
        period_reference_dot.add_updater(
            lambda mob: mob.move_to(self._graph_point(theta.get_value() - TAU))
        )

        period_connector = always_redraw(
            lambda: DashedLine(
                self._graph_point(theta.get_value() - TAU),
                self._graph_point(theta.get_value()),
                color=RADIUS_COLOR,
                stroke_width=2.0,
                stroke_opacity=0.55,
                dash_length=0.10,
            ).set_z_index(3)
        )

        same_height_label = Text(
            "même hauteur",
            font_size=17,
            color=RADIUS_COLOR,
        ).set_z_index(8)
        same_height_label.add_updater(
            lambda mob: mob.move_to(
                (
                    self._graph_point(theta.get_value() - TAU)
                    + self._graph_point(theta.get_value())
                )
                / 2
                + UP * 0.20
            )
        )

        with self.narrated(SCRIPT["P5_period"], fallback_duration=14.0) as tracker:
            duration = self._duration(tracker, 14.0)
            caption = self._replace_phase_caption(caption, next_caption)
            self.play(
                FadeOut(graph_point_formula),
                FadeOut(bridge_line),
                FadeOut(height_projection),
                FadeOut(height_scale),
                FadeIn(periodic_formula),
                run_time=0.8,
            )
            self.add(period_connector, period_reference_dot, same_height_label)
            motion_duration = max(7.0, 0.70 * duration)
            self.play(
                theta.animate.set_value(2 * TAU),
                run_time=motion_duration,
                rate_func=linear,
            )

            first_peak = self._graph_point(PI / 2)
            second_peak = self._graph_point(PI / 2 + TAU)
            peak_dots = VGroup(
                Dot(first_peak, radius=0.07, color=RADIUS_COLOR),
                Dot(second_peak, radius=0.07, color=RADIUS_COLOR),
            )
            period_arrow = DoubleArrow(
                np.array([first_peak[0], 1.56, 0.0]),
                np.array([second_peak[0], 1.56, 0.0]),
                buff=0,
                color=RADIUS_COLOR,
                stroke_width=3,
                tip_length=0.13,
            )
            period_label = MathTex(r"2\pi", color=RADIUS_COLOR).scale(0.62)
            period_label.next_to(period_arrow, UP, buff=0.08)
            period_markers = VGroup(peak_dots, period_arrow, period_label)

            self.play(
                FadeOut(period_connector),
                FadeOut(period_reference_dot),
                FadeOut(same_height_label),
                FadeIn(period_markers),
                run_time=0.9,
            )
            remaining_hold = duration - 0.8 - motion_duration - 0.9
            self.wait(max(1.4, remaining_hold + 0.2))

        # ------------------------------------------------------------------
        # P6 — Clean final synthesis
        # ------------------------------------------------------------------
        with self.narrated(SCRIPT["P6_summary"], fallback_duration=11.0) as tracker:
            duration = self._duration(tracker, 11.0)
            self.play(*[FadeOut(mob) for mob in list(self.mobjects)], run_time=0.9)

            summary_title = Text("À retenir", font_size=42, weight="BOLD")
            summary_title.to_edge(UP, buff=0.65)

            summary_lines = VGroup(
                Text("1. Le point tourne sur le cercle unité.", font_size=29),
                Text("2. Sa hauteur vaut sin(θ).", font_size=29),
                Text("3. On reporte cette hauteur à l'abscisse θ.", font_size=29),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.38)

            summary_formula = MathTex(
                r"\text{point du graphe }=(\theta,\sin\theta)",
                r"\qquad",
                r"\sin(\theta+2\pi)=\sin\theta",
            ).scale(0.82)
            summary_formula[0].set_color(CURVE_COLOR)
            summary_formula[2].set_color(RADIUS_COLOR)

            content = VGroup(summary_lines, summary_formula).arrange(DOWN, buff=0.65)
            panel = RoundedRectangle(
                corner_radius=0.18,
                width=11.2,
                height=4.4,
                stroke_color=RADIUS_COLOR,
                stroke_width=2.5,
                fill_color=LIGHT_PANEL,
                fill_opacity=0.06,
            )
            content.move_to(panel)
            final_group = VGroup(panel, content)
            final_group.next_to(summary_title, DOWN, buff=0.42)

            self.play(FadeIn(summary_title), FadeIn(final_group), run_time=1.1)
            self.wait(max(4.0, duration - 2.0))
