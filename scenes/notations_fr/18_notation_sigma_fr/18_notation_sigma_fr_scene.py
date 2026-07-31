from __future__ import annotations

from collections.abc import Iterator
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
Text.set_default(color=BLACK, font="Sans")
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
ERROR = RED_D
LIGHT_ACCENT = 0.10

I_SSML = tts.char("i")
F_SSML = tts.char("f")


SCRIPT = {
    "question": (
        "Comment écrire une longue addition sans recopier tous ses termes ? "
        "C'est la question à laquelle répond la notation sigma."
    ),
    "long_sum": (
        "Ici, on additionne tous les nombres impairs de un à cent quatre-vingt-dix-neuf. "
        "Il y a cent termes. L'écriture complète devient vite encombrante."
    ),
    "compact_need": (
        "Nous avons donc besoin d'une écriture compacte qui indique quoi calculer, "
        "où commencer et où s'arrêter."
    ),
    "symbol_origin": (
        "Le grand sigma est une lettre grecque correspondant au son s, comme dans somme. "
        "Le symbole rappelle donc l'opération que l'on veut effectuer."
    ),
    "decode_intro": (
        "Prenons un exemple plus court. Nous allons lire cette écriture un morceau à la fois."
    ),
    "decode_sum": "Le symbole sigma commande d'additionner les résultats.",
    "decode_start": f"En bas, {I_SSML} égale zéro donne la première valeur du compteur.",
    "decode_end": f"En haut, quatre donne la dernière valeur de {I_SSML}.",
    "decode_rule": f"À droite, deux {I_SSML} plus un est l'expression à calculer.",
    "decode_logic": (
        f"La logique est donc la suivante : faire varier {I_SSML} de zéro à quatre, "
        "calculer deux fois sa valeur plus un, puis additionner tous les résultats."
    ),
    "loop_start": (
        f"Rendons maintenant la boucle visible. Le compteur {I_SSML} prend d'abord la valeur zéro. "
        "Deux fois zéro plus un donne un."
    ),
    "loop_continue": (
        f"Puis {I_SSML} prend successivement un, deux, trois et quatre. "
        "On obtient alors trois, cinq, sept et neuf. "
        "Une seule nouvelle valeur est introduite à chaque passage."
    ),
    "values_ready": (
        "La notation a donc produit cinq valeurs : un, trois, cinq, sept et neuf. "
        "Il reste maintenant à les additionner."
    ),
    "accumulate": (
        "On peut suivre le total progressivement. Un plus trois donne quatre. "
        "Puis neuf, seize, et finalement vingt-cinq."
    ),
    "result": (
        "Ainsi, la somme de deux i plus un, pour i allant de zéro à quatre, vaut vingt-cinq."
    ),
    "index_warning": (
        f"Attention à une idée essentielle : {I_SSML} n'est pas une constante. "
        "Il change de valeur à chaque terme."
    ),
    "wrong_step": (
        "On ne peut donc pas écrire cinq fois la même expression deux i plus un. "
        "Cette écriture laisserait encore un i après avoir effectué la somme."
    ),
    "correct_expansion": (
        "La bonne expansion remplace i par zéro, puis un, et ainsi de suite jusqu'à quatre. "
        "Après le calcul, il ne reste plus de i."
    ),
    "product_intro": (
        "La même idée de compteur peut servir à une autre opération. "
        "Avec sigma, on additionne. Avec le grand pi, on multiplie."
    ),
    "sum_example": (
        "Pour i allant de un à quatre, la somme donne un plus deux plus trois plus quatre, donc dix."
    ),
    "product_example": (
        "Avec les mêmes valeurs de i, le produit donne un fois deux fois trois fois quatre, donc vingt-quatre."
    ),
    "summary": (
        f"À retenir : dans les deux notations, {I_SSML} parcourt les valeurs de a à b. "
        f"On calcule {F_SSML} de {I_SSML} à chaque étape. "
        "Sigma additionne les résultats, tandis que le grand pi les multiplie."
    ),
}


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class SigmaSommeBoucleFR(VoiceoverScene if VoiceoverScene is not None else Scene):
    """Comprendre les notations de somme et de produit comme des boucles.

    Learning objective:
        read the bounds, index, and expression in a finite sum; expand a
        concrete example; and distinguish summation from product notation.
    """

    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
        if load_dotenv is not None:
            load_dotenv()
        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:
            print("[voiceover] MANIM_DISABLE_VOICEOVER set. Rendering without narration.")
            return
        if VoiceoverScene is None or AzureService is None:
            print("[voiceover] manim-voiceover not installed. Rendering without narration.")
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

        try:
            self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        except Exception as exc:
            print(f"[voiceover] Azure setup failed: {exc}. Rendering without narration.")
            return
        self._voiceover_enabled = True

    @contextmanager
    def narration(self, spoken: str, caption: str | None = None) -> Iterator[object]:
        """Voiceover context with plain-text subtitles and a silent fallback."""
        if self._voiceover_enabled:
            ssml_text = tts.ssml(spoken)
            with self.voiceover(
                text=ssml_text,
                subcaption=caption if caption is not None else tts.strip_ssml(ssml_text),
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    @staticmethod
    def _fit_width(mobject: Mobject, margin: float = 1.0) -> Mobject:
        max_width = config.frame_width - margin
        if mobject.width > max_width:
            mobject.scale_to_fit_width(max_width)
        return mobject

    @staticmethod
    def _index_cell(value: int) -> VGroup:
        box = RoundedRectangle(
            width=1.05,
            height=0.78,
            corner_radius=0.08,
            stroke_color=GRAY_C,
            stroke_width=2,
            fill_color=WHITE,
            fill_opacity=1,
        )
        number = MathTex(str(value), font_size=39).move_to(box)
        return VGroup(box, number)

    @staticmethod
    def _value_cell(value: int) -> VGroup:
        box = RoundedRectangle(
            width=1.05,
            height=0.78,
            corner_radius=0.08,
            stroke_color=ACCENT,
            stroke_width=2.4,
            fill_color=ACCENT,
            fill_opacity=LIGHT_ACCENT,
        )
        number = MathTex(str(value), font_size=39, color=ACCENT).move_to(box)
        return VGroup(box, number)

    @staticmethod
    def _operation_card(title: str, formula: str, instruction: str) -> VGroup:
        box = RoundedRectangle(
            width=5.75,
            height=3.0,
            corner_radius=0.12,
            stroke_color=GRAY_C,
            stroke_width=2.5,
            fill_color=WHITE,
            fill_opacity=1,
        )

        heading = Text(title, font_size=34, color=ACCENT)
        heading.move_to(box.get_top() + DOWN * 0.42)

        expression = MathTex(formula, font_size=52)
        expression.next_to(heading, DOWN, buff=0.34)

        action = Text(instruction, font_size=27)
        action.next_to(expression, DOWN, buff=0.40)

        return VGroup(box, heading, expression, action)

    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        self.acte_1_le_besoin()
        self.acte_2_lire_la_notation()
        self.acte_3_boucle_visible()
        self.acte_4_additionner()
        self.acte_5_indice_variable()
        self.acte_6_somme_et_produit()
        self.acte_7_synthese()

        self.wait(1.5)

    # ------------------------------------------------------------------
    # Act 1 — Begin with the central question and the need for notation
    # ------------------------------------------------------------------
    def acte_1_le_besoin(self) -> None:
        question = Text(
            "Comment écrire une longue addition\nsans tout recopier ?",
            font_size=48,
            line_spacing=0.85,
        ).to_edge(UP, buff=0.58)

        long_sum = MathTex(
            "1", "+", "3", "+", "5", "+", "7", "+", "9", "+",
            r"\cdots", "+", "199",
            font_size=51,
        )
        self._fit_width(long_sum, margin=1.2)
        long_sum.move_to(DOWN * 0.05)

        hundred_terms = Text(
            "100 termes à additionner",
            font_size=32,
            color=ACCENT,
        ).next_to(long_sum, DOWN, buff=0.62)

        with self.narration(SCRIPT["question"]):
            self.play(Write(question), run_time=1.5)
            self.wait(0.7)

        with self.narration(SCRIPT["long_sum"]):
            self.play(
                LaggedStart(*[Write(part) for part in long_sum], lag_ratio=0.08),
                run_time=3.8,
            )
            self.play(FadeIn(hundred_terms, shift=UP * 0.12), run_time=0.8)
            self.wait(0.8)

        compact_prompt = Text(
            "Une consigne compacte doit remplacer la liste.",
            font_size=36,
            color=ACCENT,
        ).move_to(hundred_terms)

        with self.narration(SCRIPT["compact_need"]):
            self.play(Transform(hundred_terms, compact_prompt), run_time=0.9)
            self.wait(1.0)
            self.play(FadeOut(VGroup(question, long_sum, hundred_terms)), run_time=0.8)

        symbol_title = Text("Pourquoi la lettre sigma ?", font_size=43).to_edge(UP, buff=0.62)
        sigma_letter = MathTex(r"\Sigma", font_size=120)
        arrow = Arrow(LEFT * 0.7, RIGHT * 0.7, color=ACCENT, stroke_width=3)
        sum_word = Text("somme", font_size=48, color=ACCENT)
        symbol_link = VGroup(sigma_letter, arrow, sum_word).arrange(RIGHT, buff=0.45)
        symbol_link.move_to(DOWN * 0.15)

        with self.narration(SCRIPT["symbol_origin"]):
            self.play(Write(symbol_title), run_time=1.0)
            self.play(Write(sigma_letter), run_time=0.9)
            self.play(GrowArrow(arrow), FadeIn(sum_word, shift=LEFT * 0.10), run_time=1.0)
            self.wait(1.0)

        self.play(FadeOut(VGroup(symbol_title, symbol_link)), run_time=0.8)

    # ------------------------------------------------------------------
    # Act 2 — Decode one part at a time
    # ------------------------------------------------------------------
    def acte_2_lire_la_notation(self) -> None:
        decode_title = Text("Que commande cette écriture ?", font_size=46).to_edge(UP, buff=0.62)

        sigma = MathTex(
            r"\sum",
            r"_{i=0}",
            r"^{4}",
            r"(2i+1)",
            font_size=72,
        ).move_to(UP * 0.15)

        descriptions = [
            "additionner les résultats",
            "première valeur : i = 0",
            "dernière valeur : i = 4",
            "expression à calculer : 2i + 1",
        ]
        narration_keys = ["decode_sum", "decode_start", "decode_end", "decode_rule"]

        description = Text(descriptions[0], font_size=35, color=ACCENT)
        description.next_to(sigma, DOWN, buff=0.92)
        focus = SurroundingRectangle(sigma[0], color=ACCENT, stroke_width=3, buff=0.12)

        with self.narration(SCRIPT["decode_intro"]):
            self.play(Write(decode_title), run_time=1.0)
            self.play(Write(sigma), run_time=1.5)
            self.wait(0.7)

        with self.narration(SCRIPT[narration_keys[0]]):
            self.play(Create(focus), FadeIn(description), run_time=0.8)
            self.wait(0.8)

        for part, text, key in zip(sigma[1:], descriptions[1:], narration_keys[1:]):
            next_focus = SurroundingRectangle(part, color=ACCENT, stroke_width=3, buff=0.12)
            next_description = Text(text, font_size=35, color=ACCENT).move_to(description)
            with self.narration(SCRIPT[key]):
                self.play(
                    Transform(focus, next_focus),
                    Transform(description, next_description),
                    run_time=0.85,
                )
                self.wait(0.8)

        instruction = Text(
            "faire varier i  →  calculer 2i + 1  →  additionner",
            font_size=31,
            color=ACCENT,
        ).move_to(description)
        self._fit_width(instruction, margin=1.0)

        with self.narration(SCRIPT["decode_logic"]):
            self.play(FadeOut(focus), Transform(description, instruction), run_time=0.8)
            self.wait(1.0)

        self.play(
            FadeOut(VGroup(decode_title, description)),
            sigma.animate.scale(0.72).to_edge(UP, buff=0.45),
            run_time=0.85,
        )
        self.sigma_example = sigma

    # ------------------------------------------------------------------
    # Act 3 — Make the counter and produced values visible
    # ------------------------------------------------------------------
    def acte_3_boucle_visible(self) -> None:
        sigma = self.sigma_example
        loop_title = Text("Le compteur i parcourt cinq valeurs", font_size=38)
        loop_title.next_to(sigma, DOWN, buff=0.40)

        index_label = Text("valeur de i", font_size=27).to_edge(LEFT, buff=0.70).shift(UP * 0.25)
        value_label = Text("valeur de 2i + 1", font_size=27).to_edge(LEFT, buff=0.70).shift(DOWN * 0.75)

        index_cells = VGroup(*[self._index_cell(i) for i in range(5)]).arrange(RIGHT, buff=0.32)
        index_cells.shift(RIGHT * 1.25 + UP * 0.25)

        values = [1, 3, 5, 7, 9]
        value_cells = VGroup(*[self._value_cell(value) for value in values]).arrange(RIGHT, buff=0.32)
        value_cells.shift(RIGHT * 1.25 + DOWN * 0.75)
        for cell in value_cells:
            cell.set_opacity(0)

        active = SurroundingRectangle(index_cells[0], color=ACCENT, stroke_width=4, buff=0.08)
        rule = MathTex(r"2\cdot 0+1=1", font_size=44)
        rule.next_to(value_cells, DOWN, buff=0.58)

        with self.narration(SCRIPT["loop_start"]):
            self.play(Write(loop_title), run_time=0.9)
            self.play(
                FadeIn(index_label),
                LaggedStart(*[FadeIn(cell, shift=UP * 0.10) for cell in index_cells], lag_ratio=0.10),
                run_time=1.4,
            )
            self.play(FadeIn(value_label), Create(active), Write(rule), run_time=1.0)
            self.play(value_cells[0].animate.set_opacity(1), run_time=0.65)
            self.wait(0.8)

        with self.narration(SCRIPT["loop_continue"]):
            for i, value in enumerate(values[1:], start=1):
                next_active = SurroundingRectangle(
                    index_cells[i], color=ACCENT, stroke_width=4, buff=0.08
                )
                next_rule = MathTex(rf"2\cdot {i}+1={value}", font_size=44).move_to(rule)
                self.play(
                    Transform(active, next_active),
                    Transform(rule, next_rule),
                    value_cells[i].animate.set_opacity(1),
                    run_time=0.95,
                )
                self.wait(0.45)
            self.wait(0.8)

        produced_values = MathTex("1", "+", "3", "+", "5", "+", "7", "+", "9", font_size=54)
        produced_values.move_to(DOWN * 0.15)

        with self.narration(SCRIPT["values_ready"]):
            self.play(
                FadeOut(VGroup(loop_title, index_label, value_label, index_cells, active, rule)),
                ReplacementTransform(value_cells, produced_values),
                sigma.animate.move_to(UP * 1.65),
                run_time=1.1,
            )
            self.wait(1.0)

        self.produced_values = produced_values

    # ------------------------------------------------------------------
    # Act 4 — Accumulate the values and return to the compact notation
    # ------------------------------------------------------------------
    def acte_4_additionner(self) -> None:
        produced_values = self.produced_values
        total_title = Text("Additionnons les valeurs obtenues", font_size=36)
        total_title.next_to(produced_values, DOWN, buff=0.65)

        running_total = MathTex("1", font_size=54)
        running_total.next_to(total_title, DOWN, buff=0.52)

        equations = [r"1+3=4", r"4+5=9", r"9+7=16", r"16+9=25"]

        with self.narration(SCRIPT["accumulate"]):
            self.play(Write(total_title), Write(running_total), run_time=1.0)
            self.wait(0.55)
            for equation in equations:
                next_total = MathTex(equation, font_size=54).move_to(running_total)
                self.play(Transform(running_total, next_total), run_time=0.8)
                self.wait(0.45)
            self.wait(0.8)

        result = MathTex(r"\sum_{i=0}^{4}(2i+1)=25", font_size=57)
        result.move_to(DOWN * 0.15)
        result_box = SurroundingRectangle(result, color=ACCENT, stroke_width=3, buff=0.22)

        with self.narration(SCRIPT["result"]):
            self.play(
                FadeOut(VGroup(produced_values, total_title)),
                Transform(running_total, result),
                run_time=1.0,
            )
            self.play(Create(result_box), run_time=0.65)
            self.wait(1.1)

        self.play(
            FadeOut(VGroup(self.sigma_example, running_total, result_box)),
            run_time=0.8,
        )

    # ------------------------------------------------------------------
    # Act 5 — Common error: treating the index as a constant
    # ------------------------------------------------------------------
    def acte_5_indice_variable(self) -> None:
        index_title = Text("L'indice i change à chaque terme", font_size=44).to_edge(UP, buff=0.62)
        index_motion = MathTex(
            r"i:\quad 0\longrightarrow1\longrightarrow2\longrightarrow3\longrightarrow4",
            font_size=46,
        ).move_to(UP * 0.75)
        counter_statement = Text(
            "Après la somme, il ne doit plus rester de i.",
            font_size=33,
            color=ACCENT,
        ).next_to(index_motion, DOWN, buff=0.55)

        with self.narration(SCRIPT["index_warning"]):
            self.play(Write(index_title), run_time=0.9)
            self.play(Write(index_motion), run_time=1.3)
            self.play(FadeIn(counter_statement, shift=UP * 0.10), run_time=0.8)
            self.wait(0.9)

        wrong = MathTex(r"\sum_{i=0}^{4}(2i+1)=5(2i+1)", font_size=45)
        wrong.next_to(counter_statement, DOWN, buff=0.62)
        wrong_label = Text(
            "Faux : le même i n'est pas utilisé cinq fois.",
            font_size=29,
            color=ERROR,
        ).next_to(wrong, DOWN, buff=0.30)
        strike = Line(
            wrong.get_left() + LEFT * 0.08,
            wrong.get_right() + RIGHT * 0.08,
            color=ERROR,
            stroke_width=5,
        )

        with self.narration(SCRIPT["wrong_step"]):
            self.play(Write(wrong), run_time=1.0)
            self.play(Create(strike), FadeIn(wrong_label), run_time=0.75)
            self.wait(1.0)

        correct = MathTex(
            r"(2\cdot0+1)+(2\cdot1+1)+\cdots+(2\cdot4+1)",
            font_size=42,
        )
        self._fit_width(correct, margin=1.0)
        correct.move_to(wrong)
        correct_label = Text(
            "Chaque terme utilise la valeur suivante de i.",
            font_size=30,
            color=ACCENT,
        ).move_to(wrong_label)

        with self.narration(SCRIPT["correct_expansion"]):
            self.play(
                FadeOut(strike),
                Transform(wrong, correct),
                Transform(wrong_label, correct_label),
                run_time=1.1,
            )
            self.wait(1.2)

        self.play(
            FadeOut(VGroup(index_title, index_motion, counter_statement, wrong, wrong_label)),
            run_time=0.8,
        )

    # ------------------------------------------------------------------
    # Act 6 — Same counter, different operation
    # ------------------------------------------------------------------
    def acte_6_somme_et_produit(self) -> None:
        operation_title = Text("Même compteur, autre opération", font_size=44).to_edge(UP, buff=0.62)
        shared_counter = MathTex(r"i=1,\ 2,\ 3,\ 4", font_size=43, color=ACCENT)
        shared_counter.next_to(operation_title, DOWN, buff=0.45)

        with self.narration(SCRIPT["product_intro"]):
            self.play(Write(operation_title), run_time=0.9)
            self.play(Write(shared_counter), run_time=1.0)
            self.wait(0.8)

        sum_example = MathTex(
            r"\sum_{i=1}^{4}i", "=", "1+2+3+4", "=", "10",
            font_size=47,
        ).move_to(UP * 0.05)
        sum_caption = Text("Sigma : additionner", font_size=29, color=ACCENT)
        sum_caption.next_to(sum_example, DOWN, buff=0.28)

        with self.narration(SCRIPT["sum_example"]):
            self.play(Write(sum_example), run_time=1.4)
            self.play(FadeIn(sum_caption, shift=UP * 0.08), run_time=0.65)
            self.wait(0.9)

        product_example = MathTex(
            r"\prod_{i=1}^{4}i", "=", r"1\cdot2\cdot3\cdot4", "=", "24",
            font_size=47,
        ).move_to(DOWN * 1.55)
        product_caption = Text("Grand pi : multiplier", font_size=29, color=ACCENT)
        product_caption.next_to(product_example, DOWN, buff=0.28)

        with self.narration(SCRIPT["product_example"]):
            self.play(Write(product_example), run_time=1.4)
            self.play(FadeIn(product_caption, shift=UP * 0.08), run_time=0.65)
            self.wait(1.0)

        self.play(
            FadeOut(
                VGroup(
                    operation_title,
                    shared_counter,
                    sum_example,
                    sum_caption,
                    product_example,
                    product_caption,
                )
            ),
            run_time=0.8,
        )

    # ------------------------------------------------------------------
    # Act 7 — Stable final summary
    # ------------------------------------------------------------------
    def acte_7_synthese(self) -> None:
        summary_title = Text("Deux boucles, une même logique", font_size=46).to_edge(UP, buff=0.52)

        sum_card = self._operation_card(
            "Somme",
            r"\sum_{i=a}^{b}f(i)",
            "calculer f(i), puis additionner",
        )
        product_card = self._operation_card(
            "Produit",
            r"\prod_{i=a}^{b}f(i)",
            "calculer f(i), puis multiplier",
        )
        cards = VGroup(sum_card, product_card).arrange(RIGHT, buff=0.50)
        cards.next_to(summary_title, DOWN, buff=0.48)

        index_warning = Text(
            "Dans les deux cas, l'indice i change à chaque terme.",
            font_size=31,
            color=ACCENT,
        )
        self._fit_width(index_warning, margin=1.0)
        index_warning.next_to(cards, DOWN, buff=0.38)

        index_values = MathTex(r"i=a,\ a+1,\ \ldots,\ b", font_size=40)
        index_values.next_to(index_warning, DOWN, buff=0.22)

        with self.narration(SCRIPT["summary"]):
            self.play(Write(summary_title), run_time=0.9)
            self.play(FadeIn(sum_card, shift=RIGHT * 0.12), run_time=0.9)
            self.wait(0.45)
            self.play(FadeIn(product_card, shift=LEFT * 0.12), run_time=0.9)
            self.wait(0.45)
            self.play(FadeIn(index_warning, shift=UP * 0.10), run_time=0.75)
            self.play(Write(index_values), run_time=0.75)
            self.wait(1.8)
