"""Modèles linéaires et quadratiques — MAT0339 bridge scene."""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService

import tools.tts as tts
from tools.branding import play_uqam_intro

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
QUAD = GREEN_D
WARN = RED_D
SOFT = GRAY_D
HL = YELLOW
VOICE_SPEED = 0.82


SCRIPT_SEGMENTS = [
    {
        "name": "intro",
        "caption": "Deux modèles à distinguer : formule, graphe, tableau.",
        "ssml": tts.ssml(
            "Dans MAT0339, on rencontre très souvent deux grandes familles de modèles : "
            "<bookmark mark='bk_intro_title'/> le modèle affine et le modèle quadratique. "
            "<bookmark mark='bk_intro_goals'/> "
            "Le but de cette capsule est de les reconnaître par la formule, par le graphe, "
            "et par un tableau de valeurs."
        ),
    },
    {
        "name": "affine",
        "caption": "Affine : ax+b, droite, écarts constants.",
        "ssml": tts.ssml(
            "Commençons par le modèle affine. "
            "<bookmark mark='bk_affine_form'/> Sa forme générale est f de x égale a x plus b. "
            "<bookmark mark='bk_affine_meaning'/> "
            "Le nombre a contrôle la pente, et b donne l'ordonnée à l'origine. "
            "<bookmark mark='bk_affine_table'/> "
            "Prenons l'exemple f de x égale deux x plus un. "
            "<bookmark mark='bk_affine_diff'/> "
            "Les différences premières sont constantes. "
            "<bookmark mark='bk_affine_graph'/> "
            "Graphiquement, on obtient une droite. "
            "<bookmark mark='bk_affine_rule'/> "
            "On retient donc : forme a x plus b, droite, et taux de variation constant."
        ),
    },
    {
        "name": "transition",
        "caption": "Quand l'écart change, on passe au quadratique.",
        "ssml": tts.ssml(
            "Mais tous les phénomènes ne changent pas de façon constante. "
            "<bookmark mark='bk_transition_limit'/> "
            "Parfois, l'écart lui-même change. "
            "<bookmark mark='bk_transition_quad'/> "
            "C'est là que le modèle quadratique devient utile."
        ),
    },
    {
        "name": "quadratique",
        "caption": "Quadratique : parabole, écarts seconds constants.",
        "ssml": tts.ssml(
            "Une fonction quadratique s'écrit en général a x carré plus b x plus c, avec a non nul. "
            "<bookmark mark='bk_quad_form'/> "
            "Le terme x carré change l'allure du graphe. "
            "<bookmark mark='bk_quad_shape'/> "
            "Prenons g de x égale x carré moins quatre x plus trois. "
            "<bookmark mark='bk_quad_example'/> "
            "Les premiers écarts ne sont plus constants. "
            "<bookmark mark='bk_quad_first_diff'/> "
            "En revanche, les deuxièmes écarts le sont. "
            "<bookmark mark='bk_quad_second_diff'/> "
            "Graphiquement, on obtient une parabole. "
            "<bookmark mark='bk_quad_graph'/> "
            "Le point le plus bas s'appelle le sommet. "
            "<bookmark mark='bk_quad_vertex'/> "
            "Le signe de a indique si la parabole ouvre vers le haut ou vers le bas. "
            "<bookmark mark='bk_quad_a_role'/>"
        ),
    },
    {
        "name": "comparaison",
        "caption": "Comparer formule, graphe, tableau et contexte.",
        "ssml": tts.ssml(
            "Comparons maintenant les deux modèles. "
            "<bookmark mark='bk_compare_formula'/> "
            "Affine : a x plus b. Quadratique : a x carré plus b x plus c. "
            "<bookmark mark='bk_compare_graph'/> "
            "Droite d'un côté, parabole de l'autre ; différences premières constantes contre différences secondes constantes. "
            "<bookmark mark='bk_compare_context'/> "
            "Dans un contexte réel, un coût avec frais fixes est souvent affine, alors qu'un effet lié au carré est souvent quadratique. "
            "<bookmark mark='bk_compare_warning'/> "
            "Mais on confirme toujours avec la formule ou les données."
        ),
    },
    {
        "name": "quiz",
        "caption": "Mini-quiz : affine, quadratique, ou ni l'un ni l'autre.",
        "ssml": tts.ssml(
            "Mini-quiz. "
            "<bookmark mark='bk_quiz_intro'/> "
            "Classez trois x moins deux, x carré plus un, et un sur x. "
            "<bookmark mark='bk_quiz_answer1'/> "
            "Trois x moins deux est affine. x carré plus un est quadratique. Un sur x n'est ni affine ni quadratique. "
            "<bookmark mark='bk_quiz_rule'/> "
            "On regarde d'abord la forme algébrique, puis on confirme."
        ),
    },
    {
        "name": "conclusion",
        "caption": "Trois tests : formule, graphe, écarts.",
        "ssml": tts.ssml(
            "Pour reconnaître rapidement un modèle, posez-vous trois questions. "
            "<bookmark mark='bk_recap_three_tests'/> "
            "Quelle est la forme de la formule ? Quelle est la forme du graphe ? Quel type d'écart reste constant ? "
            "<bookmark mark='bk_recap_main'/> "
            "Le modèle affine décrit une variation constante ; le modèle quadratique décrit une variation dont la variation change régulièrement. "
            "<bookmark mark='bk_outro_transition'/> "
            "Dans la suite, on pourra approfondir le sommet, les zéros, et la factorisation."
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class ModelesLineairesQuadratiques(VoiceoverScene):
    """Production bridge between affine and quadratic models."""

    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            print("[voiceover] MANIM_DISABLE_VOICEOVER set. Rendering without narration.")
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
        self.set_speech_service(AzureService(voice=tts.VOICE_ID, global_speed=VOICE_SPEED))
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, item: dict[str, str]):
        if self._voiceover_enabled:
            with self.voiceover(text=item["ssml"], subcaption=item["caption"]) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_until_bookmark(self, mark: str) -> None:
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        self.intro_segment()
        self.affine_segment()
        self.transition_segment()
        self.quadratique_segment()
        self.comparaison_segment()
        self.quiz_segment()
        self.conclusion_segment()

    # ------------------------------------------------------------------
    # Visual builders
    # ------------------------------------------------------------------
    def _pill(self, text: str, color=BLACK, font_size: int = 27) -> VGroup:
        label = Text(text, font_size=font_size, color=color)
        box = RoundedRectangle(
            width=max(1.45, label.width + 0.45),
            height=0.5,
            corner_radius=0.12,
            color=color,
            stroke_width=2,
        )
        return VGroup(box, label)

    def _title(self, text: str, subtitle: str | None = None) -> VGroup:
        title = Text(text, font_size=42)
        if subtitle is None:
            return VGroup(title).to_edge(UP, buff=0.45)
        sub = Text(subtitle, font_size=26, color=SOFT)
        return VGroup(title, sub).arrange(DOWN, buff=0.15).to_edge(UP, buff=0.42)

    def _formula_card(self, formula: str, label: str, color=ACCENT) -> VGroup:
        title = Text(label, font_size=28, color=color)
        expr = MathTex(formula, font_size=48)
        group = VGroup(title, expr).arrange(DOWN, buff=0.18)
        box = RoundedRectangle(width=4.8, height=1.65, corner_radius=0.14, color=BLACK, stroke_width=2.2)
        return VGroup(box, group)

    def _value_rows(
        self,
        x_values: list[str],
        y_values: list[str],
        y_label: str,
        *,
        first_diffs: list[str] | None = None,
        second_diffs: list[str] | None = None,
    ) -> VGroup:
        x_row = VGroup(MathTex("x", font_size=32), *[MathTex(v, font_size=32) for v in x_values])
        y_row = VGroup(MathTex(y_label, font_size=32), *[MathTex(v, font_size=32) for v in y_values])
        x_row.arrange(RIGHT, buff=0.46)
        y_row.arrange(RIGHT, buff=0.46).next_to(x_row, DOWN, buff=0.3)
        y_row.align_to(x_row, LEFT)

        rows = VGroup(x_row, y_row)
        if first_diffs is not None:
            diff = VGroup(*[Text(v, font_size=24, color=ACCENT) for v in first_diffs])
            diff.arrange(RIGHT, buff=0.68).next_to(y_row[1:], DOWN, buff=0.24)
            diff.shift(RIGHT * 0.2)
            rows.add(diff)
        if second_diffs is not None:
            second = VGroup(*[Text(v, font_size=24, color=QUAD) for v in second_diffs])
            second.arrange(RIGHT, buff=0.88).next_to(rows[-1], DOWN, buff=0.18)
            second.shift(RIGHT * 0.28)
            rows.add(second)

        box = RoundedRectangle(
            width=rows.width + 0.55,
            height=rows.height + 0.45,
            corner_radius=0.1,
            color=BLACK,
            stroke_width=2,
        ).move_to(rows)
        return VGroup(box, rows)

    def build_affine_demo(self) -> VDict:
        axes = Axes(
            x_range=[-0.5, 3.6, 1],
            y_range=[0, 8.2, 1],
            x_length=4.7,
            y_length=3.25,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2, "include_numbers": False},
        )
        labels = axes.get_axis_labels(MathTex("x", font_size=25), MathTex("f(x)", font_size=25))
        graph = axes.plot(lambda x: 2 * x + 1, x_range=[0, 3.3], color=ACCENT, stroke_width=3.5)
        points = VGroup(*[Dot(axes.c2p(x, 2 * x + 1), color=ACCENT, radius=0.055) for x in range(4)])

        p0 = axes.c2p(0.55, 2.1)
        p1 = axes.c2p(1.55, 2.1)
        p2 = axes.c2p(1.55, 4.1)
        slope_triangle = VGroup(
            Line(p0, p1, color=WARN, stroke_width=2.4),
            Line(p1, p2, color=WARN, stroke_width=2.4),
            Line(p0, p2, color=WARN, stroke_width=2.0),
            MathTex("1", color=WARN, font_size=24).next_to(Line(p0, p1), DOWN, buff=0.05),
            MathTex("2", color=WARN, font_size=24).next_to(Line(p1, p2), RIGHT, buff=0.05),
        )

        table = self._value_rows(["0", "1", "2", "3"], ["1", "3", "5", "7"], "f(x)", first_diffs=["+2", "+2", "+2"])
        table.scale(0.86).to_edge(LEFT, buff=0.65).shift(DOWN * 0.45)
        graph_group = VGroup(axes, labels, graph, points, slope_triangle).to_edge(RIGHT, buff=0.55).shift(DOWN * 0.35)
        return VDict({"table": table, "graph": graph_group, "line": graph, "triangle": slope_triangle, "points": points})

    def build_quadratic_demo(self) -> VDict:
        axes = Axes(
            x_range=[-0.5, 4.5, 1],
            y_range=[-1.7, 3.6, 1],
            x_length=4.8,
            y_length=3.4,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2, "include_numbers": False},
        )
        labels = axes.get_axis_labels(MathTex("x", font_size=25), MathTex("g(x)", font_size=25))
        curve = axes.plot(lambda x: x**2 - 4 * x + 3, x_range=[0, 4], color=QUAD, stroke_width=3.5)
        values = [(0, 3), (1, 0), (2, -1), (3, 0), (4, 3)]
        points = VGroup(*[Dot(axes.c2p(x, y), color=QUAD, radius=0.055) for x, y in values])
        vertex = Dot(axes.c2p(2, -1), color=WARN, radius=0.075)
        vertex_label = Text("sommet", font_size=23, color=WARN).next_to(vertex, DOWN, buff=0.12)

        table = self._value_rows(
            ["0", "1", "2", "3", "4"],
            ["3", "0", "-1", "0", "3"],
            "g(x)",
            first_diffs=["-3", "-1", "+1", "+3"],
            second_diffs=["+2", "+2", "+2"],
        )
        table.scale(0.78).to_edge(LEFT, buff=0.5).shift(DOWN * 0.45)
        graph_group = VGroup(axes, labels, curve, points, vertex, vertex_label).to_edge(RIGHT, buff=0.5).shift(DOWN * 0.35)
        return VDict({"table": table, "graph": graph_group, "curve": curve, "vertex": VGroup(vertex, vertex_label), "points": points})

    def _mini_parabola(self, opens_up: bool, label: str) -> VGroup:
        axes = Axes(
            x_range=[-1.5, 1.5, 1],
            y_range=[-1, 2, 1],
            x_length=1.8,
            y_length=1.35,
            tips=False,
            axis_config={"color": SOFT, "stroke_width": 1.5, "include_numbers": False},
        )
        f = (lambda x: 0.55 * x**2 - 0.45) if opens_up else (lambda x: -0.55 * x**2 + 1.2)
        curve = axes.plot(f, x_range=[-1.25, 1.25], color=QUAD if opens_up else WARN, stroke_width=2.5)
        txt = MathTex(label, font_size=28, color=QUAD if opens_up else WARN).next_to(axes, DOWN, buff=0.08)
        return VGroup(axes, curve, txt)

    def build_comparison_table(self) -> VGroup:
        headers = VGroup(Text("Affine", font_size=31, color=ACCENT), Text("Quadratique", font_size=31, color=QUAD)).arrange(RIGHT, buff=2.35)
        rows = [
            (MathTex(r"ax+b", font_size=34), MathTex(r"ax^2+bx+c", font_size=34)),
            (Text("droite", font_size=27), Text("parabole", font_size=27)),
            (Text("écarts 1ers constants", font_size=24), Text("écarts 2ds constants", font_size=24)),
            (Text("variation constante", font_size=24), Text("variation qui change", font_size=24)),
        ]
        row_groups = VGroup()
        for left, right in rows:
            pair = VGroup(left, right).arrange(RIGHT, buff=1.65)
            row_groups.add(pair)
        row_groups.arrange(DOWN, buff=0.32)
        board = VGroup(headers, row_groups).arrange(DOWN, buff=0.4)
        box = RoundedRectangle(width=10.6, height=4.45, corner_radius=0.16, color=BLACK, stroke_width=2.2)
        return VGroup(box, board).move_to(ORIGIN + DOWN * 0.1)

    def build_context_icons(self) -> VGroup:
        bill = VGroup(
            Rectangle(width=1.2, height=1.45, color=BLACK, stroke_width=2),
            Text("$", font_size=35),
            Line(LEFT * 0.35, RIGHT * 0.35, color=BLACK, stroke_width=2).shift(DOWN * 0.25),
            Line(LEFT * 0.35, RIGHT * 0.35, color=BLACK, stroke_width=2).shift(DOWN * 0.48),
        )
        bill[1].move_to(bill[0].get_center() + UP * 0.32)
        bill_text = Text("frais fixes + unité", font_size=23, color=ACCENT).next_to(bill, DOWN, buff=0.15)

        arc = ParametricFunction(
            lambda t: np.array([t, -0.55 * t**2 + 0.75, 0]),
            t_range=[-1.1, 1.1],
            color=QUAD,
            stroke_width=3,
        )
        ground = Line(LEFT * 1.3 + DOWN * 0.55, RIGHT * 1.3 + DOWN * 0.55, color=BLACK, stroke_width=2)
        arc_text = Text("effet en carré", font_size=23, color=QUAD).next_to(ground, DOWN, buff=0.15)
        trajectory = VGroup(arc, ground, arc_text)

        return VGroup(VGroup(bill, bill_text), trajectory).arrange(RIGHT, buff=1.65)

    def build_quiz_cards(self) -> VDict:
        items = [
            (r"3x-2", "affine", ACCENT),
            (r"x^2+1", "quadratique", QUAD),
            (r"\frac{1}{x}", "ni l'un ni l'autre", WARN),
        ]
        cards = VGroup()
        answers = VGroup()
        for expr, ans, color in items:
            formula = MathTex(expr, font_size=44)
            answer = Text(ans, font_size=24, color=color)
            box = RoundedRectangle(width=3.25, height=1.9, corner_radius=0.15, color=BLACK, stroke_width=2)
            formula.move_to(box.get_center() + UP * 0.18)
            answer.next_to(formula, DOWN, buff=0.25)
            card = VGroup(box, formula)
            cards.add(card)
            answers.add(answer)
        cards.arrange(RIGHT, buff=0.35).move_to(ORIGIN)
        for answer, card in zip(answers, cards):
            answer.next_to(card[1], DOWN, buff=0.25)
        return VDict({"cards": cards, "answers": answers})

    # ------------------------------------------------------------------
    # Scene segments
    # ------------------------------------------------------------------
    def intro_segment(self) -> None:
        title = self._title("Modèles linéaires et quadratiques", "Formule • Graphe • Tableau")
        affine_icon = self._formula_card(r"f(x)=ax+b", "affine", ACCENT)
        quad_icon = self._formula_card(r"g(x)=ax^2+bx+c", "quadratique", QUAD)
        icons = VGroup(affine_icon, quad_icon).arrange(RIGHT, buff=0.65).next_to(title, DOWN, buff=0.65)
        criteria = VGroup(
            self._pill("formule", ACCENT),
            self._pill("graphe", BLACK),
            self._pill("tableau", QUAD),
        ).arrange(RIGHT, buff=0.35).to_edge(DOWN, buff=0.75)

        with self.narrated(SCRIPT_SEGMENTS[0]):
            self.wait_until_bookmark("bk_intro_title")
            self.play(Write(title), run_time=0.9)
            self.play(FadeIn(icons, shift=0.2 * UP), run_time=0.9)
            self.wait_until_bookmark("bk_intro_goals")
            self.play(LaggedStart(*(FadeIn(p, shift=0.12 * UP) for p in criteria), lag_ratio=0.12), run_time=0.9)
            self.wait(0.4)

        self.play(FadeOut(VGroup(title, icons, criteria)), run_time=0.7)

    def affine_segment(self) -> None:
        heading = self._title("1. Modèle affine", "variation constante")
        formula = MathTex(r"f(x)=ax+b", font_size=56).next_to(heading, DOWN, buff=0.35)
        a_note = VGroup(MathTex("a", color=ACCENT, font_size=38), Text("pente", font_size=26, color=ACCENT)).arrange(DOWN, buff=0.06)
        b_note = VGroup(MathTex("b", color=WARN, font_size=38), Text("valeur initiale", font_size=25, color=WARN)).arrange(DOWN, buff=0.06)
        a_note.next_to(formula, LEFT, buff=0.75)
        b_note.next_to(formula, RIGHT, buff=0.75)

        demo = self.build_affine_demo()
        summary = VGroup(
            self._pill(r"forme ax+b", ACCENT, font_size=24),
            self._pill("droite", BLACK, font_size=24),
            self._pill("écart constant", WARN, font_size=24),
        ).arrange(RIGHT, buff=0.25).to_edge(DOWN, buff=0.35)

        with self.narrated(SCRIPT_SEGMENTS[1]):
            self.wait_until_bookmark("bk_affine_form")
            self.play(Write(heading), Write(formula), run_time=1.0)
            self.wait_until_bookmark("bk_affine_meaning")
            self.play(FadeIn(a_note, shift=0.15 * RIGHT), FadeIn(b_note, shift=0.15 * LEFT), run_time=0.8)
            self.wait_until_bookmark("bk_affine_table")
            self.play(FadeOut(VGroup(a_note, b_note)), FadeIn(demo["table"], shift=0.2 * UP), run_time=0.8)
            self.wait_until_bookmark("bk_affine_diff")
            self.play(Indicate(demo["table"], color=ACCENT), run_time=0.8)
            self.wait_until_bookmark("bk_affine_graph")
            self.play(FadeIn(demo["graph"], shift=0.2 * LEFT), run_time=1.0)
            self.play(Indicate(demo["triangle"], color=WARN), run_time=0.8)
            self.wait_until_bookmark("bk_affine_rule")
            self.play(FadeIn(summary, shift=0.15 * UP), run_time=0.8)
            self.wait(0.4)

        self.play(FadeOut(VGroup(heading, formula, demo, summary)), run_time=0.7)

    def transition_segment(self) -> None:
        constant = Text("écart constant", font_size=42, color=ACCENT)
        variable = Text("écart qui change", font_size=42, color=QUAD)
        arrow = MathTex(r"\Longrightarrow", font_size=56)
        group = VGroup(constant, arrow, variable).arrange(RIGHT, buff=0.4)
        note = Text("Quand les différences premières changent, on cherche plus loin.", font_size=28, color=SOFT)
        note.next_to(group, DOWN, buff=0.45)

        with self.narrated(SCRIPT_SEGMENTS[2]):
            self.wait_until_bookmark("bk_transition_limit")
            self.play(Write(constant), run_time=0.5)
            self.play(TransformFromCopy(constant, variable), Write(arrow), run_time=0.8)
            self.wait_until_bookmark("bk_transition_quad")
            self.play(FadeIn(note, shift=0.15 * UP), run_time=0.7)
            self.wait(0.4)

        self.play(FadeOut(VGroup(group, note)), run_time=0.6)

    def quadratique_segment(self) -> None:
        heading = self._title("2. Modèle quadratique", "variation de la variation")
        formula = MathTex(r"g(x)=ax^2+bx+c,\quad a\neq0", font_size=52).next_to(heading, DOWN, buff=0.35)
        x2_box = SurroundingRectangle(formula[0][5:7], color=QUAD, buff=0.08, stroke_width=2.5)
        demo = self.build_quadratic_demo()
        mini_up = self._mini_parabola(True, "a>0")
        mini_down = self._mini_parabola(False, "a<0")
        minis = VGroup(mini_up, mini_down).arrange(RIGHT, buff=0.45).to_edge(DOWN, buff=0.35)

        with self.narrated(SCRIPT_SEGMENTS[3]):
            self.wait_until_bookmark("bk_quad_form")
            self.play(Write(heading), Write(formula), run_time=1.0)
            self.wait_until_bookmark("bk_quad_shape")
            self.play(Create(x2_box), run_time=0.5)
            self.wait_until_bookmark("bk_quad_example")
            self.play(FadeIn(demo["table"], shift=0.2 * UP), run_time=0.9)
            self.wait_until_bookmark("bk_quad_first_diff")
            self.play(Indicate(demo["table"][1][2], color=ACCENT), run_time=0.8)
            self.wait_until_bookmark("bk_quad_second_diff")
            self.play(Indicate(demo["table"], color=QUAD), run_time=0.8)
            self.wait_until_bookmark("bk_quad_graph")
            self.play(FadeIn(demo["graph"], shift=0.2 * LEFT), run_time=1.0)
            self.wait_until_bookmark("bk_quad_vertex")
            self.play(Indicate(demo["vertex"], color=WARN), run_time=0.8)
            self.wait_until_bookmark("bk_quad_a_role")
            self.play(FadeIn(minis, shift=0.15 * UP), run_time=0.8)
            self.wait(0.4)

        self.play(FadeOut(VGroup(heading, formula, x2_box, demo, minis)), run_time=0.7)

    def comparaison_segment(self) -> None:
        heading = self._title("Comparer les deux modèles")
        table = self.build_comparison_table().next_to(heading, DOWN, buff=0.35)
        context = self.build_context_icons().to_edge(DOWN, buff=0.38)
        warning = VGroup(Text("Toujours vérifier", font_size=30, color=WARN), MathTex(r"\text{formule}+\text{données}", font_size=34)).arrange(DOWN, buff=0.12)
        warning.to_corner(DR, buff=0.55)

        with self.narrated(SCRIPT_SEGMENTS[4]):
            self.wait_until_bookmark("bk_compare_formula")
            self.play(Write(heading), FadeIn(table, shift=0.2 * UP), run_time=1.0)
            self.wait_until_bookmark("bk_compare_graph")
            self.play(Indicate(table, color=ACCENT), run_time=0.8)
            self.wait_until_bookmark("bk_compare_context")
            self.play(FadeIn(context, shift=0.2 * UP), run_time=0.8)
            self.wait_until_bookmark("bk_compare_warning")
            self.play(Write(warning), run_time=0.7)
            self.wait(0.4)

        self.play(FadeOut(VGroup(heading, table, context, warning)), run_time=0.7)

    def quiz_segment(self) -> None:
        heading = self._title("Mini-quiz", "classer sans deviner")
        quiz = self.build_quiz_cards()
        quiz.move_to(ORIGIN + DOWN * 0.1)
        reminder = Text("Forme algébrique d'abord, puis graphe ou tableau.", font_size=28, color=SOFT)
        reminder.to_edge(DOWN, buff=0.55)

        with self.narrated(SCRIPT_SEGMENTS[5]):
            self.wait_until_bookmark("bk_quiz_intro")
            self.play(Write(heading), FadeIn(quiz["cards"], shift=0.2 * UP), run_time=0.9)
            self.wait(0.8)
            self.wait_until_bookmark("bk_quiz_answer1")
            self.play(LaggedStart(*(FadeIn(a, shift=0.1 * UP) for a in quiz["answers"]), lag_ratio=0.12), run_time=0.8)
            self.wait_until_bookmark("bk_quiz_rule")
            self.play(FadeIn(reminder, shift=0.15 * UP), run_time=0.6)
            self.wait(0.4)

        self.play(FadeOut(VGroup(heading, quiz, reminder)), run_time=0.7)

    def conclusion_segment(self) -> None:
        heading = self._title("À retenir")
        checklist = VGroup(
            Text("1. Forme de la formule", font_size=30),
            Text("2. Forme du graphe", font_size=30),
            Text("3. Type d'écart constant", font_size=30),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.24).next_to(heading, DOWN, buff=0.65)
        compare = VGroup(
            Text("Affine : variation constante", font_size=30, color=ACCENT),
            Text("Quadratique : variation qui change régulièrement", font_size=30, color=QUAD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).next_to(checklist, DOWN, buff=0.55)
        next_card = VGroup(
            Text("Suite", font_size=34),
            Text("sommet • zéros • factorisation", font_size=30, color=SOFT),
        ).arrange(DOWN, buff=0.18).to_edge(DOWN, buff=0.55)

        with self.narrated(SCRIPT_SEGMENTS[6]):
            self.wait_until_bookmark("bk_recap_three_tests")
            self.play(Write(heading), LaggedStart(*(FadeIn(item, shift=0.12 * RIGHT) for item in checklist), lag_ratio=0.13), run_time=1.1)
            self.wait_until_bookmark("bk_recap_main")
            self.play(FadeIn(compare, shift=0.2 * UP), run_time=0.8)
            self.wait_until_bookmark("bk_outro_transition")
            self.play(FadeIn(next_card, shift=0.2 * UP), run_time=0.8)
            self.wait(1.0)
