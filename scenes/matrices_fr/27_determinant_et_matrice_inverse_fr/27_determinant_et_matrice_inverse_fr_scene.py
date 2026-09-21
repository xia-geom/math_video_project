"""Déterminant et matrice inverse — seconde passe approfondie.

Cette quatrième capsule du module « Vecteurs et matrices » répond à une seule
question : quand une transformation matricielle peut-elle être défaite ?

Progression pédagogique
------------------------
1. Le carré unité est transformé : ``|det(A)|`` apparaît comme facteur d'aire.
2. Une réflexion montre que le signe encode l'orientation.
3. Un écrasement montre que ``det(C)=0`` signifie perte d'information.
4. Une vraie matrice inverse ramène effectivement le dessin à son état initial.
5. Les formules ``ad-bc`` et de la matrice inverse sont ensuite justifiées.

La scène privilégie les constructions progressives, les temps de lecture stables
et les liens explicites entre géométrie, calcul matriciel et inversibilité.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

import numpy as np
from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    DR,
    GRAY_D,
    GRAY_E,
    GREEN_D,
    LEFT,
    PI,
    RED_D,
    RIGHT,
    SEMIBOLD,
    UP,
    UR,
    WHITE,
    Arc,
    Arrow,
    BraceBetweenPoints,
    Circle,
    Circumscribe,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    Matrix,
    Mobject,
    Polygon,
    Rectangle,
    ReplacementTransform,
    Scene,
    SurroundingRectangle,
    Tex,
    Text,
    Transform,
    VGroup,
    Write,
    config,
)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from manim_voiceover import VoiceoverScene
    from tools.teaching_voiceover import TeachingAzureService as AzureService
except ImportError:
    VoiceoverScene = None
    AzureService = None

import tools.tts as tts
from tools.branding import play_uqam_intro

# ---------------------------------------------------------------------------
# Visual defaults
# ---------------------------------------------------------------------------
config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
GOOD = GREEN_D
WARN = RED_D
MUTED = GRAY_D
PALE = GRAY_E

UNIT = 1.16
DIAGRAM_ORIGIN = DOWN * 0.48

A_MATRIX = np.array([[1.0, 1.0], [0.0, 2.0]])
A_INVERSE = np.array([[1.0, -0.5], [0.0, 0.5]])
B_MATRIX = np.array([[-1.0, 0.0], [0.0, 1.0]])
C_MATRIX = np.array([[1.0, 2.0], [0.0, 0.0]])

# Deux points distincts du carré unité qui ont la même image par C.
P_VECTOR = np.array([0.0, 1.0])
Q_VECTOR = np.array([1.0, 0.5])
COMMON_IMAGE = np.array([2.0, 0.0])


def _validate_examples() -> None:
    """Fail early if an edited example stops matching the mathematics shown."""
    identity = np.eye(2)
    assert np.isclose(np.linalg.det(A_MATRIX), 2.0)
    assert np.isclose(np.linalg.det(B_MATRIX), -1.0)
    assert np.isclose(np.linalg.det(C_MATRIX), 0.0)
    assert np.allclose(A_INVERSE @ A_MATRIX, identity)
    assert np.allclose(A_MATRIX @ A_INVERSE, identity)
    assert np.allclose(C_MATRIX @ P_VECTOR, COMMON_IMAGE)
    assert np.allclose(C_MATRIX @ Q_VECTOR, COMMON_IMAGE)


_validate_examples()


# ---------------------------------------------------------------------------
# Narration
# ---------------------------------------------------------------------------
SCRIPT = [
    {
        "caption": "Quand peut-on revenir exactement en arrière ?",
        "ssml": tts.ssml(
            "Une matrice peut étirer, incliner, réfléchir, ou même écraser le plan. "
            "La question centrale est simple : après la transformation, "
            "peut-on retrouver chaque point de départ sans ambiguïté ? "
            "<break time='420ms'/>Le déterminant va mesurer la déformation "
            "et détecter toute perte d'information."
        ),
    },
    {
        "caption": "Le carré unité permet de voir le facteur d’aire.",
        "ssml": tts.ssml(
            "Partons du carré unité, dont l'aire vaut un. "
            "<bookmark mark='show_basis'/>Ses côtés suivent les vecteurs de base. "
            f"La première colonne de {tts.char('A')} est l'image du premier vecteur, "
            "et la deuxième colonne est l'image du second. "
            "<bookmark mark='apply_a'/>Appliquons la transformation. "
            "Le carré devient un parallélogramme. "
            "<bookmark mark='measure_area'/>Sa base vaut un et sa hauteur vaut deux : "
            "son aire vaut donc deux. "
            "<bookmark mark='name_det'/>La transformation multiplie les aires par deux. "
            f"On écrit déterminant de {tts.char('A')} égal à deux."
        ),
    },
    {
        "caption": "Le signe du déterminant repère un retournement.",
        "ssml": tts.ssml(
            "La taille du déterminant ne suffit pas. "
            "Considérons maintenant une réflexion par rapport à l'axe vertical. "
            "<bookmark mark='reflect'/>L'aire reste égale à un, "
            "mais le sens de parcours du carré est renversé, comme dans un miroir. "
            "<bookmark mark='negative_det'/>La valeur absolue du déterminant vaut un, "
            f"mais le déterminant de {tts.char('B')} vaut moins un. "
            "Le signe négatif enregistre le changement d'orientation."
        ),
    },
    {
        "caption": "Déterminant zéro : une surface est écrasée sur une ligne.",
        "ssml": tts.ssml(
            "Voici le cas décisif. "
            "Les deux colonnes de cette matrice sont colinéaires : "
            "la seconde est deux fois la première. "
            "<bookmark mark='collapse'/>Le carré et tout le quadrillage sont écrasés "
            "sur une seule droite. Leur aire devient zéro. "
            "<bookmark mark='merge_points'/>Regardons aussi deux points distincts du carré. "
            "Après la transformation, ils arrivent exactement au même point. "
            "<bookmark mark='det_zero'/>Le déterminant vaut zéro : "
            "une dimension, et donc une partie de l'information, a disparu."
        ),
    },
    {
        "caption": "Une sortie commune ne permet pas de retrouver deux entrées.",
        "ssml": tts.ssml(
            f"Les points {tts.char('P')} et {tts.char('Q')} sont différents, "
            f"mais {tts.char('C')} de {tts.char('P')} est égal à "
            f"{tts.char('C')} de {tts.char('Q')}. "
            "<bookmark mark='ask_inverse'/>Si une inverse recevait cette sortie, "
            "devrait-elle revenir vers le premier point ou vers le second ? "
            "<bookmark mark='no_inverse'/>Une fonction ne peut pas choisir deux réponses. "
            "La transformation n'est donc pas inversible."
        ),
    },
    {
        "caption": "Une vraie inverse défait effectivement la transformation.",
        "ssml": tts.ssml(
            f"Revenons à {tts.char('A')}, dont le déterminant vaut deux. "
            "<bookmark mark='deform'/>La matrice déforme le quadrillage. "
            f"<bookmark mark='undo'/>Puis {tts.char('A')} inverse applique "
            "la transformation contraire. "
            "Le calcul et le dessin ramènent exactement chaque point à sa place. "
            f"<bookmark mark='identity'/>Ainsi, {tts.char('A')} inverse, multipliée par "
            f"{tts.char('A')}, donne la matrice identité."
        ),
    },
    {
        "caption": "Pour une matrice 2 × 2, det(M) = ad − bc.",
        "ssml": tts.ssml(
            "La géométrie étant visible, calculons maintenant le déterminant. "
            "<bookmark mark='first_product'/>On multiplie les coefficients de la diagonale "
            f"{tts.char('a')}, {tts.char('d')}. "
            "<bookmark mark='second_product'/>Puis on soustrait le produit de l'autre diagonale, "
            f"{tts.char('b')}, {tts.char('c')}. "
            "<bookmark mark='check_a'/>Dans notre exemple, un fois deux, moins un fois zéro, "
            "donne bien deux."
        ),
    },
    {
        "caption": "La formule de l’inverse vient d’un produit qui se simplifie.",
        "ssml": tts.ssml(
            "Pourquoi échanger les deux coefficients diagonaux et changer deux signes ? "
            "<bookmark mark='candidate'/>Formons d'abord cette matrice auxiliaire. "
            "<bookmark mark='multiply'/>Dans les deux ordres de multiplication, "
            "les termes hors diagonale s'annulent, "
            "et les deux termes diagonaux deviennent le déterminant. "
            "<bookmark mark='divide_det'/>Si le déterminant n'est pas zéro, "
            "on divise par lui et le produit devient l'identité. "
            "C'est exactement la formule de la matrice inverse."
        ),
    },
    {
        "caption": "Aire, orientation, information et inversibilité.",
        "ssml": tts.ssml(
            "À retenir. "
            "<bookmark mark='recap_area'/>La valeur absolue du déterminant est le facteur d'aire. "
            "<bookmark mark='recap_sign'/>Un signe négatif indique un retournement d'orientation. "
            "<bookmark mark='recap_zero'/>Un déterminant nul signifie perte d'information "
            "et absence d'inverse. "
            "<bookmark mark='recap_nonzero'/>Un déterminant non nul garantit une matrice inverse. "
            "Cette idée permettra ensuite de résoudre certains systèmes linéaires."
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


BaseScene = VoiceoverScene if VoiceoverScene is not None else Scene


class DeterminantEtMatriceInverseFR(BaseScene):
    """Geometric and algebraic introduction to determinant and inverse matrices."""

    # ------------------------------------------------------------------
    # Voiceover and page management
    # ------------------------------------------------------------------
    def _setup_voiceover(self) -> None:
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

        try:
            # The speech rate is already centralised in tools.tts.ssml().
            self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        except Exception as exc:
            print(f"[voiceover] Azure Speech setup failed: {exc}. Rendering without narration.")
            return

        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, item: dict[str, str]):
        if self._voiceover_enabled:
            with self.voiceover(
                text=item["ssml"],
                subcaption=item["caption"],
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_until_bookmark(self, mark: str) -> None:
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)

    def clear_page(self, *mobjects: Mobject, run_time: float = 0.6) -> None:
        visible = [mob for mob in mobjects if mob is not None]
        if visible:
            self.play(*(FadeOut(mob) for mob in visible), run_time=run_time)

    # ------------------------------------------------------------------
    # Visual helpers
    # ------------------------------------------------------------------
    def make_heading(self, text: str) -> Text:
        heading = Text(text, font_size=36, weight=SEMIBOLD)
        if heading.width > 12.2:
            heading.scale_to_fit_width(12.2)
        return heading.to_edge(UP, buff=0.34)

    def make_grid(
        self,
        *,
        origin: np.ndarray = DIAGRAM_ORIGIN,
        unit: float = UNIT,
        x_extent: float = 2.35,
        y_extent: float = 1.08,
    ) -> VGroup:
        """Whiteboard grid with an equal visual unit on both axes."""
        lines = VGroup()

        for x_value in range(-2, 3):
            color = BLACK if x_value == 0 else PALE
            width = 2.4 if x_value == 0 else 1.35
            lines.add(
                Line(
                    origin + unit * np.array([x_value, -y_extent, 0.0]),
                    origin + unit * np.array([x_value, y_extent, 0.0]),
                    color=color,
                    stroke_width=width,
                )
            )

        for y_value in range(-1, 2):
            color = BLACK if y_value == 0 else PALE
            width = 2.4 if y_value == 0 else 1.35
            lines.add(
                Line(
                    origin + unit * np.array([-x_extent, y_value, 0.0]),
                    origin + unit * np.array([x_extent, y_value, 0.0]),
                    color=color,
                    stroke_width=width,
                )
            )

        return lines

    def make_unit_square(
        self,
        *,
        origin: np.ndarray = DIAGRAM_ORIGIN,
        unit: float = UNIT,
        color=ACCENT,
    ) -> Polygon:
        return Polygon(
            origin,
            origin + unit * RIGHT,
            origin + unit * (RIGHT + UP),
            origin + unit * UP,
            stroke_color=color,
            stroke_width=3.4,
            fill_color=color,
            fill_opacity=0.13,
        )

    def make_basis_vectors(
        self,
        *,
        origin: np.ndarray = DIAGRAM_ORIGIN,
        unit: float = UNIT,
    ) -> VGroup:
        e1 = Arrow(
            origin,
            origin + unit * RIGHT,
            buff=0,
            color=ACCENT,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.16,
        )
        e2 = Arrow(
            origin,
            origin + unit * UP,
            buff=0,
            color=GOOD,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.16,
        )
        return VGroup(e1, e2)

    def linear_target(
        self,
        mobject: Mobject,
        matrix: np.ndarray,
        *,
        origin: np.ndarray = DIAGRAM_ORIGIN,
    ) -> Mobject:
        """Return a copy transformed linearly about ``origin``."""
        target = mobject.copy()
        matrix_2d = np.asarray(matrix, dtype=float)
        about = np.asarray(origin, dtype=float)

        def transform_point(point: np.ndarray) -> np.ndarray:
            relative = point - about
            transformed_xy = matrix_2d @ relative[:2]
            return about + np.array([transformed_xy[0], transformed_xy[1], relative[2]])

        target.apply_function(transform_point)
        return target

    def make_orientation_arc(
        self,
        center: np.ndarray,
        *,
        clockwise: bool,
        color=ACCENT,
    ) -> Arc:
        if clockwise:
            arc = Arc(
                radius=0.30,
                start_angle=PI * 0.85,
                angle=-PI * 1.45,
                arc_center=center,
                color=color,
                stroke_width=3.0,
            )
        else:
            arc = Arc(
                radius=0.30,
                start_angle=-PI * 0.15,
                angle=PI * 1.45,
                arc_center=center,
                color=color,
                stroke_width=3.0,
            )
        arc.add_tip(tip_length=0.13)
        return arc

    def make_recap_row(self, formula: str, explanation: str, *, color) -> VGroup:
        marker = Line(UP * 0.30, DOWN * 0.30, color=color, stroke_width=5)
        formula_mob = MathTex(formula, font_size=42, color=color)
        formula_slot = Rectangle(
            width=2.55,
            height=0.74,
            stroke_opacity=0,
            fill_opacity=0,
        )
        formula_mob.move_to(formula_slot)
        formula_group = VGroup(formula_slot, formula_mob)
        text_mob = Text(explanation, font_size=29)
        return VGroup(marker, formula_group, text_mob).arrange(RIGHT, buff=0.42)

    # ------------------------------------------------------------------
    # Scene
    # ------------------------------------------------------------------
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        # ==============================================================
        # PAGE 1 — Central question
        # ==============================================================
        title = Text(
            "Déterminant et matrice inverse",
            font_size=44,
            weight=SEMIBOLD,
        )
        if title.width > config.frame_width - 1.0:
            title.scale_to_fit_width(config.frame_width - 1.0)
        question = Text(
            "Quand peut-on revenir exactement en arrière ?",
            font_size=33,
            color=MUTED,
        )
        keywords = VGroup(
            Text("aire", font_size=28, color=ACCENT),
            Text("orientation", font_size=28, color=ACCENT),
            Text("information", font_size=28, color=ACCENT),
        ).arrange(RIGHT, buff=0.80)
        intro = VGroup(title, question, keywords).arrange(DOWN, buff=0.32)

        with self.narrated(SCRIPT[0]):
            self.play(Write(title), run_time=0.9)
            self.play(FadeIn(question, shift=UP * 0.10), run_time=0.65)
            self.play(
                LaggedStart(
                    *(FadeIn(word, shift=UP * 0.08) for word in keywords),
                    lag_ratio=0.18,
                ),
                run_time=0.9,
            )
            self.wait(1.0)

        self.clear_page(intro)

        # ==============================================================
        # PAGE 2 — A positive determinant: area first, name second
        # ==============================================================
        heading = self.make_heading("Le carré unité révèle le facteur d’aire")
        grid = self.make_grid()
        square = self.make_unit_square()
        e1, e2 = self.make_basis_vectors()

        e1_label = MathTex(r"\vec e_1", font_size=30, color=ACCENT).next_to(
            e1.get_end(), DOWN, buff=0.12
        )
        e2_label = MathTex(r"\vec e_2", font_size=30, color=GOOD).next_to(
            e2.get_end(), LEFT, buff=0.12
        )
        matrix_a = MathTex(
            r"A=\begin{pmatrix}1&1\\0&2\end{pmatrix}",
            font_size=40,
        ).to_corner(UR, buff=0.44).shift(DOWN * 0.62)
        column_images = VGroup(
            MathTex(r"A\vec e_1=(1,0)", font_size=29, color=ACCENT),
            MathTex(r"A\vec e_2=(1,2)", font_size=29, color=GOOD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        column_images.to_corner(DR, buff=0.42).shift(UP * 0.80)

        grid_target = self.linear_target(grid, A_MATRIX)
        square_target = self.linear_target(square, A_MATRIX)
        e1_target = Arrow(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * np.array([1.0, 0.0, 0.0]),
            buff=0,
            color=ACCENT,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.16,
        )
        e2_target = Arrow(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * np.array([1.0, 2.0, 0.0]),
            buff=0,
            color=GOOD,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.11,
        )

        base_brace = BraceBetweenPoints(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * RIGHT,
            direction=DOWN,
            color=BLACK,
            buff=0.08,
        )
        base_label = MathTex("1", font_size=30).next_to(base_brace, DOWN, buff=0.08)
        height_line = DashedLine(
            DIAGRAM_ORIGIN + UNIT * RIGHT,
            DIAGRAM_ORIGIN + UNIT * np.array([1.0, 2.0, 0.0]),
            color=WARN,
            stroke_width=2.6,
        )
        height_brace = BraceBetweenPoints(
            height_line.get_start(),
            height_line.get_end(),
            direction=RIGHT,
            color=WARN,
            buff=0.08,
        )
        height_label = MathTex("2", font_size=30, color=WARN).next_to(
            height_brace, RIGHT, buff=0.08
        )
        area_chain = MathTex(
            r"\text{aire }1\ \longrightarrow\ \text{aire }2",
            font_size=41,
        ).to_edge(DOWN, buff=0.42)
        determinant_a = MathTex(r"\det(A)=2", font_size=51, color=ACCENT)
        determinant_a.next_to(area_chain, UP, buff=0.24)

        with self.narrated(SCRIPT[1]):
            self.play(FadeIn(heading), Write(matrix_a), run_time=0.7)
            self.play(Create(grid), Create(square), run_time=0.85)
            self.wait_until_bookmark("show_basis")
            self.play(
                GrowArrow(e1),
                GrowArrow(e2),
                FadeIn(e1_label),
                FadeIn(e2_label),
                run_time=0.8,
            )
            self.wait(0.9)

            self.wait_until_bookmark("apply_a")
            self.play(
                FadeOut(e1_label),
                FadeOut(e2_label),
                Transform(grid, grid_target),
                Transform(square, square_target),
                Transform(e1, e1_target),
                Transform(e2, e2_target),
                run_time=2.0,
            )
            self.play(FadeIn(column_images, shift=LEFT * 0.10), run_time=0.55)
            self.wait(0.9)

            self.wait_until_bookmark("measure_area")
            self.play(
                Create(base_brace),
                Write(base_label),
                Create(height_line),
                Create(height_brace),
                Write(height_label),
                run_time=0.9,
            )
            self.play(Write(area_chain), run_time=0.75)
            self.wait(1.0)

            self.wait_until_bookmark("name_det")
            self.play(Write(determinant_a), run_time=0.75)
            self.play(Circumscribe(determinant_a, color=ACCENT), run_time=0.8)
            self.wait(1.1)

        self.clear_page(
            heading,
            grid,
            square,
            e1,
            e2,
            matrix_a,
            column_images,
            base_brace,
            base_label,
            height_line,
            height_brace,
            height_label,
            area_chain,
            determinant_a,
        )

        # ==============================================================
        # PAGE 3 — Negative determinant: same area, reversed orientation
        # ==============================================================
        heading = self.make_heading("Le signe repère un retournement")
        mirror = DashedLine(
            UP * 2.10,
            DOWN * 2.90,
            color=MUTED,
            stroke_width=2.2,
        )
        mirror_label = Text("axe miroir", font_size=25, color=MUTED).next_to(
            mirror, DOWN, buff=0.12
        )
        square = self.make_unit_square()
        e1, e2 = self.make_basis_vectors()
        orientation = self.make_orientation_arc(
            DIAGRAM_ORIGIN + UNIT * 0.5 * (RIGHT + UP),
            clockwise=False,
        )
        direct_label = Text("sens direct", font_size=27, color=ACCENT).to_corner(
            DR, buff=0.48
        )
        matrix_b = MathTex(
            r"B=\begin{pmatrix}-1&0\\0&1\end{pmatrix}",
            font_size=40,
        ).to_corner(UR, buff=0.44).shift(DOWN * 0.62)

        square_target = self.linear_target(square, B_MATRIX)
        e1_target = Arrow(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * LEFT,
            buff=0,
            color=ACCENT,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.16,
        )
        e2_target = Arrow(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * UP,
            buff=0,
            color=GOOD,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.16,
        )
        orientation_target = self.make_orientation_arc(
            DIAGRAM_ORIGIN + UNIT * 0.5 * (LEFT + UP),
            clockwise=True,
            color=WARN,
        )
        reversed_label = Text("sens renversé", font_size=27, color=WARN).to_corner(
            DR, buff=0.48
        )
        absolute_det = MathTex(r"|\det(B)|=1", font_size=46).next_to(
            reversed_label, UP, buff=0.28
        )
        negative_det = MathTex(r"\det(B)=-1", font_size=52, color=WARN).move_to(
            absolute_det
        )

        with self.narrated(SCRIPT[2]):
            self.play(FadeIn(heading), Write(matrix_b), run_time=0.65)
            self.play(Create(mirror), FadeIn(mirror_label), run_time=0.55)
            self.play(
                Create(square),
                GrowArrow(e1),
                GrowArrow(e2),
                Create(orientation),
                FadeIn(direct_label),
                run_time=0.85,
            )
            self.wait(0.9)

            self.wait_until_bookmark("reflect")
            self.play(
                Transform(square, square_target),
                Transform(e1, e1_target),
                Transform(e2, e2_target),
                Transform(orientation, orientation_target),
                ReplacementTransform(direct_label, reversed_label),
                run_time=1.75,
            )
            self.play(Write(absolute_det), run_time=0.65)
            self.wait(0.9)

            self.wait_until_bookmark("negative_det")
            self.play(ReplacementTransform(absolute_det, negative_det), run_time=0.65)
            self.play(Indicate(orientation, color=WARN), run_time=0.75)
            self.wait(1.1)

        self.clear_page(
            heading,
            mirror,
            mirror_label,
            square,
            e1,
            e2,
            orientation,
            matrix_b,
            reversed_label,
            negative_det,
        )

        # ==============================================================
        # PAGE 4 — Zero determinant: collapse and explicit information loss
        # ==============================================================
        heading = self.make_heading("Déterminant zéro : le plan est écrasé sur une droite")
        grid = self.make_grid()
        square = self.make_unit_square()
        e1, e2 = self.make_basis_vectors()
        matrix_c = MathTex(
            r"C=\begin{pmatrix}1&2\\0&0\end{pmatrix}",
            font_size=40,
        ).to_corner(UR, buff=0.44).shift(DOWN * 0.62)
        column_relation = MathTex(
            r"C\vec e_2=2C\vec e_1",
            font_size=35,
            color=WARN,
        ).to_corner(DR, buff=0.46).shift(UP * 0.72)

        p_point = DIAGRAM_ORIGIN + UNIT * np.array([P_VECTOR[0], P_VECTOR[1], 0.0])
        q_point = DIAGRAM_ORIGIN + UNIT * np.array([Q_VECTOR[0], Q_VECTOR[1], 0.0])
        image_point = DIAGRAM_ORIGIN + UNIT * np.array(
            [COMMON_IMAGE[0], COMMON_IMAGE[1], 0.0]
        )
        p_dot = Dot(p_point, radius=0.082, color=GOOD)
        q_dot = Dot(q_point, radius=0.082, color=WARN)
        p_label = MathTex(r"P=(0,1)", font_size=28, color=GOOD).next_to(
            p_dot, LEFT, buff=0.14
        )
        q_label = MathTex(r"Q=(1,\tfrac12)", font_size=28, color=WARN).next_to(
            q_dot, RIGHT, buff=0.14
        )

        grid_target = self.linear_target(grid, C_MATRIX)
        collapsed_square = Line(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * 3 * RIGHT,
            color=ACCENT,
            stroke_width=8,
        )
        e1_target = Arrow(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * RIGHT,
            buff=0,
            color=ACCENT,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.16,
        )
        e2_target = Arrow(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * 2 * RIGHT,
            buff=0,
            color=GOOD,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.10,
        )
        p_target = Dot(image_point, radius=0.082, color=GOOD)
        q_target = Dot(image_point, radius=0.082, color=WARN)
        image_ring = Circle(radius=0.18, stroke_color=BLACK, stroke_width=2.4).move_to(
            image_point
        )
        merged_label = MathTex(
            r"C(P)=C(Q)=(2,0)",
            font_size=39,
        ).next_to(image_point, DOWN, buff=0.34)
        distinct_label = MathTex(r"P\neq Q", font_size=38).next_to(
            merged_label, DOWN, buff=0.18
        )
        determinant_zero = MathTex(r"\det(C)=0", font_size=55, color=WARN).to_corner(
            DR, buff=0.46
        )

        with self.narrated(SCRIPT[3]):
            self.play(FadeIn(heading), Write(matrix_c), run_time=0.65)
            self.play(Create(grid), Create(square), run_time=0.8)
            self.play(
                GrowArrow(e1),
                GrowArrow(e2),
                FadeIn(p_dot),
                FadeIn(q_dot),
                FadeIn(p_label),
                FadeIn(q_label),
                run_time=0.8,
            )
            self.play(Write(column_relation), run_time=0.65)
            self.wait(0.9)

            self.wait_until_bookmark("collapse")
            self.play(
                Transform(grid, grid_target),
                ReplacementTransform(square, collapsed_square),
                Transform(e1, e1_target),
                Transform(e2, e2_target),
                FadeOut(p_label),
                FadeOut(q_label),
                run_time=1.75,
            )
            self.wait(1.0)

            self.wait_until_bookmark("merge_points")
            self.play(
                Transform(p_dot, p_target),
                Transform(q_dot, q_target),
                run_time=1.2,
            )
            self.play(
                Create(image_ring),
                Write(merged_label),
                Write(distinct_label),
                run_time=0.75,
            )
            self.wait(1.0)

            self.wait_until_bookmark("det_zero")
            self.play(Write(determinant_zero), run_time=0.7)
            self.play(Circumscribe(determinant_zero, color=WARN), run_time=0.8)
            self.wait(1.1)

        self.clear_page(
            heading,
            matrix_c,
            column_relation,
            grid,
            collapsed_square,
            e1,
            e2,
            p_dot,
            q_dot,
            image_ring,
            merged_label,
            distinct_label,
            determinant_zero,
        )

        # ==============================================================
        # PAGE 5 — Why no inverse can exist
        # ==============================================================
        heading = self.make_heading("Une même sortie ne peut pas retrouver deux entrées")
        output_dot = Dot(UP * 0.70, radius=0.10, color=BLACK)
        inverse_question = MathTex(r"C^{-1}(2,0)=\ ?", font_size=48).next_to(
            output_dot, UP, buff=0.24
        )
        p_choice = Dot(LEFT * 3.10 + DOWN * 1.25, radius=0.09, color=GOOD)
        q_choice = Dot(RIGHT * 3.10 + DOWN * 1.25, radius=0.09, color=WARN)
        p_name = MathTex(r"P=(0,1)", font_size=34, color=GOOD).next_to(
            p_choice, DOWN, buff=0.15
        )
        q_name = MathTex(r"Q=(1,\tfrac12)", font_size=34, color=WARN).next_to(
            q_choice, DOWN, buff=0.15
        )
        back_to_p = Arrow(
            output_dot.get_center() + LEFT * 0.10 + DOWN * 0.08,
            p_choice.get_center() + UP * 0.12,
            buff=0.15,
            color=GOOD,
            stroke_width=3.2,
        )
        back_to_q = Arrow(
            output_dot.get_center() + RIGHT * 0.10 + DOWN * 0.08,
            q_choice.get_center() + UP * 0.12,
            buff=0.15,
            color=WARN,
            stroke_width=3.2,
        )
        two_antecedents = Text(
            "une sortie, deux antécédents",
            font_size=30,
            color=WARN,
        ).to_edge(DOWN, buff=0.88)
        no_inverse = VGroup(
            MathTex(r"\det(C)=0", font_size=45, color=WARN),
            MathTex(r"\Longrightarrow", font_size=40),
            MathTex(r"C^{-1}\ \text{n'existe pas}", font_size=42, color=WARN),
        ).arrange(RIGHT, buff=0.30).to_edge(DOWN, buff=0.32)

        with self.narrated(SCRIPT[4]):
            self.play(FadeIn(heading), FadeIn(output_dot), Write(inverse_question), run_time=0.7)
            self.play(FadeIn(p_choice), FadeIn(q_choice), FadeIn(p_name), FadeIn(q_name), run_time=0.6)
            self.wait(0.9)

            self.wait_until_bookmark("ask_inverse")
            self.play(GrowArrow(back_to_p), GrowArrow(back_to_q), run_time=0.9)
            self.play(FadeIn(two_antecedents, shift=UP * 0.10), run_time=0.55)
            self.wait(1.0)

            self.wait_until_bookmark("no_inverse")
            self.play(FadeOut(two_antecedents), run_time=0.3)
            self.play(Write(no_inverse), run_time=0.85)
            self.play(Circumscribe(no_inverse, color=WARN), run_time=0.8)
            self.wait(1.1)

        self.clear_page(
            heading,
            output_dot,
            inverse_question,
            p_choice,
            q_choice,
            p_name,
            q_name,
            back_to_p,
            back_to_q,
            no_inverse,
        )

        # ==============================================================
        # PAGE 6 — Apply the actual inverse transformation
        # ==============================================================
        heading = self.make_heading("Une matrice inverse défait la transformation")
        grid = self.make_grid()
        square = self.make_unit_square()
        e1, e2 = self.make_basis_vectors()

        grid_a = self.linear_target(grid, A_MATRIX)
        square_a = self.linear_target(square, A_MATRIX)
        e1_a = Arrow(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * np.array([1.0, 0.0, 0.0]),
            buff=0,
            color=ACCENT,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.16,
        )
        e2_a = Arrow(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * np.array([1.0, 2.0, 0.0]),
            buff=0,
            color=GOOD,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.11,
        )

        # The return targets are computed by A^{-1}; they are not mere copies.
        grid_back = self.linear_target(grid_a, A_INVERSE)
        square_back = self.linear_target(square_a, A_INVERSE)
        e1_back_xy = A_INVERSE @ (A_MATRIX @ np.array([1.0, 0.0]))
        e2_back_xy = A_INVERSE @ (A_MATRIX @ np.array([0.0, 1.0]))
        e1_back = Arrow(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * np.array([e1_back_xy[0], e1_back_xy[1], 0.0]),
            buff=0,
            color=ACCENT,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.16,
        )
        e2_back = Arrow(
            DIAGRAM_ORIGIN,
            DIAGRAM_ORIGIN + UNIT * np.array([e2_back_xy[0], e2_back_xy[1], 0.0]),
            buff=0,
            color=GOOD,
            stroke_width=4,
            max_tip_length_to_length_ratio=0.16,
        )

        matrix_a = MathTex(
            r"A=\begin{pmatrix}1&1\\0&2\end{pmatrix}",
            font_size=37,
        ).to_corner(UR, buff=0.44).shift(DOWN * 0.62)
        inverse_a = MathTex(
            r"A^{-1}=\begin{pmatrix}1&-\tfrac12\\0&\tfrac12\end{pmatrix}",
            font_size=37,
            color=GOOD,
        ).to_corner(UR, buff=0.44).shift(DOWN * 1.72)
        stage_text = Text("A : déformation", font_size=29, color=ACCENT).to_edge(
            DOWN, buff=0.44
        )
        undo_text = Text("A⁻¹ : retour exact", font_size=29, color=GOOD).to_edge(
            DOWN, buff=0.44
        )
        identity = MathTex(r"A^{-1}A=I", font_size=58, color=GOOD).to_edge(
            DOWN, buff=0.38
        )

        with self.narrated(SCRIPT[5]):
            self.play(FadeIn(heading), Write(matrix_a), Write(inverse_a), run_time=0.75)
            self.play(Create(grid), Create(square), GrowArrow(e1), GrowArrow(e2), run_time=0.85)

            self.wait_until_bookmark("deform")
            self.play(Indicate(matrix_a, color=ACCENT), run_time=0.55)
            self.play(
                Transform(grid, grid_a),
                Transform(square, square_a),
                Transform(e1, e1_a),
                Transform(e2, e2_a),
                FadeIn(stage_text, shift=UP * 0.10),
                run_time=1.8,
            )
            self.wait(1.0)

            self.wait_until_bookmark("undo")
            self.play(Indicate(inverse_a, color=GOOD), FadeOut(stage_text), run_time=0.55)
            self.play(
                Transform(grid, grid_back),
                Transform(square, square_back),
                Transform(e1, e1_back),
                Transform(e2, e2_back),
                FadeIn(undo_text, shift=UP * 0.10),
                run_time=1.8,
            )
            self.wait(1.0)

            self.wait_until_bookmark("identity")
            self.play(FadeOut(undo_text), run_time=0.3)
            self.play(Write(identity), run_time=0.75)
            self.play(Circumscribe(identity, color=GOOD), run_time=0.8)
            self.wait(1.1)

        self.clear_page(heading, grid, square, e1, e2, matrix_a, inverse_a, identity)

        # ==============================================================
        # PAGE 7 — Determinant formula, constructed and checked
        # ==============================================================
        heading = self.make_heading("Le calcul du déterminant : deux produits en croix")
        matrix_m = Matrix(
            [["a", "b"], ["c", "d"]],
            element_to_mobject_config={"font_size": 48},
            bracket_h_buff=0.22,
            bracket_v_buff=0.18,
        )
        matrix_group = VGroup(MathTex("M=", font_size=50), matrix_m).arrange(RIGHT, buff=0.25)
        matrix_group.shift(UP * 1.05)
        entries = matrix_m.get_entries()
        a_entry, b_entry, c_entry, d_entry = entries

        first_boxes = VGroup(
            SurroundingRectangle(a_entry, color=ACCENT, buff=0.10, stroke_width=2.4),
            SurroundingRectangle(d_entry, color=ACCENT, buff=0.10, stroke_width=2.4),
        )
        second_boxes = VGroup(
            SurroundingRectangle(b_entry, color=WARN, buff=0.10, stroke_width=2.4),
            SurroundingRectangle(c_entry, color=WARN, buff=0.10, stroke_width=2.4),
        )

        det_prefix = MathTex(r"\det(M)=", font_size=55)
        first_product = MathTex(r"ad", font_size=57, color=ACCENT)
        minus_sign = MathTex("-", font_size=57)
        second_product = MathTex(r"bc", font_size=57, color=WARN)
        determinant_formula = VGroup(
            det_prefix,
            first_product,
            minus_sign,
            second_product,
        ).arrange(RIGHT, buff=0.18).shift(DOWN * 0.18)

        check_a = MathTex(
            r"\det(A)=1\cdot2-1\cdot0=2",
            font_size=47,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.48)

        with self.narrated(SCRIPT[6]):
            self.play(FadeIn(heading), Write(matrix_group), run_time=0.75)
            self.play(Write(det_prefix), run_time=0.5)

            self.wait_until_bookmark("first_product")
            self.play(Create(first_boxes), Indicate(a_entry), Indicate(d_entry), run_time=0.7)
            self.play(Write(first_product), run_time=0.55)
            self.wait(0.8)

            self.wait_until_bookmark("second_product")
            self.play(ReplacementTransform(first_boxes, second_boxes), run_time=0.55)
            self.play(Write(minus_sign), Write(second_product), run_time=0.65)
            self.wait(0.9)

            self.wait_until_bookmark("check_a")
            self.play(FadeOut(second_boxes), run_time=0.3)
            self.play(Write(check_a), run_time=0.8)
            self.play(Circumscribe(check_a, color=ACCENT), run_time=0.8)
            self.wait(1.1)

        self.clear_page(heading, matrix_group, determinant_formula, check_a)

        # ==============================================================
        # PAGE 8 — Why the inverse formula has this exact structure
        # ==============================================================
        heading = self.make_heading("Pourquoi la formule de l’inverse fonctionne")
        m_formula = MathTex(
            r"M=\begin{pmatrix}a&b\\c&d\end{pmatrix}",
            font_size=43,
        )
        helper_formula = MathTex(
            r"N=\begin{pmatrix}d&-b\\-c&a\end{pmatrix}",
            font_size=43,
            color=GOOD,
        )
        top_formulas = VGroup(m_formula, helper_formula).arrange(RIGHT, buff=1.15)
        top_formulas.shift(UP * 1.22)

        product_formula = MathTex(
            r"NM=MN="
            r"\begin{pmatrix}ad-bc&0\\0&ad-bc\end{pmatrix}",
            font_size=43,
        ).shift(UP * 0.05)
        product_simplified = MathTex(
            r"NM=MN=\det(M)I",
            font_size=50,
            color=ACCENT,
        ).move_to(product_formula)
        condition = MathTex(r"\det(M)\neq0", font_size=44, color=GOOD).shift(DOWN * 0.82)
        inverse_formula = MathTex(
            r"M^{-1}=\frac1{\det(M)}"
            r"\begin{pmatrix}d&-b\\-c&a\end{pmatrix}",
            font_size=47,
        ).to_edge(DOWN, buff=0.40)
        condition_box = SurroundingRectangle(condition, color=GOOD, buff=0.15, stroke_width=2.4)

        with self.narrated(SCRIPT[7]):
            self.play(FadeIn(heading), Write(m_formula), run_time=0.6)

            self.wait_until_bookmark("candidate")
            self.play(Write(helper_formula), run_time=0.75)
            self.wait(0.9)

            self.wait_until_bookmark("multiply")
            self.play(Write(product_formula), run_time=0.95)
            self.play(Circumscribe(product_formula, color=ACCENT), run_time=0.75)
            self.play(FadeOut(product_formula), run_time=0.30)
            self.play(FadeIn(product_simplified), run_time=0.40)
            self.wait(1.0)

            self.wait_until_bookmark("divide_det")
            self.play(Write(condition), Create(condition_box), run_time=0.65)
            self.play(Write(inverse_formula), run_time=0.9)
            self.play(Circumscribe(inverse_formula, color=GOOD), run_time=0.8)
            self.wait(1.2)

        self.clear_page(
            heading,
            m_formula,
            helper_formula,
            product_simplified,
            condition,
            condition_box,
            inverse_formula,
        )

        # ==============================================================
        # PAGE 9 — Recap without decorative boxes
        # ==============================================================
        heading = self.make_heading("À retenir")
        area_row = self.make_recap_row(
            r"|\det(M)|",
            "facteur d’aire",
            color=ACCENT,
        )
        sign_row = self.make_recap_row(
            r"\det(M)<0",
            "orientation renversée",
            color=WARN,
        )
        zero_row = self.make_recap_row(
            r"\det(M)=0",
            "information perdue, aucune inverse",
            color=WARN,
        )
        nonzero_row = self.make_recap_row(
            r"\det(M)\neq0",
            "la matrice inverse existe",
            color=GOOD,
        )
        rows = VGroup(area_row, sign_row, zero_row, nonzero_row).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.36,
        )
        rows.shift(UP * 0.10)
        system_link = MathTex(
            r"Mx=b\quad\Longrightarrow\quad x=M^{-1}b",
            font_size=43,
        ).to_edge(DOWN, buff=0.30)

        with self.narrated(SCRIPT[8]):
            self.play(FadeIn(heading), run_time=0.45)
            self.wait_until_bookmark("recap_area")
            self.play(FadeIn(area_row, shift=UP * 0.08), run_time=0.55)
            self.wait(0.65)

            self.wait_until_bookmark("recap_sign")
            self.play(FadeIn(sign_row, shift=UP * 0.08), run_time=0.55)
            self.wait(0.65)

            self.wait_until_bookmark("recap_zero")
            self.play(FadeIn(zero_row, shift=UP * 0.08), run_time=0.55)
            self.wait(0.65)

            self.wait_until_bookmark("recap_nonzero")
            self.play(FadeIn(nonzero_row, shift=UP * 0.08), run_time=0.55)
            self.wait(0.8)
            self.play(Write(system_link), run_time=0.75)
            self.wait(1.3)

        self.wait(1.0)
