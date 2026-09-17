"""Modèles affines et quadratiques — comparaison par les variations."""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

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
VOICE_SPEED = 0.82


SCRIPT_SEGMENTS = [
    {
        "name": "intro",
        "caption": "Pourquoi une droite ici, et une courbe là ?",
        "ssml": tts.ssml(
            "Pourquoi certains tableaux de valeurs produisent-ils une droite, tandis que d'autres produisent une courbe ? "
            "<bookmark mark='bk_intro_title'/> "
            "Pour le comprendre, nous allons d'abord regarder comment les valeurs changent, avant d'écrire les formules. "
            "<bookmark mark='bk_intro_constant'/> "
            "Dans la première suite, on ajoute toujours deux. "
            "<bookmark mark='bk_intro_changing'/> "
            "Dans la seconde, on ajoute trois, puis cinq, puis sept. "
            "<bookmark mark='bk_intro_question'/> "
            "Ces deux rythmes de changement conduisent à deux modèles différents."
        ),
    },
    {
        "name": "affine",
        "caption": "Affine : un même gain à chaque pas donne une droite.",
        "ssml": tts.ssml(
            "Commençons par le cas le plus régulier. "
            "<bookmark mark='bk_affine_table'/> "
            "Quand x avance de zéro à un, puis à deux et à trois, les valeurs sont un, trois, cinq et sept. "
            "<bookmark mark='bk_affine_diff'/> "
            "À chaque pas de un, la sortie augmente exactement de deux. "
            "<bookmark mark='bk_affine_points'/> "
            "Plaçons maintenant les couples correspondants dans le plan. "
            "<bookmark mark='bk_affine_line'/> "
            "Les points sont alignés : le graphe est une droite. "
            "<bookmark mark='bk_affine_formula'/> "
            "Dans notre exemple, la règle est f de x égale deux x plus un. "
            "<bookmark mark='bk_affine_general'/> "
            "Plus généralement, une fonction affine s'écrit a x plus b. Le nombre a représente le gain pour un pas de un, et b la valeur de départ."
        ),
    },
    {
        "name": "transition",
        "caption": "Et si le gain lui-même changeait ?",
        "ssml": tts.ssml(
            "Le modèle affine fonctionne parce que le gain reste constant. "
            "<bookmark mark='bk_transition_constant'/> "
            "Mais imaginons maintenant des gains de trois, cinq, puis sept. "
            "<bookmark mark='bk_transition_change'/> "
            "Ils ne sont pas égaux. Pourtant, ils augmentent eux-mêmes toujours de deux. "
            "<bookmark mark='bk_transition_question'/> "
            "C'est cette régularité d'un deuxième niveau qui conduit au modèle quadratique."
        ),
    },
    {
        "name": "quadratique",
        "caption": "Quadratique : les premiers écarts changent régulièrement.",
        "ssml": tts.ssml(
            "Prenons un carré dont le côté grandit d'une unité à la fois. "
            "<bookmark mark='bk_quad_square1'/> "
            "Un carré de côté un contient une case. "
            "<bookmark mark='bk_quad_square2'/> "
            "Pour passer au côté deux, on ajoute trois cases, et l'aire devient quatre. "
            "<bookmark mark='bk_quad_square3'/> "
            "Pour passer au côté trois, on ajoute cinq cases, et l'aire devient neuf. "
            "<bookmark mark='bk_quad_square4'/> "
            "Puis on ajoute sept cases, et l'aire devient seize. "
            "<bookmark mark='bk_quad_first_diff'/> "
            "Les premiers écarts, trois, cinq et sept, ne sont donc pas constants. "
            "<bookmark mark='bk_quad_second_diff'/> "
            "Mais chacun augmente de deux. Lorsque les valeurs de x sont espacées également, les deuxièmes écarts sont constants. "
            "<bookmark mark='bk_quad_graph_points'/> "
            "Plaçons maintenant les points zéro zéro, un un, deux quatre, trois neuf et quatre seize. "
            "<bookmark mark='bk_quad_graph_curve'/> "
            "Ils ne sont pas alignés. Ils suivent une courbe appelée parabole. "
            "<bookmark mark='bk_quad_example_formula'/> "
            "Ici, la règle est simplement g de x égale x carré. "
            "<bookmark mark='bk_quad_general_form'/> "
            "La famille quadratique générale s'écrit a x carré plus b x plus c, avec a non nul. Le sommet et l'ouverture seront étudiés séparément."
        ),
    },
    {
        "name": "comparaison",
        "caption": "Affine ou quadratique : quel niveau d'écart est constant ?",
        "ssml": tts.ssml(
            "Nous pouvons maintenant comparer les deux modèles sans apprendre une liste de faits isolés. "
            "<bookmark mark='bk_compare_affine'/> "
            "Dans un modèle affine, les premiers écarts sont constants, et le graphe est une droite. "
            "<bookmark mark='bk_compare_quadratic'/> "
            "Dans un modèle quadratique, les premiers écarts changent, mais les deuxièmes écarts sont constants, et le graphe est une parabole. "
            "<bookmark mark='bk_compare_condition'/> "
            "Attention : ce test par les écarts suppose que les valeurs de x sont espacées régulièrement."
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
            "On regarde d'abord la forme algébrique, puis on confirme avec le graphe ou les données."
        ),
    },
    {
        "name": "conclusion",
        "caption": "À retenir : premiers écarts ou deuxièmes écarts.",
        "ssml": tts.ssml(
            "Retenons l'idée centrale. "
            "<bookmark mark='bk_recap_affine'/> "
            "Un modèle affine ajoute le même gain à chaque pas égal : ses premiers écarts sont constants. "
            "<bookmark mark='bk_recap_quadratic'/> "
            "Un modèle quadratique a des gains qui changent à rythme constant : ses deuxièmes écarts sont constants. "
            "<bookmark mark='bk_recap_checks'/> "
            "Pour reconnaître le modèle, on relie toujours trois représentations : le tableau, le graphe et la formule. "
            "<bookmark mark='bk_outro_transition'/> "
            "Dans une prochaine capsule, nous pourrons étudier le sommet, les zéros et l'ouverture d'une parabole."
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class ModelesLineairesQuadratiques(VoiceoverScene):
    """Bridge scene deriving affine and quadratic models from finite differences."""

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

    def _pattern_card(
        self,
        title: str,
        values: list[str],
        differences: list[str],
        color,
    ) -> VGroup:
        value_mobs = [MathTex(value, font_size=38) for value in values]
        arrows = [MathTex(rf"\xrightarrow{{{difference}}}", font_size=31, color=color) for difference in differences]
        sequence = VGroup()
        for index, value in enumerate(value_mobs):
            sequence.add(value)
            if index < len(arrows):
                sequence.add(arrows[index])
        sequence.arrange(RIGHT, buff=0.16)

        label = Text(title, font_size=27, color=color)
        content = VGroup(label, sequence).arrange(DOWN, buff=0.28)
        box = RoundedRectangle(
            width=5.55,
            height=1.8,
            corner_radius=0.14,
            color=BLACK,
            stroke_width=2,
        ).move_to(content)
        return VGroup(box, content)

    def _value_rows(
        self,
        x_values: list[str],
        y_values: list[str],
        y_label: str,
        *,
        first_diffs: list[str] | None = None,
    ) -> VGroup:
        x_row = VGroup(MathTex("x", font_size=32), *[MathTex(v, font_size=32) for v in x_values])
        y_row = VGroup(MathTex(y_label, font_size=32), *[MathTex(v, font_size=32) for v in y_values])
        x_row.arrange(RIGHT, buff=0.48)
        y_row.arrange(RIGHT, buff=0.48).next_to(x_row, DOWN, buff=0.3)
        y_row.align_to(x_row, LEFT)

        rows = VGroup(x_row, y_row)
        if first_diffs is not None:
            diff = VGroup(*[MathTex(v, font_size=27, color=ACCENT) for v in first_diffs])
            diff.arrange(RIGHT, buff=0.72).next_to(y_row[1:], DOWN, buff=0.22)
            diff.shift(RIGHT * 0.18)
            rows.add(diff)

        box = RoundedRectangle(
            width=rows.width + 0.55,
            height=rows.height + 0.45,
            corner_radius=0.1,
            color=BLACK,
            stroke_width=2,
        ).move_to(rows)
        return VGroup(box, rows)

    def build_affine_demo(self) -> dict[str, Mobject]:
        table = self._value_rows(
            ["0", "1", "2", "3"],
            ["1", "3", "5", "7"],
            "f(x)",
            first_diffs=["+2", "+2", "+2"],
        )
        table.scale(0.88).to_edge(LEFT, buff=0.65).shift(DOWN * 0.48)

        axes = Axes(
            x_range=[-0.4, 3.6, 1],
            y_range=[0, 8.2, 1],
            x_length=4.8,
            y_length=3.3,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2, "include_numbers": False},
        )
        labels = axes.get_axis_labels(MathTex("x", font_size=25), MathTex("f(x)", font_size=25))
        line = axes.plot(lambda x: 2 * x + 1, x_range=[0, 3.3], color=ACCENT, stroke_width=3.5)
        points = VGroup(*[Dot(axes.c2p(x, 2 * x + 1), color=ACCENT, radius=0.06) for x in range(4)])

        p0 = axes.c2p(0.55, 2.1)
        p1 = axes.c2p(1.55, 2.1)
        p2 = axes.c2p(1.55, 4.1)
        slope_triangle = VGroup(
            Line(p0, p1, color=WARN, stroke_width=2.4),
            Line(p1, p2, color=WARN, stroke_width=2.4),
            MathTex("1", color=WARN, font_size=23).next_to(Line(p0, p1), DOWN, buff=0.05),
            MathTex("2", color=WARN, font_size=23).next_to(Line(p1, p2), RIGHT, buff=0.05),
        )

        graph = VGroup(axes, labels, line, points, slope_triangle)
        graph.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.42)
        return {
            "table": table,
            "axes": VGroup(axes, labels),
            "line": line,
            "points": points,
            "triangle": slope_triangle,
            "graph": graph,
        }

    def _square_area_model(self, side: int) -> VGroup:
        cell_size = 0.43
        cells = VGroup()
        for row in range(side):
            for column in range(side):
                is_new_border = side == 1 or row == side - 1 or column == side - 1
                cell = Square(
                    side_length=cell_size,
                    color=BLACK,
                    stroke_width=1.35,
                    fill_color=QUAD if is_new_border else SOFT,
                    fill_opacity=0.48 if is_new_border else 0.08,
                )
                cells.add(cell)
        cells.arrange_in_grid(rows=side, cols=side, buff=0)

        area = MathTex(rf"{side}\times {side}={side**2}", font_size=35)
        if side == 1:
            note = Text("aire : 1", font_size=24, color=QUAD)
        else:
            note = Text(f"nouvelle bordure : +{2 * side - 1}", font_size=24, color=QUAD)
        labels = VGroup(area, note).arrange(DOWN, buff=0.12)
        return VGroup(cells, labels).arrange(DOWN, buff=0.24)

    def build_quadratic_difference_panel(self) -> dict[str, Mobject]:
        labels = VGroup(
            Text("côté x", font_size=23, color=SOFT),
            Text("aire x²", font_size=23, color=SOFT),
            Text("1ers écarts", font_size=23, color=ACCENT),
            Text("2es écarts", font_size=23, color=QUAD),
        ).arrange(DOWN, aligned_edge=RIGHT, buff=0.37)

        x_values = VGroup(*[MathTex(str(value), font_size=31) for value in [1, 2, 3, 4]])
        area_values = VGroup(*[MathTex(str(value), font_size=31) for value in [1, 4, 9, 16]])
        first_values = VGroup(*[MathTex(value, font_size=29, color=ACCENT) for value in ["+3", "+5", "+7"]])
        second_values = VGroup(*[MathTex(value, font_size=29, color=QUAD) for value in ["+2", "+2"]])

        for row in [x_values, area_values]:
            row.arrange(RIGHT, buff=0.66)
        first_values.arrange(RIGHT, buff=0.86)
        second_values.arrange(RIGHT, buff=1.08)

        rows = VGroup(x_values, area_values, first_values, second_values)
        for row, label in zip(rows, labels):
            row.next_to(label, RIGHT, buff=0.38)

        content = VGroup(labels, rows)
        box = RoundedRectangle(
            width=content.width + 0.55,
            height=content.height + 0.45,
            corner_radius=0.12,
            color=BLACK,
            stroke_width=2,
        ).move_to(content)
        group = VGroup(box, content)
        group.to_edge(RIGHT, buff=0.62).shift(DOWN * 0.35)

        return {
            "group": group,
            "box": box,
            "labels": labels,
            "x_values": x_values,
            "area_values": area_values,
            "first_values": first_values,
            "second_values": second_values,
        }

    def build_quadratic_graph(self) -> dict[str, Mobject]:
        axes = Axes(
            x_range=[-0.3, 4.5, 1],
            y_range=[0, 17.5, 4],
            x_length=6.2,
            y_length=3.45,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2, "include_numbers": False},
        )
        labels = axes.get_axis_labels(MathTex("x", font_size=25), MathTex("g(x)", font_size=25))
        points = VGroup(*[Dot(axes.c2p(x, x**2), color=QUAD, radius=0.065) for x in range(5)])
        curve = axes.plot(lambda x: x**2, x_range=[0, 4.08], color=QUAD, stroke_width=3.5)
        graph = VGroup(axes, labels, points, curve).move_to(ORIGIN + DOWN * 0.45)
        return {
            "group": graph,
            "axes": VGroup(axes, labels),
            "points": points,
            "curve": curve,
        }

    def _model_card(self, title: str, formula: str, difference: str, quadratic: bool) -> VGroup:
        color = QUAD if quadratic else ACCENT
        box = RoundedRectangle(
            width=5.35,
            height=3.65,
            corner_radius=0.16,
            color=BLACK,
            stroke_width=2.2,
        )
        heading = Text(title, font_size=31, color=color)
        expression = MathTex(formula, font_size=41)
        change = Text(difference, font_size=25, color=color)

        axes = Axes(
            x_range=[-1.6, 1.6, 1],
            y_range=[-1.1, 2.0, 1],
            x_length=2.8,
            y_length=1.45,
            tips=False,
            axis_config={"color": SOFT, "stroke_width": 1.5, "include_numbers": False},
        )
        if quadratic:
            graph = axes.plot(lambda x: 0.62 * x**2 - 0.45, x_range=[-1.35, 1.35], color=color, stroke_width=2.8)
        else:
            graph = axes.plot(lambda x: 0.62 * x + 0.32, x_range=[-1.35, 1.35], color=color, stroke_width=2.8)
        mini_graph = VGroup(axes, graph)

        content = VGroup(heading, expression, change, mini_graph).arrange(DOWN, buff=0.22)
        content.move_to(box)
        return VGroup(box, content)

    def build_quiz_cards(self) -> dict[str, Mobject]:
        items = [
            (r"3x-2", "affine", ACCENT),
            (r"x^2+1", "quadratique", QUAD),
            (r"\frac{1}{x}", "ni l'un ni l'autre", WARN),
        ]
        cards = VGroup()
        answers = VGroup()
        for expression, answer_text, color in items:
            formula = MathTex(expression, font_size=44)
            answer = Text(answer_text, font_size=24, color=color)
            box = RoundedRectangle(width=3.25, height=1.9, corner_radius=0.15, color=BLACK, stroke_width=2)
            formula.move_to(box.get_center() + UP * 0.18)
            answer.next_to(formula, DOWN, buff=0.25)
            cards.add(VGroup(box, formula))
            answers.add(answer)
        cards.arrange(RIGHT, buff=0.35).move_to(ORIGIN)
        for answer, card in zip(answers, cards):
            answer.next_to(card[1], DOWN, buff=0.25)
        return {"cards": cards, "answers": answers}

    # ------------------------------------------------------------------
    # Scene segments
    # ------------------------------------------------------------------
    def intro_segment(self) -> None:
        heading = self._title("Droite ou parabole ?", "Regarder comment les valeurs changent")
        constant_card = self._pattern_card("même gain", ["1", "3", "5", "7"], ["+2", "+2", "+2"], ACCENT)
        changing_card = self._pattern_card("gain qui évolue", ["1", "4", "9", "16"], ["+3", "+5", "+7"], QUAD)
        cards = VGroup(constant_card, changing_card).arrange(DOWN, buff=0.38).next_to(heading, DOWN, buff=0.5)
        question = Text("Quelle forme prendra le graphe ?", font_size=30, color=SOFT).to_edge(DOWN, buff=0.48)

        with self.narrated(SCRIPT_SEGMENTS[0]):
            self.wait_until_bookmark("bk_intro_title")
            self.play(Write(heading), run_time=0.9)
            self.wait_until_bookmark("bk_intro_constant")
            self.play(FadeIn(constant_card, shift=0.18 * UP), run_time=0.75)
            self.wait_until_bookmark("bk_intro_changing")
            self.play(FadeIn(changing_card, shift=0.18 * UP), run_time=0.75)
            self.wait_until_bookmark("bk_intro_question")
            self.play(FadeIn(question, shift=0.12 * UP), run_time=0.65)
            self.wait(0.6)

        self.play(FadeOut(VGroup(heading, cards, question)), run_time=0.7)

    def affine_segment(self) -> None:
        heading = self._title("1. Même gain à chaque pas", "le modèle affine")
        demo = self.build_affine_demo()
        formula = MathTex(r"f(x)=2x+1", font_size=49).next_to(heading, DOWN, buff=0.25)
        general_formula = MathTex(r"f(x)=ax+b", font_size=49).move_to(formula)
        rule = self._pill("premiers écarts constants", ACCENT, font_size=24).to_edge(DOWN, buff=0.35)

        with self.narrated(SCRIPT_SEGMENTS[1]):
            self.wait_until_bookmark("bk_affine_table")
            self.play(Write(heading), FadeIn(demo["table"], shift=0.18 * UP), run_time=0.95)
            self.wait_until_bookmark("bk_affine_diff")
            self.play(Indicate(demo["table"][1][2], color=ACCENT), run_time=0.85)
            self.wait_until_bookmark("bk_affine_points")
            self.play(FadeIn(demo["axes"], shift=0.15 * LEFT), run_time=0.75)
            self.play(LaggedStart(*(FadeIn(point, scale=0.7) for point in demo["points"]), lag_ratio=0.14), run_time=0.8)
            self.wait_until_bookmark("bk_affine_line")
            self.play(Create(demo["line"]), run_time=0.85)
            self.play(FadeIn(demo["triangle"]), run_time=0.55)
            self.wait_until_bookmark("bk_affine_formula")
            self.play(Write(formula), run_time=0.65)
            self.wait_until_bookmark("bk_affine_general")
            self.play(Transform(formula, general_formula), FadeIn(rule, shift=0.12 * UP), run_time=0.75)
            self.wait(0.65)

        self.play(FadeOut(VGroup(heading, formula, demo["table"], demo["graph"], rule)), run_time=0.75)

    def transition_segment(self) -> None:
        constant = self._pattern_card("premiers écarts constants", ["1", "3", "5", "7"], ["+2", "+2", "+2"], ACCENT)
        changing = self._pattern_card("premiers écarts variables", ["1", "4", "9", "16"], ["+3", "+5", "+7"], QUAD)
        constant.move_to(ORIGIN + UP * 0.55)
        changing.move_to(constant)
        question = Text("Mais les gains augmentent eux-mêmes toujours de 2.", font_size=30, color=QUAD)
        question.next_to(changing, DOWN, buff=0.52)

        with self.narrated(SCRIPT_SEGMENTS[2]):
            self.wait_until_bookmark("bk_transition_constant")
            self.play(FadeIn(constant, shift=0.18 * UP), run_time=0.7)
            self.wait_until_bookmark("bk_transition_change")
            self.play(ReplacementTransform(constant, changing), run_time=0.85)
            self.wait_until_bookmark("bk_transition_question")
            self.play(FadeIn(question, shift=0.15 * UP), run_time=0.7)
            self.wait(0.65)

        self.play(FadeOut(VGroup(changing, question)), run_time=0.65)

    def quadratique_segment(self) -> None:
        heading = self._title("2. Quand le gain lui-même change", "le modèle quadratique")
        panel = self.build_quadratic_difference_panel()

        square = self._square_area_model(1)
        square.to_edge(LEFT, buff=1.3).shift(DOWN * 0.35)

        hidden_panel_items = VGroup(
            *panel["x_values"],
            *panel["area_values"],
            panel["labels"][2],
            panel["labels"][3],
            *panel["first_values"],
            *panel["second_values"],
        )
        hidden_panel_items.set_opacity(0)

        with self.narrated(SCRIPT_SEGMENTS[3]):
            self.wait_until_bookmark("bk_quad_square1")
            self.play(Write(heading), FadeIn(square, shift=0.15 * UP), run_time=0.9)
            self.play(FadeIn(panel["box"]), FadeIn(panel["labels"][0]), FadeIn(panel["labels"][1]), run_time=0.55)
            self.play(
                panel["x_values"][0].animate.set_opacity(1),
                panel["area_values"][0].animate.set_opacity(1),
                run_time=0.45,
            )

            self.wait_until_bookmark("bk_quad_square2")
            next_square = self._square_area_model(2).move_to(square)
            self.play(ReplacementTransform(square, next_square), run_time=0.8)
            square = next_square
            self.play(
                panel["x_values"][1].animate.set_opacity(1),
                panel["area_values"][1].animate.set_opacity(1),
                run_time=0.45,
            )

            self.wait_until_bookmark("bk_quad_square3")
            next_square = self._square_area_model(3).move_to(square)
            self.play(ReplacementTransform(square, next_square), run_time=0.8)
            square = next_square
            self.play(
                panel["x_values"][2].animate.set_opacity(1),
                panel["area_values"][2].animate.set_opacity(1),
                run_time=0.45,
            )

            self.wait_until_bookmark("bk_quad_square4")
            next_square = self._square_area_model(4).move_to(square)
            self.play(ReplacementTransform(square, next_square), run_time=0.8)
            square = next_square
            self.play(
                panel["x_values"][3].animate.set_opacity(1),
                panel["area_values"][3].animate.set_opacity(1),
                run_time=0.45,
            )

            self.wait_until_bookmark("bk_quad_first_diff")
            self.play(
                panel["labels"][2].animate.set_opacity(1),
                *[value.animate.set_opacity(1) for value in panel["first_values"]],
                run_time=0.75,
            )
            self.play(Indicate(panel["first_values"], color=ACCENT), run_time=0.65)

            self.wait_until_bookmark("bk_quad_second_diff")
            self.play(
                panel["labels"][3].animate.set_opacity(1),
                *[value.animate.set_opacity(1) for value in panel["second_values"]],
                run_time=0.7,
            )
            self.play(Indicate(panel["second_values"], color=QUAD), run_time=0.7)
            self.wait(0.5)

            graph = self.build_quadratic_graph()
            example_formula = MathTex(r"g(x)=x^2", font_size=50).next_to(heading, DOWN, buff=0.22)
            general_formula = MathTex(r"g(x)=ax^2+bx+c,\quad a\neq0", font_size=46).move_to(example_formula)
            family_note = Text("une famille de paraboles", font_size=25, color=QUAD).next_to(example_formula, DOWN, buff=0.12)

            self.play(FadeOut(VGroup(square, panel["group"])), run_time=0.7)
            self.wait_until_bookmark("bk_quad_graph_points")
            self.play(FadeIn(graph["axes"], shift=0.15 * UP), run_time=0.75)
            self.play(LaggedStart(*(FadeIn(point, scale=0.65) for point in graph["points"]), lag_ratio=0.14), run_time=0.95)
            self.wait_until_bookmark("bk_quad_graph_curve")
            self.play(Create(graph["curve"]), run_time=0.95)
            self.wait_until_bookmark("bk_quad_example_formula")
            self.play(Write(example_formula), run_time=0.65)
            self.wait_until_bookmark("bk_quad_general_form")
            self.play(FadeOut(example_formula), run_time=0.25)
            self.play(FadeIn(general_formula), FadeIn(family_note, shift=0.1 * UP), run_time=0.65)
            example_formula = general_formula
            self.wait(0.75)

        self.play(FadeOut(VGroup(heading, graph["group"], example_formula, family_note)), run_time=0.75)

    def comparaison_segment(self) -> None:
        heading = self._title("Comparer les deux modèles", "chercher le niveau où l'écart devient constant")
        affine_card = self._model_card("Affine", r"f(x)=ax+b", "1ers écarts constants", quadratic=False)
        quadratic_card = self._model_card("Quadratique", r"g(x)=ax^2+bx+c", "2es écarts constants", quadratic=True)
        cards = VGroup(affine_card, quadratic_card).arrange(RIGHT, buff=0.55).next_to(heading, DOWN, buff=0.4)
        condition = VGroup(
            Text("Condition du test :", font_size=27, color=WARN),
            Text("les valeurs de x doivent être espacées régulièrement", font_size=27),
        ).arrange(RIGHT, buff=0.18).to_edge(DOWN, buff=0.35)

        with self.narrated(SCRIPT_SEGMENTS[4]):
            self.wait_until_bookmark("bk_compare_affine")
            self.play(Write(heading), FadeIn(affine_card, shift=0.18 * UP), run_time=0.9)
            self.wait_until_bookmark("bk_compare_quadratic")
            self.play(FadeIn(quadratic_card, shift=0.18 * UP), run_time=0.8)
            self.wait_until_bookmark("bk_compare_condition")
            self.play(FadeIn(condition, shift=0.12 * UP), run_time=0.7)
            self.wait(0.7)

        self.play(FadeOut(VGroup(heading, cards, condition)), run_time=0.75)

    def quiz_segment(self) -> None:
        heading = self._title("Mini-quiz", "classer sans deviner")
        quiz = self.build_quiz_cards()
        quiz["cards"].move_to(ORIGIN + DOWN * 0.1)
        reminder = Text("Forme algébrique d'abord, puis graphe ou tableau.", font_size=28, color=SOFT)
        reminder.to_edge(DOWN, buff=0.55)

        with self.narrated(SCRIPT_SEGMENTS[5]):
            self.wait_until_bookmark("bk_quiz_intro")
            self.play(Write(heading), FadeIn(quiz["cards"], shift=0.2 * UP), run_time=0.9)
            self.wait(0.8)
            self.wait_until_bookmark("bk_quiz_answer1")
            self.play(LaggedStart(*(FadeIn(answer, shift=0.1 * UP) for answer in quiz["answers"]), lag_ratio=0.12), run_time=0.8)
            self.wait_until_bookmark("bk_quiz_rule")
            self.play(FadeIn(reminder, shift=0.15 * UP), run_time=0.6)
            self.wait(0.5)

        self.play(FadeOut(VGroup(heading, quiz["cards"], quiz["answers"], reminder)), run_time=0.7)

    def conclusion_segment(self) -> None:
        heading = self._title("À retenir")
        affine_rule = VGroup(
            Text("Affine", font_size=32, color=ACCENT),
            Text("1ers écarts constants", font_size=29),
            Text("→ une droite", font_size=27, color=ACCENT),
        ).arrange(DOWN, buff=0.14)
        quadratic_rule = VGroup(
            Text("Quadratique", font_size=32, color=QUAD),
            Text("2es écarts constants", font_size=29),
            Text("→ une parabole", font_size=27, color=QUAD),
        ).arrange(DOWN, buff=0.14)
        rules = VGroup(affine_rule, quadratic_rule).arrange(RIGHT, buff=1.35).next_to(heading, DOWN, buff=0.65)

        checks = VGroup(
            self._pill("tableau", ACCENT, font_size=25),
            self._pill("graphe", BLACK, font_size=25),
            self._pill("formule", QUAD, font_size=25),
        ).arrange(RIGHT, buff=0.3).next_to(rules, DOWN, buff=0.55)
        next_card = Text("Suite : sommet • zéros • ouverture", font_size=28, color=SOFT).to_edge(DOWN, buff=0.5)

        with self.narrated(SCRIPT_SEGMENTS[6]):
            self.wait_until_bookmark("bk_recap_affine")
            self.play(Write(heading), FadeIn(affine_rule, shift=0.15 * UP), run_time=0.9)
            self.wait_until_bookmark("bk_recap_quadratic")
            self.play(FadeIn(quadratic_rule, shift=0.15 * UP), run_time=0.75)
            self.wait_until_bookmark("bk_recap_checks")
            self.play(LaggedStart(*(FadeIn(item, shift=0.1 * UP) for item in checks), lag_ratio=0.12), run_time=0.8)
            self.wait_until_bookmark("bk_outro_transition")
            self.play(FadeIn(next_card, shift=0.12 * UP), run_time=0.65)
            self.wait(1.0)
