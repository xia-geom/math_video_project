from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
import os

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Axes,
    Circle,
    Create,
    DashedLine,
    Dot,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    Line,
    MathTex,
    NumberLine,
    ReplacementTransform,
    RoundedRectangle,
    Scene,
    SurroundingRectangle,
    Tex,
    Text,
    Transform,
    TransformMatchingTex,
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
LIGHT_FILL = 0.10


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class FonctionParMorceauxFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    """Introduction progressive aux fonctions définies par morceaux.

    Learning objective:
    understand that a piecewise-defined function is still one relationship
    between two variables, whose rule changes according to the input interval.
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

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        self.acte_1_une_relation()
        self.acte_2_un_contexte_concret()
        self.acte_3_ecriture_par_morceaux()
        self.acte_4_construction_du_graphe()
        self.acte_5_choisir_la_bonne_regle()
        self.acte_6_les_points_frontieres()
        self.acte_7_synthese()

        self.wait(1.5)

    @contextmanager
    def narration(self, spoken: str, caption: str | None = None) -> Iterator[object]:
        """Voiceover context with clean plain-text captions."""
        if self._voiceover_enabled:
            with self.voiceover(
                text=tts.ssml(spoken),
                subcaption=caption if caption is not None else tts.strip_ssml(spoken),
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    @staticmethod
    def rule_card(formula: str, condition: str, width: float = 4.6) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=1.15,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2.2,
            fill_color=WHITE,
            fill_opacity=1,
        )
        formula_mob = MathTex(formula, font_size=38)
        condition_mob = MathTex(condition, font_size=27)
        content = VGroup(formula_mob, condition_mob).arrange(DOWN, buff=0.10)
        content.move_to(box)
        return VGroup(box, content)

    @staticmethod
    def closed_point(point: list[float] | tuple[float, float, float], radius: float = 0.075) -> Dot:
        return Dot(point, radius=radius, color=ACCENT)

    @staticmethod
    def open_point(point: list[float] | tuple[float, float, float], radius: float = 0.095) -> Circle:
        return Circle(
            radius=radius,
            stroke_color=ACCENT,
            stroke_width=3,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(point)

    # ------------------------------------------------------------------
    # Act 1 — A function is a relationship between two variables
    # ------------------------------------------------------------------
    def acte_1_une_relation(self) -> None:
        title = Text("Fonctions définies par morceaux", font_size=48).to_edge(UP, buff=0.45)

        x_box = RoundedRectangle(
            width=2.1,
            height=1.35,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        ).shift(LEFT * 4.3 + DOWN * 0.15)
        rule_box = RoundedRectangle(
            width=3.0,
            height=1.7,
            corner_radius=0.12,
            stroke_color=ACCENT,
            stroke_width=3,
            fill_color=ACCENT,
            fill_opacity=LIGHT_FILL,
        ).shift(DOWN * 0.15)
        y_box = RoundedRectangle(
            width=2.3,
            height=1.35,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        ).shift(RIGHT * 4.3 + DOWN * 0.15)

        x_symbol = MathTex("x", font_size=54).move_to(x_box)
        x_caption = Text("variable d'entrée", font_size=25).next_to(x_box, DOWN, buff=0.18)

        rule_text = Text("règle de la fonction", font_size=30).move_to(rule_box)
        y_symbol = MathTex("y=f(x)", font_size=45).move_to(y_box)
        y_caption = Text("variable dépendante", font_size=25).next_to(y_box, DOWN, buff=0.18)

        arrow_1 = Arrow(
            x_box.get_right(),
            rule_box.get_left(),
            buff=0.18,
            color=BLACK,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.12,
        )
        arrow_2 = Arrow(
            rule_box.get_right(),
            y_box.get_left(),
            buff=0.18,
            color=BLACK,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.12,
        )

        with self.narration(
            "Avant de regarder plusieurs formules, prenons le temps de revenir à l'idée essentielle. "
            "Une fonction décrit une relation entre deux variables.",
        ):
            self.play(Write(title), run_time=1.2)
            self.wait(0.8)
            self.play(FadeIn(x_box), Write(x_symbol), FadeIn(x_caption), run_time=1.3)
            self.wait(0.7)

        with self.narration(
            "La variable x est l'entrée. C'est la valeur que l'on choisit, ou que l'on observe.",
        ):
            self.play(Indicate(x_symbol, color=ACCENT, scale_factor=1.12), run_time=1.4)
            self.wait(1.0)

        with self.narration(
            "La règle de la fonction explique comment cette entrée détermine une autre valeur.",
        ):
            self.play(GrowArrow(arrow_1), FadeIn(rule_box), Write(rule_text), run_time=1.5)
            self.wait(1.0)

        with self.narration(
            "Cette autre valeur est y. Elle dépend de x. C'est pour cela qu'on l'appelle la variable dépendante.",
        ):
            self.play(GrowArrow(arrow_2), FadeIn(y_box), Write(y_symbol), FadeIn(y_caption), run_time=1.6)
            self.wait(1.2)

        relation = VGroup(
            x_box,
            x_symbol,
            x_caption,
            rule_box,
            rule_text,
            y_box,
            y_symbol,
            y_caption,
            arrow_1,
            arrow_2,
        )

        with self.narration(
            "Le point important est donc le suivant. Quand x change, la règle nous dit comment y doit changer.",
        ):
            self.play(Indicate(relation, color=ACCENT, scale_factor=1.02), run_time=1.8)
            self.wait(1.4)

        compact_relation = MathTex("x", r"\longmapsto", "y=f(x)", font_size=52)
        compact_relation[1].set_color(ACCENT)
        compact_relation.next_to(title, DOWN, buff=0.9)

        with self.narration(
            "Nous pouvons résumer cette relation par x envoyé sur y égal f de x.",
        ):
            self.play(
                FadeOut(relation),
                FadeIn(compact_relation),
                run_time=1.3,
            )
            self.wait(1.2)

        self.play(FadeOut(compact_relation), title.animate.scale(0.82).to_edge(UP, buff=0.28), run_time=0.9)
        self.section_title = title

    # ------------------------------------------------------------------
    # Act 2 — Concrete context: delivery cost according to weight
    # ------------------------------------------------------------------
    def acte_2_un_contexte_concret(self) -> None:
        subtitle = Text("Un coût qui dépend du poids", font_size=34).next_to(
            self.section_title, DOWN, buff=0.30
        )

        variable_line = VGroup(
            MathTex("m="),
            Text("poids du colis", font_size=28),
            MathTex("C="),
            Text("coût de livraison", font_size=28),
        ).arrange(RIGHT, buff=0.15).next_to(subtitle, DOWN, buff=0.35)
        variable_line[0].set_color(ACCENT)
        variable_line[2].set_color(ACCENT)

        number_line = NumberLine(
            x_range=[0, 5, 1],
            length=9.2,
            include_numbers=True,
            font_size=26,
            color=BLACK,
        ).shift(DOWN * 1.4)
        unit_label = Text("poids m, en kilogrammes", font_size=26).next_to(number_line, DOWN, buff=0.28)

        zones = VGroup(
            Line(number_line.n2p(0), number_line.n2p(1), stroke_width=12, color=ACCENT).set_opacity(0.24),
            Line(number_line.n2p(1), number_line.n2p(3), stroke_width=12, color=ACCENT).set_opacity(0.12),
            Line(number_line.n2p(3), number_line.n2p(5), stroke_width=12, color=ACCENT).set_opacity(0.07),
        )

        marker = Dot(number_line.n2p(0.5), radius=0.095, color=ACCENT)
        marker_label = MathTex("m", font_size=31, color=ACCENT).next_to(marker, UP, buff=0.13)

        price_box = RoundedRectangle(
            width=3.3,
            height=1.35,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2.3,
            fill_color=WHITE,
            fill_opacity=1,
        ).to_edge(RIGHT, buff=0.65).shift(DOWN * 0.15)
        price_title = Text("coût C", font_size=27).next_to(price_box.get_top(), DOWN, buff=0.16)
        price_value = MathTex("5", font_size=52, color=ACCENT).move_to(price_box).shift(DOWN * 0.15)

        rules = VGroup(
            self.rule_card("C=5", r"0<m\leq 1", width=3.35),
            self.rule_card("C=8", r"1<m\leq 3", width=3.35),
            self.rule_card("C=12", r"3<m\leq 5", width=3.35),
        ).arrange(DOWN, buff=0.18).to_edge(LEFT, buff=0.62).shift(DOWN * 0.15)

        with self.narration(
            "Prenons maintenant une situation concrète. Le coût de livraison C dépend du poids m d'un colis.",
        ):
            self.play(Write(subtitle), run_time=1.0)
            self.play(Write(variable_line), run_time=1.5)
            self.wait(1.1)

        with self.narration(
            "Pour un colis de moins d'un kilogramme, le coût est de cinq dollars.",
        ):
            self.play(Create(number_line), FadeIn(unit_label), FadeIn(zones[0]), run_time=1.4)
            self.play(FadeIn(rules[0]), FadeIn(marker), FadeIn(marker_label), run_time=1.2)
            self.play(FadeIn(price_box), FadeIn(price_title), Write(price_value), run_time=1.1)
            self.wait(1.3)

        marker_target = number_line.n2p(2.0)
        new_marker_label = MathTex("m", font_size=31, color=ACCENT).next_to(marker_target, UP, buff=0.13)
        new_price = MathTex("8", font_size=52, color=ACCENT).move_to(price_value)

        with self.narration(
            "Mais lorsque le poids dépasse un kilogramme, le système change de tarif. "
            "Entre un et trois kilogrammes, le coût devient huit dollars.",
        ):
            self.play(FadeIn(zones[1]), FadeIn(rules[1]), run_time=1.1)
            self.play(
                marker.animate.move_to(marker_target),
                Transform(marker_label, new_marker_label),
                TransformMatchingTex(price_value, new_price),
                run_time=2.1,
            )
            price_value = new_price
            self.wait(1.3)

        marker_target = number_line.n2p(4.0)
        new_marker_label = MathTex("m", font_size=31, color=ACCENT).next_to(marker_target, UP, buff=0.13)
        new_price = MathTex("12", font_size=52, color=ACCENT).move_to(price_value)

        with self.narration(
            "Au-delà de trois kilogrammes, la règle change encore. Le coût devient douze dollars.",
        ):
            self.play(FadeIn(zones[2]), FadeIn(rules[2]), run_time=1.1)
            self.play(
                marker.animate.move_to(marker_target),
                Transform(marker_label, new_marker_label),
                TransformMatchingTex(price_value, new_price),
                run_time=2.1,
            )
            price_value = new_price
            self.wait(1.4)

        one_function = Text("Une seule relation entre m et C", font_size=31, color=ACCENT).to_edge(DOWN, buff=0.38)

        with self.narration(
            "Nous n'avons pas trois problèmes séparés. Nous avons toujours les mêmes deux variables, m et C, "
            "et une seule relation entre elles. Ce sont seulement les règles qui changent selon la valeur de m.",
        ):
            self.play(Write(one_function), run_time=1.4)
            self.play(Indicate(rules, color=ACCENT, scale_factor=1.02), run_time=1.8)
            self.wait(1.5)

        self.delivery_group = VGroup(
            subtitle,
            variable_line,
            number_line,
            unit_label,
            zones,
            marker,
            marker_label,
            price_box,
            price_title,
            price_value,
            rules,
            one_function,
        )

    # ------------------------------------------------------------------
    # Act 3 — Assemble the piecewise notation only after the idea is clear
    # ------------------------------------------------------------------
    def acte_3_ecriture_par_morceaux(self) -> None:
        self.play(FadeOut(self.delivery_group), run_time=1.0)

        subtitle = Text("Écrire la relation complète", font_size=34).next_to(
            self.section_title, DOWN, buff=0.30
        )

        line_1 = MathTex("C(m)=5", r"\quad\text{si}\quad", r"0<m\leq 1", font_size=39)
        line_2 = MathTex("C(m)=8", r"\quad\text{si}\quad", r"1<m\leq 3", font_size=39)
        line_3 = MathTex("C(m)=12", r"\quad\text{si}\quad", r"3<m\leq 5", font_size=39)
        separate_lines = VGroup(line_1, line_2, line_3).arrange(DOWN, aligned_edge=LEFT, buff=0.52)
        separate_lines.move_to(DOWN * 0.25)

        with self.narration(
            "Écrivons maintenant ce que nous venons de voir. Nous commençons par la première règle, "
            "avec son intervalle d'utilisation.",
        ):
            self.play(Write(subtitle), run_time=1.0)
            self.play(Write(line_1), run_time=1.6)
            self.wait(1.3)

        with self.narration(
            "Puis nous ajoutons la deuxième règle. Elle appartient à la même fonction, mais elle agit sur un autre intervalle.",
        ):
            self.play(Write(line_2), run_time=1.6)
            self.wait(1.2)

        with self.narration(
            "Enfin, nous ajoutons la troisième règle, avec sa propre condition.",
        ):
            self.play(Write(line_3), run_time=1.5)
            self.wait(1.3)

        conditions_box = SurroundingRectangle(
            VGroup(line_1[2], line_2[2], line_3[2]),
            buff=0.18,
            color=ACCENT,
            stroke_width=3,
        )
        conditions_label = Text("Les conditions font partie de la règle", font_size=28, color=ACCENT)
        conditions_label.next_to(conditions_box, RIGHT, buff=0.35)

        with self.narration(
            "Les conditions ne sont pas des commentaires ajoutés à côté des formules. "
            "Elles font partie de la définition. Elles nous disent quand chaque formule doit être utilisée.",
        ):
            self.play(Create(conditions_box), FadeIn(conditions_label), run_time=1.4)
            self.wait(1.7)

        piecewise = MathTex(
            "C(m)=",
            r"\begin{cases}"
            r"5 & \text{si } 0<m\leq 1,\\"
            r"8 & \text{si } 1<m\leq 3,\\"
            r"12 & \text{si } 3<m\leq 5."
            r"\end{cases}",
            font_size=43,
        ).move_to(DOWN * 0.30)

        with self.narration(
            "Nous pouvons enfin regrouper ces trois lignes dans une écriture compacte. "
            "On dit que C est une fonction définie par morceaux.",
        ):
            self.play(FadeOut(conditions_box), FadeOut(conditions_label), run_time=0.6)
            self.play(ReplacementTransform(separate_lines, piecewise), run_time=1.8)
            self.wait(1.8)

        conclusion = Text(
            "Une fonction — plusieurs régimes possibles",
            font_size=31,
            color=ACCENT,
        ).next_to(piecewise, DOWN, buff=0.55)

        with self.narration(
            "Le symbole à gauche reste unique. C'est bien une seule fonction. "
            "Les différentes lignes décrivent simplement ses différents régimes.",
        ):
            self.play(Write(conclusion), run_time=1.3)
            self.wait(1.5)

        self.play(FadeOut(VGroup(subtitle, piecewise, conclusion)), run_time=0.9)

    # ------------------------------------------------------------------
    # Act 4 — Build a graph piece by piece
    # ------------------------------------------------------------------
    def acte_4_construction_du_graphe(self) -> None:
        subtitle = Text("Construire un graphe morceau par morceau", font_size=34).next_to(
            self.section_title, DOWN, buff=0.30
        )

        definition = MathTex(
            "f(x)=",
            r"\begin{cases}"
            r"x+2 & \text{si } x<0,\\"
            r"x^2 & \text{si } 0\leq x<2,\\"
            r"4 & \text{si } x\geq 2."
            r"\end{cases}",
            font_size=35,
        ).to_edge(LEFT, buff=0.48).shift(UP * 0.15)

        axes = Axes(
            x_range=[-4, 5, 1],
            y_range=[-2, 7, 1],
            x_length=7.1,
            y_length=5.2,
            axis_config={"color": BLACK, "stroke_width": 2.2, "include_ticks": True},
            tips=False,
        ).to_edge(RIGHT, buff=0.45).shift(DOWN * 0.55)
        axes_labels = axes.get_axis_labels(
            MathTex("x", font_size=30),
            MathTex("y", font_size=30),
        )

        first_piece = axes.plot(lambda x: x + 2, x_range=[-4, -0.02], color=ACCENT, stroke_width=4)
        second_piece = axes.plot(lambda x: x**2, x_range=[0, 1.98], color=ACCENT, stroke_width=4)
        third_piece = axes.plot(lambda x: 4, x_range=[2, 5], color=ACCENT, stroke_width=4)

        open_0_2 = self.open_point(axes.c2p(0, 2))
        closed_0_0 = self.closed_point(axes.c2p(0, 0))
        closed_2_4 = self.closed_point(axes.c2p(2, 4))

        with self.narration(
            "Regardons maintenant un exemple plus général. Ici, x et y sont toujours les deux variables. "
            "Mais la relation entre elles change dans trois régions.",
        ):
            self.play(Write(subtitle), run_time=1.0)
            self.play(Write(definition), run_time=1.8)
            self.wait(1.3)
            self.play(Create(axes), FadeIn(axes_labels), run_time=1.4)
            self.wait(1.0)

        active_rule = self.rule_card("y=x+2", "x<0", width=3.6).next_to(definition, DOWN, buff=0.45)

        with self.narration(
            "Pour les entrées strictement négatives, nous utilisons seulement la formule y égal x plus deux.",
        ):
            self.play(FadeIn(active_rule), run_time=0.9)
            self.play(Create(first_piece), run_time=2.2)
            self.play(FadeIn(open_0_2), run_time=0.7)
            self.wait(1.4)

        next_rule = self.rule_card("y=x^2", r"0\leq x<2", width=3.6).move_to(active_rule)

        with self.narration(
            "Ensuite, de zéro inclus jusqu'à deux exclu, la relation devient y égal x au carré. "
            "Nous ne prolongeons pas la droite dans cette région.",
        ):
            self.play(Transform(active_rule, next_rule), run_time=1.0)
            self.play(Create(second_piece), FadeIn(closed_0_0), run_time=2.2)
            self.wait(1.5)

        last_rule = self.rule_card("y=4", r"x\geq 2", width=3.6).move_to(active_rule)

        with self.narration(
            "À partir de deux, la sortie reste toujours égale à quatre. "
            "Le dernier morceau est donc horizontal.",
        ):
            self.play(Transform(active_rule, last_rule), run_time=1.0)
            self.play(Create(third_piece), FadeIn(closed_2_4), run_time=2.0)
            self.wait(1.5)

        graph = VGroup(first_piece, second_piece, third_piece, open_0_2, closed_0_0, closed_2_4)
        one_graph_label = Text("Un seul graphe, construit avec trois morceaux", font_size=28, color=ACCENT)
        one_graph_label.to_edge(DOWN, buff=0.30)

        with self.narration(
            "Les trois courbes ne sont pas trois réponses séparées. Ensemble, elles forment le graphe d'une seule fonction.",
        ):
            self.play(FadeOut(active_rule), Write(one_graph_label), run_time=1.2)
            self.play(Indicate(graph, color=ACCENT, scale_factor=1.015), run_time=2.0)
            self.wait(1.5)

        self.graph_group = VGroup(
            subtitle,
            definition,
            axes,
            axes_labels,
            graph,
            one_graph_label,
        )
        self.axes = axes
        self.definition = definition
        self.graph = graph

    # ------------------------------------------------------------------
    # Act 5 — The input selects the interval, then the formula
    # ------------------------------------------------------------------
    def acte_5_choisir_la_bonne_regle(self) -> None:
        self.play(FadeOut(self.graph_group), run_time=1.0)

        subtitle = Text("Comment calculer une valeur ?", font_size=34).next_to(
            self.section_title, DOWN, buff=0.30
        )

        definition = MathTex(
            "f(x)=",
            r"\begin{cases}"
            r"x+2 & \text{si } x<0,\\"
            r"x^2 & \text{si } 0\leq x<2,\\"
            r"4 & \text{si } x\geq 2."
            r"\end{cases}",
            font_size=40,
        ).next_to(subtitle, DOWN, buff=0.42)

        step_1 = RoundedRectangle(
            width=3.45,
            height=1.2,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2.2,
            fill_color=WHITE,
            fill_opacity=1,
        )
        step_2 = step_1.copy()
        step_3 = step_1.copy()
        steps = VGroup(step_1, step_2, step_3).arrange(RIGHT, buff=0.48).to_edge(DOWN, buff=1.05)

        text_1 = Text("1. Localiser x", font_size=28).move_to(step_1)
        text_2 = Text("2. Choisir la règle", font_size=28).move_to(step_2)
        text_3 = Text("3. Calculer y", font_size=28).move_to(step_3)
        arrows = VGroup(
            Arrow(step_1.get_right(), step_2.get_left(), buff=0.10, color=ACCENT, stroke_width=3),
            Arrow(step_2.get_right(), step_3.get_left(), buff=0.10, color=ACCENT, stroke_width=3),
        )

        with self.narration(
            "Pour calculer une valeur, nous allons suivre trois étapes. Nous les construisons lentement, une à la fois.",
        ):
            self.play(Write(subtitle), Write(definition), run_time=1.8)
            self.wait(1.2)

        with self.narration(
            "Première étape. On localise l'entrée x. On regarde dans quel intervalle elle se trouve.",
        ):
            self.play(FadeIn(step_1), Write(text_1), run_time=1.2)
            self.wait(1.4)

        with self.narration(
            "Deuxième étape. L'intervalle nous indique quelle formule utiliser.",
        ):
            self.play(GrowArrow(arrows[0]), FadeIn(step_2), Write(text_2), run_time=1.2)
            self.wait(1.4)

        with self.narration(
            "Troisième étape. Seulement maintenant, nous remplaçons x dans cette formule pour obtenir y.",
        ):
            self.play(GrowArrow(arrows[1]), FadeIn(step_3), Write(text_3), run_time=1.2)
            self.wait(1.6)

        procedure = VGroup(steps, text_1, text_2, text_3, arrows)
        self.play(procedure.animate.scale(0.82).to_edge(DOWN, buff=0.35), run_time=0.9)
        self.bring_to_front(text_1, text_2, text_3, arrows)

        example_box = RoundedRectangle(
            width=6.6,
            height=1.75,
            corner_radius=0.12,
            stroke_color=ACCENT,
            stroke_width=2.8,
            fill_color=ACCENT,
            fill_opacity=0.06,
        ).move_to(DOWN * 0.35)

        ex1 = MathTex(
            "x=-2", r"\quad\Rightarrow\quad", "x<0", r"\quad\Rightarrow\quad",
            "f(-2)=-2+2=0",
            font_size=38,
        ).move_to(example_box)

        with self.narration(
            "Prenons x égal moins deux. Moins deux est négatif. Nous choisissons donc la première règle, "
            "et nous obtenons f de moins deux égal zéro.",
        ):
            self.play(FadeIn(example_box), Write(ex1[0]), run_time=0.8)
            self.wait(0.7)
            self.play(Write(ex1[1:3]), run_time=1.0)
            self.wait(0.8)
            self.play(Write(ex1[3:]), run_time=1.4)
            self.wait(1.5)

        ex2 = MathTex(
            "x=1", r"\quad\Rightarrow\quad", r"0\leq x<2", r"\quad\Rightarrow\quad",
            "f(1)=1^2=1",
            font_size=38,
        ).move_to(example_box)

        with self.narration(
            "Prenons ensuite x égal un. Un appartient au deuxième intervalle. "
            "La bonne règle est donc x au carré, et f de un vaut un.",
        ):
            self.play(TransformMatchingTex(ex1, ex2), run_time=1.8)
            self.wait(1.5)

        ex3 = MathTex(
            "x=3", r"\quad\Rightarrow\quad", r"x\geq 2", r"\quad\Rightarrow\quad",
            "f(3)=4",
            font_size=38,
        ).move_to(example_box)

        with self.narration(
            "Enfin, trois est supérieur à deux. Nous utilisons la dernière règle. La sortie vaut quatre.",
        ):
            self.play(TransformMatchingTex(ex2, ex3), run_time=1.6)
            self.wait(1.5)

        warning = Text(
            "On ne remplace jamais x dans toutes les formules.",
            font_size=29,
            color=ACCENT,
        ).next_to(example_box, UP, buff=0.28)

        with self.narration(
            "L'erreur fréquente serait d'essayer les trois formules. Ce n'est pas nécessaire. "
            "L'entrée sélectionne d'abord un seul intervalle, donc une seule règle.",
        ):
            self.play(Write(warning), run_time=1.3)
            self.play(Indicate(procedure, color=ACCENT, scale_factor=1.02), run_time=1.8)
            self.wait(1.6)

        self.play(
            FadeOut(VGroup(subtitle, definition, procedure, example_box, ex3, warning)),
            run_time=1.0,
        )

    # ------------------------------------------------------------------
    # Act 6 — Boundaries, open/closed points, and continuity intuition
    # ------------------------------------------------------------------
    def acte_6_les_points_frontieres(self) -> None:
        subtitle = Text("Que se passe-t-il aux frontières ?", font_size=34).next_to(
            self.section_title, DOWN, buff=0.30
        )

        axes = Axes(
            x_range=[-2, 4, 1],
            y_range=[-1, 6, 1],
            x_length=8.4,
            y_length=5.0,
            axis_config={"color": BLACK, "stroke_width": 2.2},
            tips=False,
        ).shift(RIGHT * 1.25 + DOWN * 0.55)
        axes_labels = axes.get_axis_labels(MathTex("x", font_size=30), MathTex("y", font_size=30))

        first_piece = axes.plot(lambda x: x + 2, x_range=[-2, -0.02], color=ACCENT, stroke_width=4)
        second_piece = axes.plot(lambda x: x**2, x_range=[0, 1.98], color=ACCENT, stroke_width=4)
        third_piece = axes.plot(lambda x: 4, x_range=[2, 4], color=ACCENT, stroke_width=4)

        open_0_2 = self.open_point(axes.c2p(0, 2), radius=0.105)
        closed_0_0 = self.closed_point(axes.c2p(0, 0), radius=0.085)
        closed_2_4 = self.closed_point(axes.c2p(2, 4), radius=0.085)

        boundary_0 = DashedLine(
            axes.c2p(0, -1), axes.c2p(0, 6), color=BLACK, stroke_width=2
        ).set_opacity(0.35)
        boundary_2 = DashedLine(
            axes.c2p(2, -1), axes.c2p(2, 6), color=BLACK, stroke_width=2
        ).set_opacity(0.35)

        labels = VGroup(
            MathTex("x=0", font_size=30).next_to(boundary_0, DOWN, buff=0.12),
            MathTex("x=2", font_size=30).next_to(boundary_2, DOWN, buff=0.12),
        )

        side_panel = RoundedRectangle(
            width=3.45,
            height=4.75,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2.2,
            fill_color=WHITE,
            fill_opacity=1,
        ).to_edge(LEFT, buff=0.45).shift(DOWN * 0.45)
        side_title = Text("Lecture des extrémités", font_size=28).next_to(
            side_panel.get_top(), DOWN, buff=0.24
        )
        open_legend = VGroup(
            self.open_point([0, 0, 0], radius=0.10),
            Text("point ouvert : exclu", font_size=26),
        ).arrange(RIGHT, buff=0.20)
        closed_legend = VGroup(
            self.closed_point([0, 0, 0], radius=0.08),
            Text("point plein : inclus", font_size=26),
        ).arrange(RIGHT, buff=0.20)
        legend = VGroup(open_legend, closed_legend).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        legend.move_to(side_panel).shift(UP * 0.45)

        with self.narration(
            "Les frontières entre les intervalles demandent plus d'attention. Nous allons ralentir ici, "
            "car c'est souvent à ces points que les erreurs apparaissent.",
        ):
            self.play(Write(subtitle), run_time=1.0)
            self.play(Create(axes), FadeIn(axes_labels), run_time=1.3)
            self.play(
                Create(first_piece),
                Create(second_piece),
                Create(third_piece),
                FadeIn(open_0_2),
                FadeIn(closed_0_0),
                FadeIn(closed_2_4),
                run_time=2.4,
            )
            self.wait(1.2)
            self.play(FadeIn(side_panel), Write(side_title), FadeIn(legend), run_time=1.4)
            self.wait(1.3)

        with self.narration(
            "À x égal zéro, la condition x inférieur à zéro n'inclut pas zéro. "
            "Le point correspondant à la droite est donc ouvert.",
        ):
            self.play(Create(boundary_0), Write(labels[0]), run_time=1.0)
            self.play(Indicate(open_0_2, color=ACCENT, scale_factor=1.5), run_time=1.7)
            self.wait(1.5)

        zero_value = MathTex("f(0)=0^2=0", font_size=36, color=ACCENT).move_to(side_panel).shift(DOWN * 1.35)

        with self.narration(
            "Mais la deuxième condition, zéro inférieur ou égal à x, inclut zéro. "
            "Le point plein est donc à zéro, zéro. La valeur réelle de la fonction est f de zéro égal zéro.",
        ):
            self.play(Indicate(closed_0_0, color=ACCENT, scale_factor=1.5), run_time=1.7)
            self.play(Write(zero_value), run_time=1.2)
            self.wait(1.6)

        jump_label = Text("La règle change et le graphe saute.", font_size=27, color=ACCENT)
        jump_label.move_to(side_panel).shift(DOWN * 1.95)

        with self.narration(
            "À cet endroit, la formule change, et le graphe fait aussi un saut.",
        ):
            self.play(Write(jump_label), run_time=1.1)
            self.wait(1.5)

        with self.narration(
            "Regardons maintenant x égal deux. La formule change encore, mais cette fois les deux morceaux arrivent au même point.",
        ):
            self.play(FadeOut(VGroup(zero_value, jump_label)), run_time=0.7)
            self.play(Create(boundary_2), Write(labels[1]), run_time=1.0)
            self.play(Indicate(closed_2_4, color=ACCENT, scale_factor=1.5), run_time=1.8)
            self.wait(1.5)

        same_point = MathTex("2^2=4", r"\qquad", "f(2)=4", font_size=36, color=ACCENT)
        same_point.move_to(side_panel).shift(DOWN * 1.30)
        no_break = VGroup(
            Text("La règle change,", font_size=22, color=ACCENT),
            Text("mais le graphe reste joint.", font_size=22, color=ACCENT),
        ).arrange(DOWN, buff=0.08)
        no_break.move_to(side_panel).shift(DOWN * 1.90)

        with self.narration(
            "La parabole approche la hauteur quatre, et la dernière règle donne elle aussi quatre. "
            "Il n'y a donc pas de rupture du graphe.",
        ):
            self.play(Write(same_point), run_time=1.2)
            self.play(Write(no_break), run_time=1.2)
            self.wait(1.7)

        key_idea = Text(
            "Changer de formule ne signifie pas forcément casser le graphe.",
            font_size=24,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.25)

        with self.narration(
            "Retenons cette idée importante. Un changement de formule ne signifie pas automatiquement que le graphe est cassé.",
        ):
            self.play(Write(key_idea), run_time=1.4)
            self.wait(1.8)

        self.play(
            FadeOut(
                VGroup(
                    subtitle,
                    axes,
                    axes_labels,
                    first_piece,
                    second_piece,
                    third_piece,
                    open_0_2,
                    closed_0_0,
                    closed_2_4,
                    boundary_0,
                    boundary_2,
                    labels,
                    side_panel,
                    side_title,
                    legend,
                    same_point,
                    no_break,
                    key_idea,
                )
            ),
            run_time=1.0,
        )

    # ------------------------------------------------------------------
    # Act 7 — Slow summary, one idea at a time
    # ------------------------------------------------------------------
    def acte_7_synthese(self) -> None:
        subtitle = Text("Résumé", font_size=36).next_to(self.section_title, DOWN, buff=0.34)
        central = Text(
            "Une fonction par morceaux reste une seule relation entre deux variables.",
            font_size=32,
            color=ACCENT,
        ).next_to(subtitle, DOWN, buff=0.48)

        box_1 = RoundedRectangle(
            width=4.2,
            height=1.25,
            corner_radius=0.12,
            stroke_color=BLACK,
            stroke_width=2.2,
            fill_color=WHITE,
            fill_opacity=1,
        )
        box_2 = box_1.copy()
        box_3 = box_1.copy()
        boxes = VGroup(box_1, box_2, box_3).arrange(DOWN, buff=0.40).shift(DOWN * 0.85)

        text_1 = Text("1. x choisit l’intervalle", font_size=26).move_to(box_1)
        text_2 = Text("2. l’intervalle choisit la règle", font_size=24).move_to(box_2)
        text_3 = Text("3. la règle détermine y", font_size=26).move_to(box_3)

        arrow_1 = Arrow(box_1.get_bottom(), box_2.get_top(), buff=0.08, color=ACCENT, stroke_width=3)
        arrow_2 = Arrow(box_2.get_bottom(), box_3.get_top(), buff=0.08, color=ACCENT, stroke_width=3)

        with self.narration(
            "Terminons en reprenant le raisonnement, sans aller trop vite.",
        ):
            self.play(Write(subtitle), run_time=0.9)
            self.play(Write(central), run_time=1.5)
            self.wait(1.5)

        with self.narration(
            "Premièrement, la valeur de x nous dit dans quel intervalle nous sommes.",
        ):
            self.play(FadeIn(box_1), Write(text_1), run_time=1.3)
            self.wait(1.6)

        with self.narration(
            "Deuxièmement, cet intervalle nous indique la règle qui s'applique.",
        ):
            self.play(GrowArrow(arrow_1), FadeIn(box_2), Write(text_2), run_time=1.3)
            self.wait(1.6)

        with self.narration(
            "Troisièmement, la règle transforme x et détermine la valeur de y.",
        ):
            self.play(GrowArrow(arrow_2), FadeIn(box_3), Write(text_3), run_time=1.3)
            self.wait(1.7)

        self.bring_to_front(text_1, text_2, text_3, arrow_1, arrow_2)

        final_formula = VGroup(
            MathTex("x", font_size=39),
            MathTex(r"\longrightarrow", font_size=39),
            Text("intervalle", font_size=28),
            MathTex(r"\longrightarrow", font_size=39),
            Text("règle", font_size=28),
            MathTex(r"\longrightarrow", font_size=39),
            MathTex("y=f(x)", font_size=39),
        ).arrange(RIGHT, buff=0.14).to_edge(DOWN, buff=0.32)
        final_formula[1].set_color(ACCENT)
        final_formula[3].set_color(ACCENT)
        final_formula[5].set_color(ACCENT)

        with self.narration(
            "Autrement dit, x choisit l'intervalle, l'intervalle choisit la règle, "
            "et la règle détermine y. C'est cela, une fonction définie par morceaux.",
        ):
            self.play(Write(final_formula), run_time=2.0)
            self.play(Indicate(VGroup(central, boxes, final_formula), color=ACCENT, scale_factor=1.01), run_time=2.0)
            self.bring_to_front(text_1, text_2, text_3, arrow_1, arrow_2)
            self.wait(2.0)
