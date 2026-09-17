"""Permutation, arrangement ou combinaison ? — MAT0339, deuxième passe.

Capsule de dénombrement sans répétition.  La scène fait émerger les trois
modèles à partir de situations concrètes, dérive les formules seulement après
l'intuition, puis traite explicitement l'erreur « diviser par r! dès que l'on
choisit r objets ».
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GRAY_B,
    GRAY_D,
    LEFT,
    RED_D,
    RIGHT,
    UP,
    WHITE,
    Arrow,
    Circumscribe,
    Create,
    Cross,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    Mobject,
    ReplacementTransform,
    RoundedRectangle,
    Scene,
    SurroundingRectangle,
    Tex,
    Text,
    Transform,
    TransformFromCopy,
    Underline,
    VGroup,
    Write,
    config,
)

try:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.azure import AzureService
except ImportError:
    VoiceoverScene = None
    AzureService = None

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
ERROR = RED_D
SOFT = GRAY_D
PALE = GRAY_B
VOICE_SPEED = 0.82
SAFE_WIDTH = config.frame_width - 1.0

A_SPOKEN = tts.char("A")
B_SPOKEN = tts.char("B")
C_SPOKEN = tts.char("C")
N_SPOKEN = tts.char("n")
R_SPOKEN = tts.char("r")


SCRIPT_SEGMENTS: list[dict[str, str]] = [
    {
        "name": "intro",
        "caption": "Trois personnes parmi cinq : 60 ou 10 selon le rôle de l'ordre.",
        "ssml": tts.ssml(
            "On choisit trois personnes parmi cinq. Combien de résultats sont possibles ? "
            "<bookmark mark='intro_cards'/> "
            "Voici les cinq personnes disponibles. <break time='250ms'/> "
            "<bookmark mark='intro_two_answers'/> "
            "Soixante peut être correct. Dix peut aussi être correct. "
            "Ce ne sont pas deux calculs concurrents : ce sont deux questions différentes. "
            "<bookmark mark='intro_order_question'/> "
            "La question décisive est : est-ce que l'ordre compte ? "
            "Dans toute cette capsule, on travaille sans répétition : une même personne ne peut pas être choisie deux fois."
        ),
    },
    {
        "name": "arrangement",
        "caption": "Arrangement : on choisit r éléments parmi n et leurs positions comptent.",
        "ssml": tts.ssml(
            "Commençons par un podium. Il faut attribuer la première, la deuxième et la troisième place. "
            "<bookmark mark='arr_two_podiums'/> "
            f"Le podium {A_SPOKEN}, {B_SPOKEN}, {C_SPOKEN} n'est pas le même que le podium "
            f"{B_SPOKEN}, {A_SPOKEN}, {C_SPOKEN}. Les positions ont un rôle. "
            "<bookmark mark='arr_count_slots'/> "
            "Pour la première place, cinq choix. Une personne est utilisée, donc quatre choix pour la deuxième, puis trois pour la troisième. "
            "<bookmark mark='arr_specific_formula'/> "
            "On obtient cinq fois quatre fois trois, donc soixante. On note ce nombre A indice cinq exposant trois. "
            "<bookmark mark='arr_general_formula'/> "
            f"En général, pour ordonner {R_SPOKEN} éléments choisis parmi {N_SPOKEN}, on multiplie "
            f"{N_SPOKEN}, puis {N_SPOKEN} moins un, et ainsi de suite. Cela donne "
            f"{N_SPOKEN} factorielle, divisé par la factorielle de {N_SPOKEN} moins {R_SPOKEN}. "
            "C'est un arrangement."
        ),
    },
    {
        "name": "combination",
        "caption": "Combinaison : les mêmes r éléments forment un seul groupe, quel que soit leur ordre.",
        "ssml": tts.ssml(
            "Formons maintenant un comité de trois personnes. Il n'y a ni première, ni deuxième, ni troisième place. "
            "<bookmark mark='comb_same_group'/> "
            f"Le groupe contenant {A_SPOKEN}, {B_SPOKEN} et {C_SPOKEN} reste le même quand on réécrit ses membres dans un autre ordre. "
            "<bookmark mark='comb_six_orders'/> "
            "Pour ces trois personnes, il existe trois factorielle, donc six ordres possibles. "
            "Dans le calcul des arrangements, le même comité a donc été compté six fois. "
            "<bookmark mark='comb_specific_formula'/> "
            "On corrige ce surcomptage en divisant soixante par trois factorielle. Il reste dix comités. "
            "<bookmark mark='comb_general_formula'/> "
            f"En général, une combinaison vaut l'arrangement divisé par {R_SPOKEN} factorielle. "
            f"On obtient {N_SPOKEN} factorielle, divisé par le produit de {R_SPOKEN} factorielle "
            f"et de la factorielle de {N_SPOKEN} moins {R_SPOKEN}."
        ),
    },
    {
        "name": "permutation",
        "caption": "Permutation : tous les n éléments sont utilisés et l'ordre compte.",
        "ssml": tts.ssml(
            "Troisième situation : ranger les cinq personnes dans une file. Cette fois, tout le monde est utilisé. "
            "<bookmark mark='perm_fill_slots'/> "
            "Il y a cinq choix pour la première position, puis quatre, trois, deux et un. "
            "<bookmark mark='perm_specific_formula'/> "
            "Le produit est cinq factorielle, donc cent vingt. "
            "<bookmark mark='perm_general_formula'/> "
            f"Une permutation est le cas particulier où l'on ordonne les {N_SPOKEN} éléments disponibles. "
            f"Ainsi, P indice {N_SPOKEN} égale A indice {N_SPOKEN} exposant {N_SPOKEN}, égale {N_SPOKEN} factorielle."
        ),
    },
    {
        "name": "common_error",
        "caption": "Erreur fréquente : ne pas diviser par r! lorsque les rôles sont distincts.",
        "ssml": tts.ssml(
            "Voici une erreur fréquente. Pour trois médailles parmi douze finalistes, "
            "<bookmark mark='error_wrong_formula'/> "
            "on calcule douze fois onze fois dix, puis on divise par trois factorielle. "
            "Cette division est injustifiée. Elle fusionne six podiums réellement différents. "
            "<bookmark mark='error_distinct_roles'/> "
            "Échanger l'or et l'argent change le résultat. Le bon modèle est donc un arrangement : douze fois onze fois dix, soit mille trois cent vingt. "
            "<bookmark mark='error_contrast_committee'/> "
            "Le nombre deux cent vingt est correct pour une autre question : choisir un comité de trois personnes parmi douze. "
            "On ne divise par trois factorielle que lorsque les six ordres décrivent le même résultat."
        ),
    },
    {
        "name": "decision",
        "caption": "Décision : ordre d'abord, puis utilisation de tous les éléments.",
        "ssml": tts.ssml(
            "Pour choisir le bon modèle, posez deux questions dans cet ordre. "
            "<bookmark mark='tree_first_question'/> "
            "Première question : l'ordre compte-t-il ? Si non, c'est une combinaison. "
            "<bookmark mark='tree_second_question'/> "
            "Si l'ordre compte, demandez : utilise-t-on tous les éléments ? "
            "<bookmark mark='tree_leaves'/> "
            "Si non, c'est un arrangement. Si oui, c'est une permutation."
        ),
    },
    {
        "name": "quiz",
        "caption": "Mini-quiz : classer la situation avant de calculer.",
        "ssml": tts.ssml(
            "À vous de classer trois situations. "
            "<bookmark mark='quiz_one'/> "
            "Choisir quatre représentants parmi douze étudiants. "
            "<break time='900ms'/> <bookmark mark='quiz_one_answer'/> "
            "Comme l'ordre ne compte pas, c'est une combinaison. "
            "Attribuer trois rôles différents parmi douze personnes. "
            "<break time='900ms'/> <bookmark mark='quiz_two_answer'/> "
            "Les rôles comptent, mais neuf personnes ne sont pas utilisées : arrangement. "
            "Ranger six livres distincts sur une tablette. "
            "<break time='900ms'/> <bookmark mark='quiz_three_answer'/> "
            "Tous les livres sont utilisés et l'ordre compte : permutation."
        ),
    },
    {
        "name": "conclusion",
        "caption": "Résumé sans répétition : arrangement, combinaison, permutation.",
        "ssml": tts.ssml(
            f"Dans les formules, {N_SPOKEN} est le nombre d'éléments disponibles, et {R_SPOKEN} le nombre d'éléments choisis. "
            "<bookmark mark='recap_definitions'/> "
            "Voici les trois cas. <bookmark mark='recap_rows'/> "
            "Arrangement : l'ordre compte et on utilise seulement une partie des éléments. "
            "Combinaison : l'ordre ne compte pas. "
            "Permutation : l'ordre compte et tous les éléments sont utilisés. "
            "<bookmark mark='recap_final'/> "
            "Retenez surtout la logique : ordre, puis nombre d'éléments utilisés."
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


BaseScene = VoiceoverScene if VoiceoverScene is not None else Scene


class PermutationArrangementCombinaisonFR(BaseScene):
    """Distinguer les trois modèles classiques de dénombrement sans répétition."""

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
            self.set_speech_service(
                AzureService(voice=tts.VOICE_ID, global_speed=VOICE_SPEED)
            )
        except Exception as exc:
            print(f"[voiceover] Azure Speech setup failed: {exc}. Rendering without narration.")
            return

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
        self.arrangement_segment()
        self.combination_segment()
        self.permutation_segment()
        self.common_error_segment()
        self.decision_segment()
        self.quiz_segment()
        self.conclusion_segment()
        self.wait(1.2)

    # ------------------------------------------------------------------
    # Shared visual builders
    # ------------------------------------------------------------------
    def _fit_width(self, mob: Mobject, width: float = SAFE_WIDTH) -> Mobject:
        if mob.width > width:
            mob.scale_to_fit_width(width)
        return mob

    def _title(self, title: str, subtitle: str | None = None) -> VGroup:
        main = self._fit_width(Text(title, font_size=44))
        if subtitle is None:
            return VGroup(main).to_edge(UP, buff=0.42)

        sub = self._fit_width(Text(subtitle, font_size=25, color=SOFT), SAFE_WIDTH - 0.2)
        return VGroup(main, sub).arrange(DOWN, buff=0.12).to_edge(UP, buff=0.3)

    def _pill(
        self,
        text: str,
        *,
        color=ACCENT,
        font_size: int = 28,
        fill_opacity: float = 0.045,
    ) -> VGroup:
        label = Text(text, font_size=font_size, color=color)
        box = RoundedRectangle(
            width=max(1.65, label.width + 0.48),
            height=max(0.54, label.height + 0.22),
            corner_radius=0.15,
            stroke_color=color,
            stroke_width=2,
        )
        box.set_fill(color, opacity=fill_opacity)
        label.move_to(box)
        return VGroup(box, label)

    def _person_card(
        self,
        letter: str,
        *,
        width: float = 0.82,
        height: float = 0.96,
        color=ACCENT,
        font_size: int = 33,
    ) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.1,
            stroke_color=color,
            stroke_width=2.3,
        )
        box.set_fill(color, opacity=0.055)
        label = Text(letter, font_size=font_size)
        label.move_to(box)
        return VGroup(box, label)

    def _card_row(self, letters: str = "ABCDE", *, scale: float = 1.0) -> VGroup:
        row = VGroup(*[self._person_card(letter) for letter in letters])
        row.arrange(RIGHT, buff=0.22)
        row.scale(scale)
        return row

    def _slot(self, label: str, *, width: float = 0.9, height: float = 1.05) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.08,
            stroke_color=PALE,
            stroke_width=2,
        )
        text = Text(label, font_size=23, color=SOFT).next_to(box, UP, buff=0.09)
        return VGroup(box, text)

    def _podium(self, letters: str, caption: str) -> VGroup:
        slots = VGroup(self._slot("1re"), self._slot("2e"), self._slot("3e"))
        slots.arrange(RIGHT, buff=0.18)
        cards = VGroup(*[self._person_card(letter, width=0.72, height=0.84) for letter in letters])
        for card, slot in zip(cards, slots):
            card.move_to(slot[0])
        word = MathTex(letters, font_size=39).next_to(slots, DOWN, buff=0.22)
        note = Text(caption, font_size=22, color=SOFT).next_to(word, DOWN, buff=0.09)
        return VGroup(slots, cards, word, note)

    def _formula_card(
        self,
        formula: str,
        note: str,
        *,
        color=ACCENT,
        width: float = 8.3,
        formula_size: int = 48,
    ) -> VGroup:
        math = MathTex(formula, font_size=formula_size)
        detail = Text(note, font_size=24, color=SOFT)
        content = VGroup(math, detail).arrange(DOWN, buff=0.15)
        box = RoundedRectangle(
            width=max(width, content.width + 0.55),
            height=max(1.25, content.height + 0.38),
            corner_radius=0.13,
            stroke_color=color,
            stroke_width=2.2,
        )
        box.set_fill(color, opacity=0.035)
        content.move_to(box)
        return VGroup(box, content)

    def _scenario_panel(self, text: str) -> VGroup:
        label = Text(text, font_size=31, line_spacing=0.9)
        self._fit_width(label, 10.2)
        panel = RoundedRectangle(
            width=max(8.0, label.width + 0.75),
            height=max(1.28, label.height + 0.5),
            corner_radius=0.14,
            stroke_color=BLACK,
            stroke_width=2.1,
        )
        panel.set_fill(WHITE, opacity=1)
        label.move_to(panel)
        return VGroup(panel, label)

    def _summary_row(self, name: str, condition: str, formula: str) -> VGroup:
        name_text = Text(name, font_size=29, color=ACCENT)
        condition_text = Text(condition, font_size=25, color=BLACK)
        formula_text = MathTex(formula, font_size=39)

        name_text.move_to(LEFT * 4.35)
        condition_text.move_to(LEFT * 0.45)
        formula_text.move_to(RIGHT * 4.15)

        divider_1 = Line(LEFT * 2.65, LEFT * 2.65 + UP * 0.65, color=PALE, stroke_width=1.5)
        divider_1.shift(DOWN * 0.325)
        divider_2 = Line(RIGHT * 2.25, RIGHT * 2.25 + UP * 0.65, color=PALE, stroke_width=1.5)
        divider_2.shift(DOWN * 0.325)

        content = VGroup(name_text, condition_text, formula_text, divider_1, divider_2)
        box = RoundedRectangle(
            width=12.15,
            height=0.95,
            corner_radius=0.1,
            stroke_color=BLACK,
            stroke_width=1.8,
        )
        box.set_fill(ACCENT, opacity=0.018)
        return VGroup(box, content)

    def _clear(self, *mobjects: Mobject, run_time: float = 0.65) -> None:
        visible = [mob for mob in mobjects if mob is not None]
        if visible:
            self.play(*[FadeOut(mob) for mob in visible], run_time=run_time)

    # ------------------------------------------------------------------
    # Segments
    # ------------------------------------------------------------------
    def intro_segment(self) -> None:
        title = self._title(
            "Dénombrement 2 — permutation, arrangement ou combinaison ?",
            "Même sélection, réponses différentes — sans répétition",
        )
        question = Text("Choisir 3 personnes parmi 5", font_size=37).move_to(UP * 1.25)
        cards = self._card_row().move_to(UP * 0.05)

        answer_60 = self._pill("60 résultats", font_size=31)
        answer_10 = self._pill("10 résultats", font_size=31)
        answers = VGroup(answer_60, answer_10).arrange(RIGHT, buff=1.0).move_to(DOWN * 1.2)

        key_question = Text("Est-ce que l'ordre compte ?", font_size=42, color=ACCENT)
        key_question.move_to(DOWN * 2.4)
        underline = Underline(key_question, color=ACCENT, buff=0.08)

        with self.narrated(SCRIPT_SEGMENTS[0]):
            self.play(FadeIn(title), Write(question), run_time=1.0)
            self.wait_until_bookmark("intro_cards")
            self.play(
                LaggedStart(*[FadeIn(card, shift=0.1 * UP) for card in cards], lag_ratio=0.12),
                run_time=1.45,
            )
            self.wait_until_bookmark("intro_two_answers")
            self.play(FadeIn(answers, shift=0.1 * UP), run_time=0.9)
            self.wait_until_bookmark("intro_order_question")
            self.play(Write(key_question), Create(underline), run_time=1.0)
            self.wait(1.0)

        self._clear(title, question, cards, answers, key_question, underline)

    def arrangement_segment(self) -> None:
        title = self._title("Arrangement", "Une partie des éléments est choisie et l'ordre compte")
        badge = self._pill("ordre important", font_size=25).next_to(title, DOWN, buff=0.22)

        podium_abc = self._podium("ABC", "A est premier")
        podium_bac = self._podium("BAC", "B est premier")
        podiums = VGroup(podium_abc, podium_bac).arrange(RIGHT, buff=1.55).move_to(DOWN * 0.05)
        not_equal = MathTex(r"\neq", font_size=52, color=ACCENT).move_to(
            (podium_abc.get_right() + podium_bac.get_left()) / 2
        )

        candidates = self._card_row().scale(0.84).move_to(UP * 1.05)
        slots = VGroup(self._slot("1re"), self._slot("2e"), self._slot("3e"))
        slots.arrange(RIGHT, buff=0.35).move_to(DOWN * 0.05)
        choice_numbers = VGroup(
            MathTex("5", font_size=38, color=ACCENT),
            MathTex("4", font_size=38, color=ACCENT),
            MathTex("3", font_size=38, color=ACCENT),
        )
        choice_notes = VGroup(
            Text("choix", font_size=20, color=SOFT),
            Text("choix", font_size=20, color=SOFT),
            Text("choix", font_size=20, color=SOFT),
        )
        for number, note, slot in zip(choice_numbers, choice_notes, slots):
            number.next_to(slot[0], DOWN, buff=0.16)
            note.next_to(number, DOWN, buff=0.03)

        specific = self._formula_card(
            r"A_5^3=5\times4\times3=60",
            "5 disponibles, 3 positions distinctes",
            width=7.7,
        ).move_to(DOWN * 1.85)
        general = self._formula_card(
            r"A_n^r=n(n-1)\cdots(n-r+1)=\frac{n!}{(n-r)!}",
            "pour 0 ≤ r ≤ n",
            width=10.8,
            formula_size=43,
        ).move_to(DOWN * 2.05)

        with self.narrated(SCRIPT_SEGMENTS[1]):
            self.play(FadeIn(title), FadeIn(badge), run_time=0.8)
            self.wait_until_bookmark("arr_two_podiums")
            self.play(
                LaggedStart(FadeIn(podium_abc), FadeIn(podium_bac), lag_ratio=0.25),
                FadeIn(not_equal),
                run_time=1.45,
            )
            self.play(
                Indicate(podium_abc[1][0], color=ACCENT, scale_factor=1.04),
                Indicate(podium_bac[1][0], color=ACCENT, scale_factor=1.04),
                run_time=0.85,
            )

            self.wait_until_bookmark("arr_count_slots")
            self.play(FadeOut(podiums), FadeOut(not_equal), run_time=0.55)
            self.play(FadeIn(candidates), FadeIn(slots), run_time=0.85)
            for index, number in enumerate(choice_numbers):
                self.play(
                    Indicate(slots[index][0], color=ACCENT, scale_factor=1.03),
                    FadeIn(number, shift=0.08 * UP),
                    FadeIn(choice_notes[index]),
                    run_time=0.7,
                )

            self.wait_until_bookmark("arr_specific_formula")
            self.play(FadeIn(specific, shift=0.1 * UP), run_time=0.9)
            self.play(Indicate(specific[1][0], color=ACCENT, scale_factor=1.025), run_time=0.7)

            self.wait_until_bookmark("arr_general_formula")
            self.play(
                FadeOut(candidates),
                FadeOut(slots),
                FadeOut(choice_numbers),
                FadeOut(choice_notes),
                FadeOut(specific), FadeIn(general, shift=0.08 * UP),
                run_time=1.0,
            )
            self.wait(1.1)

        self._clear(title, badge, general)

    def combination_segment(self) -> None:
        title = self._title("Combinaison", "Une partie des éléments est choisie, sans tenir compte de l'ordre")
        badge = self._pill("ordre non important", font_size=25).next_to(title, DOWN, buff=0.22)

        committee_box = RoundedRectangle(
            width=3.55,
            height=1.2,
            corner_radius=0.16,
            stroke_color=ACCENT,
            stroke_width=2.3,
        )
        committee_box.set_fill(ACCENT, opacity=0.035)
        committee_cards = VGroup(*[self._person_card(letter, width=0.7, height=0.8) for letter in "ABC"])
        committee_cards.arrange(RIGHT, buff=0.25).move_to(committee_box)
        committee = VGroup(committee_box, committee_cards).move_to(UP * 1.05)
        committee_label = Text("un comité", font_size=24, color=SOFT).next_to(committee, UP, buff=0.08)

        set_equality = MathTex(r"\{A,B,C\}=\{B,A,C\}", font_size=43).move_to(DOWN * 0.1)

        orderings = VGroup(
            *[MathTex(word, font_size=31) for word in ("ABC", "ACB", "BAC", "BCA", "CAB", "CBA")]
        )
        orderings.arrange_in_grid(rows=2, cols=3, buff=(0.75, 0.28)).move_to(UP * 0.05)
        orders_box = SurroundingRectangle(orderings, color=PALE, stroke_width=1.7, buff=0.2)
        down_arrow = MathTex(r"\Downarrow", font_size=45, color=ACCENT).next_to(orders_box, DOWN, buff=0.08)
        one_group = self._pill("1 seul comité", font_size=28).next_to(down_arrow, DOWN, buff=0.08)
        factorial_note = MathTex(r"3!=6", font_size=39, color=ACCENT).next_to(orders_box, RIGHT, buff=0.42)

        specific = self._formula_card(
            r"C_5^3=\frac{A_5^3}{3!}=\frac{60}{6}=10",
            "on retire les 6 ordres du même groupe",
            width=8.9,
            formula_size=46,
        ).move_to(DOWN * 2.15)
        general = self._formula_card(
            r"C_n^r=\frac{A_n^r}{r!}=\frac{n!}{r!(n-r)!}",
            "chaque groupe possède r! écritures ordonnées",
            width=9.9,
            formula_size=44,
        ).move_to(DOWN * 2.05)

        with self.narrated(SCRIPT_SEGMENTS[2]):
            self.play(FadeIn(title), FadeIn(badge), run_time=0.8)
            self.wait_until_bookmark("comb_same_group")
            self.play(Create(committee_box), FadeIn(committee_cards), FadeIn(committee_label), run_time=1.0)
            self.play(Write(set_equality), run_time=0.9)
            self.play(Indicate(committee, color=ACCENT, scale_factor=1.035), run_time=0.75)

            self.wait_until_bookmark("comb_six_orders")
            self.play(FadeOut(committee), FadeOut(committee_label), FadeOut(set_equality), run_time=0.55)
            self.play(
                LaggedStart(*[Write(item) for item in orderings], lag_ratio=0.13),
                run_time=1.65,
            )
            self.play(Create(orders_box), FadeIn(factorial_note), run_time=0.65)
            self.play(Write(down_arrow), FadeIn(one_group), run_time=0.75)

            self.wait_until_bookmark("comb_specific_formula")
            self.play(
                FadeOut(orderings),
                FadeOut(orders_box),
                FadeOut(down_arrow),
                FadeOut(one_group),
                FadeOut(factorial_note),
                FadeIn(specific, shift=0.1 * UP),
                run_time=0.9,
            )
            self.play(Indicate(specific[1][0], color=ACCENT, scale_factor=1.025), run_time=0.7)

            self.wait_until_bookmark("comb_general_formula")
            self.play(FadeOut(specific), FadeIn(general, shift=0.08 * UP), run_time=0.95)
            self.wait(1.1)

        self._clear(title, badge, general)

    def permutation_segment(self) -> None:
        title = self._title("Permutation", "Tous les éléments sont utilisés et l'ordre compte")
        badge = self._pill("cas particulier : r=n", font_size=25).next_to(title, DOWN, buff=0.22)

        cards = self._card_row().scale(0.82).move_to(UP * 1.15)
        slots = VGroup(*[self._slot(str(i), width=0.84, height=0.98) for i in range(1, 6)])
        slots.arrange(RIGHT, buff=0.22).move_to(DOWN * 0.05)
        placed = VGroup(*[self._person_card(letter, width=0.67, height=0.77) for letter in "ABCDE"])
        for card, slot in zip(placed, slots):
            card.move_to(slot[0])

        choice_numbers = VGroup(*[MathTex(str(n), font_size=33, color=ACCENT) for n in (5, 4, 3, 2, 1)])
        for number, slot in zip(choice_numbers, slots):
            number.next_to(slot[0], DOWN, buff=0.16)

        specific = self._formula_card(
            r"P_5=5\times4\times3\times2\times1=5!=120",
            "les 5 personnes occupent les 5 positions",
            width=9.5,
            formula_size=44,
        ).move_to(DOWN * 1.75)
        general = self._formula_card(
            r"P_n=A_n^n=n!",
            "une permutation ordonne tous les éléments",
            width=7.7,
            formula_size=49,
        ).move_to(DOWN * 2.0)

        with self.narrated(SCRIPT_SEGMENTS[3]):
            self.play(FadeIn(title), FadeIn(badge), run_time=0.8)
            self.wait_until_bookmark("perm_fill_slots")
            self.play(FadeIn(cards), FadeIn(slots), run_time=0.8)
            self.play(
                LaggedStart(
                    *[TransformFromCopy(cards[i], placed[i]) for i in range(5)],
                    lag_ratio=0.12,
                ),
                run_time=1.7,
            )
            self.play(
                LaggedStart(*[FadeIn(number, shift=0.06 * UP) for number in choice_numbers], lag_ratio=0.16),
                run_time=1.2,
            )

            self.wait_until_bookmark("perm_specific_formula")
            self.play(FadeIn(specific, shift=0.1 * UP), run_time=0.9)
            self.play(Indicate(specific[1][0], color=ACCENT, scale_factor=1.025), run_time=0.7)

            self.wait_until_bookmark("perm_general_formula")
            self.play(
                FadeOut(cards),
                FadeOut(slots),
                FadeOut(placed),
                FadeOut(choice_numbers),
                FadeOut(specific), FadeIn(general, shift=0.08 * UP),
                run_time=0.95,
            )
            self.wait(1.0)

        self._clear(title, badge, general)

    def common_error_segment(self) -> None:
        title = self._title("Erreur fréquente", "« On choisit 3 personnes, donc on divise par 3! »")

        wrong_heading = Text("Médailles parmi 12", font_size=29, color=ERROR)
        wrong_formula = MathTex(r"\frac{12\times11\times10}{3!}=220", font_size=43)
        wrong_reason = Text("on a effacé des rôles distincts", font_size=22, color=SOFT)
        wrong_content = VGroup(wrong_heading, wrong_formula, wrong_reason).arrange(DOWN, buff=0.18)
        wrong_box = RoundedRectangle(
            width=5.6,
            height=2.25,
            corner_radius=0.14,
            stroke_color=ERROR,
            stroke_width=2.3,
        )
        wrong_box.set_fill(ERROR, opacity=0.025)
        wrong_content.move_to(wrong_box)
        wrong = VGroup(wrong_box, wrong_content).move_to(LEFT * 3.25 + UP * 0.35)
        cross = Cross(wrong_formula, stroke_color=ERROR, stroke_width=7)

        correct_heading = Text("Médailles parmi 12", font_size=29, color=ACCENT)
        correct_formula = MathTex(r"A_{12}^{3}=12\times11\times10=1320", font_size=40)
        correct_reason = Text("or, argent et bronze sont différents", font_size=22, color=SOFT)
        correct_content = VGroup(correct_heading, correct_formula, correct_reason).arrange(DOWN, buff=0.18)
        correct_box = RoundedRectangle(
            width=5.9,
            height=2.25,
            corner_radius=0.14,
            stroke_color=ACCENT,
            stroke_width=2.3,
        )
        correct_box.set_fill(ACCENT, opacity=0.025)
        correct_content.move_to(correct_box)
        correct = VGroup(correct_box, correct_content).move_to(RIGHT * 3.2 + UP * 0.35)

        role_swap = VGroup(
            MathTex(r"ABC", font_size=39),
            MathTex(r"\neq", font_size=39, color=ACCENT),
            MathTex(r"BAC", font_size=39),
        ).arrange(RIGHT, buff=0.28).move_to(DOWN * 1.15)
        role_note = Text("échanger l'or et l'argent change le podium", font_size=25, color=SOFT)
        role_note.next_to(role_swap, DOWN, buff=0.14)

        committee_contrast = self._formula_card(
            r"C_{12}^{3}=220",
            "220 répond à : former un comité de 3 parmi 12",
            width=8.6,
            formula_size=43,
        ).move_to(DOWN * 2.55)

        with self.narrated(SCRIPT_SEGMENTS[4]):
            self.play(FadeIn(title), run_time=0.75)
            self.wait_until_bookmark("error_wrong_formula")
            self.play(FadeIn(wrong, shift=0.1 * UP), run_time=0.85)
            self.play(Create(cross), run_time=0.75)

            self.wait_until_bookmark("error_distinct_roles")
            self.play(FadeIn(correct, shift=0.1 * UP), run_time=0.85)
            self.play(Write(role_swap), FadeIn(role_note), run_time=0.8)
            self.play(Indicate(correct_formula, color=ACCENT, scale_factor=1.025), run_time=0.7)

            self.wait_until_bookmark("error_contrast_committee")
            self.play(FadeIn(committee_contrast, shift=0.08 * UP), run_time=0.85)
            self.wait(1.2)

        self._clear(title, wrong, cross, correct, role_swap, role_note, committee_contrast)

    def decision_segment(self) -> None:
        title = self._title("Comment choisir ?", "Deux questions — sans répétition")

        root = self._pill("L'ordre compte-t-il ?", font_size=31).move_to(UP * 1.45)
        combination = self._pill("Combinaison", font_size=30).move_to(LEFT * 3.75 + DOWN * 0.25)
        second_question = self._pill("Tous les éléments sont-ils utilisés ?", font_size=27)
        second_question.move_to(RIGHT * 2.15 + UP * 0.3)
        arrangement = self._pill("Arrangement", font_size=29).move_to(RIGHT * 0.55 + DOWN * 1.55)
        permutation = self._pill("Permutation", font_size=29).move_to(RIGHT * 4.25 + DOWN * 1.55)

        arrow_comb = Arrow(
            root.get_bottom() + LEFT * 0.55,
            combination.get_top(),
            buff=0.1,
            stroke_width=2.2,
            color=BLACK,
        )
        arrow_second = Arrow(
            root.get_bottom() + RIGHT * 0.55,
            second_question.get_top(),
            buff=0.1,
            stroke_width=2.2,
            color=BLACK,
        )
        arrow_arr = Arrow(
            second_question.get_bottom() + LEFT * 0.62,
            arrangement.get_top(),
            buff=0.08,
            stroke_width=2.2,
            color=BLACK,
        )
        arrow_perm = Arrow(
            second_question.get_bottom() + RIGHT * 0.62,
            permutation.get_top(),
            buff=0.08,
            stroke_width=2.2,
            color=BLACK,
        )

        labels = VGroup(
            Text("non", font_size=23, color=SOFT).next_to(arrow_comb, LEFT, buff=0.04),
            Text("oui", font_size=23, color=ACCENT).next_to(arrow_second, RIGHT, buff=0.04),
            Text("non", font_size=23, color=SOFT).next_to(arrow_arr, LEFT, buff=0.04),
            Text("oui", font_size=23, color=ACCENT).next_to(arrow_perm, RIGHT, buff=0.04),
        )

        formulas = VGroup(
            MathTex(r"C_n^r", font_size=36).next_to(combination, DOWN, buff=0.14),
            MathTex(r"A_n^r", font_size=36).next_to(arrangement, DOWN, buff=0.14),
            MathTex(r"P_n", font_size=36).next_to(permutation, DOWN, buff=0.14),
        )
        warning = Text("La répétition sera un autre cas à traiter.", font_size=24, color=SOFT)
        warning.to_edge(DOWN, buff=0.42)

        with self.narrated(SCRIPT_SEGMENTS[5]):
            self.play(FadeIn(title), run_time=0.7)
            self.wait_until_bookmark("tree_first_question")
            self.play(FadeIn(root, shift=0.08 * UP), run_time=0.65)
            self.play(GrowArrow(arrow_comb), FadeIn(labels[0]), FadeIn(combination), FadeIn(formulas[0]), run_time=0.8)

            self.wait_until_bookmark("tree_second_question")
            self.play(GrowArrow(arrow_second), FadeIn(labels[1]), FadeIn(second_question), run_time=0.8)

            self.wait_until_bookmark("tree_leaves")
            self.play(
                GrowArrow(arrow_arr),
                GrowArrow(arrow_perm),
                FadeIn(labels[2]),
                FadeIn(labels[3]),
                FadeIn(arrangement),
                FadeIn(permutation),
                FadeIn(formulas[1]),
                FadeIn(formulas[2]),
                FadeIn(warning),
                run_time=1.0,
            )
            self.wait(1.1)

        self._clear(
            title,
            root,
            combination,
            second_question,
            arrangement,
            permutation,
            arrow_comb,
            arrow_second,
            arrow_arr,
            arrow_perm,
            labels,
            formulas,
            warning,
        )

    def quiz_segment(self) -> None:
        title = self._title("À vous de classer", "Décidez avant l'apparition de la réponse")
        prompt = Text("Quelle méthode ?", font_size=30, color=SOFT).move_to(UP * 1.35)

        scenarios = [
            "Choisir 4 représentants parmi 12 étudiants",
            "Attribuer 3 rôles différents parmi 12 personnes",
            "Ranger 6 livres distincts sur une tablette",
        ]
        answers = [
            ("Combinaison", "ordre non important", r"C_{12}^{4}"),
            ("Arrangement", "ordre important · 3 parmi 12", r"A_{12}^{3}"),
            ("Permutation", "ordre important · tous les 6", r"P_6"),
        ]

        scenario = self._scenario_panel(scenarios[0]).move_to(UP * 0.15)
        answer = self._pill(answers[0][0], font_size=34).move_to(DOWN * 1.15)
        reason = Text(answers[0][1], font_size=25, color=SOFT).next_to(answer, DOWN, buff=0.15)
        notation = MathTex(answers[0][2], font_size=40).next_to(reason, DOWN, buff=0.14)

        with self.narrated(SCRIPT_SEGMENTS[6]):
            self.play(FadeIn(title), FadeIn(prompt), run_time=0.7)

            self.wait_until_bookmark("quiz_one")
            self.play(FadeIn(scenario, shift=0.1 * UP), run_time=0.7)
            self.wait(1.2)
            self.wait_until_bookmark("quiz_one_answer")
            self.play(FadeIn(answer, shift=0.08 * UP), FadeIn(reason), Write(notation), run_time=0.75)

            second_scenario = self._scenario_panel(scenarios[1]).move_to(scenario)
            second_answer = self._pill(answers[1][0], font_size=34).move_to(answer)
            second_reason = Text(answers[1][1], font_size=25, color=SOFT).move_to(reason)
            second_notation = MathTex(answers[1][2], font_size=40).move_to(notation)
            self.play(
                Transform(scenario, second_scenario),
                FadeOut(answer),
                FadeOut(reason),
                FadeOut(notation),
                run_time=0.75,
            )
            self.wait(1.2)
            self.wait_until_bookmark("quiz_two_answer")
            self.play(FadeIn(second_answer), FadeIn(second_reason), Write(second_notation), run_time=0.75)
            answer, reason, notation = second_answer, second_reason, second_notation

            third_scenario = self._scenario_panel(scenarios[2]).move_to(scenario)
            third_answer = self._pill(answers[2][0], font_size=34).move_to(answer)
            third_reason = Text(answers[2][1], font_size=25, color=SOFT).move_to(reason)
            third_notation = MathTex(answers[2][2], font_size=40).move_to(notation)
            self.play(
                Transform(scenario, third_scenario),
                FadeOut(answer),
                FadeOut(reason),
                FadeOut(notation),
                run_time=0.75,
            )
            self.wait(1.2)
            self.wait_until_bookmark("quiz_three_answer")
            self.play(FadeIn(third_answer), FadeIn(third_reason), Write(third_notation), run_time=0.75)
            answer, reason, notation = third_answer, third_reason, third_notation
            self.wait(1.0)

        self._clear(title, prompt, scenario, answer, reason, notation)

    def conclusion_segment(self) -> None:
        title = self._title("Résumé", "Dénombrement sans répétition")
        definitions = VGroup(
            MathTex(r"n=\text{nombre disponible}", font_size=34),
            MathTex(r"r=\text{nombre choisi}", font_size=34),
            MathTex(r"0\le r\le n", font_size=34),
        ).arrange(RIGHT, buff=0.72).move_to(UP * 1.65)

        rows = VGroup(
            self._summary_row("Arrangement", "ordre oui · r parmi n", r"A_n^r=\frac{n!}{(n-r)!}"),
            self._summary_row("Combinaison", "ordre non · r parmi n", r"C_n^r=\frac{n!}{r!(n-r)!}"),
            self._summary_row("Permutation", "ordre oui · tous les n", r"P_n=n!"),
        ).arrange(DOWN, buff=0.22).move_to(DOWN * 0.35)

        final_rule = self._pill("1. L'ordre compte ?   2. Tous les éléments sont utilisés ?", font_size=28)
        final_rule.move_to(DOWN * 2.65)

        with self.narrated(SCRIPT_SEGMENTS[7]):
            self.play(FadeIn(title), run_time=0.7)
            self.wait_until_bookmark("recap_definitions")
            self.play(LaggedStart(*[FadeIn(item, shift=0.06 * UP) for item in definitions], lag_ratio=0.2), run_time=1.0)

            self.wait_until_bookmark("recap_rows")
            self.play(LaggedStart(*[FadeIn(row, shift=0.08 * UP) for row in rows], lag_ratio=0.22), run_time=1.45)

            self.wait_until_bookmark("recap_final")
            self.play(FadeIn(final_rule, shift=0.08 * UP), run_time=0.8)
            self.play(Circumscribe(final_rule, color=ACCENT, fade_out=True), run_time=1.1)
            self.wait(1.25)
