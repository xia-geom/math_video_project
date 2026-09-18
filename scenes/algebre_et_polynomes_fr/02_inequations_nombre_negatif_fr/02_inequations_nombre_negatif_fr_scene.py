from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os

from manim import (
    BLACK,
    BLUE_D,
    BLUE_E,
    DOWN,
    FadeIn,
    FadeOut,
    GrowArrow,
    GrowFromCenter,
    LEFT,
    MathTex,
    NumberLine,
    ORIGIN,
    RED,
    RIGHT,
    RoundedRectangle,
    Scene,
    Tex,
    Text,
    Transform,
    UP,
    VGroup,
    WHITE,
    Write,
    Arrow,
    Circle,
    Create,
    Cross,
    DashedLine,
    Dot,
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


config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class InequationsNombreNegatifFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    """Pourquoi une inégalité change-t-elle de sens avec un facteur négatif ?"""

    ACCENT = BLUE_D
    ACCENT_2 = BLUE_E
    ERROR = RED

    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            return
        if VoiceoverScene is None or AzureService is None:
            return

        azure_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        azure_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not azure_key or not azure_region:
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", azure_key)
        os.environ.setdefault("AZURE_SERVICE_REGION", azure_region)
        os.environ.setdefault("SPEECH_KEY", azure_key)
        os.environ.setdefault("SPEECH_REGION", azure_region)
        try:
            self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        except Exception:
            return
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, spoken: str):
        if self._voiceover_enabled:
            with self.voiceover(text=tts.ssml(spoken), subcaption=tts.strip_ssml(spoken)) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def make_number_line(
        self,
        x_min: int = -10,
        x_max: int = 10,
        length: float = 11.8,
        y: float = -1.15,
        labelled_values: tuple[int, ...] = (-10, -5, -2, 0, 2, 5, 10),
    ) -> tuple[NumberLine, VGroup]:
        line = NumberLine(
            x_range=[x_min, x_max, 1],
            length=length,
            include_tip=True,
            include_numbers=False,
            stroke_width=3,
            color=BLACK,
            tick_size=0.07,
        ).move_to([0, y, 0])

        labels = VGroup()
        for value in labelled_values:
            if x_min <= value <= x_max:
                label = MathTex(str(value), font_size=25)
                label.next_to(line.n2p(value), DOWN, buff=0.18)
                labels.add(label)

        return line, labels

    def make_point(
        self,
        line: NumberLine,
        value: float,
        label_tex: str,
        color=BLUE_D,
        label_direction=UP,
    ) -> VGroup:
        dot = Dot(line.n2p(value), radius=0.095, color=color)
        label = MathTex(label_tex, font_size=36, color=color)
        label.next_to(dot, label_direction, buff=0.16)
        return VGroup(dot, label)

    def make_operation_badge(self, tex: str) -> VGroup:
        formula = MathTex(tex, font_size=38, color=self.ACCENT)
        box = RoundedRectangle(
            width=formula.width + 0.55,
            height=formula.height + 0.34,
            corner_radius=0.14,
            stroke_color=self.ACCENT,
            stroke_width=2.5,
            fill_color=WHITE,
            fill_opacity=1,
        )
        return VGroup(box, formula)

    def make_check_row(self, tex: str, symbol: str, symbol_color) -> VGroup:
        calculation = MathTex(tex, font_size=34)
        verdict = Text(symbol, font_size=38, color=symbol_color, weight="BOLD")
        return VGroup(calculation, verdict).arrange(RIGHT, buff=0.35)

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)
        X = tts.char("x")

        # ------------------------------------------------------------------
        # Act 1 — Central question
        # ------------------------------------------------------------------
        title = Text(
            "Pourquoi le signe change-t-il ?",
            font_size=46,
            weight="BOLD",
        ).to_edge(UP, buff=0.55)

        question = MathTex(
            r"2<5",
            r"\quad\Longrightarrow\quad",
            r"-2>-5\,?",
            font_size=60,
        )
        question[0].set_color(self.ACCENT)
        question[2].set_color(self.ACCENT)

        intro = (
            "Pourquoi deux est-il inférieur à cinq, mais moins deux devient-il supérieur "
            "à moins cinq ? Nous allons voir que le changement de signe n'est pas une règle "
            "à apprendre par cœur. Il vient d'un mouvement très simple sur la droite numérique."
        )
        with self.narrated(intro) as tracker:
            duration = max(tracker.duration, 4.0)
            self.play(Write(title), run_time=0.24 * duration)
            self.play(Write(question), run_time=0.30 * duration)
            self.wait(0.46 * duration)

        self.play(
            title.animate.scale(0.78).to_edge(UP, buff=0.28),
            FadeOut(question),
            run_time=0.8,
        )

        # ------------------------------------------------------------------
        # Act 2 — Order means left and right
        # ------------------------------------------------------------------
        line, number_labels = self.make_number_line()
        point_2 = self.make_point(line, 2, "2", self.ACCENT)
        point_5 = self.make_point(line, 5, "5", self.ACCENT_2)
        inequality = MathTex(r"2<5", font_size=54).next_to(title, DOWN, buff=0.42)

        relation_arrow = Arrow(
            line.n2p(2) + UP * 0.55,
            line.n2p(5) + UP * 0.55,
            buff=0.10,
            stroke_width=4,
            color=self.ACCENT,
            max_tip_length_to_length_ratio=0.12,
        )
        relation_text = Text(
            "5 est à droite de 2",
            font_size=29,
            color=self.ACCENT,
        ).next_to(relation_arrow, UP, buff=0.16)

        narration = (
            "Sur une droite numérique, comparer deux nombres signifie regarder leur position. "
            "Deux est placé à gauche de cinq. C'est exactement ce que signifie deux inférieur à cinq."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 4.0)
            self.play(FadeIn(line), FadeIn(number_labels), run_time=0.20 * duration)
            self.play(
                GrowFromCenter(point_2),
                GrowFromCenter(point_5),
                Write(inequality),
                run_time=0.25 * duration,
            )
            self.play(
                GrowArrow(relation_arrow),
                FadeIn(relation_text),
                run_time=0.25 * duration,
            )
            self.wait(0.30 * duration)

        self.play(FadeOut(relation_arrow), FadeOut(relation_text), run_time=0.5)

        # ------------------------------------------------------------------
        # Act 3 — A positive factor preserves the order
        # ------------------------------------------------------------------
        positive_badge = self.make_operation_badge(r"\times 2")
        positive_badge.next_to(inequality, RIGHT, buff=0.55)

        point_4_target = self.make_point(line, 4, "4", self.ACCENT)
        point_10_target = self.make_point(line, 10, "10", self.ACCENT_2)
        inequality_times_2 = MathTex(r"4<10", font_size=54).move_to(inequality)
        preserved = Text(
            "ordre conservé",
            font_size=30,
            color=self.ACCENT,
        ).next_to(inequality_times_2, DOWN, buff=0.22)

        narration = (
            "Commençons par multiplier les deux nombres par un nombre positif. "
            "En multipliant par deux, deux se déplace vers quatre, et cinq se déplace vers dix. "
            "Les deux points s'éloignent de zéro, mais quatre reste à gauche de dix. "
            "L'ordre est conservé."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 5.0)
            self.play(FadeIn(positive_badge), run_time=0.16 * duration)
            self.play(
                Transform(point_2, point_4_target),
                Transform(point_5, point_10_target),
                Transform(inequality, inequality_times_2),
                run_time=0.34 * duration,
            )
            self.play(FadeIn(preserved), run_time=0.16 * duration)
            self.wait(0.34 * duration)

        # Reset to the original points before introducing the new idea.
        point_2_original = self.make_point(line, 2, "2", self.ACCENT)
        point_5_original = self.make_point(line, 5, "5", self.ACCENT_2)
        inequality_original = MathTex(r"2<5", font_size=54).move_to(inequality)

        reset_narration = (
            "Revenons maintenant aux nombres deux et cinq. Cette fois, nous allons multiplier par moins un."
        )
        with self.narrated(reset_narration) as tracker:
            duration = max(tracker.duration, 2.7)
            self.play(
                FadeOut(preserved),
                FadeOut(positive_badge),
                Transform(point_2, point_2_original),
                Transform(point_5, point_5_original),
                Transform(inequality, inequality_original),
                run_time=0.62 * duration,
            )
            self.wait(0.38 * duration)

        # ------------------------------------------------------------------
        # Act 4 — A negative factor is a reflection
        # ------------------------------------------------------------------
        zero_marker = DashedLine(
            line.n2p(0) + DOWN * 0.25,
            line.n2p(0) + UP * 2.15,
            dash_length=0.12,
            color=self.ACCENT,
            stroke_width=2.5,
        )
        mirror_label = Text(
            "miroir autour de 0",
            font_size=28,
            color=self.ACCENT,
        ).next_to(zero_marker, UP, buff=0.14)
        negative_badge = self.make_operation_badge(r"\times(-1)")
        negative_badge.next_to(inequality, RIGHT, buff=0.55)

        narration = (
            "Multiplier par moins un ne fait pas seulement changer les étiquettes. "
            "Chaque point traverse zéro et arrive à la même distance de l'autre côté. "
            "Autrement dit, la droite numérique se réfléchit comme dans un miroir placé en zéro."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 4.8)
            self.play(
                FadeIn(zero_marker),
                FadeIn(mirror_label),
                FadeIn(negative_badge),
                run_time=0.30 * duration,
            )
            self.wait(0.70 * duration)

        point_minus_2_target = self.make_point(line, -2, "-2", self.ACCENT)
        point_minus_5_target = self.make_point(line, -5, "-5", self.ACCENT_2)

        narration = (
            "Le point deux arrive en moins deux. Le point cinq, qui était plus loin de zéro, "
            "arrive en moins cinq. Regardons leur nouvelle position avant d'écrire une formule."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 4.2)
            self.play(
                Transform(point_2, point_minus_2_target, path_arc=1.15),
                Transform(point_5, point_minus_5_target, path_arc=1.15),
                run_time=0.58 * duration,
            )
            self.wait(0.42 * duration)

        spatial_reading = MathTex(r"-5<-2", font_size=54).move_to(inequality)
        reversed_reading = MathTex(r"-2>-5", font_size=54).move_to(inequality)
        reversed_label = Text(
            "ordre inversé",
            font_size=30,
            color=self.ACCENT,
        ).next_to(spatial_reading, DOWN, buff=0.22)

        narration = (
            "Maintenant, moins cinq est à gauche de moins deux. Nous lisons donc : "
            "moins cinq est inférieur à moins deux. Mais si nous gardons dans le même ordre "
            "les descendants de deux et de cinq, nous écrivons moins deux supérieur à moins cinq. "
            "Le sens de l'inégalité s'est inversé parce que gauche et droite se sont inversées."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 6.0)
            self.play(
                Transform(inequality, spatial_reading),
                FadeIn(reversed_label),
                run_time=0.28 * duration,
            )
            self.wait(0.22 * duration)
            self.play(
                Transform(inequality, reversed_reading),
                run_time=0.22 * duration,
            )
            self.wait(0.28 * duration)

        key_box = RoundedRectangle(
            width=11.8,
            height=1.05,
            corner_radius=0.16,
            stroke_color=self.ACCENT,
            stroke_width=2.6,
            fill_color=self.ACCENT,
            fill_opacity=0.07,
        ).to_edge(DOWN, buff=0.25)
        key_text = Text(
            "Facteur négatif : réflexion, donc ordre inversé.",
            font_size=31,
            color=BLACK,
        ).move_to(key_box)

        narration = (
            "Voici l'idée essentielle : multiplier par un nombre négatif produit une réflexion. "
            "Une réflexion inverse l'ordre des points."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 3.3)
            self.play(FadeIn(key_box), Write(key_text), run_time=0.55 * duration)
            self.wait(0.45 * duration)

        # ------------------------------------------------------------------
        # Act 5 — Formal rule, introduced after the intuition
        # ------------------------------------------------------------------
        self.play(
            FadeOut(
                VGroup(
                    line,
                    number_labels,
                    point_2,
                    point_5,
                    zero_marker,
                    mirror_label,
                    negative_badge,
                    inequality,
                    reversed_label,
                    key_box,
                    key_text,
                )
            ),
            run_time=0.8,
        )

        rule_title = Text("La règle générale", font_size=39, weight="BOLD")
        rule_title.next_to(title, DOWN, buff=0.45)

        premise = MathTex(r"a<b", font_size=54)
        positive_rule = MathTex(
            r"c>0", r"\quad\Longrightarrow\quad", r"ac<bc", font_size=45
        )
        negative_rule = MathTex(
            r"c<0", r"\quad\Longrightarrow\quad", r"ac>bc", font_size=45
        )
        negative_rule[0].set_color(self.ACCENT)
        negative_rule[2].set_color(self.ACCENT)

        rules = VGroup(premise, positive_rule, negative_rule).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.55,
        ).move_to(ORIGIN + DOWN * 0.15)

        narration = (
            "Nous pouvons maintenant écrire la règle générale. Si a est inférieur à b, "
            "multiplier par un nombre positif conserve le sens. Multiplier par un nombre négatif "
            "inverse le sens. Cette règle résume exactement les deux mouvements que nous venons de voir."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 5.4)
            self.play(Write(rule_title), run_time=0.18 * duration)
            self.play(Write(premise), run_time=0.18 * duration)
            self.play(Write(positive_rule), run_time=0.23 * duration)
            self.play(Write(negative_rule), run_time=0.23 * duration)
            self.wait(0.18 * duration)

        self.wait(1.0)
        self.play(FadeOut(VGroup(rule_title, rules)), run_time=0.8)

        # ------------------------------------------------------------------
        # Act 6 — Worked example
        # ------------------------------------------------------------------
        example_title = Text(
            "Exemple : résoudre une inéquation",
            font_size=39,
            weight="BOLD",
        ).next_to(title, DOWN, buff=0.45)

        equation = MathTex(r"-3x<6", font_size=62)
        equation.move_to(UP * 0.35)

        narration = (
            f"Résolvons maintenant moins trois fois {X} est inférieur à six. "
            "Notre objectif est d'isoler x, comme dans une équation, mais en surveillant le signe du nombre par lequel nous divisons."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 4.3)
            self.play(Write(example_title), run_time=0.26 * duration)
            self.play(Write(equation), run_time=0.30 * duration)
            self.wait(0.44 * duration)

        division_left = MathTex(r"\div(-3)", font_size=30, color=self.ACCENT)
        division_right = division_left.copy()
        division_left.next_to(equation, DOWN, buff=0.32).shift(LEFT * 0.95)
        division_right.next_to(equation, DOWN, buff=0.32).shift(RIGHT * 0.95)

        solved = MathTex(r"x>-2", font_size=62)
        solved.move_to(equation)
        reason = Text(
            "on divise par un nombre négatif",
            font_size=29,
            color=self.ACCENT,
        ).next_to(solved, DOWN, buff=0.42)

        narration = (
            "Nous divisons les deux membres par moins trois. Puisque moins trois est négatif, "
            "la division réfléchit l'ordre. Le signe inférieur devient donc supérieur. "
            "Six divisé par moins trois vaut moins deux. La solution est x supérieur à moins deux."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 5.4)
            self.play(
                FadeIn(division_left),
                FadeIn(division_right),
                run_time=0.22 * duration,
            )
            self.wait(0.18 * duration)
            self.play(
                FadeOut(division_left),
                FadeOut(division_right),
                Transform(equation, solved),
                run_time=0.30 * duration,
            )
            self.play(FadeIn(reason), run_time=0.14 * duration)
            self.wait(0.16 * duration)

        # Number-line representation of x > -2
        solution_line, solution_labels = self.make_number_line(
            x_min=-6,
            x_max=5,
            length=9.6,
            y=-1.35,
            labelled_values=(-6, -3, -2, 0, 5),
        )
        open_circle = Circle(
            radius=0.115,
            stroke_color=self.ACCENT,
            stroke_width=3.2,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(solution_line.n2p(-2))
        ray = Arrow(
            solution_line.n2p(-2) + RIGHT * 0.15,
            solution_line.n2p(4.75),
            buff=0,
            stroke_width=6,
            color=self.ACCENT,
            max_tip_length_to_length_ratio=0.08,
        )
        interval = MathTex(r"]-2,+\infty[", font_size=36, color=self.ACCENT)
        interval.next_to(solution_line, DOWN, buff=0.52)

        narration = (
            "Sur la droite numérique, nous plaçons un cercle ouvert en moins deux, "
            "car moins deux lui-même ne vérifie pas une inégalité stricte. "
            "Puis nous colorons tous les nombres situés à droite."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 4.4)
            self.play(
                FadeOut(reason),
                FadeIn(solution_line),
                FadeIn(solution_labels),
                run_time=0.24 * duration,
            )
            self.play(GrowFromCenter(open_circle), run_time=0.18 * duration)
            self.play(GrowArrow(ray), run_time=0.24 * duration)
            self.play(Write(interval), run_time=0.16 * duration)
            self.wait(0.18 * duration)

        # ------------------------------------------------------------------
        # Act 7 — Three tests: solution, boundary, counterexample
        # ------------------------------------------------------------------
        self.play(
            FadeOut(VGroup(solution_line, solution_labels, open_circle, ray, interval)),
            equation.animate.to_edge(LEFT, buff=1.1).shift(UP * 0.15),
            run_time=0.8,
        )

        tests_title = Text("Vérifions trois valeurs", font_size=34, weight="BOLD")
        tests_title.next_to(example_title, DOWN, buff=0.48)
        test_good = self.make_check_row(r"x=0:\quad -3(0)=0<6", "✓", self.ACCENT)
        test_boundary = self.make_check_row(r"x=-2:\quad -3(-2)=6\not<6", "✗", self.ERROR)
        test_bad = self.make_check_row(r"x=-3:\quad -3(-3)=9\not<6", "✗", self.ERROR)
        tests = VGroup(test_good, test_boundary, test_bad).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.45,
        )
        tests.next_to(tests_title, DOWN, buff=0.48)

        narration = (
            "Testons plusieurs cas. Zéro est à droite de moins deux, et il vérifie l'inéquation. "
            "Moins deux donne exactement six : il est donc exclu. "
            "Enfin, moins trois est à gauche de moins deux, et il ne vérifie pas l'inéquation. "
            "Ces trois tests correspondent parfaitement à la droite numérique."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 6.3)
            self.play(Write(tests_title), run_time=0.14 * duration)
            self.play(FadeIn(test_good), run_time=0.22 * duration)
            self.play(FadeIn(test_boundary), run_time=0.22 * duration)
            self.play(FadeIn(test_bad), run_time=0.22 * duration)
            self.wait(0.20 * duration)

        # ------------------------------------------------------------------
        # Act 8 — Common mistake
        # ------------------------------------------------------------------
        self.play(
            FadeOut(VGroup(tests_title, tests, equation)),
            run_time=0.7,
        )

        mistake_title = Text("Erreur fréquente", font_size=39, weight="BOLD", color=self.ERROR)
        mistake_title.next_to(example_title, DOWN, buff=0.55)
        wrong = MathTex(
            r"-3x<6", r"\quad\Longrightarrow\quad", r"x<-2", font_size=52
        )
        wrong.next_to(mistake_title, DOWN, buff=0.48)
        wrong[2].set_color(self.ERROR)
        wrong_cross = Cross(wrong, stroke_color=self.ERROR, stroke_width=6)

        contradiction = VGroup(
            MathTex(r"x=-3", font_size=36),
            Text("serait accepté, mais", font_size=29),
            MathTex(r"9<6", font_size=36),
            Text("est faux.", font_size=29),
        ).arrange(RIGHT, buff=0.20).next_to(wrong, DOWN, buff=0.55)
        correct = MathTex(r"\boxed{x>-2}", font_size=60, color=self.ACCENT)
        correct.next_to(contradiction, DOWN, buff=0.58)

        narration = (
            "L'erreur fréquente consiste à diviser par moins trois sans inverser le signe. "
            "On obtiendrait alors x inférieur à moins deux. Mais cette réponse accepterait moins trois, "
            "alors que moins trois produit neuf inférieur à six, ce qui est faux. "
            "Le test révèle immédiatement l'erreur."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 6.0)
            self.play(Write(mistake_title), Write(wrong), run_time=0.30 * duration)
            self.play(Write(contradiction), run_time=0.27 * duration)
            self.play(Create(wrong_cross), run_time=0.16 * duration)
            self.play(Write(correct), run_time=0.15 * duration)
            self.wait(0.12 * duration)

        # ------------------------------------------------------------------
        # Act 9 — Summary, one line at a time
        # ------------------------------------------------------------------
        self.play(
            FadeOut(VGroup(example_title, mistake_title, wrong, wrong_cross, contradiction, correct)),
            run_time=0.8,
        )

        summary_title = Text("À retenir", font_size=43, weight="BOLD")
        summary_title.next_to(title, DOWN, buff=0.48)

        summary_1 = VGroup(
            MathTex(r"c>0", font_size=42, color=self.ACCENT),
            Text("l'ordre est conservé", font_size=32),
        ).arrange(RIGHT, buff=0.55)

        summary_2 = VGroup(
            MathTex(r"c<0", font_size=42, color=self.ACCENT),
            Text("l'ordre est inversé", font_size=32),
        ).arrange(RIGHT, buff=0.55)

        summary_3 = Text(
            "Pourquoi ? Un facteur négatif réfléchit la droite numérique.",
            font_size=32,
            color=self.ACCENT,
        )

        summary = VGroup(summary_1, summary_2, summary_3).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.62,
        ).move_to(DOWN * 0.15)

        narration = (
            "Retenons trois choses. Un facteur positif conserve l'ordre. "
            "Un facteur négatif inverse l'ordre. Et la raison géométrique est simple : "
            "un facteur négatif réfléchit les points de l'autre côté de zéro."
        )
        with self.narrated(narration) as tracker:
            duration = max(tracker.duration, 5.0)
            self.play(Write(summary_title), run_time=0.18 * duration)
            self.play(FadeIn(summary_1), run_time=0.22 * duration)
            self.play(FadeIn(summary_2), run_time=0.22 * duration)
            self.play(FadeIn(summary_3), run_time=0.22 * duration)
            self.wait(0.16 * duration)

        self.wait(1.5)
