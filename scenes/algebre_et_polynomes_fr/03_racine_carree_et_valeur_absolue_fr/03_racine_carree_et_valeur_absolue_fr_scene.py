from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService

from tools.tts import VOICE_ID, char, ssml, strip_ssml


config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
SOFT = GREY_B
DARK_SOFT = GREY_D
SAFE_WIDTH = 12.4


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class RacineCarreeValeurAbsolueFR(VoiceoverScene):
    """Explain why sqrt(x^2) equals |x| rather than x in general.

    The scene stays focused on one question. It tests a tempting formula,
    distinguishes an equation from the principal square root, shows where the
    sign is lost, and finishes with a proof by cases.
    """

    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            print("[voiceover] MANIM_DISABLE_VOICEOVER set. Rendering without narration.")
            return

        key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
        region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
        if not key or not region:
            print("[voiceover] Missing Azure Speech credentials. Rendering without narration.")
            return

        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", key)
        os.environ.setdefault("AZURE_SERVICE_REGION", region)
        os.environ.setdefault("SPEECH_KEY", key)
        os.environ.setdefault("SPEECH_REGION", region)
        try:
            self.set_speech_service(AzureService(voice=VOICE_ID))
        except Exception as exc:
            print(f"[voiceover] Azure setup failed: {exc}. Rendering without narration.")
            return
        self._voiceover_enabled = True

    @contextmanager
    def narration(self, spoken: str):
        """Create a voiceover context with an explicit silent fallback."""
        if self._voiceover_enabled:
            with self.voiceover(
                text=ssml(spoken),
                subcaption=strip_ssml(spoken),
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def clear_stage(self, run_time: float = 0.65) -> None:
        """Clear the stage between major parts."""
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=run_time)

    @staticmethod
    def heading(text: str) -> Text:
        return Text(text, font_size=42, weight=BOLD).to_edge(UP, buff=0.30)

    @staticmethod
    def fit_width(mobject: Mobject, max_width: float = SAFE_WIDTH) -> Mobject:
        """Scale down a wide object without enlarging smaller ones."""
        if mobject.width > max_width:
            mobject.scale_to_fit_width(max_width)
        return mobject

    @staticmethod
    def card(
        width: float,
        height: float,
        *,
        fill_opacity: float = 0.04,
        stroke_color=ACCENT,
    ) -> RoundedRectangle:
        return RoundedRectangle(
            corner_radius=0.15,
            width=width,
            height=height,
            stroke_color=stroke_color,
            stroke_width=2.4,
            fill_color=stroke_color,
            fill_opacity=fill_opacity,
        )

    @staticmethod
    def summary_row(formula: str, explanation: str) -> VGroup:
        formula_mob = MathTex(formula).scale(1.02)
        explanation_mob = Text(explanation, font_size=25)
        content = VGroup(formula_mob, explanation_mob).arrange(
            RIGHT,
            buff=0.65,
        )
        content[1].align_to(content[0], DOWN)

        box = RoundedRectangle(
            corner_radius=0.14,
            width=11.3,
            height=1.05,
            stroke_color=ACCENT,
            stroke_width=2.2,
            fill_color=ACCENT,
            fill_opacity=0.04,
        )
        content.move_to(box)
        return VGroup(box, content)

    def construct(self) -> None:
        self._setup_voiceover()
        x_spoken = char("x")

        # ------------------------------------------------------------------
        # PART 0 — Central question
        # ------------------------------------------------------------------
        title = Text(
            "Racine carrée et valeur absolue",
            font_size=48,
            weight=BOLD,
        ).to_edge(UP, buff=0.42)
        question = MathTex(r"\sqrt{x^2}\stackrel{?}{=}x").scale(1.78)
        question.shift(UP * 0.42)
        prompt = Text(
            "Cette égalité est-elle toujours vraie ?",
            font_size=31,
        ).next_to(question, DOWN, buff=0.48)
        clue = Text(
            "Testons aussi un nombre négatif.",
            font_size=27,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.78)

        with self.narration(
            f"La racine carrée de {x_spoken} au carré est-elle toujours égale à {x_spoken} ?"
        ):
            self.play(Write(title), run_time=0.9)
            self.play(Write(question), run_time=1.0)
            self.play(FadeIn(prompt, shift=UP * 0.10), run_time=0.7)
            self.wait(0.8)

        with self.narration(
            "La formule paraît naturelle. Mais pour la tester sérieusement, il faut aussi essayer un nombre négatif."
        ):
            self.play(FadeIn(clue, shift=UP * 0.10), run_time=0.7)
            self.wait(1.0)

        self.clear_stage()

        # ------------------------------------------------------------------
        # PART 1 — Test the conjecture
        # ------------------------------------------------------------------
        section = self.heading("Tester la formule")
        case_label = Text("Premier essai : x = 4", font_size=29, color=ACCENT)
        case_label.next_to(section, DOWN, buff=0.46)

        calculation = MathTex(r"\sqrt{4^2}=\sqrt{16}=4").scale(1.38)
        calculation.move_to(UP * 0.65)

        observation = Text(
            "Ici, le résultat est bien égal à l'entrée.",
            font_size=28,
        ).move_to(DOWN * 0.35)

        conjecture = MathTex(r"\sqrt{x^2}=x").scale(1.28)
        conjecture_box = self.card(4.8, 1.08)
        conjecture_group = VGroup(conjecture_box, conjecture)
        conjecture.move_to(conjecture_box)
        conjecture_group.move_to(DOWN * 1.82)
        conjecture_tag = Text("Conjecture", font_size=24, color=ACCENT)
        conjecture_tag.next_to(conjecture_group, UP, buff=0.14)

        with self.narration(
            f"Avec {x_spoken} égal à quatre, quatre au carré donne seize, puis la racine carrée de seize donne quatre."
        ):
            self.play(Write(section), FadeIn(case_label), run_time=0.8)
            self.play(Write(calculation), run_time=1.0)
            self.play(FadeIn(observation, shift=UP * 0.08), run_time=0.6)
            self.wait(0.8)

        with self.narration("Cet exemple suggère la formule affichée."):
            self.play(
                FadeIn(conjecture_tag),
                Create(conjecture_box),
                Write(conjecture),
                run_time=0.9,
            )
            self.wait(0.8)

        negative_label = Text("Deuxième essai : x = -4", font_size=29, color=ACCENT)
        negative_label.move_to(case_label)
        negative_calculation = MathTex(
            r"\sqrt{(-4)^2}=\sqrt{16}=4"
        ).scale(1.30)
        negative_calculation.move_to(calculation)
        contradiction = MathTex(
            r"\underbrace{4}_{\text{résultat}}\neq"
            r"\underbrace{-4}_{\text{entrée}}"
        ).scale(1.08)
        contradiction.move_to(DOWN * 0.30)

        with self.narration(
            f"Avec {x_spoken} égal à moins quatre, le carré vaut encore seize, et la racine carrée vaut encore quatre."
        ):
            self.play(
                Transform(case_label, negative_label),
                FadeOut(observation),
                TransformMatchingTex(calculation, negative_calculation),
                run_time=1.0,
            )
            self.wait(0.8)

        with self.narration(
            "Mais le résultat quatre n'est pas égal à l'entrée moins quatre. C'est un contre-exemple."
        ):
            self.play(Write(contradiction), run_time=0.9)
            self.play(
                conjecture.animate.set_color(DARK_SOFT),
                conjecture_tag.animate.set_color(DARK_SOFT),
                conjecture_box.animate.set_stroke(DARK_SOFT),
                run_time=0.45,
            )
            strike = Line(
                conjecture_group.get_left() + LEFT * 0.06,
                conjecture_group.get_right() + RIGHT * 0.06,
                color=DARK_SOFT,
                stroke_width=4,
            )
            self.play(Create(strike), run_time=0.5)
            self.wait(1.2)

        self.clear_stage()

        # ------------------------------------------------------------------
        # PART 2 — Equation versus principal square root
        # ------------------------------------------------------------------
        section = self.heading("Deux questions différentes")

        left_box = self.card(5.65, 4.35)
        right_box = self.card(5.65, 4.35)
        boxes = VGroup(left_box, right_box).arrange(RIGHT, buff=0.55)
        boxes.shift(DOWN * 0.35)

        equation_title = Text(
            "Résoudre une équation",
            font_size=29,
            weight=BOLD,
        ).next_to(left_box.get_top(), DOWN, buff=0.35)
        equation_question = Text(
            "Quels nombres ont pour carré 16 ?",
            font_size=25,
        ).next_to(equation_title, DOWN, buff=0.38)
        equation = MathTex(r"u^2=16").scale(1.36)
        equation.next_to(equation_question, DOWN, buff=0.50)
        equation_solutions = MathTex(r"u=-4\quad\text{ou}\quad u=4").scale(1.07)
        equation_solutions.next_to(equation, DOWN, buff=0.52)
        equation_note = Text(
            "On cherche toutes les solutions.",
            font_size=24,
            color=ACCENT,
        ).next_to(equation_solutions, DOWN, buff=0.48)

        root_title = Text(
            "Évaluer une racine carrée",
            font_size=29,
            weight=BOLD,
        ).next_to(right_box.get_top(), DOWN, buff=0.35)
        root_question = Text(
            "Quelle valeur désigne le symbole ?",
            font_size=25,
        ).next_to(root_title, DOWN, buff=0.38)
        root_expression = MathTex(r"\sqrt{16}").scale(1.48)
        root_expression.next_to(root_question, DOWN, buff=0.45)
        root_answer = MathTex(r"\sqrt{16}=4").scale(1.18)
        root_answer.next_to(root_expression, DOWN, buff=0.43)
        root_note = Text(
            "Par définition : la valeur non négative.",
            font_size=23,
            color=ACCENT,
        ).next_to(root_answer, DOWN, buff=0.46)

        with self.narration(
            "Résoudre u au carré égale seize, c'est chercher tous les nombres dont le carré vaut seize."
        ):
            self.play(Write(section), Create(left_box), run_time=0.8)
            self.play(Write(equation_title), FadeIn(equation_question), run_time=0.7)
            self.play(Write(equation), run_time=0.7)
            self.wait(0.6)

        with self.narration("Il y en a deux : moins quatre et quatre."):
            self.play(Write(equation_solutions), run_time=0.8)
            self.play(FadeIn(equation_note, shift=UP * 0.08), run_time=0.6)
            self.wait(0.8)

        with self.narration(
            "Le symbole racine carrée pose une autre question : il doit désigner une seule valeur."
        ):
            self.play(Create(right_box), run_time=0.6)
            self.play(Write(root_title), FadeIn(root_question), run_time=0.7)
            self.play(Write(root_expression), run_time=0.7)
            self.wait(0.6)

        with self.narration(
            "Par définition, racine carrée de seize désigne l'unique nombre non négatif dont le carré vaut seize. Donc elle vaut quatre."
        ):
            self.play(Write(root_answer), run_time=0.8)
            self.play(FadeIn(root_note, shift=UP * 0.08), run_time=0.6)
            self.wait(1.2)

        self.clear_stage()

        # ------------------------------------------------------------------
        # PART 3 — Where the sign is lost, and what absolute value keeps
        # ------------------------------------------------------------------
        section = self.heading("Où le signe disparaît-il ?")

        inputs = VGroup(
            MathTex(r"-4").scale(1.20),
            MathTex(r"4").scale(1.20),
        ).arrange(DOWN, buff=0.82)
        inputs.move_to(LEFT * 5.25 + DOWN * 0.10)

        square_box = self.card(2.6, 2.25, fill_opacity=0.07)
        square_box.move_to(LEFT * 2.25 + DOWN * 0.10)
        square_formula = MathTex(r"x\longmapsto x^2").scale(0.98)
        square_formula.move_to(square_box)

        sixteen = MathTex(r"16").scale(1.35).move_to(RIGHT * 0.35 + DOWN * 0.10)

        root_box = self.card(2.25, 1.55, fill_opacity=0.07)
        root_box.move_to(RIGHT * 2.65 + DOWN * 0.10)
        root_formula = MathTex(r"\sqrt{\phantom{a}}").scale(1.12).move_to(root_box)
        final_four = MathTex(r"4").scale(1.35).move_to(RIGHT * 5.15 + DOWN * 0.10)

        square_ports = [
            square_box.get_left() + UP * 0.55,
            square_box.get_left() + DOWN * 0.55,
        ]
        arrows_in = VGroup(
            Arrow(inputs[0].get_right(), square_ports[0], buff=0.14, color=ACCENT),
            Arrow(inputs[1].get_right(), square_ports[1], buff=0.14, color=ACCENT),
        )
        arrow_to_sixteen = Arrow(
            square_box.get_right(),
            sixteen.get_left(),
            buff=0.16,
            color=ACCENT,
        )
        arrow_to_root = Arrow(
            sixteen.get_right(),
            root_box.get_left(),
            buff=0.16,
            color=ACCENT,
        )
        arrow_to_four = Arrow(
            root_box.get_right(),
            final_four.get_left(),
            buff=0.16,
            color=ACCENT,
        )
        lost_sign = Text(
            "Après le carré, les entrées 4 et -4 sont devenues indiscernables.",
            font_size=27,
        ).to_edge(DOWN, buff=0.60)

        with self.narration(
            "Moins quatre et quatre passent par la même opération : mettre au carré."
        ):
            self.play(Write(section), FadeIn(inputs), run_time=0.8)
            self.play(FadeIn(square_box), Write(square_formula), run_time=0.7)
            self.play(GrowArrow(arrows_in[0]), GrowArrow(arrows_in[1]), run_time=0.8)
            self.wait(0.6)

        with self.narration(
            "Les deux entrées donnent la même sortie, seize. À ce moment, le signe d'origine est perdu."
        ):
            self.play(GrowArrow(arrow_to_sixteen), FadeIn(sixteen), run_time=0.8)
            self.play(FadeIn(lost_sign, shift=UP * 0.08), run_time=0.7)
            self.wait(0.9)

        with self.narration(
            "La racine carrée de seize choisit ensuite la valeur non négative, quatre."
        ):
            self.play(FadeIn(root_box), Write(root_formula), run_time=0.6)
            self.play(GrowArrow(arrow_to_root), run_time=0.5)
            self.play(GrowArrow(arrow_to_four), FadeIn(final_four), run_time=0.7)
            self.wait(1.0)

        machine_group = VGroup(
            inputs,
            square_box,
            square_formula,
            sixteen,
            root_box,
            root_formula,
            final_four,
            arrows_in,
            arrow_to_sixteen,
            arrow_to_root,
            arrow_to_four,
            lost_sign,
        )
        self.play(FadeOut(machine_group), run_time=0.7)

        distance_heading = Text(
            "La valeur absolue conserve la distance à zéro",
            font_size=32,
            weight=BOLD,
        ).next_to(section, DOWN, buff=0.45)
        number_line = NumberLine(
            x_range=[-5, 5, 1],
            length=10.2,
            include_numbers=True,
            font_size=24,
            color=BLACK,
        ).shift(UP * 0.25)
        zero_dot = Dot(number_line.n2p(0), radius=0.07, color=BLACK)
        minus_four_dot = Dot(number_line.n2p(-4), radius=0.09, color=ACCENT)
        plus_four_dot = Dot(number_line.n2p(4), radius=0.09, color=ACCENT)

        left_distance = DoubleArrow(
            number_line.n2p(-4) + UP * 0.50,
            number_line.n2p(0) + UP * 0.50,
            buff=0.02,
            color=ACCENT,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.08,
        )
        right_distance = DoubleArrow(
            number_line.n2p(0) + UP * 0.50,
            number_line.n2p(4) + UP * 0.50,
            buff=0.02,
            color=ACCENT,
            stroke_width=2.5,
            max_tip_length_to_length_ratio=0.08,
        )
        left_label = MathTex(r"4").next_to(left_distance, UP, buff=0.10)
        right_label = MathTex(r"4").next_to(right_distance, UP, buff=0.10)
        examples = MathTex(r"|-4|=4\qquad |4|=4").scale(1.15)
        examples.shift(DOWN * 1.10)
        definition = MathTex(
            r"|x|=\text{la distance entre }x\text{ et }0"
        ).scale(1.02)
        self.fit_width(definition, 10.5)
        definition_box = SurroundingRectangle(
            definition,
            color=ACCENT,
            buff=0.22,
            stroke_width=2.4,
            corner_radius=0.12,
        )
        definition_group = VGroup(definition_box, definition)
        definition_group.to_edge(DOWN, buff=0.38)

        with self.narration(
            "Ce que moins quatre et quatre ont encore en commun, c'est leur distance à zéro."
        ):
            self.play(Write(distance_heading), run_time=0.7)
            self.play(Create(number_line), FadeIn(zero_dot), run_time=0.8)
            self.play(
                FadeIn(minus_four_dot),
                GrowArrow(left_distance),
                FadeIn(left_label),
                run_time=0.8,
            )
            self.play(
                FadeIn(plus_four_dot),
                GrowArrow(right_distance),
                FadeIn(right_label),
                run_time=0.8,
            )
            self.wait(0.8)

        with self.narration(
            "Ils sont tous les deux à distance quatre. La valeur absolue mesure précisément cette distance."
        ):
            self.play(Write(examples), run_time=0.8)
            self.play(Create(definition_box), Write(definition), run_time=0.9)
            self.wait(1.2)

        self.clear_stage()

        # ------------------------------------------------------------------
        # PART 4 — Correct formula and proof by cases
        # ------------------------------------------------------------------
        section = self.heading("Corriger et démontrer la formule")
        principle = Text(
            "Une racine carrée est toujours non négative.",
            font_size=29,
            color=ACCENT,
        ).next_to(section, DOWN, buff=0.42)

        positive_box = self.card(5.65, 3.45)
        negative_box = self.card(5.65, 3.45)
        proof_boxes = VGroup(positive_box, negative_box).arrange(RIGHT, buff=0.55)
        proof_boxes.shift(DOWN * 0.28)

        positive_title = MathTex(r"\text{Cas 1 : }x\geq 0").scale(1.00)
        positive_title.next_to(positive_box.get_top(), DOWN, buff=0.28)
        positive_abs = MathTex(r"|x|=x").scale(1.05)
        positive_abs.next_to(positive_title, DOWN, buff=0.42)
        positive_root = MathTex(r"\sqrt{x^2}=x").scale(1.05)
        positive_root.next_to(positive_abs, DOWN, buff=0.38)
        positive_result = MathTex(r"\therefore\quad \sqrt{x^2}=|x|").scale(1.03)
        positive_result.set_color(ACCENT)
        positive_result.next_to(positive_root, DOWN, buff=0.42)

        negative_title = MathTex(r"\text{Cas 2 : }x<0").scale(1.00)
        negative_title.next_to(negative_box.get_top(), DOWN, buff=0.28)
        negative_positive = MathTex(r"-x>0").scale(1.05)
        negative_positive.next_to(negative_title, DOWN, buff=0.31)
        negative_abs = MathTex(r"|x|=-x").scale(1.05)
        negative_abs.next_to(negative_positive, DOWN, buff=0.27)
        negative_root = MathTex(r"\sqrt{x^2}=-x").scale(1.05)
        negative_root.next_to(negative_abs, DOWN, buff=0.27)
        negative_result = MathTex(r"\therefore\quad \sqrt{x^2}=|x|").scale(1.03)
        negative_result.set_color(ACCENT)
        negative_result.next_to(negative_root, DOWN, buff=0.30)

        conclusion = MathTex(
            r"\boxed{\sqrt{x^2}=|x|\qquad\text{pour tout }x\in\mathbb{R}}"
        ).scale(1.10)
        conclusion.to_edge(DOWN, buff=0.33)

        with self.narration(
            f"Pour démontrer la formule corrigée, séparons les deux signes possibles de {x_spoken}."
        ):
            self.play(Write(section), FadeIn(principle), run_time=0.8)
            self.play(Create(positive_box), Create(negative_box), run_time=0.8)
            self.wait(0.6)

        with self.narration(
            f"Si {x_spoken} est positif ou nul, sa valeur absolue vaut {x_spoken}, et la racine carrée de son carré vaut aussi {x_spoken}."
        ):
            self.play(Write(positive_title), run_time=0.5)
            self.play(Write(positive_abs), run_time=0.6)
            self.play(Write(positive_root), run_time=0.6)
            self.play(Write(positive_result), run_time=0.7)
            self.wait(0.8)

        with self.narration(
            f"Si {x_spoken} est négatif, alors moins {x_spoken} est positif. La valeur absolue vaut moins {x_spoken}, et la racine carrée de {x_spoken} au carré vaut elle aussi moins {x_spoken}."
        ):
            self.play(Write(negative_title), run_time=0.5)
            self.play(Write(negative_positive), run_time=0.5)
            self.play(Write(negative_abs), run_time=0.6)
            self.play(Write(negative_root), run_time=0.6)
            self.play(Write(negative_result), run_time=0.7)
            self.wait(0.9)

        with self.narration(
            f"Dans les deux cas, pour tout réel {x_spoken}, la racine carrée de {x_spoken} au carré vaut la valeur absolue de {x_spoken}."
        ):
            self.play(Write(conclusion), run_time=1.0)
            self.play(
                Indicate(conclusion, color=ACCENT, scale_factor=1.035),
                run_time=0.8,
            )
            self.wait(1.5)

        self.clear_stage()

        # ------------------------------------------------------------------
        # PART 5 — Final stable summary
        # ------------------------------------------------------------------
        section = self.heading("À retenir")
        row_one = self.summary_row(
            r"\sqrt{16}=4",
            "une seule valeur, non négative",
        )
        row_two = self.summary_row(
            r"u^2=16\ \Longleftrightarrow\ u\in\{-4,4\}",
            "toutes les solutions de l'équation",
        )
        row_three = self.summary_row(
            r"\sqrt{x^2}=|x|",
            "la règle correcte pour tout réel x",
        )
        rows = VGroup(row_one, row_two, row_three).arrange(DOWN, buff=0.30)
        rows.shift(DOWN * 0.05)

        footer = Text(
            "Un seul contre-exemple suffit à réfuter une formule universelle.",
            font_size=26,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.34)

        with self.narration(
            "Retenons trois idées. La racine carrée de seize vaut quatre."
        ):
            self.play(Write(section), run_time=0.7)
            self.play(FadeIn(row_one, shift=UP * 0.10), run_time=0.8)
            self.wait(0.7)

        with self.narration(
            "L'équation u au carré égale seize a deux solutions : moins quatre et quatre."
        ):
            self.play(FadeIn(row_two, shift=UP * 0.10), run_time=0.8)
            self.wait(0.7)

        with self.narration(
            f"Et pour tout réel {x_spoken}, la racine carrée de {x_spoken} au carré vaut la valeur absolue de {x_spoken}."
        ):
            self.play(FadeIn(row_three, shift=UP * 0.10), run_time=0.8)
            self.play(Indicate(row_three, color=ACCENT, scale_factor=1.02), run_time=0.7)
            self.wait(0.9)

        with self.narration(
            "La méthode compte aussi : un exemple suggère une règle, mais un contre-exemple suffit à la réfuter."
        ):
            self.play(FadeIn(footer, shift=UP * 0.08), run_time=0.7)
            self.wait(2.0)

        self.wait(1.0)
