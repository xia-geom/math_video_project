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
    Indicate,
    Line,
    MathTex,
    NumberLine,
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

ACCENT = BLUE_D
LIGHT_FILL = 0.08


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class FonctionParMorceauxFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    """Introduction visuelle aux fonctions définies par morceaux.

    Idée centrale : une même fonction peut utiliser des règles différentes,
    parce que l'entrée choisit d'abord l'intervalle où elle se trouve.
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
    def narration(self, spoken: str, caption: str | None = None) -> Iterator[object]:
        if self._voiceover_enabled:
            with self.voiceover(
                text=tts.ssml(spoken),
                subcaption=caption if caption is not None else tts.strip_ssml(spoken),
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    @staticmethod
    def closed_point(point: list[float] | tuple[float, float, float], radius: float = 0.08) -> Dot:
        return Dot(point, radius=radius, color=ACCENT)

    @staticmethod
    def open_point(point: list[float] | tuple[float, float, float], radius: float = 0.10) -> Circle:
        return Circle(
            radius=radius,
            stroke_color=ACCENT,
            stroke_width=3,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(point)

    @staticmethod
    def price_badge(price: int) -> VGroup:
        box = RoundedRectangle(
            width=3.0,
            height=1.35,
            corner_radius=0.12,
            stroke_color=ACCENT,
            stroke_width=2.8,
            fill_color=ACCENT,
            fill_opacity=LIGHT_FILL,
        )
        value = MathTex(rf"C={price}\,\$", font_size=48, color=ACCENT).move_to(box)
        return VGroup(box, value)

    @staticmethod
    def rule_line(formula: str, condition: str, font_size: int = 38) -> MathTex:
        line = MathTex(formula, r"\quad\text{si}\quad", condition, font_size=font_size)
        line[2].set_color(ACCENT)
        return line

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        self.acte_1_question_et_intuition()
        self.acte_2_de_l_histoire_a_la_notation()
        self.acte_3_choisir_une_regle()
        self.acte_4_construire_le_graphe()
        self.acte_5_lire_une_frontiere()
        self.acte_6_synthese()

        self.wait(1.5)

    # ------------------------------------------------------------------
    # Act 1 — Begin with the central question and one concrete change
    # ------------------------------------------------------------------
    def acte_1_question_et_intuition(self) -> None:
        title = Text("Fonctions définies par morceaux", font_size=46).to_edge(UP, buff=0.38)
        question = Text(
            "Comment une seule fonction peut-elle changer de formule ?",
            font_size=32,
            color=ACCENT,
        ).next_to(title, DOWN, buff=0.34)

        with self.narration(
            "Voici la question centrale. Comment une seule fonction peut-elle changer de formule ?",
        ):
            self.play(Write(title), run_time=1.0)
            self.play(Write(question), run_time=1.4)
            self.wait(1.4)

        context = Text("Exemple : le prix d'un colis dépend de son poids.", font_size=30)
        context.next_to(question, DOWN, buff=0.55)

        number_line = NumberLine(
            x_range=[0, 5, 1],
            length=7.6,
            include_numbers=True,
            font_size=25,
            color=BLACK,
        ).shift(LEFT * 1.25 + DOWN * 1.0)
        unit = Text("poids m, en kg", font_size=25).next_to(number_line, DOWN, buff=0.22)

        marker = Dot(number_line.n2p(0.6), radius=0.095, color=ACCENT)
        marker_label = MathTex("m=0{,}6", font_size=30, color=ACCENT).next_to(marker, UP, buff=0.16)
        badge = self.price_badge(5).to_edge(RIGHT, buff=0.65).shift(DOWN * 0.05)

        with self.narration(
            "Prenons un service de livraison. Pour un colis de zéro virgule six kilogramme, le prix est cinq dollars.",
        ):
            self.play(Write(context), run_time=1.2)
            self.play(Create(number_line), FadeIn(unit), run_time=1.3)
            self.play(FadeIn(marker), Write(marker_label), FadeIn(badge), run_time=1.3)
            self.wait(1.4)

        new_marker_point = number_line.n2p(2.0)
        new_marker_label = MathTex("m=2", font_size=30, color=ACCENT).next_to(
            new_marker_point, UP, buff=0.16
        )
        new_badge = self.price_badge(8).move_to(badge)
        threshold = DashedLine(
            number_line.n2p(1) + DOWN * 0.55,
            number_line.n2p(1) + UP * 0.55,
            color=BLACK,
            stroke_width=2,
        ).set_opacity(0.45)
        threshold_label = MathTex(r"1\text{ kg}", font_size=27).next_to(threshold, UP, buff=0.10)

        with self.narration(
            "Mais quand le poids dépasse un kilogramme, le tarif change. Pour deux kilogrammes, le prix est huit dollars.",
        ):
            self.play(Create(threshold), Write(threshold_label), run_time=0.9)
            self.play(
                marker.animate.move_to(new_marker_point),
                Transform(marker_label, new_marker_label),
                Transform(badge, new_badge),
                run_time=2.0,
            )
            self.wait(1.5)

        answer = Text(
            "La fonction reste la même ; la règle dépend de l'intervalle.",
            font_size=30,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.35)

        with self.narration(
            "La fonction n'a pas changé d'identité. C'est toujours le prix en fonction du poids. "
            "Ce qui change, c'est la règle utilisée dans chaque intervalle.",
        ):
            self.play(Write(answer), run_time=1.5)
            self.wait(1.8)

        self.play(
            FadeOut(VGroup(question, context, number_line, unit, marker, marker_label, badge, threshold, threshold_label, answer)),
            title.animate.scale(0.84).to_edge(UP, buff=0.26),
            run_time=1.0,
        )
        self.section_title = title

    # ------------------------------------------------------------------
    # Act 2 — Build the notation from the already-understood situation
    # ------------------------------------------------------------------
    def acte_2_de_l_histoire_a_la_notation(self) -> None:
        subtitle = Text("Trois intervalles, trois tarifs", font_size=33).next_to(
            self.section_title, DOWN, buff=0.30
        )

        line_1 = self.rule_line("C(m)=5", r"0<m\leq 1")
        line_2 = self.rule_line("C(m)=8", r"1<m\leq 3")
        line_3 = self.rule_line("C(m)=12", r"3<m\leq 5")
        lines = VGroup(line_1, line_2, line_3).arrange(DOWN, aligned_edge=LEFT, buff=0.55)
        lines.move_to(DOWN * 0.20)

        with self.narration(
            "Écrivons d'abord la première règle. Jusqu'à un kilogramme inclus, le prix est cinq dollars.",
        ):
            self.play(Write(subtitle), run_time=0.9)
            self.play(Write(line_1), run_time=1.5)
            self.wait(1.4)

        with self.narration(
            "Entre un kilogramme exclu et trois kilogrammes inclus, le prix est huit dollars.",
        ):
            self.play(Write(line_2), run_time=1.5)
            self.wait(1.4)

        with self.narration(
            "Enfin, au-dessus de trois kilogrammes et jusqu'à cinq kilogrammes inclus, le prix est douze dollars.",
        ):
            self.play(Write(line_3), run_time=1.5)
            self.wait(1.5)

        condition_focus = SurroundingRectangle(
            VGroup(line_1[2], line_2[2], line_3[2]),
            color=ACCENT,
            stroke_width=2.8,
            buff=0.16,
        )
        reminder = Text("Chaque condition indique quand utiliser la formule.", font_size=28, color=ACCENT)
        reminder.to_edge(DOWN, buff=0.42)

        with self.narration(
            "Les conditions sont essentielles. Elles indiquent quand chaque formule est autorisée.",
        ):
            self.play(Create(condition_focus), run_time=1.0)
            self.play(Write(reminder), run_time=1.2)
            self.wait(1.6)

        piecewise = MathTex(
            "C(m)=",
            r"\begin{cases}"
            r"5 & \text{si } 0<m\leq 1,\\"
            r"8 & \text{si } 1<m\leq 3,\\"
            r"12 & \text{si } 3<m\leq 5."
            r"\end{cases}",
            font_size=44,
        ).move_to(DOWN * 0.15)

        with self.narration(
            "On regroupe ensuite ces trois règles sous un seul nom, C. Voilà une fonction définie par morceaux.",
        ):
            self.play(FadeOut(VGroup(condition_focus, reminder)), run_time=0.5)
            self.play(TransformMatchingTex(lines, piecewise), run_time=1.7)
            self.wait(1.8)

        single_name = Text("Un seul nom : C", font_size=29, color=ACCENT).next_to(piecewise, DOWN, buff=0.48)
        with self.narration(
            "Le nom C apparaît une seule fois, parce qu'il s'agit bien d'une seule fonction.",
        ):
            self.play(Write(single_name), run_time=1.1)
            self.wait(1.5)

        self.play(FadeOut(VGroup(subtitle, piecewise, single_name)), run_time=0.9)

    # ------------------------------------------------------------------
    # Act 3 — One input selects one interval, then one rule
    # ------------------------------------------------------------------
    def acte_3_choisir_une_regle(self) -> None:
        subtitle = Text("Calculer C(2,4)", font_size=33).next_to(
            self.section_title, DOWN, buff=0.30
        )

        number_line = NumberLine(
            x_range=[0, 5, 1],
            length=9.0,
            include_numbers=True,
            font_size=25,
            color=BLACK,
        ).shift(UP * 0.55)
        marker = Dot(number_line.n2p(2.4), radius=0.10, color=ACCENT)
        marker_label = MathTex("2{,}4", font_size=31, color=ACCENT).next_to(marker, UP, buff=0.16)

        with self.narration(
            "Pour calculer C de deux virgule quatre, on commence seulement par placer l'entrée.",
        ):
            self.play(Write(subtitle), run_time=0.9)
            self.play(Create(number_line), FadeIn(marker), Write(marker_label), run_time=1.4)
            self.wait(1.4)

        interval = MathTex(r"1<2{,}4\leq 3", font_size=43, color=ACCENT).shift(DOWN * 0.75)
        arrow_1 = Arrow(marker.get_bottom(), interval.get_top(), buff=0.18, color=ACCENT, stroke_width=3)

        with self.narration(
            "Deux virgule quatre se trouve entre un et trois. Nous avons donc identifié le bon intervalle.",
        ):
            self.play(Create(arrow_1), Write(interval), run_time=1.4)
            self.wait(1.5)

        rule = MathTex("C(m)=8", font_size=45).next_to(interval, DOWN, buff=0.45)
        rule_box = SurroundingRectangle(rule, color=ACCENT, stroke_width=2.8, buff=0.18)

        with self.narration(
            "Cet intervalle sélectionne une seule règle : C de m égale huit.",
        ):
            self.play(Write(rule), Create(rule_box), run_time=1.3)
            self.wait(1.5)

        result = MathTex(r"C(2{,}4)=8\,\$", font_size=48, color=ACCENT).move_to(rule)

        with self.narration(
            "Il ne reste rien à essayer dans les deux autres formules. Le résultat est huit dollars.",
        ):
            self.play(FadeOut(rule_box), TransformMatchingTex(rule, result), run_time=1.3)
            self.wait(1.7)

        method = VGroup(
            Text("entrée", font_size=27),
            MathTex(r"\longrightarrow", font_size=35, color=ACCENT),
            Text("intervalle", font_size=27),
            MathTex(r"\longrightarrow", font_size=35, color=ACCENT),
            Text("règle", font_size=27),
            MathTex(r"\longrightarrow", font_size=35, color=ACCENT),
            Text("valeur", font_size=27),
        ).arrange(RIGHT, buff=0.14).to_edge(DOWN, buff=0.28)

        with self.narration(
            "Le raisonnement est toujours le même : l'entrée choisit l'intervalle, puis l'intervalle choisit la règle.",
        ):
            self.play(Write(method), run_time=1.8)
            self.wait(1.7)

        self.play(FadeOut(VGroup(subtitle, number_line, marker, marker_label, arrow_1, interval, result, method)), run_time=1.0)

    # ------------------------------------------------------------------
    # Act 4 — Build the graph using the same example, one piece at a time
    # ------------------------------------------------------------------
    def acte_4_construire_le_graphe(self) -> None:
        subtitle = Text("Le graphe se construit de la même façon", font_size=33).next_to(
            self.section_title, DOWN, buff=0.30
        )

        axes = Axes(
            x_range=[0, 5.5, 1],
            y_range=[0, 14, 2],
            x_length=9.0,
            y_length=4.4,
            axis_config={"color": BLACK, "stroke_width": 2.2, "include_ticks": True},
            tips=False,
        ).shift(DOWN * 0.78)
        labels = axes.get_axis_labels(
            MathTex("m", font_size=30),
            MathTex("C(m)", font_size=30),
        )

        segment_1 = Line(axes.c2p(0, 5), axes.c2p(1, 5), color=ACCENT, stroke_width=4)
        segment_2 = Line(axes.c2p(1, 8), axes.c2p(3, 8), color=ACCENT, stroke_width=4)
        segment_3 = Line(axes.c2p(3, 12), axes.c2p(5, 12), color=ACCENT, stroke_width=4)

        points_1 = VGroup(self.open_point(axes.c2p(0, 5)), self.closed_point(axes.c2p(1, 5)))
        points_2 = VGroup(self.open_point(axes.c2p(1, 8)), self.closed_point(axes.c2p(3, 8)))
        points_3 = VGroup(self.open_point(axes.c2p(3, 12)), self.closed_point(axes.c2p(5, 12)))

        active_rule = self.rule_line("C(m)=5", r"0<m\leq 1", font_size=34)
        active_rule.next_to(subtitle, DOWN, buff=0.28)

        with self.narration(
            "Pour tracer le graphe, nous reprenons les règles une par une. Commençons avec le tarif de cinq dollars.",
        ):
            self.play(Write(subtitle), run_time=0.9)
            self.play(Create(axes), FadeIn(labels), run_time=1.3)
            self.play(Write(active_rule), run_time=1.0)
            self.play(Create(segment_1), FadeIn(points_1), run_time=1.8)
            self.wait(1.5)

        next_rule = self.rule_line("C(m)=8", r"1<m\leq 3", font_size=34).move_to(active_rule)
        with self.narration(
            "Puis nous remplaçons seulement la règle active. Entre un et trois kilogrammes, le graphe est à la hauteur huit.",
        ):
            self.play(TransformMatchingTex(active_rule, next_rule), run_time=1.0)
            active_rule = next_rule
            self.play(Create(segment_2), FadeIn(points_2), run_time=1.9)
            self.wait(1.5)

        last_rule = self.rule_line("C(m)=12", r"3<m\leq 5", font_size=34).move_to(active_rule)
        with self.narration(
            "Enfin, le dernier intervalle donne un segment horizontal à la hauteur douze.",
        ):
            self.play(TransformMatchingTex(active_rule, last_rule), run_time=1.0)
            active_rule = last_rule
            self.play(Create(segment_3), FadeIn(points_3), run_time=1.9)
            self.wait(1.5)

        graph = VGroup(segment_1, segment_2, segment_3, points_1, points_2, points_3)
        conclusion = Text("Trois morceaux, mais un seul graphe.", font_size=29, color=ACCENT)
        conclusion.to_edge(DOWN, buff=0.28)

        with self.narration(
            "Les trois segments réunis forment le graphe d'une seule fonction.",
        ):
            self.play(FadeOut(active_rule), Write(conclusion), run_time=1.1)
            self.play(Indicate(graph, color=ACCENT, scale_factor=1.015), run_time=1.8)
            self.wait(1.7)

        self.play(FadeOut(VGroup(subtitle, axes, labels, graph, conclusion)), run_time=1.0)

    # ------------------------------------------------------------------
    # Act 5 — Explain one boundary without adding continuity terminology
    # ------------------------------------------------------------------
    def acte_5_lire_une_frontiere(self) -> None:
        subtitle = Text("À m=1, quel tarif faut-il prendre ?", font_size=33).next_to(
            self.section_title, DOWN, buff=0.30
        )

        conditions = VGroup(
            self.rule_line("C(m)=5", r"0<m\leq 1", font_size=39),
            self.rule_line("C(m)=8", r"1<m\leq 3", font_size=39),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.75).shift(UP * 0.25)

        with self.narration(
            "Regardons maintenant une frontière. À m égal un, les deux tarifs sont proches, mais un seul s'applique.",
        ):
            self.play(Write(subtitle), run_time=0.9)
            self.play(Write(conditions), run_time=1.6)
            self.wait(1.5)

        first_test = MathTex(r"0<1\leq 1", font_size=42, color=ACCENT).next_to(conditions[0], RIGHT, buff=0.65)
        first_box = SurroundingRectangle(conditions[0], color=ACCENT, stroke_width=2.8, buff=0.16)

        with self.narration(
            "La première condition contient le signe inférieur ou égal. Elle accepte donc m égal un.",
        ):
            self.play(Create(first_box), Write(first_test), run_time=1.3)
            self.wait(1.5)

        second_test = MathTex(r"1<1", font_size=42).next_to(conditions[1], RIGHT, buff=0.65)
        cross = Text("faux", font_size=27, color=ACCENT).next_to(second_test, DOWN, buff=0.15)

        with self.narration(
            "La deuxième condition exige que m soit strictement plus grand que un. Elle refuse donc cette valeur.",
        ):
            self.play(Write(second_test), Write(cross), run_time=1.2)
            self.wait(1.5)

        result = MathTex(r"C(1)=5\,\$", font_size=50, color=ACCENT).to_edge(DOWN, buff=0.42)

        with self.narration(
            "La valeur appartient donc au premier morceau, et C de un vaut cinq dollars.",
        ):
            self.play(Write(result), run_time=1.2)
            self.wait(1.8)

        self.play(FadeOut(VGroup(subtitle, conditions, first_test, first_box, second_test, cross, result)), run_time=1.0)

    # ------------------------------------------------------------------
    # Act 6 — A sparse final frame that answers the opening question
    # ------------------------------------------------------------------
    def acte_6_synthese(self) -> None:
        subtitle = Text("Idée essentielle", font_size=34).next_to(
            self.section_title, DOWN, buff=0.32
        )
        answer = Text(
            "Une fonction peut changer de formule selon l'entrée.",
            font_size=33,
            color=ACCENT,
        ).next_to(subtitle, DOWN, buff=0.55)

        flow = VGroup(
            MathTex("m", font_size=46),
            MathTex(r"\longrightarrow", font_size=42, color=ACCENT),
            Text("intervalle", font_size=30),
            MathTex(r"\longrightarrow", font_size=42, color=ACCENT),
            Text("tarif", font_size=30),
            MathTex(r"\longrightarrow", font_size=42, color=ACCENT),
            MathTex("C(m)", font_size=46),
        ).arrange(RIGHT, buff=0.18).move_to(DOWN * 0.35)

        with self.narration(
            "Répondons à la question du début. Une fonction peut changer de formule parce que l'entrée détermine d'abord son intervalle.",
        ):
            self.play(Write(subtitle), run_time=0.9)
            self.play(Write(answer), run_time=1.4)
            self.wait(1.4)

        with self.narration(
            "L'intervalle sélectionne alors une seule règle, et cette règle donne la valeur de la fonction.",
        ):
            self.play(Write(flow), run_time=2.0)
            self.wait(1.8)

        final = Text(
            "Une entrée → une règle active → une seule sortie",
            font_size=29,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.38)

        with self.narration(
            "Pour chaque entrée, une seule règle est active, et la fonction donne une seule sortie.",
        ):
            self.play(Write(final), run_time=1.4)
            self.wait(2.0)
