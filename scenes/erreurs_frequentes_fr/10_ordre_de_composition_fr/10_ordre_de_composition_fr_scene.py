from __future__ import annotations

from manim import (
    BLACK,
    BLUE_D,
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    GREEN_D,
    GrowArrow,
    LEFT,
    MathTex,
    RED_D,
    RIGHT,
    RoundedRectangle,
    SurroundingRectangle,
    Text,
    Transform,
    UP,
    VGroup,
    WHITE,
    Write,
    Arrow,
    config,
)
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService

from tools.tts import VOICE_ID, X, char, ssml, strip_ssml


config.background_color = WHITE
Text.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


ACCENT = BLUE_D
GOOD = GREEN_D
ERROR = RED_D


class CompositionNonCommutativeFR(VoiceoverScene):
    """Pourquoi l'ordre d'une composition de fonctions compte-t-il ?

    Objectif pédagogique
    --------------------
    Faire comprendre que, contrairement à l'addition ou à la multiplication
    des nombres, la composition de fonctions n'est pas commutative en général.
    L'élève doit aussi distinguer :

    - l'égalité de deux fonctions composées ;
    - l'égalité de leurs valeurs pour une seule entrée ;
    - les cas particuliers où deux fonctions commutent réellement.

    Progression
    -----------
    1. Question centrale : deux machines, deux ordres possibles.
    2. Contre-exemple concret avec l'entrée 2.
    3. Lecture correcte de (f o g)(x) : la fonction de droite agit d'abord.
    4. Comparaison algébrique pour une entrée générale x.
    5. Même résultat en x = 0, mais fonctions toujours différentes.
    6. Exemple spécial où deux fonctions commutent.
    7. Synthèse : règle générale, critère d'égalité et piège à éviter.
    """

    def construct(self) -> None:
        self.set_speech_service(AzureService(voice=VOICE_ID))

        self._opening_question()
        self._two_orders_with_two()
        self._read_composition_notation()
        self._general_comparison()
        self._one_coincidence_is_not_equality()
        self._special_commuting_case()
        self._summary()

        self.wait(1.2)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _machine(
        self,
        name_tex: str,
        rule_tex: str,
        color,
        width: float = 2.35,
        height: float = 1.55,
    ) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.18,
            color=color,
            stroke_width=2.7,
            fill_color=color,
            fill_opacity=0.06,
        )
        name = MathTex(name_tex).scale(0.88)
        rule = MathTex(rule_tex).scale(1.02)
        content = VGroup(name, rule).arrange(DOWN, buff=0.22)
        content.move_to(box)
        return VGroup(box, content)

    def _value_box(self, value_tex: str, color=BLACK) -> VGroup:
        box = RoundedRectangle(
            width=1.55,
            height=1.02,
            corner_radius=0.14,
            color=color,
            stroke_width=2.3,
            fill_color=color,
            fill_opacity=0.035,
        )
        value = MathTex(value_tex).scale(1.08)
        value.move_to(box)
        return VGroup(box, value)

    def _pipeline(
        self,
        input_tex: str,
        first_machine: VGroup,
        middle_tex: str,
        second_machine: VGroup,
        output_tex: str,
    ) -> VGroup:
        input_box = self._value_box(input_tex, ACCENT)
        middle_box = self._value_box(middle_tex, BLACK)
        output_box = self._value_box(output_tex, GOOD)

        arrow_1 = Arrow(
            LEFT,
            RIGHT,
            buff=0,
            color=BLACK,
            stroke_width=2.4,
            max_tip_length_to_length_ratio=0.18,
        ).set_width(0.72)
        arrow_2 = arrow_1.copy()
        arrow_3 = arrow_1.copy()
        arrow_4 = arrow_1.copy()

        group = VGroup(
            input_box,
            arrow_1,
            first_machine,
            arrow_2,
            middle_box,
            arrow_3,
            second_machine,
            arrow_4,
            output_box,
        ).arrange(RIGHT, buff=0.18)
        group.scale_to_fit_width(12.2)
        return group

    # ------------------------------------------------------------------
    # Acte 1 — Question centrale
    # ------------------------------------------------------------------
    def _opening_question(self) -> None:
        eyebrow = Text("ERREUR CONCEPTUELLE", font_size=26, color=ACCENT)
        title = Text(
            "Peut-on changer l'ordre de deux fonctions ?",
            font_size=45,
            weight="SEMIBOLD",
        )
        title.scale_to_fit_width(11.8)
        header = VGroup(eyebrow, title).arrange(DOWN, buff=0.22)
        header.to_edge(UP, buff=0.42)

        f_machine = self._machine(r"f", r"x\mapsto x+1", ACCENT)
        g_machine = self._machine(r"g", r"x\mapsto x^2", GOOD)
        machines = VGroup(f_machine, g_machine).arrange(RIGHT, buff=1.15)
        machines.move_to(UP * 0.25)

        order_1 = MathTex(r"f\circ g").scale(1.45)
        question_mark = MathTex(r"\overset{?}{=}").scale(1.35).set_color(ERROR)
        order_2 = MathTex(r"g\circ f").scale(1.45)
        question = VGroup(order_1, question_mark, order_2).arrange(RIGHT, buff=0.38)
        question.next_to(machines, DOWN, buff=0.72)

        f_spoken = char("f")
        g_spoken = char("g")
        spoken = ssml(
            f"Voici deux fonctions. La fonction {f_spoken} ajoute un. "
            f"La fonction {g_spoken} élève au carré. Si nous appliquons les deux, "
            "peut-on changer leur ordre comme on change l'ordre d'une addition ou d'une multiplication ?"
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(eyebrow, shift=DOWN * 0.12), run_time=0.6)
            self.play(Write(title), run_time=1.0)
            self.play(FadeIn(f_machine, shift=RIGHT * 0.18), run_time=0.65)
            self.wait(0.35)
            self.play(FadeIn(g_machine, shift=LEFT * 0.18), run_time=0.65)
            self.wait(0.65)
            self.play(Write(order_1), run_time=0.45)
            self.play(FadeIn(question_mark, scale=0.8), run_time=0.4)
            self.play(Write(order_2), run_time=0.45)
            self.wait(1.0)

        self.play(
            header.animate.scale(0.76).to_edge(UP, buff=0.25),
            FadeOut(machines),
            question.animate.scale(0.82).next_to(header, DOWN, buff=0.3),
            run_time=0.85,
        )

        self.header = header
        self.composition_question = question

    # ------------------------------------------------------------------
    # Acte 2 — Deux ordres, deux résultats
    # ------------------------------------------------------------------
    def _two_orders_with_two(self) -> None:
        first_title = MathTex(r"(f\circ g)(2)").scale(1.12).set_color(ACCENT)
        first_title.next_to(self.composition_question, DOWN, buff=0.42)

        pipeline_fg = self._pipeline(
            r"2",
            self._machine(r"g", r"x\mapsto x^2", GOOD),
            r"4",
            self._machine(r"f", r"x\mapsto x+1", ACCENT),
            r"5",
        )
        pipeline_fg.next_to(first_title, DOWN, buff=0.3)

        g_spoken = char("g")
        f_spoken = char("f")
        spoken = ssml(
            f"Commençons par {f_spoken} rond {g_spoken}, appliqué à deux. "
            f"La fonction {g_spoken} agit d'abord : deux au carré donne quatre. "
            f"Ensuite, {f_spoken} ajoute un. Nous obtenons cinq."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(first_title), run_time=0.5)
            for mob in pipeline_fg:
                if isinstance(mob, Arrow):
                    self.play(GrowArrow(mob), run_time=0.34)
                else:
                    self.play(FadeIn(mob, shift=RIGHT * 0.08), run_time=0.4)
                self.wait(0.12)
            self.wait(0.8)

        first_result = MathTex(r"(f\circ g)(2)=5").scale(1.08).set_color(GOOD)
        first_result.next_to(pipeline_fg, DOWN, buff=0.25)
        self.play(Write(first_result), run_time=0.6)
        self.wait(0.65)

        self.play(
            FadeOut(first_title),
            FadeOut(pipeline_fg),
            first_result.animate.scale(0.9).to_edge(LEFT, buff=0.75).shift(DOWN * 2.55),
            run_time=0.7,
        )

        second_title = MathTex(r"(g\circ f)(2)").scale(1.12).set_color(ACCENT)
        second_title.next_to(self.composition_question, DOWN, buff=0.42)

        pipeline_gf = self._pipeline(
            r"2",
            self._machine(r"f", r"x\mapsto x+1", ACCENT),
            r"3",
            self._machine(r"g", r"x\mapsto x^2", GOOD),
            r"9",
        )
        pipeline_gf.next_to(second_title, DOWN, buff=0.3)

        spoken = ssml(
            f"Changeons maintenant l'ordre. Dans {g_spoken} rond {f_spoken}, "
            f"la fonction {f_spoken} agit d'abord : deux devient trois. "
            f"Puis {g_spoken} élève trois au carré. Nous obtenons neuf."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(second_title), run_time=0.5)
            for mob in pipeline_gf:
                if isinstance(mob, Arrow):
                    self.play(GrowArrow(mob), run_time=0.34)
                else:
                    self.play(FadeIn(mob, shift=RIGHT * 0.08), run_time=0.4)
                self.wait(0.12)
            self.wait(0.8)

        second_result = MathTex(r"(g\circ f)(2)=9").scale(1.08).set_color(ERROR)
        second_result.next_to(pipeline_gf, DOWN, buff=0.25)
        self.play(Write(second_result), run_time=0.6)
        self.wait(0.7)

        comparison = VGroup(first_result, second_result)
        first_result.generate_target()
        second_result.generate_target()
        comparison_target = VGroup(first_result.target, second_result.target).arrange(RIGHT, buff=1.0)
        comparison_target.move_to(DOWN * 2.55)

        not_equal = MathTex(r"5\neq 9").scale(1.25).set_color(ERROR)
        not_equal.next_to(comparison_target, UP, buff=0.25)

        spoken = ssml(
            "Avec la même entrée, le premier ordre donne cinq et le second donne neuf. "
            "Un seul contre-exemple suffit donc à montrer que les deux fonctions composées ne sont pas égales."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(
                FadeOut(second_title),
                FadeOut(pipeline_gf),
                first_result.animate.move_to(first_result.target),
                second_result.animate.move_to(second_result.target),
                run_time=0.7,
            )
            self.play(Write(not_equal), run_time=0.55)
            self.wait(1.0)

        verdict = MathTex(r"f\circ g\neq g\circ f").scale(1.2)
        verdict_box = SurroundingRectangle(verdict, color=ERROR, buff=0.18)
        verdict_group = VGroup(verdict, verdict_box).move_to(DOWN * 0.95)

        self.play(
            FadeOut(first_result),
            FadeOut(second_result),
            Transform(not_equal, verdict),
            Create(verdict_box),
            run_time=0.75,
        )
        self.wait(0.7)

        self.not_equal_display = VGroup(not_equal, verdict_box)

    # ------------------------------------------------------------------
    # Acte 3 — Lire la notation de droite à gauche
    # ------------------------------------------------------------------
    def _read_composition_notation(self) -> None:
        self.play(FadeOut(self.not_equal_display), run_time=0.45)

        formula = MathTex(
            r"(f\circ g)(x)=",
            r"f\bigl(",
            r"g(x)",
            r"\bigr)",
        ).scale(1.45)
        formula.move_to(UP * 0.55)

        g_first = SurroundingRectangle(
            formula[2],
            color=GOOD,
            buff=0.12,
        )
        f_second = SurroundingRectangle(
            VGroup(formula[1], formula[2], formula[3]),
            color=ACCENT,
            buff=0.16,
        )

        right_first = Text(
            "La fonction écrite à droite agit d'abord.",
            font_size=34,
            color=ERROR,
            weight="SEMIBOLD",
        )
        right_first.next_to(formula, DOWN, buff=0.62)

        spoken = ssml(
            f"La notation se lit avec attention. {char('f')} rond {char('g')} de {X} signifie "
            f"{char('f')} de {char('g')} de {X}. On calcule donc d'abord la fonction écrite à droite, "
            "puis on applique celle de gauche au résultat obtenu."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(formula), run_time=0.85)
            self.wait(0.5)
            self.play(Create(g_first), run_time=0.55)
            self.wait(0.7)
            self.play(Transform(g_first, f_second), run_time=0.65)
            self.wait(0.6)
            self.play(FadeIn(right_first, shift=UP * 0.12), run_time=0.55)
            self.wait(1.0)

        self.play(
            FadeOut(g_first),
            FadeOut(right_first),
            formula.animate.scale(0.82).next_to(self.composition_question, DOWN, buff=0.48),
            run_time=0.7,
        )
        self.composition_definition = formula

    # ------------------------------------------------------------------
    # Acte 4 — Comparaison algébrique générale
    # ------------------------------------------------------------------
    def _general_comparison(self) -> None:
        left_title = MathTex(r"f\circ g").scale(1.08).set_color(ACCENT)
        right_title = MathTex(r"g\circ f").scale(1.08).set_color(GOOD)

        left_steps = VGroup(
            MathTex(r"(f\circ g)(x)=f(g(x))"),
            MathTex(r"=f(x^2)"),
            MathTex(r"=x^2+1"),
        ).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        left_steps.scale(0.93)

        right_steps = VGroup(
            MathTex(r"(g\circ f)(x)=g(f(x))"),
            MathTex(r"=g(x+1)"),
            MathTex(r"=(x+1)^2"),
            MathTex(r"=x^2+2x+1"),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        right_steps.scale(0.9)

        left_card = RoundedRectangle(
            width=5.35,
            height=3.45,
            corner_radius=0.18,
            color=ACCENT,
            stroke_width=2.4,
            fill_color=ACCENT,
            fill_opacity=0.04,
        )
        right_card = RoundedRectangle(
            width=5.35,
            height=3.45,
            corner_radius=0.18,
            color=GOOD,
            stroke_width=2.4,
            fill_color=GOOD,
            fill_opacity=0.04,
        )

        left_content = VGroup(left_title, left_steps).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        right_content = VGroup(right_title, right_steps).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        left_content.move_to(left_card)
        right_content.move_to(right_card)

        cards = VGroup(VGroup(left_card, left_content), VGroup(right_card, right_content))
        cards.arrange(RIGHT, buff=0.55)
        cards.next_to(self.composition_definition, DOWN, buff=0.42)

        spoken = ssml(
            "Calculons maintenant avec une entrée générale. Dans le premier ordre, nous élevons au carré, "
            "puis nous ajoutons un : le résultat est x au carré plus un. Dans l'autre ordre, nous ajoutons "
            "un avant d'élever au carré. Le terme deux x apparaît. Les deux règles obtenues sont différentes."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Create(left_card), FadeIn(left_title), run_time=0.55)
            for step in left_steps:
                self.play(Write(step), run_time=0.48)
                self.wait(0.22)
            self.wait(0.55)
            self.play(Create(right_card), FadeIn(right_title), run_time=0.55)
            for step in right_steps:
                self.play(Write(step), run_time=0.48)
                self.wait(0.22)
            self.wait(0.8)

        difference = MathTex(
            r"(g\circ f)(x)-(f\circ g)(x)=2x"
        ).scale(1.02)
        difference.set_color(ERROR)
        difference.to_edge(DOWN, buff=0.38)
        difference_box = SurroundingRectangle(difference, color=ERROR, buff=0.15)

        self.play(Write(difference), Create(difference_box), run_time=0.8)
        self.wait(0.9)

        self.general_group = VGroup(cards, difference, difference_box)

    # ------------------------------------------------------------------
    # Acte 5 — Une coïncidence ponctuelle ne suffit pas
    # ------------------------------------------------------------------
    def _one_coincidence_is_not_equality(self) -> None:
        self.play(FadeOut(self.general_group), run_time=0.65)

        question = Text(
            "Mais les deux ordres peuvent-ils parfois donner la même valeur ?",
            font_size=33,
            weight="SEMIBOLD",
        )
        question.scale_to_fit_width(11.4)
        question.next_to(self.composition_definition, DOWN, buff=0.65)

        equality_condition = MathTex(r"x^2+1=x^2+2x+1").scale(1.22)
        reduced = MathTex(r"2x=0").scale(1.22)
        answer = MathTex(r"x=0").scale(1.32).set_color(GOOD)
        steps = VGroup(equality_condition, reduced, answer).arrange(DOWN, buff=0.34)
        steps.move_to(DOWN * 0.65)

        values = VGroup(
            MathTex(r"(f\circ g)(0)=1"),
            MathTex(r"(g\circ f)(0)=1"),
        ).arrange(RIGHT, buff=0.8)
        values.scale(0.98)
        values.next_to(steps, DOWN, buff=0.42)

        spoken = ssml(
            "Il existe pourtant une entrée où les deux chemins coïncident. Pour la trouver, égalons leurs "
            "formules. Après simplification, nous obtenons deux x égale zéro, donc x égale zéro. "
            "À cette entrée précise, les deux compositions valent un."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(question, shift=UP * 0.12), run_time=0.55)
            self.wait(0.6)
            self.play(Write(equality_condition), run_time=0.65)
            self.play(Write(reduced), run_time=0.5)
            self.play(Write(answer), run_time=0.5)
            self.wait(0.65)
            self.play(FadeIn(values, shift=UP * 0.12), run_time=0.6)
            self.wait(0.85)

        warning = Text(
            "Même valeur une fois  ≠  mêmes fonctions",
            font_size=35,
            color=ERROR,
            weight="SEMIBOLD",
        )
        warning.to_edge(DOWN, buff=0.35)
        warning_box = SurroundingRectangle(warning, color=ERROR, buff=0.16)

        spoken = ssml(
            "Mais cette coïncidence en une seule entrée ne rend pas les fonctions égales. Pour être égales, "
            "elles doivent donner le même résultat pour chaque entrée de leur domaine. L'entrée deux a déjà "
            "fourni un contre-exemple."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Create(warning_box), FadeIn(warning), run_time=0.65)
            self.wait(1.1)

        self.coincidence_group = VGroup(question, steps, values, warning, warning_box)

    # ------------------------------------------------------------------
    # Acte 6 — Certains couples commutent vraiment
    # ------------------------------------------------------------------
    def _special_commuting_case(self) -> None:
        self.play(FadeOut(self.coincidence_group), FadeOut(self.composition_definition), run_time=0.7)

        title = Text(
            "La composition peut commuter dans des cas particuliers",
            font_size=35,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        title.scale_to_fit_width(11.6)
        title.next_to(self.composition_question, DOWN, buff=0.48)

        definitions = VGroup(
            MathTex(r"p(x)=x+1"),
            MathTex(r"q(x)=x+2"),
        ).arrange(RIGHT, buff=1.4)
        definitions.scale(1.15)
        definitions.next_to(title, DOWN, buff=0.5)

        left_calc = VGroup(
            MathTex(r"(p\circ q)(x)"),
            MathTex(r"=p(x+2)"),
            MathTex(r"=x+3"),
        ).arrange(DOWN, buff=0.28)

        right_calc = VGroup(
            MathTex(r"(q\circ p)(x)"),
            MathTex(r"=q(x+1)"),
            MathTex(r"=x+3"),
        ).arrange(DOWN, buff=0.28)

        calculations = VGroup(left_calc, right_calc).arrange(RIGHT, buff=1.5)
        calculations.scale(1.0)
        calculations.next_to(definitions, DOWN, buff=0.55)

        equality = MathTex(r"p\circ q=q\circ p").scale(1.25).set_color(GOOD)
        equality_box = SurroundingRectangle(equality, color=GOOD, buff=0.17)
        equality_group = VGroup(equality, equality_box)
        equality_group.to_edge(DOWN, buff=0.42)

        spoken = ssml(
            "Il faut toutefois éviter l'excès inverse. La composition n'est pas toujours non commutative. "
            "Prenons deux translations : p ajoute un et q ajoute deux. Dans les deux ordres, le résultat est "
            "x plus trois. Ces deux fonctions particulières commutent."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(title, shift=UP * 0.12), run_time=0.55)
            self.play(Write(definitions), run_time=0.7)
            self.wait(0.55)
            for row in zip(left_calc, right_calc):
                self.play(Write(row[0]), Write(row[1]), run_time=0.55)
                self.wait(0.25)
            self.wait(0.6)
            self.play(Write(equality), Create(equality_box), run_time=0.7)
            self.wait(1.0)

        nuance = Text(
            "Conclusion correcte : pas commutative en général, parfois commutative.",
            font_size=30,
            color=ERROR,
            weight="SEMIBOLD",
        )
        nuance.scale_to_fit_width(11.4)
        nuance.next_to(equality_group, UP, buff=0.34)

        self.play(FadeIn(nuance, shift=UP * 0.1), run_time=0.55)
        self.wait(0.9)

        self.special_case_group = VGroup(
            title,
            definitions,
            calculations,
            equality,
            equality_box,
            nuance,
        )

    # ------------------------------------------------------------------
    # Acte 7 — Synthèse
    # ------------------------------------------------------------------
    def _summary(self) -> None:
        self.play(
            FadeOut(self.special_case_group),
            FadeOut(self.composition_question),
            run_time=0.7,
        )

        title = Text("À retenir", font_size=42, color=ACCENT, weight="SEMIBOLD")
        title.next_to(self.header, DOWN, buff=0.55)

        rule_1 = VGroup(
            MathTex(r"1."),
            MathTex(r"(f\circ g)(x)=f(g(x))"),
            Text("La fonction de droite agit d'abord.", font_size=28),
        ).arrange(RIGHT, buff=0.28)

        rule_2 = VGroup(
            MathTex(r"2."),
            MathTex(r"f\circ g\neq g\circ f\quad\text{en général}"),
        ).arrange(RIGHT, buff=0.28)

        rule_3 = VGroup(
            MathTex(r"3."),
            Text(
                "Une valeur commune ne prouve pas l'égalité des fonctions.",
                font_size=28,
            ),
        ).arrange(RIGHT, buff=0.28)

        rule_4 = VGroup(
            MathTex(r"4."),
            Text(
                "Pour prouver l'inégalité, un seul contre-exemple suffit.",
                font_size=28,
            ),
        ).arrange(RIGHT, buff=0.28)

        rules = VGroup(rule_1, rule_2, rule_3, rule_4).arrange(
            DOWN,
            buff=0.43,
            aligned_edge=LEFT,
        )
        rules.scale_to_fit_width(11.5)
        rules.move_to(DOWN * 0.45)

        final = MathTex(
            r"\boxed{\text{Composer, c'est exécuter des processus dans un ordre précis.}}"
        ).scale(0.93)
        final.set_color(ACCENT)
        final.to_edge(DOWN, buff=0.42)

        spoken = ssml(
            "Retenons quatre idées. Dans une composition, la fonction de droite agit d'abord. "
            "L'ordre ne peut pas être échangé en général. Une coïncidence pour une entrée ne prouve pas "
            "l'égalité de deux fonctions. En revanche, un seul contre-exemple suffit à prouver qu'elles "
            "sont différentes. Composer, c'est exécuter des processus dans un ordre précis."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(title, shift=UP * 0.12), run_time=0.55)
            for rule in rules:
                self.play(FadeIn(rule, shift=RIGHT * 0.1), run_time=0.55)
                self.wait(0.35)
            self.wait(0.65)
            self.play(Write(final), run_time=0.8)
            self.wait(1.2)
