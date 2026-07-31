from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

import numpy as np
from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GRAY_B,
    GRAY_C,
    GRAY_D,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    NumberPlane,
    Scene,
    Tex,
    Text,
    VGroup,
    Write,
    config,
)

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional local convenience
    load_dotenv = None

try:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.azure import AzureService
except ImportError:  # pragma: no cover - silent standalone fallback
    VoiceoverScene = Scene
    AzureService = None

try:
    import tools.tts as tts
except ImportError:  # pragma: no cover - standalone syntax/preview fallback
    class _TTSFallback:
        VOICE_ID = "fr-CA-SylvieNeural"

        @staticmethod
        def ssml(text: str, rate: str = "-14%") -> str:
            return text

        @staticmethod
        def strip_ssml(text: str) -> str:
            import re

            return re.sub(r"<[^>]+>", "", text).replace("  ", " ").strip()

        @staticmethod
        def char(letter: str) -> str:
            return letter

    tts = _TTSFallback()

try:
    from tools.branding import play_uqam_intro
except ImportError:  # pragma: no cover - standalone preview fallback
    def play_uqam_intro(scene: Scene) -> None:
        return None


config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D

A_SPOKEN = tts.char("A")
B_SPOKEN = tts.char("B")
X_SPOKEN = tts.char("x")
Y_SPOKEN = tts.char("y")
Z_SPOKEN = tts.char("z")


