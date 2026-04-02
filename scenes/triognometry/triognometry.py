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
        "On part d'un cercle de rayon 1, appelé cercle trigonométrique. "
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
        f"Quand le point tourne sur le cercle unité, sa coordonnée verticale varie entre moins 1{ET} 1. "
        "Et par définition, pour un angle thêta, on appelle sinus de thêta "
        "la hauteur du point sur le cercle, autrement dit sa coordonnée {Y}. "
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
    # contributed by heejin_park, https://infograph.tistory.com/230

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

    def construct(self):
        self._setup_voiceover()
        self.show_intro_static()
        self.show_axis()
        self.show_circle()
        self.move_dot_and_draw_curve()
        self.wait()

    # ------------------------------------------------------------------
    # Static scene builders
    # ------------------------------------------------------------------

    def show_axis(self):
        x_start = np.array([-6, 0, 0])
        x_end   = np.array([ 6, 0, 0])
        y_start = np.array([-4, -2, 0])
        y_end   = np.array([-4,  2, 0])

        x_axis = Line(x_start, x_end)
        y_axis = Line(y_start, y_end)

        self.add(x_axis, y_axis)
        self.add_x_labels()

        self.origin_point = np.array([-5, 0, 0])  # right edge at x=-4, tangent to y-axis
        self.curve_start  = np.array([-4, 0, 0])  # curve starts at y-axis

    def add_x_labels(self):
        x_labels = [
            MathTex(r"\pi"), MathTex(r"2\pi"), MathTex(r"3\pi"),
        ]
        for i, label in enumerate(x_labels):
            label.next_to(np.array([-4 + (i + 1) * np.pi, 0, 0]), DOWN)
            self.add(label)

    def show_circle(self):
        circle = Circle(radius=1)
        circle.move_to(self.origin_point)
        self.add(circle)
        self.circle = circle

    def show_intro_static(self):
        """P0 — Static intro: frozen circle with θ arc label and title."""
        # Title
        title = Text("Qu'est-ce que le sinus ?", font_size=36, color=WHITE)
        title.to_edge(UP, buff=0.4)

        # Circle centered at origin for the intro (before show_axis moves it)
        intro_center = np.array([0, 0, 0])
        intro_circle = Circle(radius=1.5, color=WHITE)
        intro_circle.move_to(intro_center)

        # Dot at 35°
        theta_val = 35 * DEGREES
        dot_pos = intro_center + 1.5 * np.array([np.cos(theta_val), np.sin(theta_val), 0])
        intro_dot = Dot(dot_pos, radius=0.08, color=YELLOW)

        # Radius line
        radius_line = Line(intro_center, dot_pos, color=BLUE, stroke_width=3)

        # Horizontal reference line (x-axis stub)
        x_ref = Line(intro_center, intro_center + RIGHT * 1.5, color=WHITE, stroke_width=2)
        start_dot = Dot(intro_center + RIGHT * 1.5, radius=0.06, color=WHITE)

        # Arc from 0 to theta_val
        theta_arc = Arc(
            radius=0.55,
            start_angle=0,
            angle=theta_val,
            arc_center=intro_center,
            color=GREEN,
            stroke_width=3,
        )

        # θ label next to the arc midpoint
        arc_mid_angle = theta_val / 2
        theta_label = MathTex(r"\theta", color=GREEN).scale(0.9)
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
    # Main animation — 6 phased narration blocks
    # ------------------------------------------------------------------

    def move_dot_and_draw_curve(self):
        orbit        = self.circle
        origin_point = self.origin_point
        start_point  = orbit.point_from_proportion(0)

        dot = Dot(radius=0.08, color=YELLOW)
        dot.move_to(orbit.point_from_proportion(0))
        self.t_offset = 0
        rate = 0.125

        # ---- Updater functions ----------------------------------------

        def go_around_circle(mob, dt):
            self.t_offset += dt * rate
            mob.move_to(orbit.point_from_proportion(self.t_offset % 1))

        def get_line_to_circle():
            return Line(origin_point, dot.get_center(), color=BLUE)

        def get_line_to_curve():
            x = self.curve_start[0] + (self.t_offset - self.curve_t_start) * 2 * np.pi
            y = dot.get_center()[1]
            return Line(dot.get_center(), np.array([x, y, 0]),
                        color=YELLOW_A, stroke_width=2)

        self.curve = VGroup()
        self.curve.add(Line(self.curve_start, self.curve_start))
        self.curve_t_start = 0  # will be set when curve drawing begins

        def get_curve():
            last_line = self.curve[-1]
            x = self.curve_start[0] + (self.t_offset - self.curve_t_start) * 2 * np.pi
            y = dot.get_center()[1]
            new_line = Line(last_line.get_end(), np.array([x, y, 0]), color=YELLOW_D)
            self.curve.add(new_line)
            return self.curve

        def get_travel_arc():
            center      = orbit.get_center()
            start_angle = angle_of_vector(start_point - center)
            proportion  = self.t_offset % 1
            return Arc(
                radius=float(np.linalg.norm(start_point - center)),
                start_angle=start_angle,
                angle=TAU * proportion,
                arc_center=center,
                color=GREEN,
                stroke_width=6,
            )

        def get_travel_line():
            return Line(
                origin_point,
                np.array([self.curve_start[0] + (self.t_offset - self.curve_t_start) * 2 * np.pi, 0, 0]),
                color=GREEN,
                stroke_width=6,
            )


        # ---- Build always_redraw mobjects ------------------------------

        origin_to_circle_line = always_redraw(get_line_to_circle)
        dot_to_curve_line     = always_redraw(get_line_to_curve)
        sine_curve_line       = always_redraw(get_curve)
        travel_arc            = always_redraw(get_travel_arc)
        travel_line           = always_redraw(get_travel_line)

        # ---- Phase 1 : Circle + dot + blue radius ---------------------
        # Script: P1_circle

        dot.add_updater(go_around_circle)
        self.add(dot, origin_to_circle_line)

        with self.narrated(SCRIPT["P1_circle"], fallback_wait=8.0):
            self.wait(8.0)

        # ---- Phase 2 : sin(θ) definition — vertical dashed line -------
        # Script: P2_sinus

        def get_sin_projection():
            dot_pos = dot.get_center()
            foot    = np.array([dot_pos[0], 0, 0])  # directly below dot on x-axis
            return DashedLine(foot, dot_pos, color=RED, stroke_width=2)

        sin_projection = always_redraw(get_sin_projection)

        sin_label = MathTex(r"\sin(\theta)", color=RED).scale(0.7)
        sin_label.add_updater(
            lambda m: m.next_to(
                np.array([dot.get_center()[0], dot.get_center()[1] / 2, 0]),
                LEFT, buff=0.1
            )
        )

        self.add(sin_projection, sin_label)

        with self.narrated(SCRIPT["P2_sinus"], fallback_wait=8.0):
            self.wait(8.0)

        # ---- Phase 3 : Green arc + green x-axis line ------------------
        # Script: P3_arc

        self.add(travel_arc, travel_line)

        with self.narrated(SCRIPT["P3_arc"], fallback_wait=7.0):
            self.wait(7.0)

        # ---- Phase 4 : Yellow bridge line (dot → curve) ---------------
        # Script: P4_bridge
        # Anchor curve x to current t_offset so it starts at curve_start
        self.curve_t_start = self.t_offset
        self.curve.add(Line(self.curve_start, self.curve_start))
        self.add(sine_curve_line)
        self.add(dot_to_curve_line)

        with self.narrated(SCRIPT["P4_bridge"], fallback_wait=8.0):
            self.wait(8.0)

        # ---- Phase 5 : Sine curve draws itself (2 full rotations) -----
        # Script: P5_curve
        # 1 orbit = 8 s at rate=0.125; 2 orbits = 16 s

        with self.narrated(SCRIPT["P5_curve"], fallback_wait=16.0):
            self.wait(16.0)

        # ---- Phase 6 : Summary text -----------------------------------
        # Script: P6_summary

        dot.remove_updater(go_around_circle)

        summary = Text(
            "Le sinus = hauteur d'un point\nsur le cercle unité.",
            font_size=24,
            color=WHITE,
        ).to_edge(DOWN, buff=0.3)

        with self.narrated(SCRIPT["P6_summary"], fallback_wait=9.0):
            self.play(FadeIn(summary))
            self.wait(8.0)

        self.play(FadeOut(summary))
