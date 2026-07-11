from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import os

from manim import *

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
SOFT = GREY_B
DARK_SOFT = GREY_D


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class RacineCarreeValeurAbsolueFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    """Pourquoi sqrt(x^2) vaut |x|, et non toujours x.

    La scène suit une véritable démarche mathématique : observation,
    conjecture, contre-exemple, correction, définition et généralisation.
    """

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
    def narration(self, spoken: str):
        """Create a voiceover context with SSML-free captions."""
        if self._voiceover_enabled:
            with self.voiceover(
                text=tts.ssml(spoken),
                subcaption=tts.strip_ssml(spoken),
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def fade_stage(self, run_time: float = 0.8) -> None:
        """Clear the visible stage between major acts."""
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=run_time)

    @staticmethod
    def heading(text: str) -> Text:
        return Text(text, font_size=44, weight=BOLD).to_edge(UP, buff=0.35)

    @staticmethod
    def label_box(text: str, width: float = 2.5) -> VGroup:
        label = Text(text, font_size=27)
        box = RoundedRectangle(
            corner_radius=0.14,
            width=max(width, label.width + 0.5),
            height=0.72,
            stroke_color=ACCENT,
            stroke_width=2.5,
            fill_color=ACCENT,
            fill_opacity=0.06,
        )
        label.move_to(box)
        return VGroup(box, label)

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)
        x_spoken = tts.char("x")

        # ------------------------------------------------------------------
        # ACT 0 — Central question and roadmap
        # ------------------------------------------------------------------
        title = Text(
            "Racine carrée et valeur absolue",
            font_size=48,
            weight=BOLD,
        ).to_edge(UP, buff=0.45)
        question = MathTex(r"\sqrt{x^2}\stackrel{?}{=}x").scale(1.65)
        question.shift(UP * 0.45)
        prompt = Text("Cette égalité est-elle toujours vraie ?", font_size=31)
        prompt.next_to(question, DOWN, buff=0.45)

        reasoning_words = VGroup(
            self.label_box("Observer", 2.2),
            self.label_box("Conjecturer", 2.4),
            self.label_box("Tester", 2.0),
            self.label_box("Corriger", 2.1),
        ).arrange(RIGHT, buff=0.25)
        reasoning_words.to_edge(DOWN, buff=0.65)

        with self.narration(
            f"Pourquoi la racine carrée de {x_spoken} au carré n'est-elle pas toujours égale à {x_spoken} ? "
            "Cette question nous donnera un bel exemple de raisonnement mathématique. "
            "Nous allons observer, proposer une règle, la tester, puis la corriger."
        ):
            self.play(Write(title), run_time=1.2)
            self.play(Write(question), run_time=1.2)
            self.play(FadeIn(prompt, shift=UP * 0.15), run_time=0.8)
            self.play(
                LaggedStart(
                    *[FadeIn(box, shift=UP * 0.1) for box in reasoning_words],
                    lag_ratio=0.22,
                ),
                run_time=2.0,
            )
            self.wait(1.0)

        self.fade_stage()

        # ------------------------------------------------------------------
        # ACT 1 — A natural conjecture, then a counterexample
        # ------------------------------------------------------------------
        section = self.heading("1. Une règle qui semble évidente")
        positive_tag = Text("Premier test : un nombre positif", font_size=30)
        positive_tag.next_to(section, DOWN, buff=0.45)

        x_equals_4 = MathTex(r"x=4").scale(1.15).shift(UP * 1.0)
        chain_positive = VGroup(
            MathTex(r"\sqrt{x^2}"),
            MathTex("="),
            MathTex(r"\sqrt{4^2}"),
            MathTex("="),
            MathTex(r"\sqrt{16}"),
            MathTex("="),
            MathTex("4"),
        ).arrange(RIGHT, buff=0.18)
        chain_positive.scale(1.15)
        chain_positive.shift(DOWN * 0.1)

        conjecture = MathTex(r"\sqrt{x^2}=x").scale(1.35)
        conjecture.next_to(chain_positive, DOWN, buff=0.8)
        conjecture_label = Text("Conjecture", font_size=27, color=ACCENT)
        conjecture_label.next_to(conjecture, LEFT, buff=0.35)
        conjecture_box = SurroundingRectangle(
            VGroup(conjecture_label, conjecture),
            color=ACCENT,
            buff=0.22,
            stroke_width=2.5,
            corner_radius=0.12,
        )

        with self.narration(
            f"Commençons par {x_spoken} égal à quatre. "
            "Quatre au carré vaut seize, et la racine carrée de seize vaut quatre. "
            "On pourrait donc proposer la règle suivante : la racine carrée de "
            f"{x_spoken} au carré est égale à {x_spoken}."
        ):
            self.play(Write(section), FadeIn(positive_tag), run_time=1.2)
            self.play(Write(x_equals_4), run_time=0.7)
            self.play(Write(chain_positive[0]), run_time=0.6)
            for symbol in chain_positive[1:]:
                self.play(Write(symbol), run_time=0.45)
            self.wait(0.8)
            self.play(
                FadeIn(conjecture_label),
                Write(conjecture),
                Create(conjecture_box),
                run_time=1.2,
            )
            self.wait(1.2)

        # Keep the conjecture visible, but replace the example.
        self.play(
            FadeOut(VGroup(positive_tag, x_equals_4, chain_positive)),
            run_time=0.7,
        )

        negative_tag = Text("Deuxième test : un nombre négatif", font_size=30)
        negative_tag.next_to(section, DOWN, buff=0.45)
        x_equals_minus_4 = MathTex(r"x=-4").scale(1.15).shift(UP * 1.0)
        chain_negative = VGroup(
            MathTex(r"\sqrt{x^2}"),
            MathTex("="),
            MathTex(r"\sqrt{(-4)^2}"),
            MathTex("="),
            MathTex(r"\sqrt{16}"),
            MathTex("="),
            MathTex("4"),
        ).arrange(RIGHT, buff=0.18)
        chain_negative.scale(1.15)
        chain_negative.shift(DOWN * 0.1)

        comparison = MathTex(r"4\neq -4").scale(1.25)
        comparison.next_to(conjecture_box, DOWN, buff=0.50)
        counterexample = Text("Contre-exemple", font_size=28, color=ACCENT)
        counterexample.next_to(comparison, LEFT, buff=0.35)

        with self.narration(
            f"Mais une conjecture doit être testée. Prenons maintenant {x_spoken} égal à moins quatre. "
            "Son carré vaut encore seize. La racine carrée de seize vaut quatre, et non moins quatre. "
            "Nous venons de trouver un contre-exemple. La règle proposée n'est donc pas vraie pour tous les réels."
        ):
            self.play(FadeIn(negative_tag), Write(x_equals_minus_4), run_time=1.0)
            self.play(Write(chain_negative[0]), run_time=0.55)
            for symbol in chain_negative[1:]:
                self.play(Write(symbol), run_time=0.42)
            self.play(Write(comparison), FadeIn(counterexample), run_time=0.9)
            self.play(
                conjecture.animate.set_color(DARK_SOFT),
                conjecture_label.animate.set_color(DARK_SOFT),
                conjecture_box.animate.set_stroke(DARK_SOFT),
                run_time=0.6,
            )
            strike = Line(
                conjecture_box.get_left() + LEFT * 0.05,
                conjecture_box.get_right() + RIGHT * 0.05,
                color=DARK_SOFT,
                stroke_width=4,
            )
            self.play(Create(strike), run_time=0.5)
            self.wait(1.2)

        self.fade_stage()

        # ------------------------------------------------------------------
        # ACT 2 — Make the reasoning method explicit
        # ------------------------------------------------------------------
        section = self.heading("2. Ce que fait un mathématicien")
        flow = VGroup(
            self.label_box("1. Observer", 2.45),
            self.label_box("2. Conjecturer", 2.75),
            self.label_box("3. Tester", 2.30),
            self.label_box("4. Corriger", 2.45),
        ).arrange(RIGHT, buff=0.38)
        flow.shift(UP * 0.5)

        arrows = VGroup(
            *[
                Arrow(
                    flow[i].get_right(),
                    flow[i + 1].get_left(),
                    buff=0.12,
                    stroke_width=2.5,
                    max_tip_length_to_length_ratio=0.16,
                    color=ACCENT,
                )
                for i in range(3)
            ]
        )

        explanations = VGroup(
            Text("Un exemple positif fonctionne.", font_size=27),
            Text("On propose une règle générale.", font_size=27),
            Text("Un nombre négatif la contredit.", font_size=27),
            Text("On cherche l'énoncé exact.", font_size=27),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        explanations.next_to(flow, DOWN, buff=0.85)

        with self.narration(
            "Ce petit échec est utile. En mathématiques, un exemple peut suggérer une conjecture, "
            "mais il ne suffit pas à la démontrer. Nous testons d'autres cas. "
            "Un seul contre-exemple suffit à réfuter une affirmation universelle. "
            "Notre objectif est maintenant de comprendre ce qui manque à la règle."
        ):
            self.play(Write(section), run_time=0.8)
            for i, box in enumerate(flow):
                self.play(FadeIn(box, shift=RIGHT * 0.15), run_time=0.65)
                if i < len(arrows):
                    self.play(GrowArrow(arrows[i]), run_time=0.4)
            self.play(
                LaggedStart(
                    *[FadeIn(line, shift=UP * 0.1) for line in explanations],
                    lag_ratio=0.2,
                ),
                run_time=1.8,
            )
            self.wait(1.0)

        self.fade_stage()

        # ------------------------------------------------------------------
        # ACT 3 — Equation versus square-root function
        # ------------------------------------------------------------------
        section = self.heading("3. Une équation n'est pas une fonction")
        divider = Line(UP * 2.45, DOWN * 2.75, color=SOFT, stroke_width=2)

        left_title = Text("Résoudre une équation", font_size=31, weight=BOLD)
        left_title.move_to(LEFT * 3.55 + UP * 1.85)
        right_title = Text("Évaluer une fonction", font_size=31, weight=BOLD)
        right_title.move_to(RIGHT * 3.55 + UP * 1.85)

        equation = MathTex(r"u^2=16").scale(1.35).move_to(LEFT * 3.55 + UP * 0.55)
        equation_question = Text(
            "Quels nombres ont un carré égal à 16 ?",
            font_size=25,
        ).next_to(equation, DOWN, buff=0.42)
        equation_solutions = MathTex(r"u=-4\quad\text{ou}\quad u=4").scale(1.15)
        equation_solutions.move_to(LEFT * 3.55 + DOWN * 1.25)

        root_expression = MathTex(r"\sqrt{16}").scale(1.45)
        root_expression.move_to(RIGHT * 3.55 + UP * 0.55)
        root_question = Text(
            "Une entrée doit avoir une seule sortie.",
            font_size=25,
        ).next_to(root_expression, DOWN, buff=0.42)
        root_answer = MathTex(r"\sqrt{16}=4").scale(1.25)
        root_answer.move_to(RIGHT * 3.55 + DOWN * 1.25)
        principal_note = Text(
            "La racine carrée désigne la valeur non négative.",
            font_size=23,
            color=ACCENT,
        ).next_to(root_answer, DOWN, buff=0.45)

        with self.narration(
            "Il faut maintenant distinguer deux questions. "
            "Résoudre l'équation u au carré égale seize signifie chercher toutes les valeurs possibles. "
            "Il y en a deux : moins quatre et quatre."
        ):
            self.play(Write(section), Create(divider), run_time=1.0)
            self.play(Write(left_title), run_time=0.7)
            self.play(Write(equation), FadeIn(equation_question), run_time=0.9)
            self.play(Write(equation_solutions), run_time=1.0)
            self.wait(0.8)

        with self.narration(
            "En revanche, le symbole racine carrée représente une fonction. "
            "Une fonction doit associer une seule sortie à chaque entrée. "
            "Par définition, la racine carrée choisit la solution non négative. "
            "Ainsi, la racine carrée de seize vaut quatre, sans signe plus ou moins."
        ):
            self.play(Write(right_title), run_time=0.7)
            self.play(Write(root_expression), FadeIn(root_question), run_time=0.9)
            self.play(Write(root_answer), run_time=0.9)
            self.play(FadeIn(principal_note, shift=UP * 0.1), run_time=0.7)
            self.wait(1.2)

        self.fade_stage()

        # ------------------------------------------------------------------
        # ACT 4 — Squaring loses the sign
        # ------------------------------------------------------------------
        section = self.heading("4. Mettre au carré fait disparaître le signe")

        input_left = VGroup(
            MathTex("-4").scale(1.25),
            MathTex("4").scale(1.25),
        ).arrange(DOWN, buff=0.75)
        input_left.move_to(LEFT * 4.6 + UP * 0.55)

        machine_box = RoundedRectangle(
            corner_radius=0.18,
            width=3.0,
            height=1.55,
            stroke_color=ACCENT,
            stroke_width=3,
            fill_color=ACCENT,
            fill_opacity=0.08,
        )
        machine_box.move_to(UP * 0.55)
        machine_formula = MathTex(r"x\longmapsto x^2").scale(1.1)
        machine_formula.move_to(machine_box)
        machine = VGroup(machine_box, machine_formula)

        output = MathTex("16").scale(1.4).move_to(RIGHT * 4.55 + UP * 0.55)
        arrows_to_machine = VGroup(
            Arrow(input_left[0].get_right(), machine_box.get_left(), buff=0.18, color=ACCENT),
            Arrow(input_left[1].get_right(), machine_box.get_left(), buff=0.18, color=ACCENT),
        )
        arrow_to_output = Arrow(
            machine_box.get_right(), output.get_left(), buff=0.18, color=ACCENT
        )

        first_record = MathTex(r"-4,\ 4\ \longmapsto\ 16").scale(1.0)
        first_record.move_to(LEFT * 2.3 + DOWN * 1.25)
        second_record = MathTex(r"-2,\ 2\ \longmapsto\ 4").scale(1.0)
        second_record.move_to(RIGHT * 2.3 + DOWN * 1.25)

        lost_sign = Text("Le résultat ne contient plus le signe d'origine.", font_size=29)
        lost_sign.to_edge(DOWN, buff=0.65)

        with self.narration(
            "Pourquoi les deux signes se confondent-ils ? Regardons l'opération qui consiste à mettre au carré. "
            "Moins quatre et quatre produisent tous les deux seize."
        ):
            self.play(Write(section), run_time=0.8)
            self.play(FadeIn(machine), run_time=0.8)
            self.play(FadeIn(input_left), run_time=0.7)
            self.play(*[GrowArrow(a) for a in arrows_to_machine], run_time=0.8)
            self.play(GrowArrow(arrow_to_output), FadeIn(output), run_time=0.8)
            self.play(Write(first_record), run_time=0.8)
            self.wait(0.7)

        new_inputs = VGroup(
            MathTex("-2").scale(1.25),
            MathTex("2").scale(1.25),
        ).arrange(DOWN, buff=0.75)
        new_inputs.move_to(input_left)
        new_output = MathTex("4").scale(1.4).move_to(output)

        with self.narration(
            "Essayons une autre paire. Moins deux et deux produisent tous les deux quatre. "
            "Après l'opération, le signe du nombre d'origine a disparu. "
            "Le carré conserve la grandeur, mais il ne permet plus de savoir de quel côté de zéro se trouvait le nombre."
        ):
            self.play(
                TransformMatchingTex(input_left, new_inputs),
                TransformMatchingTex(output, new_output),
                run_time=1.0,
            )
            self.play(Write(second_record), run_time=0.8)
            self.play(FadeIn(lost_sign, shift=UP * 0.1), run_time=0.8)
            self.wait(1.0)

        self.fade_stage()

        # ------------------------------------------------------------------
        # ACT 5 — Absolute value as distance from zero
        # ------------------------------------------------------------------
        section = self.heading("5. La valeur absolue mesure une distance")
        number_line = NumberLine(
            x_range=[-5, 5, 1],
            length=10,
            include_numbers=True,
            font_size=24,
            color=BLACK,
        ).shift(UP * 0.65)

        zero_point = number_line.n2p(0)
        minus_four_point = number_line.n2p(-4)
        plus_four_point = number_line.n2p(4)
        dot_minus = Dot(minus_four_point, radius=0.09, color=ACCENT)
        dot_plus = Dot(plus_four_point, radius=0.09, color=ACCENT)
        dot_zero = Dot(zero_point, radius=0.075, color=BLACK)

        distance_left = DoubleArrow(
            minus_four_point + UP * 0.45,
            zero_point + UP * 0.45,
            buff=0.02,
            color=ACCENT,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.08,
        )
        distance_right = DoubleArrow(
            zero_point + UP * 0.45,
            plus_four_point + UP * 0.45,
            buff=0.02,
            color=ACCENT,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.08,
        )
        label_left = MathTex("4").next_to(distance_left, UP, buff=0.10)
        label_right = MathTex("4").next_to(distance_right, UP, buff=0.10)

        abs_examples = VGroup(
            MathTex(r"|-4|=4"),
            MathTex(r"|4|=4"),
        ).arrange(RIGHT, buff=1.2)
        abs_examples.scale(1.15)
        abs_examples.shift(DOWN * 1.35)

        distance_definition = VGroup(
            MathTex(r"|x|"),
            Text("= distance entre", font_size=29),
            MathTex("x"),
            Text("et", font_size=29),
            MathTex("0"),
        ).arrange(RIGHT, buff=0.16)
        distance_definition.to_edge(DOWN, buff=0.45)
        definition_box = SurroundingRectangle(
            distance_definition,
            color=ACCENT,
            buff=0.22,
            stroke_width=2.5,
            corner_radius=0.12,
        )

        with self.narration(
            "Ce que le carré conserve, ce n'est pas le signe, mais la grandeur du nombre. "
            "Sur une droite numérique, moins quatre et quatre sont tous les deux à une distance quatre de zéro. "
            "La valeur absolue d'un nombre est précisément sa distance à zéro."
        ):
            self.play(Write(section), Create(number_line), run_time=1.2)
            self.play(FadeIn(dot_minus), FadeIn(dot_plus), FadeIn(dot_zero), run_time=0.6)
            self.play(GrowArrow(distance_left), FadeIn(label_left), run_time=0.8)
            self.play(GrowArrow(distance_right), FadeIn(label_right), run_time=0.8)
            self.play(Write(abs_examples[0]), run_time=0.8)
            self.play(Write(abs_examples[1]), run_time=0.8)
            self.play(Write(distance_definition), Create(definition_box), run_time=1.2)
            self.wait(1.1)

        self.fade_stage()

        # ------------------------------------------------------------------
        # ACT 6 — Build the absolute-value function graph progressively
        # ------------------------------------------------------------------
        section = self.heading("6. La fonction valeur absolue")
        axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-1, 5, 1],
            x_length=7.4,
            y_length=4.44,
            axis_config={
                "color": BLACK,
                "stroke_width": 2,
                "include_tip": True,
            },
            tips=True,
        ).shift(LEFT * 2.85 + DOWN * 0.35)
        axes_labels = MathTex("y").next_to(axes.y_axis.get_end(), UR, buff=0.1)

        positive_branch = axes.plot(
            lambda t: t,
            x_range=[0, 4.5],
            color=ACCENT,
            stroke_width=4,
        )
        negative_original = axes.plot(
            lambda t: t,
            x_range=[-1, 0],
            color=DARK_SOFT,
            stroke_width=3,
        )
        negative_extension = axes.plot(
            lambda t: t,
            x_range=[-4.5, -1],
            color=DARK_SOFT,
            stroke_width=3,
        )
        negative_folded = axes.plot(
            lambda t: -t,
            x_range=[-4.5, 0],
            color=ACCENT,
            stroke_width=4,
        )

        positive_formula = MathTex(r"|x|=x\quad\text{si }x\geq 0").scale(0.95)
        positive_formula.to_corner(UR, buff=0.55).shift(DOWN * 0.65)
        negative_formula = MathTex(r"|x|=-x\quad\text{si }x<0").scale(0.95)
        negative_formula.next_to(positive_formula, DOWN, aligned_edge=RIGHT, buff=0.32)

        graph_title = MathTex(r"y=|x|").scale(1.15)
        graph_title.next_to(axes, UP, buff=0.18).align_to(axes, LEFT)

        with self.narration(
            "Construisons maintenant la fonction valeur absolue. "
            "Pour un nombre positif ou nul, la distance à zéro est le nombre lui-même. "
            "La partie droite du graphique est donc la droite y égale x."
        ):
            self.play(Write(section), Create(axes), FadeIn(axes_labels), run_time=1.2)
            self.play(Write(graph_title), run_time=0.6)
            self.play(Create(positive_branch), run_time=1.3)
            self.play(Write(positive_formula), run_time=1.0)
            self.wait(0.8)

        with self.narration(
            "Pour un nombre négatif, le point situé sous l'axe doit être replié au-dessus de l'axe. "
            "Par exemple, moins trois devient une distance trois. "
            "Algébriquement, quand x est négatif, moins x est positif. "
            "La partie gauche est donc donnée par y égale moins x."
        ):
            self.play(Create(negative_original), run_time=0.6)
            self.play(Create(negative_extension), run_time=1.0)
            old_negative = VGroup(negative_original, negative_extension)
            self.play(Transform(old_negative, negative_folded), run_time=1.6)
            self.play(Write(negative_formula), run_time=1.0)
            self.wait(1.1)

        piecewise = MathTex(
            r"|x|=\begin{cases}"
            r"x,&x\geq 0,\\"
            r"-x,&x<0."
            r"\end{cases}"
        ).scale(1.08)
        piecewise.move_to(RIGHT * 3.55 + DOWN * 1.55)
        piecewise_box = SurroundingRectangle(
            piecewise,
            color=ACCENT,
            buff=0.22,
            stroke_width=2.5,
            corner_radius=0.12,
        )
        domain_image = VGroup(
            MathTex(r"\mathrm{Dom}=\mathbb{R}"),
            MathTex(r"\mathrm{Im}=[0,+\infty["),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        domain_image.scale(0.92)
        domain_image.next_to(piecewise_box, DOWN, aligned_edge=LEFT, buff=0.35)

        with self.narration(
            "Nous pouvons maintenant réunir les deux morceaux dans une définition par cas. "
            "La valeur absolue laisse les nombres positifs inchangés, et change le signe des nombres négatifs. "
            "Elle accepte tous les nombres réels, mais ses valeurs sont toujours positives ou nulles. "
            "Son graphique forme un V, entièrement situé au-dessus de l'axe horizontal."
        ):
            self.play(
                FadeOut(VGroup(positive_formula, negative_formula)),
                run_time=0.6,
            )
            self.play(Write(piecewise), Create(piecewise_box), run_time=1.3)
            self.play(FadeIn(domain_image, shift=UP * 0.1), run_time=0.8)
            self.wait(1.2)

        self.fade_stage()

        # ------------------------------------------------------------------
        # ACT 7 — Formal proof by cases
        # ------------------------------------------------------------------
        section = self.heading("7. Corrigeons la conjecture")
        original_wrong = MathTex(r"\sqrt{x^2}=x").scale(1.15)
        original_wrong.shift(UP * 1.8)
        wrong_line = Line(
            original_wrong.get_left() + LEFT * 0.08,
            original_wrong.get_right() + RIGHT * 0.08,
            color=DARK_SOFT,
            stroke_width=4,
        )

        left_case_box = RoundedRectangle(
            corner_radius=0.16,
            width=5.6,
            height=3.0,
            stroke_color=ACCENT,
            stroke_width=2.5,
            fill_color=ACCENT,
            fill_opacity=0.05,
        ).move_to(LEFT * 3.05 + DOWN * 0.35)
        right_case_box = left_case_box.copy().move_to(RIGHT * 3.05 + DOWN * 0.35)

        left_case_title = MathTex(r"\text{Si }x\geq 0").scale(1.1)
        left_case_title.next_to(left_case_box.get_top(), DOWN, buff=0.35)
        left_case_steps = VGroup(
            MathTex(r"\sqrt{x^2}=x"),
            MathTex(r"|x|=x"),
            MathTex(r"\therefore\ \sqrt{x^2}=|x|"),
        ).arrange(DOWN, buff=0.35)
        left_case_steps.scale(0.95)
        left_case_steps.move_to(left_case_box.get_center() + DOWN * 0.25)

        right_case_title = MathTex(r"\text{Si }x<0").scale(1.1)
        right_case_title.next_to(right_case_box.get_top(), DOWN, buff=0.35)
        right_case_steps = VGroup(
            MathTex(r"-x>0"),
            MathTex(r"\sqrt{x^2}=-x"),
            MathTex(r"|x|=-x"),
            MathTex(r"\therefore\ \sqrt{x^2}=|x|"),
        ).arrange(DOWN, buff=0.25)
        right_case_steps.scale(0.9)
        right_case_steps.move_to(right_case_box.get_center() + DOWN * 0.18)

        with self.narration(
            "Nous sommes prêts à corriger la conjecture. "
            "Commençons par le cas où x est positif ou nul. "
            "La racine carrée de x au carré vaut alors x, et la valeur absolue de x vaut aussi x. "
            "Les deux expressions sont donc égales."
        ):
            self.play(Write(section), Write(original_wrong), Create(wrong_line), run_time=1.1)
            self.play(Create(left_case_box), Write(left_case_title), run_time=0.9)
            for step in left_case_steps:
                self.play(Write(step), run_time=0.7)
            self.wait(0.8)

        with self.narration(
            "Considérons maintenant le cas où x est négatif. "
            "Alors moins x est positif. La racine carrée doit produire cette valeur positive, donc elle vaut moins x. "
            "Mais c'est exactement aussi la définition de la valeur absolue dans le cas négatif."
        ):
            self.play(Create(right_case_box), Write(right_case_title), run_time=0.9)
            for step in right_case_steps:
                self.play(Write(step), run_time=0.62)
            self.wait(0.9)

        corrected = MathTex(r"\boxed{\sqrt{x^2}=|x|\quad\text{pour tout }x\in\mathbb{R}}").scale(1.15)
        corrected.to_edge(DOWN, buff=0.38)

        with self.narration(
            "Dans les deux cas, nous obtenons la même conclusion. "
            "Pour tout nombre réel x, la racine carrée de x au carré est égale à la valeur absolue de x. "
            "Ce n'est pas une correction artificielle : la valeur absolue exprime précisément la grandeur non négative qui subsiste après le carré."
        ):
            self.play(Write(corrected), run_time=1.3)
            self.play(Indicate(corrected, color=ACCENT, scale_factor=1.04), run_time=1.0)
            self.wait(1.3)

        self.fade_stage()

        # ------------------------------------------------------------------
        # ACT 8 — A compact conceptual proof
        # ------------------------------------------------------------------
        section = self.heading("8. Une preuve plus condensée")
        fact_one = MathTex(r"|x|\geq 0").scale(1.25).shift(UP * 1.2)
        fact_two = MathTex(r"(|x|)^2=x^2").scale(1.25)
        fact_two.next_to(fact_one, DOWN, buff=0.65)
        conclusion = MathTex(r"\sqrt{x^2}=|x|").scale(1.55)
        conclusion.next_to(fact_two, DOWN, buff=0.85)
        conclusion_box = SurroundingRectangle(
            conclusion,
            color=ACCENT,
            buff=0.25,
            stroke_width=3,
            corner_radius=0.12,
        )

        with self.narration(
            "On peut maintenant résumer la démonstration en une seule idée. "
            "La valeur absolue de x est non négative, et son carré vaut x au carré. "
            "Elle est donc, par définition, l'unique racine carrée non négative de x au carré."
        ):
            self.play(Write(section), run_time=0.8)
            self.play(Write(fact_one), run_time=0.8)
            self.play(Write(fact_two), run_time=0.8)
            self.play(Write(conclusion), Create(conclusion_box), run_time=1.2)
            self.wait(1.2)

        self.fade_stage()

        # ------------------------------------------------------------------
        # ACT 9 — Transfer: distance from x to 3
        # ------------------------------------------------------------------
        section = self.heading("9. Une idée qui se généralise")
        generalization = MathTex(r"\sqrt{(x-3)^2}=|x-3|").scale(1.35)
        generalization.shift(UP * 1.7)

        line = NumberLine(
            x_range=[-1, 7, 1],
            length=10,
            include_numbers=True,
            font_size=24,
            color=BLACK,
        ).shift(DOWN * 0.05)
        point_three = Dot(line.n2p(3), radius=0.09, color=BLACK)
        point_one = Dot(line.n2p(1), radius=0.09, color=ACCENT)
        point_five = Dot(line.n2p(5), radius=0.09, color=ACCENT)

        arrow_one = DoubleArrow(
            line.n2p(1) + UP * 0.42,
            line.n2p(3) + UP * 0.42,
            buff=0.02,
            color=ACCENT,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.12,
        )
        arrow_five = DoubleArrow(
            line.n2p(3) + UP * 0.42,
            line.n2p(5) + UP * 0.42,
            buff=0.02,
            color=ACCENT,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.12,
        )
        two_left = MathTex("2").next_to(arrow_one, UP, buff=0.10)
        two_right = MathTex("2").next_to(arrow_five, UP, buff=0.10)

        interpretation = VGroup(
            MathTex(r"|x-3|"),
            Text("= distance entre", font_size=28),
            MathTex("x"),
            Text("et", font_size=28),
            MathTex("3"),
        ).arrange(RIGHT, buff=0.15)
        interpretation.to_edge(DOWN, buff=0.42)
        interpretation_frame = SurroundingRectangle(
            interpretation,
            color=ACCENT,
            buff=0.22,
            stroke_width=2.5,
            corner_radius=0.12,
        )

        with self.narration(
            "La même idée fonctionne avec une expression plus compliquée. "
            "La racine carrée de x moins trois, le tout au carré, vaut la valeur absolue de x moins trois. "
            "Cette valeur absolue représente la distance entre x et trois."
        ):
            self.play(Write(section), Write(generalization), run_time=1.2)
            self.play(Create(line), FadeIn(point_three), run_time=1.0)
            self.play(FadeIn(point_one), GrowArrow(arrow_one), FadeIn(two_left), run_time=0.9)
            self.play(FadeIn(point_five), GrowArrow(arrow_five), FadeIn(two_right), run_time=0.9)
            self.play(Write(interpretation), Create(interpretation_frame), run_time=1.1)
            self.wait(1.0)

        example_one = MathTex(
            r"x=1:\quad \sqrt{(1-3)^2}=2=|1-3|"
        ).scale(0.98)
        example_five = MathTex(
            r"x=5:\quad \sqrt{(5-3)^2}=2=|5-3|"
        ).scale(0.98)
        with self.narration(
            "Par exemple, un et cinq sont chacun à une distance deux de trois. "
            "L'expression x moins trois peut être négative ou positive, mais son carré puis sa racine carrée renvoient toujours cette distance non négative."
        ):
            self.play(FadeOut(VGroup(interpretation, interpretation_frame)), run_time=0.5)
            self.play(Write(example_one), run_time=1.0)
            self.play(Write(example_five), run_time=1.0)
            self.wait(1.2)

        self.fade_stage()

        # ------------------------------------------------------------------
        # ACT 10 — Final distinctions and summary
        # ------------------------------------------------------------------
        section = self.heading("À retenir")

        card_1_formula = MathTex(r"\sqrt{16}=4").scale(1.0)
        card_1_text = Text("Une valeur : la racine non négative", font_size=23)
        card_1 = VGroup(card_1_formula, card_1_text).arrange(DOWN, buff=0.28)

        card_2_formula = MathTex(r"u^2=16\Rightarrow u=\pm4").scale(1.0)
        card_2_text = Text("Une équation : toutes les solutions", font_size=23)
        card_2 = VGroup(card_2_formula, card_2_text).arrange(DOWN, buff=0.28)

        card_3_formula = MathTex(r"\sqrt{x^2}=|x|").scale(1.05)
        card_3_text = Text("La grandeur non négative de x", font_size=23)
        card_3 = VGroup(card_3_formula, card_3_text).arrange(DOWN, buff=0.28)

        cards = VGroup(card_1, card_2, card_3).arrange(DOWN, buff=0.52)
        cards.shift(UP * 0.15)
        card_frames = VGroup(
            *[
                SurroundingRectangle(
                    card,
                    color=ACCENT,
                    buff=0.2,
                    stroke_width=2.2,
                    corner_radius=0.12,
                )
                for card in cards
            ]
        )

        reasoning_footer = Text(
            "Observer → conjecturer → tester → corriger → démontrer",
            font_size=27,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.45)

        with self.narration(
            "Retenons trois distinctions. "
            "La racine carrée de seize vaut quatre. "
            "L'équation u au carré égale seize possède deux solutions, plus ou moins quatre. "
            "Et pour tout réel x, la racine carrée de x au carré vaut la valeur absolue de x."
        ):
            self.play(Write(section), run_time=0.8)
            for card, frame in zip(cards, card_frames):
                self.play(FadeIn(card, shift=UP * 0.12), Create(frame), run_time=0.9)
                self.wait(0.35)

        with self.narration(
            "Mais il faut aussi retenir la démarche. "
            "Nous avons observé un exemple, formulé une conjecture, trouvé un contre-exemple, introduit une nouvelle fonction, puis démontré l'énoncé corrigé. "
            "C'est exactement ainsi que le raisonnement mathématique transforme une intuition en connaissance fiable."
        ):
            self.play(FadeIn(reasoning_footer, shift=UP * 0.1), run_time=0.9)
            self.play(Indicate(cards[2], color=ACCENT, scale_factor=1.03), run_time=0.9)
            self.wait(2.0)

        self.wait(1.0)
