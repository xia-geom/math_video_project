"""Opérations sur les matrices — seconde passe approfondie.

La capsule distingue les opérations entrée par entrée du produit matriciel. Le
produit n'est pas donné comme une recette arbitraire : il est construit à partir
de l'action d'une matrice sur un vecteur, puis de la composition de deux actions.

Principes de cette seconde passe : résultats cachés avant le calcul, plans à unités
égales, deux chemins séparés pour la non-commutativité, et pauses lisibles même sans TTS.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GRAY_D,
    GRAY_E,
    GREEN_D,
    LEFT,
    RED_D,
    RIGHT,
    SEMIBOLD,
    UP,
    WHITE,
    Arrow,
    Create,
    Cross,
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    MathTex,
    Matrix,
    Mobject,
    NumberPlane,
    Rectangle,
    ReplacementTransform,
    RoundedRectangle,
    Scene,
    Square,
    SurroundingRectangle,
    Tex,
    Text,
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
    from manim_voiceover.services.azure import AzureService
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
SECONDARY = GRAY_D
RESULT = GREEN_D
WARN = RED_D
PALE = GRAY_E
VOICE_SPEED = 0.86


# ---------------------------------------------------------------------------
# Narration
# ---------------------------------------------------------------------------
SCRIPT = [
    {
        "caption": "Pourquoi l’addition et le produit suivent-ils des règles différentes ?",
        "ssml": tts.ssml(
            "Pourquoi additionne-t-on les matrices case par case, "
            "mais les multiplie-t-on ligne par colonne ? "
            "<break time='350ms'/>Nous allons construire le sens de chaque opération."
        ),
    },
    {
        "caption": "Additionner, c’est combiner les mêmes positions.",
        "ssml": tts.ssml(
            "Dans deux matrices de mêmes dimensions, une même position représente une même catégorie. "
            "<bookmark mark='sum_11'/>La première entrée combine donc les deux premières entrées. "
            "<bookmark mark='sum_12'/>On garde exactement la même position pour l'entrée suivante. "
            "<bookmark mark='sum_rest'/>La règle se répète dans toute la matrice. "
            "<bookmark mark='sum_done'/>La soustraction suit la même logique : elle ajoute la matrice opposée."
        ),
    },
    {
        "caption": "Un scalaire multiplie toutes les entrées.",
        "ssml": tts.ssml(
            "Multiplier une matrice par un nombre reste une opération entrée par entrée. "
            "<bookmark mark='scalar_first'/>Trois fois deux donne six. "
            "<bookmark mark='scalar_rest'/>Le même facteur trois agit ensuite partout. "
            "<bookmark mark='scalar_done'/>La forme de la matrice ne change pas."
        ),
    },
    {
        "caption": "Une matrice transforme un vecteur.",
        "ssml": tts.ssml(
            "Pour comprendre le produit matriciel, commençons par une matrice qui agit sur un vecteur. "
            f"<bookmark mark='show_p'/>Le vecteur {tts.char('p')} vaut un, deux. "
            f"<bookmark mark='show_ap'/>La matrice {tts.char('A')} l'envoie vers trois, deux. "
            "<bookmark mark='row_one'/>La première coordonnée vient de la première ligne de la matrice. "
            "<bookmark mark='row_two'/>La deuxième coordonnée vient de la deuxième ligne. "
            "<bookmark mark='vector_done'/>Chaque ligne produit donc une coordonnée de sortie."
        ),
    },
    {
        "caption": "Appliquer A puis B donne la transformation BA.",
        "ssml": tts.ssml(
            f"Appliquons maintenant {tts.char('A')}, puis {tts.char('B')}. "
            f"<bookmark mark='first_action'/>Après {tts.char('A')}, le point arrive en trois, deux. "
            f"<bookmark mark='second_action'/>{tts.char('B')} double ensuite la hauteur et donne trois, quatre. "
            f"<bookmark mark='composition_name'/>La transformation complète s'écrit {tts.char('B')} {tts.char('A')}, "
            "car la matrice de droite agit en premier."
        ),
    },
    {
        "caption": "Le produit transforme les colonnes de la matrice de droite.",
        "ssml": tts.ssml(
            "Une matrice est déterminée par ce qu'elle fait aux deux directions de base. "
            "Ses colonnes enregistrent précisément ces deux images. "
            f"<bookmark mark='first_column'/>Pour la première colonne du produit, {tts.char('B')} agit sur la première colonne de {tts.char('A')}. "
            f"<bookmark mark='second_column'/>Pour la deuxième, {tts.char('B')} agit sur la deuxième colonne de {tts.char('A')}. "
            "<bookmark mark='row_column'/>Écrit entrée par entrée, ce même calcul devient ligne par colonne. "
            "<bookmark mark='product_done'/>On obtient la matrice un, un, zéro, deux."
        ),
    },
    {
        "caption": "Les dimensions intérieures doivent coïncider.",
        "ssml": tts.ssml(
            "La règle ligne par colonne impose une condition de taille. "
            "<bookmark mark='matching_grid'/>Une ligne de trois nombres peut rencontrer une colonne de trois nombres. "
            "<bookmark mark='output_grid'/>Deux lignes à gauche et deux colonnes à droite produisent une matrice deux par deux. "
            "<bookmark mark='bad_grid'/>Si les nombres intérieurs diffèrent, le produit n'est pas défini."
        ),
    },
    {
        "caption": "Changer l’ordre change généralement le résultat.",
        "ssml": tts.ssml(
            "Comparons maintenant les deux ordres sur le même point de départ. "
            f"<bookmark mark='left_path'/>À gauche, {tts.char('A')} puis {tts.char('B')} conduit à trois, quatre. "
            f"<bookmark mark='right_path'/>À droite, {tts.char('B')} puis {tts.char('A')} conduit à cinq, quatre. "
            f"<bookmark mark='neq'/>Les deux points finaux sont différents : {tts.char('B')} {tts.char('A')} n'est pas égal à {tts.char('A')} {tts.char('B')}."
        ),
    },
    {
        "caption": "Mêmes cases, même scalaire, ou composition de transformations.",
        "ssml": tts.ssml(
            "À retenir. "
            "<bookmark mark='recap_add'/>Addition et soustraction : mêmes positions et mêmes dimensions. "
            "<bookmark mark='recap_scalar'/>Scalaire : le même nombre multiplie toutes les entrées. "
            "<bookmark mark='recap_product'/>Produit : composition, ligne par colonne, dimensions compatibles, et ordre essentiel."
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


BaseScene = VoiceoverScene if VoiceoverScene is not None else Scene


class OperationsMatricesFR(BaseScene):
    """Addition, multiplication scalaire et multiplication matricielle."""

    # ------------------------------------------------------------------
    # Voiceover
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
            self.set_speech_service(
                AzureService(voice=tts.VOICE_ID, global_speed=VOICE_SPEED)
            )
        except Exception as exc:
            print(f"[voiceover] Azure Speech setup failed: {exc}. Rendering without narration.")
            return
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, item: dict[str, str]):
        if self._voiceover_enabled:
            with self.voiceover(text=item["ssml"], subcaption=item["caption"]) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def sync(self, mark: str, silent_wait: float = 0.55) -> None:
        """Wait for a narration bookmark, or pause in silent previews."""
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)
        else:
            self.wait(silent_wait)

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------
    def clear_page(self, *mobjects: Mobject, run_time: float = 0.65) -> None:
        """Fade the frame to white, then remove the actual scene graph.

        Several worked examples replace entries inside a ``Matrix``.  Fading a
        previously assembled parent group after such a replacement can make
        Manim add the parent's obsolete ``?`` entries back to the scene.  A
        full-frame curtain gives the same soft page transition without
        replaying any stale submobjects.
        """
        del mobjects  # Kept in the signature for readable call sites.
        if not self.mobjects:
            return
        curtain = Rectangle(
            width=config.frame_width + 0.2,
            height=config.frame_height + 0.2,
            stroke_opacity=0,
            fill_color=WHITE,
            fill_opacity=1,
        ).set_z_index(10_000)
        self.play(FadeIn(curtain), run_time=run_time)
        self.clear()

    def make_heading(self, text: str) -> Text:
        heading = Text(text, font_size=36, weight=SEMIBOLD)
        if heading.width > 12.2:
            heading.scale_to_fit_width(12.2)
        return heading.to_edge(UP, buff=0.35)

    def make_matrix(self, entries: list[list[object]], *, font_size: int = 42) -> Matrix:
        return Matrix(
            entries,
            h_buff=1.0,
            v_buff=0.76,
            bracket_h_buff=0.16,
            bracket_v_buff=0.14,
            element_to_mobject_config={"font_size": font_size},
        )

    def labeled_matrix(self, symbol: str, entries: list[list[object]]) -> VGroup:
        symbol_mob = MathTex(symbol, font_size=38)
        matrix = self.make_matrix(entries)
        return VGroup(symbol_mob, matrix).arrange(RIGHT, buff=0.18)

    def make_plane(
        self,
        *,
        x_range: tuple[int, int, int] = (-1, 7, 1),
        y_range: tuple[int, int, int] = (-1, 5, 1),
        unit_size: float = 0.68,
        center=LEFT * 3.2 + DOWN * 0.15,
    ) -> NumberPlane:
        """Create a plane with the same visual unit on both axes."""
        x_span = x_range[1] - x_range[0]
        y_span = y_range[1] - y_range[0]
        plane = NumberPlane(
            x_range=x_range,
            y_range=y_range,
            x_length=x_span * unit_size,
            y_length=y_span * unit_size,
            background_line_style={
                "stroke_color": PALE,
                "stroke_width": 1.3,
                "stroke_opacity": 0.82,
            },
            axis_config={
                "color": BLACK,
                "stroke_width": 2.1,
                "include_tip": True,
            },
        )
        plane.move_to(center)
        return plane

    def point_vector(
        self,
        plane: NumberPlane,
        coordinates: tuple[float, float],
        *,
        color=ACCENT,
        stroke_width: float = 6,
    ) -> VGroup:
        arrow = Arrow(
            plane.c2p(0, 0),
            plane.c2p(*coordinates),
            buff=0,
            color=color,
            stroke_width=stroke_width,
            max_tip_length_to_length_ratio=0.16,
        )
        dot = Dot(plane.c2p(*coordinates), radius=0.085, color=color)
        return VGroup(arrow, dot)

    def formula_panel(self, *lines: Mobject, width: float = 5.1) -> VGroup:
        content = VGroup(*lines).arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        if content.width > width - 0.55:
            content.scale_to_fit_width(width - 0.55)
        box = RoundedRectangle(
            width=width,
            height=max(2.2, content.height + 0.58),
            corner_radius=0.16,
            stroke_color=BLACK,
            stroke_width=2.2,
            fill_color=WHITE,
            fill_opacity=0.97,
        )
        content.move_to(box)
        return VGroup(box, content).move_to(RIGHT * 3.72 + DOWN * 0.1)

    def make_grid(self, rows: int, columns: int, *, cell_size: float = 0.5) -> VGroup:
        cells = VGroup()
        for row in range(rows):
            for column in range(columns):
                cell = Square(
                    side_length=cell_size,
                    stroke_color=BLACK,
                    stroke_width=2,
                    fill_color=ACCENT,
                    fill_opacity=0.035,
                )
                cell.move_to(
                    RIGHT * column * cell_size
                    + DOWN * row * cell_size
                )
                cells.add(cell)
        cells.center()
        return cells

    def recap_card(self, title: str, formula: str, note: str) -> VGroup:
        box = RoundedRectangle(
            width=3.85,
            height=3.2,
            corner_radius=0.18,
            stroke_color=BLACK,
            stroke_width=2.1,
            fill_color=ACCENT,
            fill_opacity=0.05,
        )
        title_mob = Text(title, font_size=30, weight=SEMIBOLD)
        formula_mob = MathTex(formula, font_size=39, color=ACCENT)
        if formula_mob.width > 3.25:
            formula_mob.scale_to_fit_width(3.25)
        note_mob = Text(note, font_size=24, line_spacing=0.95)
        note_mob.scale_to_fit_width(3.15)
        content = VGroup(title_mob, formula_mob, note_mob).arrange(DOWN, buff=0.34)
        content.move_to(box)
        return VGroup(box, content)

    # ------------------------------------------------------------------
    # Scene
    # ------------------------------------------------------------------
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        # --------------------------------------------------------------
        # 0. Central question
        # --------------------------------------------------------------
        title = Text("Matrices 2 — opérations", font_size=48, weight=SEMIBOLD)
        question = Text(
            "Pourquoi deux règles de calcul différentes ?",
            font_size=34,
        )
        title.shift(UP * 0.95)
        question.next_to(title, DOWN, buff=0.48)
        addition_icon = MathTex(
            r"\begin{pmatrix}a&b\\c&d\end{pmatrix}"
            r"+"
            r"\begin{pmatrix}e&f\\g&h\end{pmatrix}",
            font_size=41,
            color=ACCENT,
        )
        product_icon = MathTex(
            r"\text{ligne}\cdot\text{colonne}",
            font_size=42,
            color=RESULT,
        )
        icons = VGroup(addition_icon, product_icon).arrange(RIGHT, buff=1.0)
        icons.move_to(DOWN * 0.8)

        with self.narrated(SCRIPT[0]):
            self.play(FadeIn(title), run_time=0.7)
            self.play(Write(question), run_time=1.0)
            self.play(Write(addition_icon), run_time=0.9)
            self.play(Write(product_icon), run_time=0.9)
            self.wait(1.1)
        self.clear_page(title, question, icons)

        # --------------------------------------------------------------
        # 1. Addition and subtraction: same positions
        # --------------------------------------------------------------
        heading = self.make_heading("Addition : mêmes dimensions, mêmes positions")
        matrix_a = self.make_matrix([[12, 8], [5, 10]])
        matrix_b = self.make_matrix([[3, 4], [2, 1]])
        result_matrix = self.make_matrix([["?", "?"], ["?", "?"]])
        plus = MathTex("+", font_size=52)
        equals = MathTex("=", font_size=52)
        group = VGroup(matrix_a, plus, matrix_b, equals, result_matrix)
        group.arrange(RIGHT, buff=0.4).scale_to_fit_width(11.5).move_to(UP * 0.25)
        label_a = MathTex("A", font_size=31, color=ACCENT).next_to(matrix_a, DOWN, buff=0.2)
        label_b = MathTex("B", font_size=31, color=SECONDARY).next_to(matrix_b, DOWN, buff=0.2)
        label_sum = MathTex("A+B", font_size=31, color=RESULT).next_to(result_matrix, DOWN, buff=0.2)

        entries_a = matrix_a.get_entries()
        entries_b = matrix_b.get_entries()
        entries_r = result_matrix.get_entries()
        calculations = [
            (r"12+3=15", "15", "sum_11"),
            (r"8+4=12", "12", "sum_12"),
            (r"5+2=7", "7", None),
            (r"10+1=11", "11", None),
        ]
        computed_entries = VGroup()
        current_boxes: VGroup | None = None
        current_calc: MathTex | None = None

        subtraction_note = MathTex(
            r"A-B=A+(-1)B",
            font_size=40,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.55)
        dimensions_note = Text(
            "Addition et soustraction : matrices de mêmes dimensions",
            font_size=27,
            color=SECONDARY,
        ).next_to(subtraction_note, UP, buff=0.28)

        with self.narrated(SCRIPT[1]):
            self.play(
                FadeIn(heading),
                FadeIn(group),
                FadeIn(label_a),
                FadeIn(label_b),
                FadeIn(label_sum),
                run_time=1.0,
            )
            for index, (calculation, value, bookmark) in enumerate(calculations):
                if bookmark is not None:
                    self.sync(bookmark, 0.55)
                elif index == 2:
                    self.sync("sum_rest", 0.5)

                boxes = VGroup(
                    SurroundingRectangle(entries_a[index], color=ACCENT, buff=0.1, stroke_width=3),
                    SurroundingRectangle(entries_b[index], color=SECONDARY, buff=0.1, stroke_width=3),
                )
                calc = MathTex(calculation, font_size=38, color=RESULT).to_edge(DOWN, buff=0.55)
                new_entry = MathTex(value, font_size=42, color=RESULT).move_to(entries_r[index])

                if current_boxes is None:
                    self.play(Create(boxes), Write(calc), run_time=0.75)
                else:
                    self.play(
                        ReplacementTransform(current_boxes, boxes),
                        ReplacementTransform(current_calc, calc),
                        run_time=0.68,
                    )
                self.play(ReplacementTransform(entries_r[index], new_entry), run_time=0.48)
                computed_entries.add(new_entry)
                current_boxes = boxes
                current_calc = calc

            self.sync("sum_done", 0.55)
            self.play(FadeOut(current_boxes), FadeOut(current_calc), run_time=0.5)
            self.play(FadeIn(dimensions_note), Write(subtraction_note), run_time=0.9)
            self.wait(1.5)
        self.clear_page(
            heading,
            group,
            label_a,
            label_b,
            label_sum,
            computed_entries,
            dimensions_note,
            subtraction_note,
        )

        # --------------------------------------------------------------
        # 2. Scalar multiplication with hidden output
        # --------------------------------------------------------------
        heading = self.make_heading("Scalaire : le même facteur dans chaque case")
        scalar = MathTex("3", font_size=54, color=ACCENT)
        matrix_a = self.make_matrix([[2, -1], [0, 4]])
        equals = MathTex("=", font_size=52)
        result_matrix = self.make_matrix([["?", "?"], ["?", "?"]])
        group = VGroup(scalar, matrix_a, equals, result_matrix)
        group.arrange(RIGHT, buff=0.55).scale_to_fit_width(10.6).move_to(UP * 0.2)

        entries_a = matrix_a.get_entries()
        entries_r = result_matrix.get_entries()
        values = ["6", "-3", "0", "12"]
        calculations = [r"3\cdot2=6", r"3\cdot(-1)=-3", r"3\cdot0=0", r"3\cdot4=12"]
        computed_entries = VGroup()
        current_boxes: VGroup | None = None
        current_calc: MathTex | None = None
        rule = MathTex(r"k(a_{ij})=(ka_{ij})", font_size=46, color=ACCENT).to_edge(DOWN, buff=0.5)

        with self.narrated(SCRIPT[2]):
            self.play(FadeIn(heading), FadeIn(group), run_time=1.0)
            for index, (calculation, value) in enumerate(zip(calculations, values)):
                if index == 0:
                    self.sync("scalar_first", 0.55)
                elif index == 1:
                    self.sync("scalar_rest", 0.55)

                boxes = VGroup(
                    SurroundingRectangle(entries_a[index], color=ACCENT, buff=0.1, stroke_width=3),
                    SurroundingRectangle(entries_r[index], color=RESULT, buff=0.1, stroke_width=3),
                )
                calc = MathTex(calculation, font_size=38, color=RESULT).to_edge(DOWN, buff=0.55)
                new_entry = MathTex(value, font_size=42, color=RESULT).move_to(entries_r[index])
                if current_boxes is None:
                    self.play(Create(boxes), Write(calc), run_time=0.75)
                else:
                    self.play(
                        ReplacementTransform(current_boxes, boxes),
                        ReplacementTransform(current_calc, calc),
                        run_time=0.65,
                    )
                self.play(ReplacementTransform(entries_r[index], new_entry), run_time=0.45)
                computed_entries.add(new_entry)
                current_boxes = boxes
                current_calc = calc

            self.sync("scalar_done", 0.55)
            self.play(FadeOut(current_boxes), ReplacementTransform(current_calc, rule), run_time=0.7)
            self.wait(1.5)
        self.clear_page(heading, group, computed_entries, rule)

        # --------------------------------------------------------------
        # 3. Matrix-vector multiplication: each row gives one output
        # --------------------------------------------------------------
        heading = self.make_heading("Une matrice transforme un vecteur")
        plane = self.make_plane()
        p_visual = self.point_vector(plane, (1, 2), color=ACCENT)
        ap_visual = self.point_vector(plane, (3, 2), color=RESULT)
        p_label = MathTex(r"p=(1,2)", font_size=32, color=ACCENT).next_to(p_visual[1], UP, buff=0.13)
        ap_label = MathTex(r"Ap=(3,2)", font_size=32, color=RESULT).next_to(ap_visual[1], UP, buff=0.13)

        matrix_a = self.make_matrix([[1, 1], [0, 1]], font_size=39)
        vector_p = self.make_matrix([[1], [2]], font_size=39)
        result_vector = self.make_matrix([["?"], ["?"]], font_size=39)
        formula_group = VGroup(
            MathTex("A=", font_size=37),
            matrix_a,
            vector_p,
            MathTex("=", font_size=44),
            result_vector,
        )
        formula_group.arrange(RIGHT, buff=0.24).scale_to_fit_width(4.75)
        formula_group.move_to(RIGHT * 3.72 + UP * 0.72)
        multiplication_sign = MathTex(r"\cdot", font_size=39).move_to(
            (matrix_a.get_right() + vector_p.get_left()) / 2
        )

        rows = matrix_a.get_rows()
        p_entries = vector_p.get_entries()
        result_entries = result_vector.get_entries()
        row_calcs = [
            MathTex(r"1\cdot1+1\cdot2=3", font_size=36, color=RESULT),
            MathTex(r"0\cdot1+1\cdot2=2", font_size=36, color=RESULT),
        ]
        row_calcs[0].move_to(RIGHT * 3.72 + DOWN * 0.55)
        row_calcs[1].move_to(RIGHT * 3.72 + DOWN * 1.25)
        output_note = Text(
            "une ligne → une coordonnée de sortie",
            font_size=26,
            color=SECONDARY,
        ).to_edge(DOWN, buff=0.38)
        computed_entries = VGroup()

        with self.narrated(SCRIPT[3]):
            self.play(FadeIn(heading), Create(plane), FadeIn(formula_group), FadeIn(multiplication_sign), run_time=1.0)
            self.sync("show_p", 0.55)
            self.play(GrowArrow(p_visual[0]), FadeIn(p_visual[1]), FadeIn(p_label), run_time=1.0)
            self.sync("show_ap", 0.6)
            self.play(
                ReplacementTransform(p_visual.copy(), ap_visual),
                FadeIn(ap_label),
                Indicate(matrix_a, color=ACCENT),
                run_time=1.15,
            )
            self.sync("row_one", 0.6)
            row_one_boxes = VGroup(
                SurroundingRectangle(rows[0], color=ACCENT, buff=0.1, stroke_width=3),
                SurroundingRectangle(p_entries, color=SECONDARY, buff=0.1, stroke_width=3),
            )
            first_entry = MathTex("3", font_size=39, color=RESULT).move_to(result_entries[0])
            self.play(Create(row_one_boxes), Write(row_calcs[0]), run_time=0.8)
            self.play(ReplacementTransform(result_entries[0], first_entry), run_time=0.5)
            computed_entries.add(first_entry)
            self.sync("row_two", 0.6)
            row_two_boxes = VGroup(
                SurroundingRectangle(rows[1], color=ACCENT, buff=0.1, stroke_width=3),
                SurroundingRectangle(p_entries, color=SECONDARY, buff=0.1, stroke_width=3),
            )
            second_entry = MathTex("2", font_size=39, color=RESULT).move_to(result_entries[1])
            self.play(ReplacementTransform(row_one_boxes, row_two_boxes), Write(row_calcs[1]), run_time=0.8)
            self.play(ReplacementTransform(result_entries[1], second_entry), run_time=0.5)
            computed_entries.add(second_entry)
            self.sync("vector_done", 0.55)
            self.play(FadeOut(row_two_boxes), FadeIn(output_note), run_time=0.7)
            self.wait(1.5)
        self.clear_page(
            heading,
            plane,
            p_visual,
            p_label,
            ap_visual,
            ap_label,
            formula_group,
            multiplication_sign,
            row_calcs[0],
            row_calcs[1],
            output_note,
            computed_entries,
        )

        # --------------------------------------------------------------
        # 4. Composition: A then B = BA
        # --------------------------------------------------------------
        heading = self.make_heading("Composer : la matrice de droite agit d’abord")
        plane = self.make_plane()
        p = Dot(plane.c2p(1, 2), radius=0.095, color=BLACK)
        ap = Dot(plane.c2p(3, 2), radius=0.09, color=ACCENT)
        bap = Dot(plane.c2p(3, 4), radius=0.1, color=RESULT)
        p_label = MathTex(r"p=(1,2)", font_size=30).next_to(p, DOWN, buff=0.13)
        ap_label = MathTex(r"Ap=(3,2)", font_size=30, color=ACCENT).next_to(ap, DOWN, buff=0.13)
        bap_label = MathTex(r"B(Ap)=(3,4)", font_size=30, color=RESULT).next_to(bap, RIGHT, buff=0.15)
        path_a = Arrow(plane.c2p(1, 2), plane.c2p(3, 2), buff=0.08, color=ACCENT, stroke_width=5)
        path_b = Arrow(plane.c2p(3, 2), plane.c2p(3, 4), buff=0.08, color=RESULT, stroke_width=5)
        label_path_a = MathTex("A", font_size=32, color=ACCENT).next_to(path_a, UP, buff=0.08)
        label_path_b = MathTex("B", font_size=32, color=RESULT).next_to(path_b, RIGHT, buff=0.08)

        matrix_a = self.labeled_matrix("A=", [[1, 1], [0, 1]])
        matrix_b = self.labeled_matrix("B=", [[1, 0], [0, 2]])
        combined = MathTex(r"B(Ap)=(BA)p", font_size=45, color=RESULT)
        order_note = Text("A agit avant B dans le produit BA", font_size=26, color=SECONDARY)
        panel = self.formula_panel(matrix_a, matrix_b, combined, order_note)

        with self.narrated(SCRIPT[4]):
            self.play(
                FadeIn(heading),
                Create(plane),
                FadeIn(p),
                FadeIn(p_label),
                FadeIn(panel[0]),
                FadeIn(matrix_a),
                FadeIn(matrix_b),
                run_time=1.0,
            )
            self.sync("first_action", 0.6)
            self.play(GrowArrow(path_a), FadeIn(label_path_a), FadeIn(ap), FadeIn(ap_label), run_time=1.0)
            self.sync("second_action", 0.6)
            self.play(GrowArrow(path_b), FadeIn(label_path_b), FadeIn(bap), FadeIn(bap_label), run_time=1.0)
            self.sync("composition_name", 0.6)
            self.play(Write(combined), FadeIn(order_note), run_time=1.0)
            self.wait(1.5)
        self.clear_page(
            heading,
            plane,
            p,
            ap,
            bap,
            p_label,
            ap_label,
            bap_label,
            path_a,
            path_b,
            label_path_a,
            label_path_b,
            panel,
        )

        # --------------------------------------------------------------
        # 5. Product: columns first, then row-by-column notation
        # --------------------------------------------------------------
        heading = self.make_heading("Produit matriciel : composer les deux actions")
        matrix_b = self.make_matrix([[1, 0], [0, 2]], font_size=39)
        matrix_a = self.make_matrix([[1, 1], [0, 1]], font_size=39)
        result_matrix = self.make_matrix([["?", "?"], ["?", "?"]], font_size=39)
        product_group = VGroup(
            matrix_b,
            MathTex(r"\cdot", font_size=48),
            matrix_a,
            MathTex("=", font_size=48),
            result_matrix,
        )
        product_group.arrange(RIGHT, buff=0.34).scale_to_fit_width(11.4).move_to(UP * 0.55)
        label_b = MathTex("B", font_size=30, color=ACCENT).next_to(matrix_b, DOWN, buff=0.2)
        label_a = MathTex("A", font_size=30, color=SECONDARY).next_to(matrix_a, DOWN, buff=0.2)
        label_result = MathTex("BA", font_size=30, color=RESULT).next_to(result_matrix, DOWN, buff=0.2)

        columns_a = matrix_a.get_columns()
        columns_r = result_matrix.get_columns()
        rows_b = matrix_b.get_rows()
        result_entries = result_matrix.get_entries()
        computed_entries = VGroup()
        col_one_calc = MathTex(
            r"B\begin{pmatrix}1\\0\end{pmatrix}=\begin{pmatrix}1\\0\end{pmatrix}",
            font_size=37,
            color=RESULT,
        ).to_edge(DOWN, buff=0.58)
        col_two_calc = MathTex(
            r"B\begin{pmatrix}1\\1\end{pmatrix}=\begin{pmatrix}1\\2\end{pmatrix}",
            font_size=37,
            color=RESULT,
        ).to_edge(DOWN, buff=0.58)
        row_column_calc = MathTex(
            r"(BA)_{12}=(1,0)\cdot\begin{pmatrix}1\\1\end{pmatrix}=1",
            font_size=37,
            color=RESULT,
        ).to_edge(DOWN, buff=0.58)
        general_rule = MathTex(
            r"(BA)_{ij}=\text{ligne }i\text{ de }B\cdot\text{colonne }j\text{ de }A",
            font_size=36,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.45)

        with self.narrated(SCRIPT[5]):
            self.play(
                FadeIn(heading),
                FadeIn(product_group),
                FadeIn(label_b),
                FadeIn(label_a),
                FadeIn(label_result),
                run_time=1.0,
            )

            self.sync("first_column", 0.6)
            first_boxes = VGroup(
                SurroundingRectangle(columns_a[0], color=SECONDARY, buff=0.11, stroke_width=3),
                SurroundingRectangle(columns_r[0], color=RESULT, buff=0.11, stroke_width=3),
            )
            first_values = [
                MathTex("1", font_size=39, color=RESULT).move_to(result_entries[0]),
                MathTex("0", font_size=39, color=RESULT).move_to(result_entries[2]),
            ]
            self.play(Create(first_boxes), Write(col_one_calc), run_time=0.85)
            self.play(
                ReplacementTransform(result_entries[0], first_values[0]),
                ReplacementTransform(result_entries[2], first_values[1]),
                run_time=0.6,
            )
            computed_entries.add(*first_values)

            self.sync("second_column", 0.6)
            second_boxes = VGroup(
                SurroundingRectangle(columns_a[1], color=SECONDARY, buff=0.11, stroke_width=3),
                SurroundingRectangle(columns_r[1], color=RESULT, buff=0.11, stroke_width=3),
            )
            second_values = [
                MathTex("1", font_size=39, color=RESULT).move_to(result_entries[1]),
                MathTex("2", font_size=39, color=RESULT).move_to(result_entries[3]),
            ]
            self.play(
                ReplacementTransform(first_boxes, second_boxes),
                ReplacementTransform(col_one_calc, col_two_calc),
                run_time=0.8,
            )
            self.play(
                ReplacementTransform(result_entries[1], second_values[0]),
                ReplacementTransform(result_entries[3], second_values[1]),
                run_time=0.6,
            )
            computed_entries.add(*second_values)

            self.sync("row_column", 0.65)
            row_column_boxes = VGroup(
                SurroundingRectangle(rows_b[0], color=ACCENT, buff=0.11, stroke_width=3),
                SurroundingRectangle(columns_a[1], color=SECONDARY, buff=0.11, stroke_width=3),
            )
            self.play(
                ReplacementTransform(second_boxes, row_column_boxes),
                ReplacementTransform(col_two_calc, row_column_calc),
                run_time=0.85,
            )
            self.sync("product_done", 0.55)
            self.play(FadeOut(row_column_boxes), ReplacementTransform(row_column_calc, general_rule), run_time=0.75)
            final_box = SurroundingRectangle(result_matrix, color=RESULT, buff=0.16, stroke_width=3)
            self.play(Create(final_box), run_time=0.8)
            self.wait(1.5)
        self.clear_page(
            heading,
            product_group,
            label_b,
            label_a,
            label_result,
            computed_entries,
            general_rule,
            final_box,
        )

        # --------------------------------------------------------------
        # 6. Dimensions with actual row and column counts
        # --------------------------------------------------------------
        heading = self.make_heading("Dimensions : la longueur d’une ligne doit convenir")
        left_grid = self.make_grid(2, 3, cell_size=0.55).move_to(LEFT * 3.65 + UP * 0.55)
        right_grid = self.make_grid(3, 2, cell_size=0.55).move_to(LEFT * 0.5 + UP * 0.55)
        result_grid = self.make_grid(2, 2, cell_size=0.55).move_to(RIGHT * 3.25 + UP * 0.55)
        times = MathTex(r"\cdot", font_size=48).move_to(LEFT * 2.0 + UP * 0.55)
        arrow = MathTex(r"\longrightarrow", font_size=48).move_to(RIGHT * 1.35 + UP * 0.55)
        left_label = MathTex(r"2\times3", font_size=36).next_to(left_grid, DOWN, buff=0.28)
        right_label = MathTex(r"3\times2", font_size=36).next_to(right_grid, DOWN, buff=0.28)
        result_label = MathTex(r"2\times2", font_size=36, color=RESULT).next_to(result_grid, DOWN, buff=0.28)

        selected_row = SurroundingRectangle(VGroup(*left_grid[:3]), color=ACCENT, buff=0.08, stroke_width=3)
        selected_column = SurroundingRectangle(
            VGroup(right_grid[0], right_grid[2], right_grid[4]),
            color=SECONDARY,
            buff=0.08,
            stroke_width=3,
        )
        matching_note = Text("3 nombres rencontrent 3 nombres", font_size=27, color=RESULT)
        matching_note.move_to(DOWN * 1.15)
        generic_rule = MathTex(
            r"(m\times n)(n\times p)\longrightarrow(m\times p)",
            font_size=43,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.38)

        bad_left = self.make_grid(2, 3, cell_size=0.43).move_to(LEFT * 1.15 + DOWN * 2.0)
        bad_right = self.make_grid(2, 2, cell_size=0.43).move_to(RIGHT * 1.15 + DOWN * 2.0)
        bad_times = MathTex(r"\cdot", font_size=40).move_to(DOWN * 2.0)
        bad_group = VGroup(bad_left, bad_times, bad_right)
        bad_cross = Cross(bad_group, stroke_color=WARN, stroke_width=6)
        bad_note = MathTex(r"(2\times3)(2\times2)", font_size=34, color=WARN).next_to(
            bad_group, DOWN, buff=0.22
        )

        with self.narrated(SCRIPT[6]):
            self.play(
                FadeIn(heading),
                FadeIn(left_grid),
                FadeIn(right_grid),
                FadeIn(times),
                FadeIn(left_label),
                FadeIn(right_label),
                run_time=1.0,
            )
            self.sync("matching_grid", 0.6)
            self.play(Create(selected_row), Create(selected_column), FadeIn(matching_note), run_time=0.9)
            self.sync("output_grid", 0.6)
            self.play(FadeIn(arrow), FadeIn(result_grid), FadeIn(result_label), Write(generic_rule), run_time=1.0)
            self.sync("bad_grid", 0.65)
            self.play(FadeIn(bad_group), FadeIn(bad_note), Create(bad_cross), run_time=1.0)
            self.wait(1.5)
        self.clear_page(
            heading,
            left_grid,
            right_grid,
            result_grid,
            times,
            arrow,
            left_label,
            right_label,
            result_label,
            selected_row,
            selected_column,
            matching_note,
            generic_rule,
            bad_group,
            bad_note,
            bad_cross,
        )

        # --------------------------------------------------------------
        # 7. Non-commutativity on two separate planes
        # --------------------------------------------------------------
        heading = self.make_heading("L’ordre change généralement le résultat")
        left_plane = self.make_plane(
            x_range=(0, 6, 1),
            y_range=(0, 5, 1),
            unit_size=0.48,
            center=LEFT * 3.45 + DOWN * 0.05,
        )
        right_plane = self.make_plane(
            x_range=(0, 6, 1),
            y_range=(0, 5, 1),
            unit_size=0.48,
            center=RIGHT * 3.45 + DOWN * 0.05,
        )
        left_title = Text("A puis B", font_size=29, weight=SEMIBOLD).next_to(left_plane, UP, buff=0.18)
        right_title = Text("B puis A", font_size=29, weight=SEMIBOLD).next_to(right_plane, UP, buff=0.18)

        # Left path: p=(1,2) -> Ap=(3,2) -> BAp=(3,4)
        lp = Dot(left_plane.c2p(1, 2), radius=0.075, color=BLACK)
        lap = Dot(left_plane.c2p(3, 2), radius=0.075, color=ACCENT)
        lbap = Dot(left_plane.c2p(3, 4), radius=0.09, color=RESULT)
        left_a = Arrow(left_plane.c2p(1, 2), left_plane.c2p(3, 2), buff=0.07, color=ACCENT, stroke_width=5)
        left_b = Arrow(left_plane.c2p(3, 2), left_plane.c2p(3, 4), buff=0.07, color=RESULT, stroke_width=5)
        left_formula = MathTex(r"BAp=(3,4)", font_size=37, color=RESULT).next_to(left_plane, DOWN, buff=0.28)

        # Right path: p=(1,2) -> Bp=(1,4) -> ABp=(5,4)
        rp = Dot(right_plane.c2p(1, 2), radius=0.075, color=BLACK)
        rbp = Dot(right_plane.c2p(1, 4), radius=0.075, color=ACCENT)
        rabp = Dot(right_plane.c2p(5, 4), radius=0.09, color=WARN)
        right_b = Arrow(right_plane.c2p(1, 2), right_plane.c2p(1, 4), buff=0.07, color=ACCENT, stroke_width=5)
        right_a = Arrow(right_plane.c2p(1, 4), right_plane.c2p(5, 4), buff=0.07, color=WARN, stroke_width=5)
        right_formula = MathTex(r"ABp=(5,4)", font_size=37, color=WARN).next_to(right_plane, DOWN, buff=0.28)

        neq = MathTex(r"BA\ne AB", font_size=53, color=ACCENT).to_edge(DOWN, buff=0.35)

        with self.narrated(SCRIPT[7]):
            self.play(
                FadeIn(heading),
                Create(left_plane),
                Create(right_plane),
                FadeIn(left_title),
                FadeIn(right_title),
                FadeIn(lp),
                FadeIn(rp),
                run_time=1.0,
            )
            self.sync("left_path", 0.6)
            self.play(GrowArrow(left_a), FadeIn(lap), run_time=0.8)
            self.play(GrowArrow(left_b), FadeIn(lbap), Write(left_formula), run_time=0.9)
            self.sync("right_path", 0.6)
            self.play(GrowArrow(right_b), FadeIn(rbp), run_time=0.8)
            self.play(GrowArrow(right_a), FadeIn(rabp), Write(right_formula), run_time=0.9)
            self.sync("neq", 0.6)
            self.play(Write(neq), Indicate(neq, color=ACCENT), run_time=1.0)
            self.wait(1.5)
        self.clear_page(
            heading,
            left_plane,
            right_plane,
            left_title,
            right_title,
            lp,
            lap,
            lbap,
            rp,
            rbp,
            rabp,
            left_a,
            left_b,
            right_b,
            right_a,
            left_formula,
            right_formula,
            neq,
        )

        # --------------------------------------------------------------
        # 8. Recap
        # --------------------------------------------------------------
        heading = self.make_heading("Trois opérations, trois significations")
        card_add = self.recap_card(
            "Addition",
            r"(A+B)_{ij}=a_{ij}+b_{ij}",
            "mêmes dimensions,\nmêmes positions",
        )
        card_scalar = self.recap_card(
            "Scalaire",
            r"(kA)_{ij}=ka_{ij}",
            "le même nombre\ndans chaque case",
        )
        card_product = self.recap_card(
            "Produit",
            r"(AB)_{ij}=\text{ligne }i\cdot\text{colonne }j",
            "composer des actions;\nl’ordre compte",
        )
        cards = VGroup(card_add, card_scalar, card_product).arrange(RIGHT, buff=0.42)
        cards.scale_to_fit_width(12.25).move_to(DOWN * 0.08)

        with self.narrated(SCRIPT[8]):
            self.play(FadeIn(heading), run_time=0.6)
            self.sync("recap_add", 0.55)
            self.play(FadeIn(card_add, shift=UP * 0.12), run_time=0.8)
            self.sync("recap_scalar", 0.55)
            self.play(FadeIn(card_scalar, shift=UP * 0.12), run_time=0.8)
            self.sync("recap_product", 0.55)
            self.play(FadeIn(card_product, shift=UP * 0.12), run_time=0.8)
            self.wait(2.0)

        self.wait(1.0)