SCRIPT = {
    "intro": (
        "Deux positions sont connues. Comment trouver la distance directe entre elles, "
        "et le point exactement à mi-chemin? "
        "<bookmark mark='intro_points'/> "
        f"Ici, pour aller de {A_SPOKEN} vers {B_SPOKEN} en suivant les axes, "
        "on parcourt quatre unités, puis trois. "
        "<bookmark mark='intro_route'/> Le trajet mesure donc sept unités. "
        "<bookmark mark='intro_direct'/> Mais la distance directe est plus courte. "
        "Nous allons construire une méthode qui fonctionne dans le plan, puis dans l'espace."
    ),
    "r2": (
        "Commençons dans le plan. "
        f"<bookmark mark='r2_a'/> Le point {A_SPOKEN} a pour coordonnées moins deux, moins un. "
        f"<bookmark mark='r2_b'/> Le point {B_SPOKEN} a pour coordonnées deux, deux. "
        "<bookmark mark='r2_components'/> Pour connaître le déplacement, on fait arrivée moins départ, "
        "coordonnée par coordonnée. On obtient quatre horizontalement et trois verticalement. "
        f"<bookmark mark='r2_vector'/> Ainsi, le vecteur {A_SPOKEN} {B_SPOKEN} vaut quatre, trois. "
        "<bookmark mark='r2_route'/> Le trajet en deux étapes mesure quatre plus trois, donc sept. "
        "<bookmark mark='r2_distance'/> La distance directe est plutôt la longueur du vecteur. "
        "Le triangle rectangle donne la racine de quatre au carré plus trois au carré. "
        "<bookmark mark='r2_result'/> La distance directe vaut donc cinq. "
        "<bookmark mark='r2_warning'/> Il ne faut pas confondre la longueur d'un trajet "
        "avec la distance directe entre ses extrémités."
    ),
    "midpoint_r2": (
        "Cherchons maintenant le point à mi-chemin. "
        "<bookmark mark='mid_dot'/> Il doit se trouver sur le segment qui relie les deux positions. "
        "<bookmark mark='mid_formula'/> On moyenne séparément les coordonnées de départ et d'arrivée. "
        "Ici, le milieu est zéro, un demi. "
        f"<bookmark mark='mid_equal'/> Il est à la même distance de {A_SPOKEN} et de {B_SPOKEN}."
    ),
    "r3": (
        "Passons à l'espace avec un drone. "
        "<bookmark mark='r3_xy_axes'/> Les deux premières directions forment le plan horizontal. "
        "<bookmark mark='r3_z_axis'/> Une troisième coordonnée ajoute la direction verticale. "
        "Le schéma est dessiné en perspective; dans l'espace, les trois axes sont perpendiculaires. "
        f"<bookmark mark='r3_a'/> Le drone part du point {A_SPOKEN}, de coordonnées un, zéro, zéro. "
        f"<bookmark mark='r3_b'/> Il arrive au point {B_SPOKEN}, de coordonnées quatre, deux, deux. "
        "<bookmark mark='r3_components'/> Arrivée moins départ donne trois, deux, deux. "
        f"<bookmark mark='r3_vector'/> C'est le vecteur direct de {A_SPOKEN} vers {B_SPOKEN}. "
        "<bookmark mark='r3_route'/> En suivant successivement les trois directions, "
        "le trajet mesure encore trois plus deux plus deux, donc sept. "
        "<bookmark mark='r3_distance'/> La distance directe est la norme du vecteur : "
        "racine de trois au carré plus deux au carré plus deux au carré. "
        "Elle vaut racine de dix-sept, soit environ quatre virgule douze. "
        "<bookmark mark='r3_mid'/> Le milieu s'obtient encore en moyennant les coordonnées. "
        "On trouve cinq demis, un, un."
    ),
    "summary": (
        "La méthode tient en trois étapes. "
        f"<bookmark mark='summary_vector'/> Premièrement, le déplacement est {B_SPOKEN} moins {A_SPOKEN}. "
        "<bookmark mark='summary_distance'/> Deuxièmement, la distance directe est la norme de ce vecteur. "
        "<bookmark mark='summary_midpoint'/> Troisièmement, le milieu est la moyenne des deux positions. "
        "<bookmark mark='summary_r2r3'/> Dans R deux, on calcule avec deux coordonnées. "
        "Dans R trois, on fait exactement les mêmes opérations avec trois coordonnées."
    ),
}


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class VecteursR2R3FR(VoiceoverScene):
    """Distance et milieu dans R² puis R³.

    Cette deuxième passe évite de répéter la vidéo d'introduction aux vecteurs.
    La scène suppose déjà connue l'idée qu'un vecteur décrit un déplacement et
    concentre l'attention sur trois calculs réutilisables : B-A, la norme et le milieu.
    """

    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False

        if load_dotenv is not None:
            load_dotenv()

        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            print("[voiceover] Disabled by MANIM_DISABLE_VOICEOVER.")
            return

        if AzureService is None:
            print("[voiceover] manim-voiceover is unavailable. Rendering silently.")
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            print("[voiceover] Azure credentials missing. Rendering silently.")
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)

        try:
            # Pronunciation rate is already centralized in tools.tts.ssml().
            self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        except Exception as exc:  # pragma: no cover - external service setup
            print(f"[voiceover] Azure setup failed: {exc}. Rendering silently.")
            return

        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text: str):
        if self._voiceover_enabled:
            with self.voiceover(
                text=tts.ssml(text),
                subcaption=tts.strip_ssml(text),
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_until_bookmark(self, mark: str) -> None:
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)
        else:
            # Silent previews remain readable instead of collapsing all bookmarked
            # actions into a rapid sequence.
            self.wait(0.22)

    def _title(self, text: str, *, size: int = 44) -> Text:
        title = Text(text, font_size=size, weight="SEMIBOLD")
        title.to_edge(UP, buff=0.34)
        return title

    def _section_title(self, text: str) -> Text:
        title = Text(text, font_size=33, weight="SEMIBOLD")
        title.to_edge(UP, buff=0.30)
        return title

    @staticmethod
    def _divider() -> Line:
        return Line(
            np.array([0.65, -3.05, 0.0]),
            np.array([0.65, 2.65, 0.0]),
            color=GRAY_C,
            stroke_width=1.5,
        )

    @staticmethod
    def _project_3d(origin: np.ndarray, point: tuple[float, float, float]) -> np.ndarray:
        """Oblique projection chosen for a legible, uncluttered 2D rendering."""
        x, y, z = point
        e_x = np.array([0.78, -0.05, 0.0])
        e_y = np.array([-0.46, 0.28, 0.0])
        e_z = np.array([0.0, 0.75, 0.0])
        return origin + x * e_x + y * e_y + z * e_z

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        self._show_intro()
        self._show_r2()
        self._show_r3()
        self._show_summary()
        self.wait(1.4)

    # ------------------------------------------------------------------
    # Act 0 — The central problem: path length is not direct distance
    # ------------------------------------------------------------------

    def _show_intro(self) -> None:
        title = self._title("Vecteurs 3 — dans R² et R³")
        subtitle = Text(
            "Distance directe, déplacement et milieu",
            font_size=29,
            color=ACCENT,
        ).next_to(title, DOWN, buff=0.22)

        a = LEFT * 3.4 + DOWN * 1.05
        corner = a + RIGHT * 4.0
        b = corner + UP * 2.25

        dot_a = Dot(a, color=BLACK, radius=0.08)
        dot_b = Dot(b, color=BLACK, radius=0.08)
        label_a = MathTex("A").scale(0.82).next_to(dot_a, DOWN + LEFT, buff=0.12)
        label_b = MathTex("B").scale(0.82).next_to(dot_b, UP + RIGHT, buff=0.12)

        route_h = Arrow(a, corner, buff=0, color=GRAY_D, stroke_width=4)
        route_v = Arrow(corner, b, buff=0, color=GRAY_D, stroke_width=4)
        route_labels = VGroup(
            MathTex("4", color=GRAY_D).scale(0.78).next_to(route_h, DOWN, buff=0.12),
            MathTex("3", color=GRAY_D).scale(0.78).next_to(route_v, RIGHT, buff=0.12),
        )
        route_total = MathTex(r"4+3=7", color=GRAY_D).scale(0.88)
        route_total.move_to(RIGHT * 3.15 + DOWN * 0.75)
        route_caption = Text("longueur du trajet", font_size=23, color=GRAY_D)
        route_caption.next_to(route_total, DOWN, buff=0.12)

        direct = Arrow(a, b, buff=0, color=ACCENT, stroke_width=6)
        direct_question = MathTex(r"d(A,B)=?", color=ACCENT).scale(1.05)
        direct_question.move_to(RIGHT * 3.2 + UP * 0.55)
        direct_caption = Text("distance directe", font_size=23, color=ACCENT)
        direct_caption.next_to(direct_question, DOWN, buff=0.12)

        with self.narrated(SCRIPT["intro"]):
            self.play(FadeIn(title), FadeIn(subtitle), run_time=0.85)
            self.wait_until_bookmark("intro_points")
            self.play(
                FadeIn(dot_a),
                FadeIn(dot_b),
                Write(label_a),
                Write(label_b),
                run_time=0.65,
            )
            self.wait_until_bookmark("intro_route")
            self.play(Create(route_h), Create(route_v), run_time=0.95)
            self.play(Write(route_labels), run_time=0.65)
            self.play(Write(route_total), FadeIn(route_caption), run_time=0.7)
            self.wait(0.65)
            self.wait_until_bookmark("intro_direct")
            self.play(Create(direct), run_time=0.9)
            self.play(Write(direct_question), FadeIn(direct_caption), run_time=0.7)
            self.wait(1.45)

        self.play(
            FadeOut(
                VGroup(
                    title,
                    subtitle,
                    dot_a,
                    dot_b,
                    label_a,
                    label_b,
                    route_h,
                    route_v,
                    route_labels,
                    route_total,
                    route_caption,
                    direct,
                    direct_question,
                    direct_caption,
                )
            ),
            run_time=0.8,
        )

    # ------------------------------------------------------------------
    # Act 1 — R²: displacement, direct distance, midpoint
    # ------------------------------------------------------------------

    def _show_r2(self) -> None:
        header = self._section_title(r"Dans le plan : trois calculs à partir de A et B")
        divider = self._divider()

        plane = NumberPlane(
            x_range=[-3, 3, 1],
            y_range=[-2, 3, 1],
            x_length=6.35,
            y_length=4.85,
            axis_config={
                "color": GRAY_D,
                "stroke_width": 2,
                "include_numbers": True,
                "font_size": 20,
            },
            background_line_style={
                "stroke_color": GRAY_B,
                "stroke_width": 1,
                "stroke_opacity": 0.38,
            },
        ).move_to(LEFT * 3.65 + DOWN * 0.35)

        a_xy = (-2, -1)
        b_xy = (2, 2)
        m_xy = (0, 0.5)

        a = plane.c2p(*a_xy)
        b = plane.c2p(*b_xy)
        corner = plane.c2p(b_xy[0], a_xy[1])
        midpoint = plane.c2p(*m_xy)

        dot_a = Dot(a, color=BLACK, radius=0.075)
        dot_b = Dot(b, color=BLACK, radius=0.075)
        label_a = MathTex(r"A(-2,-1)").scale(0.70).next_to(dot_a, DOWN + LEFT, buff=0.10)
        label_b = MathTex(r"B(2,2)").scale(0.70).next_to(dot_b, UP + RIGHT, buff=0.10)

        component_x = DashedLine(a, corner, color=GRAY_D, stroke_width=3)
        component_y = DashedLine(corner, b, color=GRAY_D, stroke_width=3)
        component_labels = VGroup(
            MathTex(r"+4", color=GRAY_D).scale(0.72).next_to(component_x, DOWN, buff=0.10),
            MathTex(r"+3", color=GRAY_D).scale(0.72).next_to(component_y, RIGHT, buff=0.10),
        )
        direct = Arrow(a, b, buff=0, color=ACCENT, stroke_width=6)
        direct_label = MathTex(r"\overrightarrow{AB}", color=ACCENT).scale(0.78)
        direct_label.move_to((a + b) / 2 + 0.28 * UP + 0.12 * LEFT)

        right_angle = VGroup(
            Line(corner + 0.18 * LEFT, corner + 0.18 * LEFT + 0.18 * UP, color=GRAY_D, stroke_width=2),
            Line(corner + 0.18 * LEFT + 0.18 * UP, corner + 0.18 * UP, color=GRAY_D, stroke_width=2),
        )

        formula_x = 3.55
        label_x = 1.35

        displacement_label = Text("1  Déplacement", font_size=25, weight="SEMIBOLD")
        displacement_label.move_to(np.array([label_x + 0.75, 1.65, 0.0]))
        displacement_formula = VGroup(
            MathTex(r"\overrightarrow{AB}=B-A").scale(0.82),
            MathTex(r"=(2-(-2),\,2-(-1))").scale(0.76),
            MathTex(r"=(4,3)", color=ACCENT).scale(1.02),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.19)
        displacement_formula.move_to(np.array([formula_x, 0.90, 0.0]))

        route_note = VGroup(
            Text("Trajet par les axes", font_size=23, color=GRAY_D),
            MathTex(r"4+3=7", color=GRAY_D).scale(0.82),
        ).arrange(RIGHT, buff=0.25)
        route_note.move_to(np.array([3.75, -0.08, 0.0]))

        distance_label = Text("2  Distance directe", font_size=25, weight="SEMIBOLD")
        distance_label.move_to(np.array([label_x + 0.98, -0.72, 0.0]))
        distance_formula = VGroup(
            MathTex(r"d(A,B)=\|\overrightarrow{AB}\|").scale(0.77),
            MathTex(r"=\sqrt{4^2+3^2}").scale(0.82),
            MathTex(r"=5", color=ACCENT).scale(1.08),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        distance_formula.move_to(np.array([formula_x, -1.57, 0.0]))

        warning = Text(
            "trajet 7  ≠  distance directe 5",
            font_size=23,
            color=GRAY_D,
        ).move_to(np.array([3.75, -2.72, 0.0]))

        with self.narrated(SCRIPT["r2"]):
            self.play(FadeIn(header), FadeIn(divider), run_time=0.65)
            self.play(FadeIn(plane), run_time=0.85)
            self.wait_until_bookmark("r2_a")
            self.play(FadeIn(dot_a), Write(label_a), run_time=0.65)
            self.wait_until_bookmark("r2_b")
            self.play(FadeIn(dot_b), Write(label_b), run_time=0.65)
            self.wait_until_bookmark("r2_components")
            self.play(Create(component_x), Write(component_labels[0]), run_time=0.75)
            self.play(Create(component_y), Write(component_labels[1]), run_time=0.75)
            self.play(Write(displacement_label), run_time=0.55)
            self.play(Write(displacement_formula[0]), run_time=0.75)
            self.play(Write(displacement_formula[1]), run_time=0.75)
            self.wait_until_bookmark("r2_vector")
            self.play(Create(direct), Write(direct_label), run_time=0.85)
            self.play(Write(displacement_formula[2]), run_time=0.6)
            self.wait(0.75)
            self.wait_until_bookmark("r2_route")
            self.play(FadeIn(route_note), run_time=0.6)
            self.wait(0.65)
            self.wait_until_bookmark("r2_distance")
            self.play(FadeIn(right_angle), Write(distance_label), run_time=0.65)
            self.play(Write(distance_formula[0]), run_time=0.75)
            self.play(Write(distance_formula[1]), run_time=0.75)
            self.wait_until_bookmark("r2_result")
            self.play(Write(distance_formula[2]), run_time=0.6)
            self.wait(0.85)
            self.wait_until_bookmark("r2_warning")
            self.play(FadeIn(warning), run_time=0.6)
            self.wait(1.25)

        # Keep the geometric context and replace the right column by the midpoint step.
        midpoint_label = Text("3  Point milieu", font_size=26, weight="SEMIBOLD")
        midpoint_label.move_to(np.array([2.35, 1.55, 0.0]))
        midpoint_formula = VGroup(
            MathTex(r"M=\frac{A+B}{2}").scale(0.90),
            MathTex(
                r"=\left(\frac{-2+2}{2},\frac{-1+2}{2}\right)"
            ).scale(0.77),
            MathTex(r"=\left(0,\frac12\right)", color=ACCENT).scale(1.03),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.27)
        midpoint_formula.move_to(np.array([3.65, 0.45, 0.0]))
        equal_distance = MathTex(r"d(A,M)=d(M,B)=\frac52").scale(0.78)
        equal_distance.move_to(np.array([3.65, -1.05, 0.0]))

        dot_m = Dot(midpoint, color=ACCENT, radius=0.085)
        label_m = MathTex(r"M\left(0,\frac12\right)", color=ACCENT).scale(0.70)
        label_m.next_to(dot_m, DOWN + RIGHT, buff=0.12)
        first_half = Line(a, midpoint, color=ACCENT, stroke_width=7)
        second_half = Line(midpoint, b, color=ACCENT, stroke_width=7)

        right_column_r2 = VGroup(
            displacement_label,
            displacement_formula,
            route_note,
            distance_label,
            distance_formula,
            warning,
        )

        with self.narrated(SCRIPT["midpoint_r2"]):
            self.play(FadeOut(right_column_r2), FadeOut(right_angle), run_time=0.6)
            self.wait_until_bookmark("mid_dot")
            self.play(FadeIn(dot_m), Write(label_m), run_time=0.65)
            self.play(Create(first_half), Create(second_half), run_time=0.75)
            self.wait_until_bookmark("mid_formula")
            self.play(Write(midpoint_label), run_time=0.55)
            self.play(Write(midpoint_formula[0]), run_time=0.7)
            self.play(Write(midpoint_formula[1]), run_time=0.8)
            self.play(Write(midpoint_formula[2]), run_time=0.65)
            self.wait_until_bookmark("mid_equal")
            self.play(Write(equal_distance), run_time=0.7)
            self.wait(1.3)

        self.play(
            FadeOut(
                VGroup(
                    header,
                    divider,
                    plane,
                    dot_a,
                    dot_b,
                    label_a,
                    label_b,
                    component_x,
                    component_y,
                    component_labels,
                    direct,
                    direct_label,
                    dot_m,
                    label_m,
                    first_half,
                    second_half,
                    midpoint_label,
                    midpoint_formula,
                    equal_distance,
                )
            ),
            run_time=0.85,
        )

    # ------------------------------------------------------------------
    # Act 2 — R³: no new method, only a third coordinate
    # ------------------------------------------------------------------

    def _show_r3(self) -> None:
        header = self._section_title(r"Dans l'espace : exactement les mêmes étapes")
        divider = self._divider()

        origin = np.array([-4.35, -1.55, 0.0])
        x_end = self._project_3d(origin, (5.2, 0, 0))
        y_end = self._project_3d(origin, (0, 3.2, 0))
        z_end = self._project_3d(origin, (0, 0, 3.6))

        x_axis = Arrow(origin, x_end, buff=0, color=GRAY_D, stroke_width=3)
        y_axis = Arrow(origin, y_end, buff=0, color=GRAY_D, stroke_width=3)
        z_axis = Arrow(origin, z_end, buff=0, color=GRAY_D, stroke_width=3)
        axis_labels = VGroup(
            MathTex("x").scale(0.70).next_to(x_end, RIGHT, buff=0.08),
            MathTex("y").scale(0.70).next_to(y_end, UP + LEFT, buff=0.08),
            MathTex("z").scale(0.70).next_to(z_end, UP, buff=0.08),
        )
        perspective_note = Text("schéma en perspective", font_size=20, color=GRAY_D)
        perspective_note.move_to(np.array([-4.35, -2.82, 0.0]))

        a_xyz = (1, 0, 0)
        b_xyz = (4, 2, 2)
        m_xyz = (2.5, 1, 1)

        a = self._project_3d(origin, a_xyz)
        b = self._project_3d(origin, b_xyz)
        midpoint = self._project_3d(origin, m_xyz)
        step_x_end = self._project_3d(origin, (4, 0, 0))
        step_y_end = self._project_3d(origin, (4, 2, 0))

        dot_a = Dot(a, color=BLACK, radius=0.075)
        dot_b = Dot(b, color=BLACK, radius=0.075)
        label_a = MathTex(r"A(1,0,0)").scale(0.68).next_to(dot_a, DOWN, buff=0.10)
        label_b = MathTex(r"B(4,2,2)").scale(0.68).next_to(dot_b, UP + RIGHT, buff=0.10)

        step_x = Arrow(a, step_x_end, buff=0, color=GRAY_D, stroke_width=4)
        step_y = Arrow(step_x_end, step_y_end, buff=0, color=GRAY_D, stroke_width=4)
        step_z = Arrow(step_y_end, b, buff=0, color=GRAY_D, stroke_width=4)
        step_labels = VGroup(
            MathTex("3", color=GRAY_D).scale(0.68).next_to(step_x, DOWN, buff=0.08),
            MathTex("2", color=GRAY_D).scale(0.68).move_to((step_x_end + step_y_end) / 2 + 0.18 * UP),
            MathTex("2", color=GRAY_D).scale(0.68).next_to(step_z, RIGHT, buff=0.08),
        )

        direct = Arrow(a, b, buff=0, color=ACCENT, stroke_width=6)
        direct_label = MathTex(r"\overrightarrow{AB}", color=ACCENT).scale(0.76)
        direct_label.move_to((a + b) / 2 + 0.44 * RIGHT + 0.30 * DOWN)

        displacement_label = Text("1  Déplacement", font_size=25, weight="SEMIBOLD")
        displacement_label.move_to(np.array([2.20, 1.78, 0.0]))
        displacement_formula = VGroup(
            MathTex(r"\overrightarrow{AB}=B-A").scale(0.80),
            MathTex(r"=(4-1,\,2-0,\,2-0)").scale(0.73),
            MathTex(r"=(3,2,2)", color=ACCENT).scale(1.00),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        displacement_formula.move_to(np.array([3.70, 1.05, 0.0]))

        route_note = VGroup(
            Text("Trajet par les axes", font_size=22, color=GRAY_D),
            MathTex(r"3+2+2=7", color=GRAY_D).scale(0.78),
        ).arrange(RIGHT, buff=0.22)
        route_note.move_to(np.array([3.75, 0.02, 0.0]))

        distance_label = Text("2  Distance directe", font_size=25, weight="SEMIBOLD")
        distance_label.move_to(np.array([2.45, -0.72, 0.0]))
        distance_formula = VGroup(
            MathTex(r"d(A,B)=\sqrt{3^2+2^2+2^2}").scale(0.77),
            MathTex(r"=\sqrt{17}\approx 4{,}12", color=ACCENT).scale(0.93),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        distance_formula.move_to(np.array([3.72, -1.38, 0.0]))

        midpoint_label = Text("3  Point milieu", font_size=25, weight="SEMIBOLD")
        midpoint_label.move_to(np.array([2.10, -2.17, 0.0]))
        midpoint_formula = MathTex(
            r"M=\frac{A+B}{2}=\left(\frac52,1,1\right)",
            color=ACCENT,
        ).scale(0.78)
        midpoint_formula.move_to(np.array([4.05, -2.72, 0.0]))

        dot_m = Dot(midpoint, color=ACCENT, radius=0.082)
        label_m = MathTex(r"M\left(\frac52,1,1\right)", color=ACCENT).scale(0.64)
        label_m.next_to(dot_m, LEFT + UP, buff=0.10)

        with self.narrated(SCRIPT["r3"]):
            self.play(FadeIn(header), FadeIn(divider), run_time=0.65)
            self.wait_until_bookmark("r3_xy_axes")
            self.play(
                Create(x_axis),
                Create(y_axis),
                FadeIn(axis_labels[0]),
                FadeIn(axis_labels[1]),
                run_time=0.85,
            )
            self.wait_until_bookmark("r3_z_axis")
            self.play(
                Create(z_axis),
                FadeIn(axis_labels[2]),
                FadeIn(perspective_note),
                run_time=0.75,
            )
            self.wait_until_bookmark("r3_a")
            self.play(FadeIn(dot_a), Write(label_a), run_time=0.65)
            self.wait_until_bookmark("r3_b")
            self.play(FadeIn(dot_b), Write(label_b), run_time=0.65)
            self.wait_until_bookmark("r3_components")
            self.play(Create(step_x), Write(step_labels[0]), run_time=0.7)
            self.play(Create(step_y), Write(step_labels[1]), run_time=0.7)
            self.play(Create(step_z), Write(step_labels[2]), run_time=0.7)
            self.play(Write(displacement_label), run_time=0.5)
            self.play(Write(displacement_formula[0]), run_time=0.7)
            self.play(Write(displacement_formula[1]), run_time=0.75)
            self.wait_until_bookmark("r3_vector")
            self.play(Create(direct), Write(direct_label), run_time=0.85)
            self.play(Write(displacement_formula[2]), run_time=0.6)
            self.wait(0.7)
            self.wait_until_bookmark("r3_route")
            self.play(FadeIn(route_note), run_time=0.6)
            self.wait(0.65)
            self.wait_until_bookmark("r3_distance")
            self.play(Write(distance_label), run_time=0.5)
            self.play(Write(distance_formula[0]), run_time=0.8)
            self.play(Write(distance_formula[1]), run_time=0.7)
            self.wait(0.8)
            self.wait_until_bookmark("r3_mid")
            self.play(FadeIn(dot_m), Write(label_m), run_time=0.65)
            self.play(Write(midpoint_label), run_time=0.5)
            self.play(Write(midpoint_formula), run_time=0.75)
            self.wait(1.45)

        self.play(
            FadeOut(
                VGroup(
                    header,
                    divider,
                    x_axis,
                    y_axis,
                    z_axis,
                    axis_labels,
                    perspective_note,
                    dot_a,
                    dot_b,
                    label_a,
                    label_b,
                    step_x,
                    step_y,
                    step_z,
                    step_labels,
                    direct,
                    direct_label,
                    dot_m,
                    label_m,
                    displacement_label,
                    displacement_formula,
                    route_note,
                    distance_label,
                    distance_formula,
                    midpoint_label,
                    midpoint_formula,
                )
            ),
            run_time=0.85,
        )

    # ------------------------------------------------------------------
    # Act 3 — Stable reusable method
    # ------------------------------------------------------------------

    def _show_summary(self) -> None:
        title = self._title("Une méthode, deux dimensions possibles", size=42)
        subtitle = Text(
            "Tous les calculs se font coordonnée par coordonnée",
            font_size=27,
            color=GRAY_D,
        ).next_to(title, DOWN, buff=0.22)

        left_rule = Line(
            np.array([-5.95, 1.25, 0.0]),
            np.array([-5.95, -1.85, 0.0]),
            color=ACCENT,
            stroke_width=5,
        )

        step_1 = VGroup(
            Text("1", font_size=31, color=ACCENT, weight="SEMIBOLD"),
            Text("Déplacement", font_size=29, weight="SEMIBOLD"),
            MathTex(r"\overrightarrow{AB}=B-A").scale(0.93),
        ).arrange(RIGHT, buff=0.35)

        step_2 = VGroup(
            Text("2", font_size=31, color=ACCENT, weight="SEMIBOLD"),
            Text("Distance directe", font_size=29, weight="SEMIBOLD"),
            MathTex(r"d(A,B)=\|\overrightarrow{AB}\|").scale(0.90),
        ).arrange(RIGHT, buff=0.35)

        step_3 = VGroup(
            Text("3", font_size=31, color=ACCENT, weight="SEMIBOLD"),
            Text("Point milieu", font_size=29, weight="SEMIBOLD"),
            MathTex(r"M=\frac{A+B}{2}").scale(0.93),
        ).arrange(RIGHT, buff=0.35)

        steps = VGroup(step_1, step_2, step_3).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.58,
        )
        steps.move_to(np.array([-0.25, -0.25, 0.0]))

        comparison = VGroup(
            MathTex(r"\mathbb R^2:\ (x,y)", color=ACCENT).scale(0.90),
            MathTex(r"\mathbb R^3:\ (x,y,z)", color=ACCENT).scale(0.90),
        ).arrange(RIGHT, buff=1.25)
        comparison.to_edge(DOWN, buff=0.42)

        with self.narrated(SCRIPT["summary"]):
            self.play(FadeIn(title), FadeIn(subtitle), FadeIn(left_rule), run_time=0.75)
            self.wait_until_bookmark("summary_vector")
            self.play(Write(step_1), run_time=0.85)
            self.wait(0.55)
            self.wait_until_bookmark("summary_distance")
            self.play(Write(step_2), run_time=0.85)
            self.wait(0.55)
            self.wait_until_bookmark("summary_midpoint")
            self.play(Write(step_3), run_time=0.85)
            self.wait(0.75)
            self.wait_until_bookmark("summary_r2r3")
            self.play(Write(comparison), run_time=0.85)
            self.wait(2.2)
