"""Matrices 1 — lire une matrice et appliquer une règle linéaire.

Second-pass production version for the MAT0339 French video series.
The scene connects a data table, a matrix-vector product, dimensions, a common
mistake, and a geometric transformation while introducing one idea at a time.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    LEFT,
    ORIGIN,
    RED_D,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Axes,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    LaggedStart,
    Line,
    MathTex,
    Matrix,
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
    from manim_voiceover.services.azure import AzureService
except ImportError:
    VoiceoverScene = None
    AzureService = None

import tools.tts as tts
from tools.branding import play_uqam_intro

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
ERROR = RED_D
A = tts.A
B = tts.B

@dataclass
class _NoVoiceTracker:
    duration: float = 0.0

    def wait_until_bookmark(self, _mark: str) -> None:
        return None


BaseScene = VoiceoverScene if VoiceoverScene is not None else Scene


class MatricesLireEtAppliquerFR(BaseScene):
    """Interpret rows as outputs and columns as input components."""

    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            return
        if VoiceoverScene is None or AzureService is None:
            return

        key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not key or not region:
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", key)
        os.environ.setdefault("AZURE_SERVICE_REGION", region)
        os.environ.setdefault("SPEECH_KEY", key)
        os.environ.setdefault("SPEECH_REGION", region)
        try:
            self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        except Exception as exc:
            print(f"[voiceover] Azure setup failed: {exc}. Rendering silently.")
            return
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, spoken: str, caption: str):
        if self._voiceover_enabled:
            with self.voiceover(
                text=tts.ssml(spoken),
                subcaption=caption,
            ):
                # Bookmark waiting is a VoiceoverScene method in the current
                # manim-voiceover API, not a VoiceoverTracker method.
                yield self
        else:
            yield _NoVoiceTracker()

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        # ------------------------------------------------------------------
        # 1. Central question
        # ------------------------------------------------------------------
        title = Text("Matrices 1", font_size=46, weight="BOLD")
        question = Text(
            "Une matrice est-elle seulement\nun tableau de nombres ?",
            font_size=35,
            line_spacing=0.92,
        ).next_to(title, DOWN, buff=0.55)
        title_group = VGroup(title, question).move_to(ORIGIN)

        caption = (
            "Une matrice est-elle seulement un tableau de nombres ? Non. Elle peut "
            "organiser des données et décrire une règle de calcul."
        )
        spoken = (
            "Une matrice est-elle seulement un tableau de nombres ? "
            "<bookmark mark='answer'/>Non. Elle peut organiser des données et décrire une "
            "règle de calcul."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(Write(title), run_time=0.75)
            self.play(FadeIn(question, shift=UP * 0.12), run_time=0.85)
            tracker.wait_until_bookmark("answer")
            self.play(question.animate.set_color(ACCENT), run_time=0.45)
        self.wait(0.65)
        self.play(FadeOut(title_group), run_time=0.55)

        # ------------------------------------------------------------------
        # 2. Matrix as an organized table
        # ------------------------------------------------------------------
        header = Text("Deux recettes, deux ingrédients", font_size=34, weight="BOLD")
        header.to_edge(UP, buff=0.42)

        recipe_matrix = Matrix(
            [[2, 1], [1, 3]],
            left_bracket="(",
            right_bracket=")",
            h_buff=1.12,
            v_buff=0.72,
        ).scale(1.12)
        recipe_matrix.move_to(LEFT * 0.35 + DOWN * 0.05)

        columns = recipe_matrix.get_columns()
        rows = recipe_matrix.get_rows()
        col_a = Text("recette A", font_size=25, color=ACCENT).next_to(
            columns[0], UP, buff=0.33
        )
        col_b = Text("recette B", font_size=25, color=ACCENT).next_to(
            columns[1], UP, buff=0.33
        )
        row_apples = Text("pommes", font_size=26).next_to(rows[0], LEFT, buff=0.52)
        row_bananas = Text("bananes", font_size=26).next_to(rows[1], LEFT, buff=0.52)

        size_formula = MathTex(r"2\times 2", font_size=34, color=ACCENT)
        size_formula.to_edge(RIGHT, buff=0.75).shift(UP * 0.45)
        size_words = Text("2 lignes · 2 colonnes", font_size=27)
        size_words.next_to(size_formula, DOWN, buff=0.27)

        caption = (
            "Cette matrice est de format deux par deux. Les colonnes représentent les "
            "recettes A et B; les lignes représentent les pommes et les bananes. "
            "La position de chaque nombre indique donc ce qu'il signifie."
        )
        spoken = (
            "Cette matrice est de format deux par deux. "
            f"<bookmark mark='columns'/>Les colonnes représentent les recettes {A} et {B}. "
            "<bookmark mark='rows'/>Les lignes représentent les pommes et les bananes. "
            "La position de chaque nombre indique donc ce qu'il signifie."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(Write(header), FadeIn(recipe_matrix), run_time=0.95)
            tracker.wait_until_bookmark("columns")
            self.play(FadeIn(col_a, col_b), run_time=0.55)
            tracker.wait_until_bookmark("rows")
            self.play(
                FadeIn(row_apples, row_bananas),
                Write(size_formula),
                FadeIn(size_words),
                run_time=0.75,
            )
        self.wait(0.75)

        first_entry = recipe_matrix.get_entries()[0]
        entry_box = SurroundingRectangle(
            first_entry,
            color=ACCENT,
            buff=0.16,
            stroke_width=3,
        )
        entry_meaning = VGroup(
            MathTex(r"a_{11}=2", font_size=38, color=ACCENT),
            Text("2 pommes pour une recette A", font_size=27),
        ).arrange(DOWN, buff=0.25)
        entry_meaning.to_edge(DOWN, buff=0.52)

        caption = (
            "L'entrée située en première ligne et première colonne vaut deux. "
            "Elle signifie qu'une recette A utilise deux pommes. Le nombre seul ne suffit "
            "pas : sa ligne et sa colonne donnent son sens."
        )
        spoken = (
            "L'entrée située en première ligne et première colonne vaut deux. "
            f"<bookmark mark='meaning'/>Elle signifie qu'une recette {A} utilise deux pommes. "
            "Le nombre seul ne suffit pas : sa ligne et sa colonne donnent son sens."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(Create(entry_box), run_time=0.45)
            tracker.wait_until_bookmark("meaning")
            self.play(FadeIn(entry_meaning, shift=UP * 0.08), run_time=0.75)
        self.wait(0.7)

        # ------------------------------------------------------------------
        # 3. The matrix becomes a rule: one row, one output
        # ------------------------------------------------------------------
        calculation_header = Text(
            "La matrice devient une règle de calcul",
            font_size=34,
            weight="BOLD",
        ).move_to(header)

        matrix_target = recipe_matrix.copy().scale(0.76)
        input_vector = Matrix(
            [[4], [2]],
            left_bracket="(",
            right_bracket=")",
        ).scale(0.86)
        equals = MathTex("=", font_size=42)
        output_vector = Matrix(
            [["?"], ["?"]],
            left_bracket="(",
            right_bracket=")",
        ).scale(0.86)
        product_group = VGroup(
            matrix_target,
            input_vector,
            equals,
            output_vector,
        ).arrange(RIGHT, buff=0.36)
        product_group.move_to(UP * 0.55)

        input_labels = VGroup(
            Text("4 recettes A", font_size=24),
            Text("2 recettes B", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        input_labels.next_to(input_vector, DOWN, buff=0.34)

        output_labels = VGroup(
            Text("pommes", font_size=24),
            Text("bananes", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        output_labels.next_to(output_vector, DOWN, buff=0.34)

        caption = (
            "Supposons que l'on prépare quatre recettes A et deux recettes B. "
            "Ces deux nombres forment le vecteur d'entrée. La matrice doit calculer "
            "deux sorties : le total de pommes et le total de bananes."
        )
        spoken = (
            f"Supposons que l'on prépare quatre recettes {A} et deux recettes {B}. "
            "<bookmark mark='input'/>Ces deux nombres forment le vecteur d'entrée. "
            "<bookmark mark='outputs'/>La matrice doit calculer deux sorties : le total de "
            "pommes et le total de bananes."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(FadeOut(header), run_time=0.30)
            self.play(
                FadeOut(
                    entry_box,
                    entry_meaning,
                    size_formula,
                    size_words,
                    col_a,
                    col_b,
                    row_apples,
                    row_bananas,
                ),
                FadeIn(calculation_header),
                Transform(recipe_matrix, matrix_target),
                run_time=0.7,
            )
            header = calculation_header
            tracker.wait_until_bookmark("input")
            self.play(FadeIn(input_vector, input_labels), run_time=0.6)
            tracker.wait_until_bookmark("outputs")
            self.play(
                Write(equals),
                FadeIn(output_vector, output_labels),
                run_time=0.7,
            )
        self.wait(0.75)

        row_1_box = SurroundingRectangle(
            recipe_matrix.get_rows()[0],
            color=ACCENT,
            buff=0.15,
            stroke_width=3,
        )
        row_2_box = SurroundingRectangle(
            recipe_matrix.get_rows()[1],
            color=ACCENT,
            buff=0.15,
            stroke_width=3,
        )
        input_box = SurroundingRectangle(
            input_vector,
            color=ACCENT,
            buff=0.13,
            stroke_width=2.4,
        )

        calc_1 = MathTex(
            r"2\cdot 4+1\cdot 2=10",
            font_size=39,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.54)
        calc_2 = MathTex(
            r"1\cdot 4+3\cdot 2=10",
            font_size=39,
            color=ACCENT,
        ).move_to(calc_1)

        first_question = output_vector.get_entries()[0]
        second_question = output_vector.get_entries()[1]
        first_ten = MathTex("10", font_size=35, color=ACCENT).move_to(first_question)
        second_ten = MathTex("10", font_size=35, color=ACCENT).move_to(second_question)

        caption = (
            "Chaque ligne calcule une sortie. La première ligne utilise toutes les "
            "composantes d'entrée et donne dix pommes. La deuxième ligne recommence "
            "avec ses propres coefficients et donne dix bananes."
        )
        spoken = (
            "Chaque ligne calcule une sortie. "
            "<bookmark mark='row1'/>La première ligne fait deux fois quatre, plus une fois "
            "deux : on obtient dix pommes. "
            "<bookmark mark='row2'/>La deuxième ligne fait une fois quatre, plus trois fois "
            "deux : on obtient dix bananes."
        )
        with self.narrated(spoken, caption) as tracker:
            tracker.wait_until_bookmark("row1")
            self.play(Create(row_1_box), Create(input_box), Write(calc_1), run_time=0.75)
            self.play(Transform(first_question, first_ten), run_time=0.4)
            tracker.wait_until_bookmark("row2")
            self.play(
                Transform(row_1_box, row_2_box),
                Transform(calc_1, calc_2),
                run_time=0.75,
            )
            self.play(Transform(second_question, second_ten), run_time=0.4)
        self.wait(0.8)

        # ------------------------------------------------------------------
        # 4. Dimensions explain why the product is possible
        # ------------------------------------------------------------------
        columns_rule = Text(
            "2 colonnes  ↔  2 entrées",
            font_size=27,
            color=ACCENT,
        )
        rows_rule = Text(
            "2 lignes  ↔  2 sorties",
            font_size=27,
            color=ACCENT,
        )
        dimension_rules = VGroup(columns_rule, rows_rule).arrange(DOWN, buff=0.25)
        dimension_rules.to_edge(DOWN, buff=0.45)
        dimension_box = SurroundingRectangle(
            dimension_rules,
            color=ACCENT,
            buff=0.2,
            stroke_width=2.4,
        )

        caption = (
            "Le format de la matrice annonce le calcul. Ses deux colonnes correspondent "
            "aux deux composantes d'entrée; ses deux lignes produisent deux composantes de sortie."
        )
        spoken = (
            "Le format de la matrice annonce le calcul. "
            "<bookmark mark='columns'/>Ses deux colonnes correspondent aux deux composantes "
            "d'entrée. <bookmark mark='rows'/>Ses deux lignes produisent deux composantes de sortie."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(FadeOut(row_1_box, input_box, calc_1), run_time=0.4)
            tracker.wait_until_bookmark("columns")
            self.play(FadeIn(columns_rule), run_time=0.5)
            tracker.wait_until_bookmark("rows")
            self.play(FadeIn(rows_rule), Create(dimension_box), run_time=0.6)
        self.wait(0.75)

        # ------------------------------------------------------------------
        # 5. Common error while the relevant matrix is still visible
        # ------------------------------------------------------------------
        entries = recipe_matrix.get_entries()
        diagonal_boxes = VGroup(
            SurroundingRectangle(entries[0], color=ERROR, buff=0.13, stroke_width=3),
            SurroundingRectangle(entries[3], color=ERROR, buff=0.13, stroke_width=3),
        )
        wrong_formula = MathTex(
            r"(2\cdot4,\,3\cdot2)=(8,6)",
            font_size=36,
            color=ERROR,
        ).to_edge(DOWN, buff=0.5)
        cross_1 = Line(
            wrong_formula.get_corner(LEFT + UP),
            wrong_formula.get_corner(RIGHT + DOWN),
            color=ERROR,
            stroke_width=5,
        )
        cross_2 = Line(
            wrong_formula.get_corner(LEFT + DOWN),
            wrong_formula.get_corner(RIGHT + UP),
            color=ERROR,
            stroke_width=5,
        )
        all_rows = VGroup(
            SurroundingRectangle(
                recipe_matrix.get_rows()[0],
                color=ACCENT,
                buff=0.15,
                stroke_width=2.7,
            ),
            SurroundingRectangle(
                recipe_matrix.get_rows()[1],
                color=ACCENT,
                buff=0.15,
                stroke_width=2.7,
            ),
        )
        correct_words = Text(
            "Une ligne entière calcule une sortie.",
            font_size=28,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.52)
        correct_box = SurroundingRectangle(
            correct_words,
            color=ACCENT,
            buff=0.18,
            stroke_width=2.4,
        )

        caption = (
            "Erreur fréquente : ne multiplier que les nombres de la diagonale. "
            "Cette règle ignore les autres coefficients. Pour chaque sortie, il faut "
            "utiliser une ligne entière de la matrice."
        )
        spoken = (
            "Erreur fréquente : ne multiplier que les nombres de la diagonale. "
            "<bookmark mark='wrong'/>Cette règle ignore les autres coefficients. "
            "<bookmark mark='correct'/>Pour chaque sortie, il faut utiliser une ligne entière "
            "de la matrice."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(FadeOut(dimension_rules, dimension_box), run_time=0.35)
            tracker.wait_until_bookmark("wrong")
            self.play(
                Create(diagonal_boxes),
                Write(wrong_formula),
                Create(cross_1),
                Create(cross_2),
                run_time=0.9,
            )
            tracker.wait_until_bookmark("correct")
            self.play(
                FadeOut(diagonal_boxes, wrong_formula, cross_1, cross_2),
                Create(all_rows),
                FadeIn(correct_words),
                Create(correct_box),
                run_time=0.8,
            )
        self.wait(0.8)

        # ------------------------------------------------------------------
        # 6. Abstract reading: rule times input equals output
        # ------------------------------------------------------------------
        symbol_a = MathTex("A", font_size=58, color=ACCENT)
        times = MathTex(r"\cdot", font_size=48)
        symbol_x = MathTex(r"\vec x", font_size=58, color=ACCENT)
        abstract_equals = MathTex("=", font_size=50)
        symbol_y = MathTex(r"\vec y", font_size=58, color=ACCENT)
        abstract_formula = VGroup(
            symbol_a,
            times,
            symbol_x,
            abstract_equals,
            symbol_y,
        ).arrange(RIGHT, buff=0.28)
        abstract_formula.move_to(UP * 0.35)

        labels = VGroup(
            Text("règle", font_size=25),
            Text("entrée", font_size=25),
            Text("sortie", font_size=25),
        )
        labels[0].next_to(symbol_a, DOWN, buff=0.28)
        labels[1].next_to(symbol_x, DOWN, buff=0.28)
        labels[2].next_to(symbol_y, DOWN, buff=0.28)
        abstract_caption = Text(
            "La matrice transforme un vecteur d'entrée en vecteur de sortie.",
            font_size=29,
        ).next_to(abstract_formula, DOWN, buff=0.85)

        caption = (
            "On résume le produit ainsi : une matrice A agit sur un vecteur d'entrée x "
            "et produit un vecteur de sortie y."
        )
        spoken = (
            f"On résume le produit ainsi. Une matrice {A} agit sur un vecteur d'entrée "
            "et produit un vecteur de sortie."
        )
        with self.narrated(spoken, caption):
            self.play(
                FadeOut(
                    header,
                    recipe_matrix,
                    input_vector,
                    equals,
                    output_vector,
                    input_labels,
                    output_labels,
                    all_rows,
                    correct_words,
                    correct_box,
                ),
                run_time=0.6,
            )
            self.play(
                Write(abstract_formula),
                FadeIn(labels),
                FadeIn(abstract_caption, shift=UP * 0.08),
                run_time=1.0,
            )
        self.wait(0.85)

        # ------------------------------------------------------------------
        # 7. Geometric example: swapping coordinates reflects across y=x
        # ------------------------------------------------------------------
        geometry_header = Text("Une transformation du plan", font_size=34, weight="BOLD")
        geometry_header.to_edge(UP, buff=0.42)
        axes = Axes(
            x_range=[-1, 4, 1],
            y_range=[-1, 4, 1],
            x_length=4.8,
            y_length=4.8,
            axis_config={
                "color": BLACK,
                "stroke_width": 2.1,
                "include_ticks": True,
            },
            tips=False,
        ).to_edge(LEFT, buff=0.7).shift(DOWN * 0.35)
        mirror = DashedLine(
            axes.c2p(-1, -1),
            axes.c2p(4, 4),
            color=BLACK,
            stroke_width=2,
            dash_length=0.12,
        ).set_opacity(0.42)
        mirror_label = MathTex(r"y=x", font_size=27).next_to(
            axes.c2p(3.2, 3.2),
            UP + LEFT,
            buff=0.08,
        )

        vector_before = Arrow(
            axes.c2p(0, 0),
            axes.c2p(3, 1),
            buff=0,
            color=ACCENT,
            stroke_width=5,
            max_tip_length_to_length_ratio=0.16,
        )
        before_dot = Dot(axes.c2p(3, 1), radius=0.065, color=ACCENT)
        before_label = MathTex(r"\vec x=(3,1)", font_size=31, color=ACCENT)
        before_label.next_to(before_dot, RIGHT, buff=0.12)

        swap_matrix = Matrix(
            [[0, 1], [1, 0]],
            left_bracket="(",
            right_bracket=")",
        ).scale(0.86)
        swap_input = Matrix(
            [[3], [1]],
            left_bracket="(",
            right_bracket=")",
        ).scale(0.78)
        swap_equals = MathTex("=", font_size=38)
        swap_output = Matrix(
            [[1], [3]],
            left_bracket="(",
            right_bracket=")",
        ).scale(0.78)
        swap_formula = VGroup(
            swap_matrix,
            swap_input,
            swap_equals,
            swap_output,
        ).arrange(RIGHT, buff=0.28)
        swap_formula.to_edge(RIGHT, buff=0.42).shift(UP * 0.45)
        swap_words = Text(
            "La matrice échange\nles deux composantes.",
            font_size=27,
            line_spacing=0.94,
        ).next_to(swap_formula, DOWN, buff=0.43)

        vector_after = Arrow(
            axes.c2p(0, 0),
            axes.c2p(1, 3),
            buff=0,
            color=ACCENT,
            stroke_width=5,
            max_tip_length_to_length_ratio=0.16,
        )
        after_dot = Dot(axes.c2p(1, 3), radius=0.065, color=ACCENT)
        after_label = MathTex(r"\vec y=(1,3)", font_size=31, color=ACCENT)
        after_label.next_to(after_dot, UP, buff=0.12)
        reflection_segment = DashedLine(
            axes.c2p(3, 1),
            axes.c2p(1, 3),
            color=ACCENT,
            stroke_width=2.4,
        ).set_opacity(0.55)
        midpoint = Dot(axes.c2p(2, 2), radius=0.055, color=BLACK)

        caption = (
            "Une matrice peut aussi agir sur les coordonnées d'un vecteur. "
            "Ici, elle échange trois et un. Le vecteur trois, un devient un, trois; "
            "géométriquement, c'est une réflexion par rapport à la droite y égale x."
        )
        spoken = (
            "Une matrice peut aussi agir sur les coordonnées d'un vecteur. "
            "<bookmark mark='start'/>Ici, elle échange trois et un. "
            "<bookmark mark='swap'/>Le vecteur trois, un devient un, trois. "
            "Géométriquement, c'est une réflexion par rapport à la droite y égale x."
        )
        with self.narrated(spoken, caption) as tracker:
            self.play(
                FadeOut(abstract_formula, labels, abstract_caption),
                Write(geometry_header),
                Create(axes),
                Create(mirror),
                FadeIn(mirror_label),
                run_time=0.85,
            )
            tracker.wait_until_bookmark("start")
            self.play(
                GrowArrow(vector_before),
                FadeIn(before_dot),
                Write(before_label),
                FadeIn(swap_formula, swap_words),
                run_time=0.95,
            )
            tracker.wait_until_bookmark("swap")
            self.play(
                Transform(vector_before, vector_after),
                Transform(before_dot, after_dot),
                Transform(before_label, after_label),
                Create(reflection_segment),
                FadeIn(midpoint),
                run_time=1.1,
            )
        self.wait(0.95)

        # ------------------------------------------------------------------
        # 8. Stable summary
        # ------------------------------------------------------------------
        self.play(
            FadeOut(
                geometry_header,
                axes,
                mirror,
                mirror_label,
                vector_before,
                before_dot,
                before_label,
                swap_formula,
                swap_words,
                reflection_segment,
                midpoint,
            ),
            run_time=0.65,
        )

        summary_title = Text("À retenir", font_size=42, weight="BOLD", color=ACCENT)
        summary_lines = VGroup(
            Text("Les colonnes correspondent aux entrées.", font_size=29),
            Text("Chaque ligne calcule une sortie.", font_size=29),
            MathTex(r"A\vec x=\vec y", font_size=45),
            Text("Une matrice peut organiser ou transformer des données.", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        summary = VGroup(summary_title, summary_lines).arrange(DOWN, buff=0.52)
        summary.move_to(ORIGIN)
        summary_box = SurroundingRectangle(
            summary,
            color=ACCENT,
            buff=0.34,
            stroke_width=2.5,
        )

        caption = (
            "À retenir : les colonnes correspondent aux données d'entrée; chaque ligne "
            "calcule une sortie. Une matrice peut ainsi organiser des données ou décrire "
            "une transformation."
        )
        spoken = (
            "À retenir. Les colonnes correspondent aux données d'entrée; chaque ligne "
            "calcule une sortie. Une matrice peut ainsi organiser des données ou décrire "
            "une transformation."
        )
        with self.narrated(spoken, caption):
            self.play(Write(summary_title), run_time=0.55)
            self.play(
                LaggedStart(
                    *[FadeIn(line, shift=UP * 0.07) for line in summary_lines],
                    lag_ratio=0.18,
                ),
                run_time=1.55,
            )
            self.play(Create(summary_box), run_time=0.45)
        self.wait(1.4)
