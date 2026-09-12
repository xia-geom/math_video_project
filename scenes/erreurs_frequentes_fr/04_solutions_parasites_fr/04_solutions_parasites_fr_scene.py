from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    LEFT,
    ORIGIN,
    RED_D,
    RIGHT,
    UP,
    WHITE,
    Circle,
    Create,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    NumberLine,
    RoundedRectangle,
    SurroundingRectangle,
    Text,
    VGroup,
    Write,
    config,
)
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService

from tools.tts import PLUS, X, azure_service_kwargs, ssml, strip_ssml

config.background_color = WHITE
Text.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


ACCENT = BLUE_D
GOOD = GREEN_D
ERROR = RED_D


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class CarreEtSolutionsParasitesFR(VoiceoverScene):

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
            self.set_speech_service(AzureService(**azure_service_kwargs()))
        except Exception as exc:
            print(f"[voiceover] Azure setup failed: {exc}. Rendering without narration.")
            return
        self._voiceover_enabled = True

    @contextmanager
    def voiceover(self, text: str, subcaption: str | None = None, **kwargs):
        if self._voiceover_enabled:
            with super().voiceover(text=text, subcaption=subcaption, **kwargs) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()
    """Pourquoi élever au carré peut produire une solution parasite.

    Objectif pédagogique
    --------------------
    Faire comprendre que l'étape « élever au carré » est correcte, mais pas
    toujours réversible. Le carré oublie le signe : deux nombres opposés ont
    le même carré. Les valeurs obtenues après cette étape sont donc des
    candidates, qui doivent encore satisfaire les conditions de signe et
    l'équation initiale.
    """

    def construct(self) -> None:
        self._setup_voiceover()

        self._opening_question()
        self._tempting_calculation()
        self._test_candidates()
        self._why_the_extra_value_appears()
        self._recover_the_hidden_condition()
        self._safe_method_and_summary()

        self.wait(1.2)

    # ------------------------------------------------------------------
    # Acte 1 — La question centrale
    # ------------------------------------------------------------------
    def _opening_question(self) -> None:
        eyebrow = Text("ERREUR FRÉQUENTE", font_size=26, color=ACCENT)
        title = Text(
            "Une étape correcte peut-elle créer une fausse solution ?",
            font_size=44,
            weight="SEMIBOLD",
        )
        title.scale_to_fit_width(12.2)
        header = VGroup(eyebrow, title).arrange(DOWN, buff=0.22).to_edge(UP, buff=0.45)

        equation = MathTex(r"\sqrt{x+2}=x").scale(1.55)
        equation.move_to(ORIGIN + UP * 0.25)

        prompt = Text(
            "Résolvons cette équation sans perdre l'information cachée.",
            font_size=31,
        )
        prompt.next_to(equation, DOWN, buff=0.75)

        spoken = ssml(
            f"Une étape de calcul parfaitement correcte peut-elle pourtant faire "
            f"apparaître une fausse solution ? Regardons l'équation : racine de "
            f"{X} {PLUS} deux égale {X}."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(eyebrow, shift=DOWN * 0.15), run_time=0.7)
            self.play(Write(title), run_time=1.2)
            self.play(Write(equation), run_time=0.9)
            self.play(FadeIn(prompt, shift=UP * 0.15), run_time=0.7)
            self.wait(0.8)

        self.play(FadeOut(prompt), run_time=0.45)
        self.play(
            header.animate.scale(0.78).to_edge(UP, buff=0.28),
            equation.animate.move_to(UP * 1.7),
            run_time=0.8,
        )

        self.header = header
        self.original_equation = equation

    # ------------------------------------------------------------------
    # Acte 2 — Le calcul tentant
    # ------------------------------------------------------------------
    def _tempting_calculation(self) -> None:
        square_note = Text(
            "On élève les deux membres au carré",
            font_size=28,
            color=ACCENT,
        )
        square_note.next_to(self.original_equation, DOWN, buff=0.42)

        step_1 = MathTex(r"x+2=x^2").scale(1.18)
        step_2 = MathTex(r"x^2-x-2=0").scale(1.18)
        step_3 = MathTex(r"(x-2)(x+1)=0").scale(1.18)
        candidates = MathTex(r"x=2", r"\quad\text{ou}\quad", r"x=-1").scale(1.18)

        derivation = VGroup(step_1, step_2, step_3, candidates).arrange(
            DOWN, buff=0.36
        )
        derivation.next_to(square_note, DOWN, buff=0.42)

        spoken = ssml(
            f"La première idée semble naturelle. On élève les deux membres au carré. "
            f"La racine disparaît, et l'on obtient {X} {PLUS} deux égale {X} au carré."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(square_note, shift=UP * 0.12), run_time=0.6)
            self.play(Write(step_1), run_time=0.85)
            self.wait(0.65)

        spoken = ssml(
            f"On ramène tout du même côté, puis on factorise. Le calcul donne deux "
            f"valeurs candidates : {X} égale deux, ou {X} égale moins un."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(step_2), run_time=0.75)
            self.wait(0.35)
            self.play(Write(step_3), run_time=0.8)
            self.wait(0.45)
            self.play(Write(candidates), run_time=0.8)
            self.wait(0.9)

        question_box = SurroundingRectangle(candidates, color=ACCENT, buff=0.18)
        question = Text("Deux solutions ?", font_size=28, color=ACCENT)
        question.next_to(question_box, RIGHT, buff=0.35)

        spoken = ssml("Mais avons-nous réellement trouvé deux solutions ?")
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(question_box), FadeIn(question, shift=LEFT * 0.15), run_time=0.65)
            self.wait(0.8)

        self.derivation_group = VGroup(
            square_note,
            derivation,
            question_box,
            question,
        )

    # ------------------------------------------------------------------
    # Acte 3 — Vérifier les candidates
    # ------------------------------------------------------------------
    def _candidate_card(
        self,
        candidate_tex: str,
        substitution_tex: str,
        verdict: str,
        verdict_color,
    ) -> VGroup:
        box = RoundedRectangle(
            width=5.45,
            height=2.75,
            corner_radius=0.18,
            color=verdict_color,
            stroke_width=2.5,
            fill_color=verdict_color,
            fill_opacity=0.06,
        )
        candidate = MathTex(candidate_tex).scale(1.08)
        substitution = MathTex(substitution_tex).scale(0.95)
        verdict_text = Text(verdict, font_size=28, color=verdict_color, weight="SEMIBOLD")
        content = VGroup(candidate, substitution, verdict_text).arrange(DOWN, buff=0.36)
        content.move_to(box)
        return VGroup(box, content)

    def _test_candidates(self) -> None:
        self.play(
            FadeOut(self.derivation_group),
            self.original_equation.animate.move_to(UP * 2.0),
            run_time=0.75,
        )

        instruction = Text(
            "On revient toujours à l'équation initiale.",
            font_size=31,
            color=ACCENT,
        )
        instruction.next_to(self.original_equation, DOWN, buff=0.38)

        good_card = self._candidate_card(
            r"x=2",
            r"\sqrt{2+2}=2\quad\Longrightarrow\quad 2=2",
            "Solution valide",
            GOOD,
        )
        good_card.move_to(LEFT * 3.05 + DOWN * 0.8)

        bad_card = self._candidate_card(
            r"x=-1",
            r"\sqrt{-1+2}=-1\quad\Longrightarrow\quad 1\neq-1",
            "Solution parasite",
            ERROR,
        )
        bad_card.move_to(RIGHT * 3.05 + DOWN * 0.8)

        spoken = ssml(
            f"Testons d'abord {X} égale deux dans l'équation de départ. "
            f"Racine de quatre vaut deux. Cette valeur fonctionne."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(instruction, shift=UP * 0.12), run_time=0.55)
            self.play(FadeIn(good_card[0]), run_time=0.45)
            self.play(Write(good_card[1][0]), run_time=0.5)
            self.play(Write(good_card[1][1]), run_time=0.85)
            self.play(FadeIn(good_card[1][2], shift=UP * 0.1), run_time=0.55)
            self.wait(0.8)

        spoken = ssml(
            f"Testons maintenant {X} égale moins un. Le membre de gauche vaut un, "
            f"mais le membre de droite vaut moins un. Cette valeur ne résout pas "
            f"l'équation initiale. C'est une solution parasite."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(bad_card[0]), run_time=0.45)
            self.play(Write(bad_card[1][0]), run_time=0.5)
            self.play(Write(bad_card[1][1]), run_time=0.9)
            self.play(FadeIn(bad_card[1][2], shift=UP * 0.1), run_time=0.55)
            self.wait(1.0)

        mystery = Text(
            "Le calcul était correct. Alors, d'où vient −1 ?",
            font_size=32,
            weight="SEMIBOLD",
        )
        mystery.to_edge(DOWN, buff=0.42)

        spoken = ssml(
            "Pour comprendre l'erreur, il ne suffit pas de dire : vérifiez à la fin. "
            "Il faut voir quelle information l'opération carré a effacée."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(mystery), run_time=0.9)
            self.wait(1.0)

        self.test_group = VGroup(instruction, good_card, bad_card, mystery)

    # ------------------------------------------------------------------
    # Acte 4 — Le carré plie la droite numérique
    # ------------------------------------------------------------------
    def _why_the_extra_value_appears(self) -> None:
        self.play(
            FadeOut(self.test_group),
            FadeOut(self.original_equation),
            run_time=0.75,
        )

        section_title = Text(
            "Le carré oublie le signe",
            font_size=38,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        section_title.next_to(self.header, DOWN, buff=0.28)

        input_label = Text("entrée  t", font_size=27)
        input_line = NumberLine(
            x_range=[-3, 3, 1],
            length=8.0,
            include_numbers=True,
            color=BLACK,
            stroke_width=2.5,
        )
        input_group = VGroup(input_label, input_line).arrange(DOWN, buff=0.16)
        input_group.move_to(UP * 0.75)

        output_label = Text("sortie  t²", font_size=27)
        output_line = NumberLine(
            x_range=[0, 5, 1],
            length=6.5,
            include_numbers=True,
            color=BLACK,
            stroke_width=2.5,
        )
        output_group = VGroup(output_label, output_line).arrange(DOWN, buff=0.16)
        output_group.move_to(DOWN * 1.65)

        minus_two = input_line.n2p(-2)
        plus_two = input_line.n2p(2)
        four = output_line.n2p(4)

        minus_dot = MathTex(r"\bullet", color=ERROR).scale(1.35).move_to(minus_two)
        plus_dot = MathTex(r"\bullet", color=ACCENT).scale(1.35).move_to(plus_two)
        output_dot = MathTex(r"\bullet", color=GOOD).scale(1.35).move_to(four)

        minus_label = MathTex(r"-2").next_to(minus_dot, UP, buff=0.2)
        plus_label = MathTex(r"2").next_to(plus_dot, UP, buff=0.2)
        four_label = MathTex(r"4").next_to(output_dot, DOWN, buff=0.22)

        arrow_left = Line(
            minus_dot.get_bottom(),
            output_dot.get_top(),
            color=ERROR,
            stroke_width=3,
        ).add_tip(tip_length=0.18)
        arrow_right = Line(
            plus_dot.get_bottom(),
            output_dot.get_top(),
            color=ACCENT,
            stroke_width=3,
        ).add_tip(tip_length=0.18)

        rule = MathTex(r"t\longmapsto t^2").scale(1.0)
        rule.move_to(RIGHT * 4.65 + DOWN * 0.3)

        spoken = ssml(
            "Regardons l'opération carré comme une machine. Prenons d'abord moins deux. "
            "Son carré vaut quatre."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(section_title, shift=DOWN * 0.12), run_time=0.6)
            self.play(FadeIn(input_group), FadeIn(output_group), FadeIn(rule), run_time=0.8)
            self.play(FadeIn(minus_dot), Write(minus_label), run_time=0.55)
            self.play(Create(arrow_left), run_time=0.8)
            self.play(FadeIn(output_dot), Write(four_label), run_time=0.55)
            self.wait(0.75)

        spoken = ssml(
            "Prenons maintenant deux. Son carré vaut également quatre. Deux entrées "
            "différentes viennent donc se confondre à la même sortie."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(plus_dot), Write(plus_label), run_time=0.55)
            self.play(Create(arrow_right), run_time=0.8)
            self.wait(1.1)

        fold_statement = MathTex(r"(-2)^2=2^2=4").scale(1.2)
        fold_statement.to_edge(DOWN, buff=0.35)
        fold_box = SurroundingRectangle(fold_statement, color=ACCENT, buff=0.16)

        spoken = ssml(
            "Le carré conserve la distance à zéro, mais il oublie de quel côté du zéro "
            "se trouvait le nombre. C'est exactement l'information perdue dans notre équation."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(fold_statement), FadeIn(fold_box), run_time=0.85)
            self.wait(1.0)

        mapping_group = VGroup(
            section_title,
            input_group,
            output_group,
            minus_dot,
            plus_dot,
            output_dot,
            minus_label,
            plus_label,
            four_label,
            arrow_left,
            arrow_right,
            rule,
            fold_statement,
            fold_box,
        )

        self.play(FadeOut(mapping_group), run_time=0.75)

        forward = MathTex(r"A=B", r"\Longrightarrow", r"A^2=B^2").scale(1.35)
        forward[1].set_color(ACCENT)
        forward.move_to(UP * 1.55)

        reverse_question = MathTex(r"A^2=B^2", r"\Longrightarrow", r"A=B").scale(1.35)
        reverse_question[1].set_color(ERROR)
        reverse_question.move_to(UP * 0.25)
        cross = Text("✗", font_size=52, color=ERROR, weight="BOLD")
        cross.next_to(reverse_question, RIGHT, buff=0.35)

        correct_reverse = MathTex(
            r"A^2=B^2",
            r"\Longleftrightarrow",
            r"A=B\ \text{ou}\ A=-B",
            r"\qquad(A,B\in\mathbb{R})",
        ).scale(1.12)
        correct_reverse[1].set_color(ACCENT)
        correct_reverse.move_to(DOWN * 1.35)

        spoken = ssml(
            "Si deux nombres sont égaux, leurs carrés sont forcément égaux. Cette "
            "direction est toujours correcte."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(forward), run_time=0.9)
            self.wait(0.8)

        spoken = ssml(
            "Mais l'égalité des carrés ne permet pas de conclure que les nombres étaient "
            "égaux. Ils pouvaient aussi être opposés."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(reverse_question), run_time=0.85)
            self.play(FadeIn(cross, scale=0.7), run_time=0.4)
            self.wait(0.65)
            self.play(Write(correct_reverse), run_time=1.0)
            self.wait(1.1)

        implication_caption = Text(
            "Élever au carré donne une implication, pas toujours une équivalence.",
            font_size=31,
            color=ACCENT,
        )
        implication_caption.to_edge(DOWN, buff=0.42)

        spoken = ssml(
            "Autrement dit, élever au carré peut élargir l'ensemble des possibilités. "
            "Les nouvelles valeurs sont des candidates, pas encore des solutions."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(implication_caption, shift=UP * 0.12), run_time=0.65)
            self.wait(1.1)

        self.logic_group = VGroup(
            forward,
            reverse_question,
            cross,
            correct_reverse,
            implication_caption,
        )

    # ------------------------------------------------------------------
    # Acte 5 — Retrouver l'information de signe
    # ------------------------------------------------------------------
    def _recover_the_hidden_condition(self) -> None:
        self.play(FadeOut(self.logic_group), run_time=0.7)

        equation = MathTex(r"\sqrt{x+2}", "=", "x").scale(1.5)
        equation.move_to(UP * 1.85)

        left_nonnegative = MathTex(r"\sqrt{x+2}\ge 0").scale(1.05)
        left_nonnegative.set_color(ACCENT)
        left_nonnegative.next_to(equation[0], DOWN, buff=0.42)

        therefore = MathTex(r"\Longrightarrow\quad x\ge 0").scale(1.2)
        therefore.next_to(left_nonnegative, DOWN, buff=0.48)

        number_line = NumberLine(
            x_range=[-3, 4, 1],
            length=8.5,
            include_numbers=True,
            color=BLACK,
            stroke_width=2.5,
        )
        number_line.move_to(DOWN * 1.15)
        zero_point = number_line.n2p(0)
        right_end = number_line.n2p(4)
        allowed_segment = Line(zero_point, right_end, color=ACCENT, stroke_width=8)
        zero_dot = MathTex(r"\bullet", color=ACCENT).scale(1.25).move_to(zero_point)
        allowed_label = Text("valeurs possibles", font_size=27, color=ACCENT)
        allowed_label.next_to(allowed_segment, DOWN, buff=0.38)

        minus_one_marker = MathTex(r"-1", color=ERROR).scale(1.0)
        minus_one_marker.next_to(number_line.n2p(-1), UP, buff=0.22)
        minus_one_cross = Text("✗", font_size=39, color=ERROR, weight="BOLD")
        minus_one_cross.next_to(minus_one_marker, UP, buff=0.08)

        spoken = ssml(
            f"Revenons à l'équation avant de calculer. Une racine carrée est toujours "
            f"positive ou nulle. Puisqu'elle est égale à {X}, le nombre {X} doit lui aussi "
            f"être positif ou nul."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(equation), run_time=0.8)
            self.play(Write(left_nonnegative), run_time=0.75)
            self.wait(0.55)
            self.play(Write(therefore), run_time=0.7)
            self.wait(0.75)

        spoken = ssml(
            f"Cette condition de signe était déjà présente dans l'équation initiale, "
            f"même si elle n'était pas écrite. Elle élimine immédiatement {X} égale moins un."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(number_line), run_time=0.6)
            self.play(FadeIn(allowed_segment), FadeIn(zero_dot), run_time=0.65)
            self.play(FadeIn(allowed_label, shift=UP * 0.1), run_time=0.45)
            self.play(Write(minus_one_marker), FadeIn(minus_one_cross, scale=0.7), run_time=0.6)
            self.wait(1.0)

        condition_box = SurroundingRectangle(
            VGroup(left_nonnegative, therefore),
            color=ACCENT,
            buff=0.22,
        )
        condition_caption = Text(
            "L'équation contient une information de signe.",
            font_size=30,
            color=ACCENT,
        )
        condition_caption.to_edge(DOWN, buff=0.38)

        spoken = ssml(
            "La valeur parasite est apparue parce que le carré a effacé cette information "
            "de signe. Le problème n'était donc pas le calcul. Le problème était de traiter "
            "une implication comme si elle était réversible."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(condition_box), run_time=0.5)
            self.play(FadeIn(condition_caption, shift=UP * 0.12), run_time=0.55)
            self.wait(1.2)

        self.sign_group = VGroup(
            equation,
            left_nonnegative,
            therefore,
            number_line,
            allowed_segment,
            zero_dot,
            allowed_label,
            minus_one_marker,
            minus_one_cross,
            condition_box,
            condition_caption,
        )

    # ------------------------------------------------------------------
    # Acte 6 — Méthode sûre et conclusion
    # ------------------------------------------------------------------
    def _safe_method_and_summary(self) -> None:
        self.play(FadeOut(self.sign_group), run_time=0.75)

        title = Text(
            "Une méthode sûre",
            font_size=38,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        title.next_to(self.header, DOWN, buff=0.3)

        def numbered_row(number: str, sentence: str) -> VGroup:
            circle = Circle(
                radius=0.25,
                color=ACCENT,
                fill_color=ACCENT,
                fill_opacity=1.0,
                stroke_width=0,
            )
            digit = Text(number, font_size=25, color=WHITE, weight="BOLD")
            digit.move_to(circle)
            badge = VGroup(circle, digit)
            text = Text(sentence, font_size=30)
            return VGroup(badge, text).arrange(RIGHT, buff=0.4)

        rows = VGroup(
            numbered_row(
                "1",
                "Repérer les conditions de domaine et de signe.",
            ),
            numbered_row(
                "2",
                "Après une étape non réversible, parler de candidates.",
            ),
            numbered_row(
                "3",
                "Vérifier chaque candidate dans l'équation initiale.",
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        rows.move_to(UP * 0.25)

        spoken = ssml(
            "Voici la méthode générale. Premièrement, repérer les conditions de domaine "
            "et de signe avant de transformer l'équation."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.55)
            self.play(FadeIn(rows[0][0]), Write(rows[0][1]), run_time=0.8)
            self.wait(0.7)

        spoken = ssml(
            "Deuxièmement, lorsqu'une étape n'est pas réversible, les valeurs obtenues "
            "sont seulement des candidates."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(rows[1][0]), Write(rows[1][1]), run_time=0.85)
            self.wait(0.7)

        spoken = ssml(
            "Troisièmement, vérifier chaque candidate dans l'équation initiale, là où "
            "toute l'information est encore présente."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(rows[2][0]), Write(rows[2][1]), run_time=0.85)
            self.wait(0.9)

        self.play(FadeOut(rows), FadeOut(title), run_time=0.65)

        original = MathTex(r"\sqrt{x+2}=x").scale(1.25)
        arrow_candidates = MathTex(r"\Longrightarrow").scale(1.2).set_color(ACCENT)
        candidates = MathTex(r"x\in\{-1,2\}").scale(1.18)
        arrow_check = MathTex(r"\xrightarrow{\text{vérification}}").scale(1.0).set_color(ACCENT)
        solution = MathTex(r"S=\{2\}").scale(1.28).set_color(GOOD)

        flow = VGroup(original, arrow_candidates, candidates, arrow_check, solution).arrange(
            RIGHT, buff=0.4
        )
        flow.scale_to_fit_width(11.8)
        flow.move_to(UP * 0.55)

        note = Text(
            "Le carré n'est pas faux : il oublie simplement le signe.",
            font_size=34,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        note.move_to(DOWN * 1.15)

        conclusion = Text(
            "Une transformation peut être correcte sans être réversible.",
            font_size=32,
        )
        conclusion.move_to(DOWN * 2.0)

        spoken = ssml(
            f"Dans notre exemple, le carré produit deux candidates, moins un et deux. "
            f"La vérification conserve seulement deux. La solution de l'équation est donc "
            f"{X} égale deux."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(original), run_time=0.55)
            self.play(Write(arrow_candidates), Write(candidates), run_time=0.75)
            self.wait(0.55)
            self.play(Write(arrow_check), run_time=0.65)
            self.play(Write(solution), run_time=0.6)
            self.wait(0.85)

        spoken = ssml(
            "Retenez surtout ceci : élever au carré n'est pas une mauvaise opération. "
            "Elle oublie simplement le signe. Une transformation peut donc être correcte "
            "sans être réversible."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(note, shift=UP * 0.12), run_time=0.65)
            self.wait(0.7)
            self.play(FadeIn(conclusion, shift=UP * 0.12), run_time=0.65)
            self.wait(1.35)
