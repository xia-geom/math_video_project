from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import (
    BLACK,
    BLUE_D,
    Create,
    DOWN,
    FadeIn,
    FadeOut,
    GREEN_D,
    LEFT,
    MathTex,
    RED_D,
    RIGHT,
    RoundedRectangle,
    Square,
    SurroundingRectangle,
    Tex,
    Text,
    UP,
    VGroup,
    WHITE,
    Write,
    config,
)
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService

import tools.tts as tts
from tools.branding import play_uqam_intro


config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


ACCENT = BLUE_D
GOOD = GREEN_D
ERROR = RED_D


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class RacineProduitHypothesesFR(VoiceoverScene):
    """Pourquoi ``sqrt(ab) = sqrt(a)sqrt(b)`` exige-t-elle des hypothèses ?

    Objectif pédagogique
    --------------------
    Faire comprendre qu'une identité mathématique n'est pas une règle isolée :
    ses hypothèses font partie du théorème. Dans les nombres réels,

        sqrt(ab) = sqrt(a)sqrt(b)

    est garantie lorsque ``a >= 0`` et ``b >= 0``. En dehors de ce domaine,
    une expression peut ne plus exister, ou la formule peut devenir fausse si
    on change de cadre sans précaution.

    Progression
    -----------
    1. Une vérification numérique qui rend la règle plausible.
    2. Révélation des hypothèses cachées ``a,b >= 0``.
    3. Substitution tentante ``a=b=-1`` et diagnostic dans R.
    4. Brève extension complexe : la racine principale ne préserve pas la règle.
    5. Preuve de l'identité sous les bonnes hypothèses.
    6. Tableau des signes et méthode générale en trois portes.
    """

    def _setup_voiceover(self) -> None:
        self._voiceover_enabled = False
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
        try:
            self.set_speech_service(AzureService(voice=tts.VOICE_ID))
        except Exception as exc:
            print(f"[voiceover] Azure Speech setup failed: {exc}. Rendering without narration.")
            return
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, text: str):
        if self._voiceover_enabled:
            with self.voiceover(
                text=text,
                subcaption=tts.strip_ssml(text),
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_until_bookmark(self, mark: str) -> None:
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)

    def construct(self) -> None:
        self._setup_voiceover()
        play_uqam_intro(self)

        self._opening_question()
        self._working_example()
        self._reveal_hypotheses()
        self._illegal_substitution()
        self._complex_extension()
        self._why_theorem_works()
        self._sign_table()
        self._general_method()
        self._summary()

        self.wait(1.2)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _card(
        self,
        content: VGroup | MathTex | Text,
        color=BLACK,
        width: float = 5.6,
        height: float = 2.0,
        fill_opacity: float = 0.04,
    ) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.18,
            color=color,
            stroke_width=2.4,
            fill_color=color,
            fill_opacity=fill_opacity,
        )
        if content.width > width - 0.55:
            content.scale_to_fit_width(width - 0.55)
        if content.height > height - 0.35:
            content.scale_to_fit_height(height - 0.35)
        content.move_to(box)
        return VGroup(box, content)

    def _gate(self, number: str, title: str, question: str, color) -> VGroup:
        box = RoundedRectangle(
            width=3.65,
            height=2.05,
            corner_radius=0.16,
            color=color,
            stroke_width=2.4,
            fill_color=color,
            fill_opacity=0.045,
        )
        badge = Square(
            side_length=0.62,
            color=color,
            stroke_width=2.2,
            fill_color=color,
            fill_opacity=0.1,
        )
        badge_text = Text(number, font_size=26, color=color, weight="BOLD")
        badge_text.move_to(badge)
        badge_group = VGroup(badge, badge_text)

        heading = Text(title, font_size=27, color=color, weight="SEMIBOLD")
        body = Text(question, font_size=23, color=BLACK, line_spacing=0.9)
        if body.width > 2.72:
            body.scale_to_fit_width(2.72)
        text_group = VGroup(heading, body).arrange(DOWN, buff=0.18, aligned_edge=LEFT)

        row = VGroup(badge_group, text_group).arrange(RIGHT, buff=0.28)
        row.move_to(box)
        return VGroup(box, row)

    def _top_header(self, title_text: str) -> VGroup:
        eyebrow = Text("ERREUR SOPHISTIQUÉE", font_size=25, color=ACCENT)
        title = Text(title_text, font_size=42, weight="SEMIBOLD")
        title.scale_to_fit_width(12.2)
        header = VGroup(eyebrow, title).arrange(DOWN, buff=0.17)
        header.to_edge(UP, buff=0.3)
        return header

    # ------------------------------------------------------------------
    # Acte 1 — Question centrale
    # ------------------------------------------------------------------
    def _opening_question(self) -> None:
        header = self._top_header("Une règle reste-t-elle vraie sans ses conditions ?")

        formula = MathTex(
            r"\sqrt{ab}",
            r"\overset{?}{=}",
            r"\sqrt a\,\sqrt b",
        ).scale(1.65)
        formula.set_color_by_tex(r"\overset{?}{=}", ACCENT)
        formula.move_to(UP * 0.15)

        prompt = Text(
            "Pour quels nombres cette identité est-elle réellement valable ?",
            font_size=31,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        prompt.scale_to_fit_width(11.2)
        prompt.next_to(formula, DOWN, buff=0.65)

        spoken = tts.ssml(
            "Nous utilisons souvent cette règle sans hésiter : la racine d'un produit serait "
            "le produit des racines. <bookmark mark='opening_formula'/> "
            "Mais une identité mathématique n'est jamais seulement une formule. "
            "Elle vient avec un domaine et des hypothèses. <bookmark mark='opening_prompt'/> "
            "Pour quels nombres cette règle est-elle réellement valable ?"
        )
        with self.narrated(spoken):
            self.play(FadeIn(header[0], shift=DOWN * 0.1), run_time=0.5)
            self.play(Write(header[1]), run_time=0.95)
            self.wait(0.4)
            self.wait_until_bookmark("opening_formula")
            self.play(Write(formula), run_time=0.9)
            self.wait(0.75)
            self.wait_until_bookmark("opening_prompt")
            self.play(FadeIn(prompt, shift=UP * 0.1), run_time=0.55)
            self.wait(1.0)

        self.play(
            header.animate.scale(0.78).to_edge(UP, buff=0.18),
            FadeOut(prompt),
            formula.animate.scale(0.72).next_to(header, DOWN, buff=0.28),
            run_time=0.85,
        )

        self.header = header
        self.formula = formula

    # ------------------------------------------------------------------
    # Acte 2 — Pourquoi la règle semble évidente
    # ------------------------------------------------------------------
    def _working_example(self) -> None:
        label = Text("Un exemple rassurant", font_size=32, weight="SEMIBOLD")
        label.next_to(self.formula, DOWN, buff=0.48)

        left_start = MathTex(r"\sqrt{4\cdot9}").scale(1.28)
        left_mid = MathTex(r"=\sqrt{36}").scale(1.28)
        left_end = MathTex(r"=6").scale(1.28)
        left_chain = VGroup(left_start, left_mid, left_end).arrange(RIGHT, buff=0.15)

        right_start = MathTex(r"\sqrt4\,\sqrt9").scale(1.28)
        right_mid = MathTex(r"=2\cdot3").scale(1.28)
        right_end = MathTex(r"=6").scale(1.28)
        right_chain = VGroup(right_start, right_mid, right_end).arrange(RIGHT, buff=0.15)

        left_card = self._card(left_chain, ACCENT, width=5.25, height=1.65)
        right_card = self._card(right_chain, GOOD, width=5.25, height=1.65)
        cards = VGroup(left_card, right_card).arrange(RIGHT, buff=0.65)
        cards.move_to(DOWN * 0.65)

        conclusion = MathTex(r"6=6").scale(1.35).set_color(GOOD)
        conclusion.next_to(cards, DOWN, buff=0.42)

        spoken = tts.ssml(
            "Commençons par un cas où tout fonctionne. <bookmark mark='example_left'/> "
            "Avec quatre et neuf, la racine de trente-six vaut six. <bookmark mark='example_right'/> "
            "De l'autre côté, la racine de quatre vaut deux et celle de neuf vaut trois. "
            "<bookmark mark='example_result'/> Nous obtenons encore six. "
            "Cet exemple confirme la règle, mais il ne nous dit pas encore jusqu'où elle s'applique."
        )
        with self.narrated(spoken):
            self.play(FadeIn(label, shift=DOWN * 0.1), run_time=0.5)
            self.wait_until_bookmark("example_left")
            self.play(Create(left_card[0]), FadeIn(left_start), run_time=0.65)
            self.play(Write(left_mid), Write(left_end), run_time=0.75)
            self.wait(0.45)
            self.wait_until_bookmark("example_right")
            self.play(Create(right_card[0]), FadeIn(right_start), run_time=0.65)
            self.play(Write(right_mid), Write(right_end), run_time=0.75)
            self.wait(0.55)
            self.wait_until_bookmark("example_result")
            self.play(Write(conclusion), run_time=0.45)
            self.wait(0.9)

        self.play(FadeOut(label), FadeOut(cards), FadeOut(conclusion), run_time=0.65)

    # ------------------------------------------------------------------
    # Acte 3 — Les hypothèses font partie du théorème
    # ------------------------------------------------------------------
    def _reveal_hypotheses(self) -> None:
        self.play(FadeOut(self.formula), run_time=0.4)

        incomplete = MathTex(r"\sqrt{ab}=\sqrt a\,\sqrt b").scale(1.35)
        incomplete.move_to(UP * 0.25)
        incomplete_box = SurroundingRectangle(incomplete, color=BLACK, buff=0.24)

        conditions = MathTex(r"a\ge0,\qquad b\ge0").scale(1.25).set_color(ACCENT)
        conditions.next_to(incomplete_box, UP, buff=0.28)

        complete = VGroup(conditions, incomplete_box, incomplete)

        theorem_label = Text(
            "Les conditions ne sont pas une note en bas de page.",
            font_size=31,
            color=ERROR,
            weight="SEMIBOLD",
        )
        theorem_label.scale_to_fit_width(11.2)
        theorem_label.next_to(incomplete_box, DOWN, buff=0.58)

        full_statement = MathTex(
            r"a,b\in\mathbb R,\ a\ge0,\ b\ge0",
            r"\quad\Longrightarrow\quad",
            r"\sqrt{ab}=\sqrt a\,\sqrt b",
        ).scale(1.08)
        full_statement.set_color_by_tex(r"\Longrightarrow", ACCENT)
        full_statement.next_to(theorem_label, DOWN, buff=0.52)

        spoken = tts.ssml(
            "Voici l'énoncé complet dans les nombres réels. <bookmark mark='hypotheses_conditions'/> "
            "Il faut que a et b soient positifs ou nuls. <bookmark mark='hypotheses_status'/> "
            "Ces conditions ne sont pas une remarque facultative. "
            "Elles font partie du théorème au même titre que l'égalité. "
            "<bookmark mark='hypotheses_statement'/> "
            "Sans elles, nous ne sommes plus autorisés à appliquer la règle."
        )
        with self.narrated(spoken):
            self.play(Write(incomplete), Create(incomplete_box), run_time=0.75)
            self.wait(0.65)
            self.wait_until_bookmark("hypotheses_conditions")
            self.play(FadeIn(conditions, shift=DOWN * 0.14), run_time=0.65)
            self.wait(0.75)
            self.wait_until_bookmark("hypotheses_status")
            self.play(FadeIn(theorem_label, shift=UP * 0.1), run_time=0.55)
            self.wait(0.75)
            self.wait_until_bookmark("hypotheses_statement")
            self.play(Write(full_statement), run_time=0.95)
            self.wait(1.0)

        self.play(FadeOut(complete), FadeOut(theorem_label), run_time=0.55)
        self.play(
            full_statement.animate.scale(0.83).next_to(self.header, DOWN, buff=0.3),
            run_time=0.65,
        )
        self.full_statement = full_statement

    # ------------------------------------------------------------------
    # Acte 4 — Substitution illégale dans R
    # ------------------------------------------------------------------
    def _illegal_substitution(self) -> None:
        title = Text(
            "La substitution tentante :  a = b = -1",
            font_size=33,
            weight="SEMIBOLD",
        )
        title.next_to(self.full_statement, DOWN, buff=0.48)

        lhs_1 = MathTex(r"\sqrt{(-1)(-1)}").scale(1.2)
        lhs_2 = MathTex(r"=\sqrt1").scale(1.2)
        lhs_3 = MathTex(r"=1").scale(1.2)
        lhs = VGroup(lhs_1, lhs_2, lhs_3).arrange(RIGHT, buff=0.13)
        lhs_card = self._card(lhs, GOOD, width=5.35, height=1.65)

        rhs_1 = MathTex(r"\sqrt{-1}\,\sqrt{-1}").scale(1.15)
        rhs_2 = Text("n'existe pas dans  ℝ", font_size=29, color=ERROR, weight="SEMIBOLD")
        rhs = VGroup(rhs_1, rhs_2).arrange(DOWN, buff=0.18)
        rhs_card = self._card(rhs, ERROR, width=5.35, height=1.65)

        cards = VGroup(lhs_card, rhs_card).arrange(RIGHT, buff=0.65)
        cards.move_to(DOWN * 0.7)

        stop = Text(
            "La formule n'est pas en cause : ses hypothèses ne sont pas respectées.",
            font_size=30,
            color=ERROR,
            weight="SEMIBOLD",
        )
        stop.scale_to_fit_width(11.5)
        stop.next_to(cards, DOWN, buff=0.45)

        spoken = tts.ssml(
            "Essayons pourtant de remplacer a et b par moins un. <bookmark mark='illegal_left'/> "
            "À gauche, le produit vaut un, donc la racine vaut un. <bookmark mark='illegal_right'/> "
            "À droite, chaque racine de moins un n'existe pas dans les nombres réels. "
            "<bookmark mark='illegal_undefined'/> Le problème n'est donc pas une petite erreur de calcul. "
            "Le membre de droite n'est même pas défini. <bookmark mark='illegal_diagnosis'/> "
            "Nous avons utilisé un théorème en dehors de son domaine."
        )
        with self.narrated(spoken):
            self.play(FadeIn(title, shift=DOWN * 0.1), run_time=0.5)
            self.wait_until_bookmark("illegal_left")
            self.play(Create(lhs_card[0]), FadeIn(lhs_1), run_time=0.6)
            self.play(Write(lhs_2), Write(lhs_3), run_time=0.7)
            self.wait(0.5)
            self.wait_until_bookmark("illegal_right")
            self.play(Create(rhs_card[0]), FadeIn(rhs_1), run_time=0.6)
            self.wait(0.55)
            self.wait_until_bookmark("illegal_undefined")
            self.play(FadeIn(rhs_2, shift=UP * 0.08), run_time=0.5)
            self.wait(0.65)
            self.wait_until_bookmark("illegal_diagnosis")
            self.play(FadeIn(stop, shift=UP * 0.1), run_time=0.55)
            self.wait(1.0)

        self.play(FadeOut(title), FadeOut(cards), FadeOut(stop), run_time=0.65)

    # ------------------------------------------------------------------
    # Acte 5 — Extension complexe facultative
    # ------------------------------------------------------------------
    def _complex_extension(self) -> None:
        tag = Text("EXTENSION FACULTATIVE", font_size=24, color=ACCENT)
        tag.next_to(self.full_statement, DOWN, buff=0.45)

        intro = Text(
            "Même avec les nombres complexes, la règle ne survit pas telle quelle.",
            font_size=31,
            weight="SEMIBOLD",
        )
        intro.scale_to_fit_width(11.4)
        intro.next_to(tag, DOWN, buff=0.25)

        principal = MathTex(r"\sqrt{-1}=i\qquad\text{(racine principale)}").scale(1.05)
        principal.next_to(intro, DOWN, buff=0.48)

        lhs = MathTex(r"\sqrt{(-1)(-1)}=\sqrt1=1").scale(1.13)
        rhs = MathTex(r"\sqrt{-1}\,\sqrt{-1}=i^2=-1").scale(1.13)
        lhs_card = self._card(lhs, GOOD, width=5.45, height=1.5)
        rhs_card = self._card(rhs, ERROR, width=5.45, height=1.5)
        cards = VGroup(lhs_card, rhs_card).arrange(RIGHT, buff=0.55)
        cards.next_to(principal, DOWN, buff=0.5)

        contradiction = MathTex(r"1\neq-1").scale(1.35).set_color(ERROR)
        contradiction.next_to(cards, DOWN, buff=0.35)

        spoken = tts.ssml(
            "On pourrait vouloir sauver le calcul en introduisant le nombre complexe i. "
            "<bookmark mark='complex_principal'/> La racine principale de moins un est alors égale à i. "
            "<bookmark mark='complex_cards'/> "
            "Mais alors le côté gauche vaut toujours un, tandis que le produit des deux racines vaut i au carré, donc moins un. "
            "<bookmark mark='complex_contradiction'/> "
            "La conclusion n'est pas que un égale moins un. La conclusion est que la règle du produit n'est pas valable en général pour les racines complexes principales."
        )
        with self.narrated(spoken):
            self.play(FadeIn(tag), FadeIn(intro, shift=DOWN * 0.08), run_time=0.6)
            self.wait_until_bookmark("complex_principal")
            self.play(Write(principal), run_time=0.75)
            self.wait(0.5)
            self.wait_until_bookmark("complex_cards")
            self.play(Create(lhs_card[0]), Write(lhs), run_time=0.75)
            self.play(Create(rhs_card[0]), Write(rhs), run_time=0.75)
            self.wait(0.65)
            self.wait_until_bookmark("complex_contradiction")
            self.play(Write(contradiction), run_time=0.55)
            self.wait(1.0)

        self.play(
            FadeOut(tag),
            FadeOut(intro),
            FadeOut(principal),
            FadeOut(cards),
            FadeOut(contradiction),
            run_time=0.65,
        )

    # ------------------------------------------------------------------
    # Acte 6 — Pourquoi les hypothèses suffisent
    # ------------------------------------------------------------------
    def _why_theorem_works(self) -> None:
        title = Text(
            "Pourquoi la règle est-elle vraie lorsque a, b ≥ 0 ?",
            font_size=33,
            weight="SEMIBOLD",
        )
        title.next_to(self.full_statement, DOWN, buff=0.47)

        condition = MathTex(r"a\ge0,\qquad b\ge0").scale(1.08).set_color(ACCENT)
        condition.next_to(title, DOWN, buff=0.35)

        left_name = MathTex(r"u=\sqrt{ab}").scale(1.15)
        left_nonnegative = MathTex(r"u\ge0").scale(0.98).set_color(ACCENT)
        left_square = MathTex(r"u^2=ab").scale(1.12)
        left_content = VGroup(left_name, left_nonnegative, left_square).arrange(DOWN, buff=0.2)
        left_card = self._card(left_content, ACCENT, width=5.1, height=2.25)

        right_name = MathTex(r"v=\sqrt a\,\sqrt b").scale(1.15)
        right_nonnegative = MathTex(r"v\ge0").scale(0.98).set_color(GOOD)
        right_square = MathTex(r"v^2=(\sqrt a)^2(\sqrt b)^2=ab").scale(0.96)
        right_content = VGroup(right_name, right_nonnegative, right_square).arrange(DOWN, buff=0.2)
        right_card = self._card(right_content, GOOD, width=5.1, height=2.25)

        cards = VGroup(left_card, right_card).arrange(RIGHT, buff=0.72)
        cards.next_to(condition, DOWN, buff=0.42)

        bridge = MathTex(
            r"u\ge0,\ v\ge0,\ u^2=v^2",
            r"\quad\Longrightarrow\quad",
            r"u=v",
        ).scale(1.03)
        bridge.set_color_by_tex(r"\Longrightarrow", ACCENT)
        bridge.next_to(cards, DOWN, buff=0.42)

        spoken = tts.ssml(
            "Sous les bonnes hypothèses, posons u égal à la racine de a fois b. "
            "<bookmark mark='proof_left'/> Posons aussi v égal au produit des deux racines. "
            "<bookmark mark='proof_right'/> Les deux nombres sont positifs ou nuls. "
            "De plus, leur carré vaut dans les deux cas a fois b. "
            "Deux nombres opposés peuvent avoir le même carré. Mais ici, la condition de non-négativité élimine cette ambiguïté. "
            "<bookmark mark='proof_conclusion'/> "
            "Deux nombres non négatifs ayant le même carré sont nécessairement égaux. Voilà le rôle exact des hypothèses."
        )
        with self.narrated(spoken):
            self.play(FadeIn(title, shift=DOWN * 0.08), Write(condition), run_time=0.65)
            self.wait(0.45)
            self.wait_until_bookmark("proof_left")
            self.play(Create(left_card[0]), Write(left_name), run_time=0.65)
            self.play(Write(left_nonnegative), Write(left_square), run_time=0.65)
            self.wait(0.45)
            self.wait_until_bookmark("proof_right")
            self.play(Create(right_card[0]), Write(right_name), run_time=0.65)
            self.play(Write(right_nonnegative), Write(right_square), run_time=0.65)
            self.wait(0.65)
            self.wait_until_bookmark("proof_conclusion")
            self.play(Write(bridge), run_time=0.85)
            self.wait(1.1)

        self.play(
            FadeOut(title), FadeOut(condition), FadeOut(cards), FadeOut(bridge), run_time=0.65
        )

    # ------------------------------------------------------------------
    # Acte 7 — Les quatre combinaisons de signes
    # ------------------------------------------------------------------
    def _sign_table(self) -> None:
        title = Text(
            "Que se passe-t-il hors du domaine autorisé ?",
            font_size=33,
            weight="SEMIBOLD",
        )
        title.next_to(self.full_statement, DOWN, buff=0.48)

        col_widths = [4.15, 3.25, 3.75]
        row_height = 0.66
        headers = ["Cas", "√(ab)", "√a · √b"]
        rows = [
            ("a ≥ 0 et b ≥ 0", "définie", "définie : règle valide", GOOD),
            ("signes opposés, aucun zéro", "non définie", "non définie", ERROR),
            ("un zéro, l'autre négatif", "définie : vaut 0", "non définie", ERROR),
            ("a < 0 et b < 0", "définie", "non définie", ERROR),
        ]

        header_cells = VGroup()
        for text, width in zip(headers, col_widths):
            box = RoundedRectangle(
                width=width,
                height=row_height,
                corner_radius=0.08,
                color=ACCENT,
                stroke_width=2.0,
                fill_color=ACCENT,
                fill_opacity=0.1,
            )
            label = Text(text, font_size=23, color=ACCENT, weight="SEMIBOLD")
            if label.width > width - 0.18:
                label.scale_to_fit_width(width - 0.18)
            label.move_to(box)
            header_cells.add(VGroup(box, label))
        header_cells.arrange(RIGHT, buff=0.08)

        body_rows = VGroup()
        for case_text, left_text, right_text, color in rows:
            values = [case_text, left_text, right_text]
            cells = VGroup()
            for value, width in zip(values, col_widths):
                box = RoundedRectangle(
                    width=width,
                    height=row_height,
                    corner_radius=0.08,
                    color=color,
                    stroke_width=1.8,
                    fill_color=color,
                    fill_opacity=0.035,
                )
                label = Text(value, font_size=21, color=BLACK)
                if label.width > width - 0.18:
                    label.scale_to_fit_width(width - 0.18)
                label.move_to(box)
                cells.add(VGroup(box, label))
            cells.arrange(RIGHT, buff=0.08)
            body_rows.add(cells)
        body_rows.arrange(DOWN, buff=0.08)

        table = VGroup(header_cells, body_rows).arrange(DOWN, buff=0.08)
        table.scale_to_fit_width(11.5)
        table.next_to(title, DOWN, buff=0.3)

        danger = Text(
            "Deux facteurs négatifs : le produit est positif, mais les racines séparées n'existent pas dans ℝ.",
            font_size=25,
            color=ERROR,
            weight="SEMIBOLD",
        )
        danger.scale_to_fit_width(11.3)
        danger.next_to(table, DOWN, buff=0.22)

        spoken = tts.ssml(
            "Examinons ce qui se passe lorsque les hypothèses ne sont pas respectées. "
            "<bookmark mark='sign_header'/> Si a et b sont positifs ou nuls, les deux membres sont définis et la règle est valable. "
            "<bookmark mark='sign_positive'/> "
            "Si les signes sont strictement opposés, le produit est négatif et aucune écriture complète n'existe dans les réels. "
            "<bookmark mark='sign_opposite'/> "
            "Si un facteur vaut zéro et l'autre est négatif, la racine du produit existe et vaut zéro, mais le produit des racines n'existe toujours pas. "
            "<bookmark mark='sign_zero'/> "
            "Enfin, lorsque les deux facteurs sont négatifs, leur produit est positif : le côté gauche existe, alors que le côté droit n'existe pas. "
            "<bookmark mark='sign_negative'/> "
            "Ces cas montrent pourquoi vérifier seulement le produit ne suffit pas."
        )
        with self.narrated(spoken):
            self.play(FadeIn(title, shift=DOWN * 0.08), run_time=0.5)
            self.wait_until_bookmark("sign_header")
            self.play(FadeIn(header_cells, shift=DOWN * 0.08), run_time=0.55)
            self.wait_until_bookmark("sign_positive")
            self.play(FadeIn(body_rows[0], shift=DOWN * 0.06), run_time=0.42)
            self.wait(0.18)
            self.wait_until_bookmark("sign_opposite")
            self.play(FadeIn(body_rows[1], shift=DOWN * 0.06), run_time=0.42)
            self.wait(0.18)
            self.wait_until_bookmark("sign_zero")
            self.play(FadeIn(body_rows[2], shift=DOWN * 0.06), run_time=0.42)
            self.wait(0.18)
            self.wait_until_bookmark("sign_negative")
            self.play(FadeIn(body_rows[3], shift=DOWN * 0.06), run_time=0.42)
            self.wait(0.18)
            self.wait(0.55)
            self.play(FadeIn(danger, shift=UP * 0.08), run_time=0.55)
            self.wait(1.0)

        self.play(FadeOut(title), FadeOut(table), FadeOut(danger), run_time=0.65)

    # ------------------------------------------------------------------
    # Acte 8 — Méthode transférable
    # ------------------------------------------------------------------
    def _general_method(self) -> None:
        title = Text(
            "Avant d'utiliser une identité : trois portes",
            font_size=34,
            weight="SEMIBOLD",
        )
        title.next_to(self.full_statement, DOWN, buff=0.5)

        gate_1 = self._gate("1", "HYPOTHÈSES", "Quelles valeurs sont autorisées ?", ACCENT)
        gate_2 = self._gate("2", "EXISTENCE", "Chaque expression est-elle définie ?", GOOD)
        gate_3 = self._gate("3", "RÈGLE", "La transformation est-elle alors permise ?", ERROR)
        gates = VGroup(gate_1, gate_2, gate_3).arrange(RIGHT, buff=0.38)
        gates.scale_to_fit_width(11.65)
        gates.move_to(DOWN * 0.45)

        arrows = VGroup(
            MathTex(r"\Longrightarrow").set_color(BLACK),
            MathTex(r"\Longrightarrow").set_color(BLACK),
        )
        arrows[0].move_to((gate_1.get_right() + gate_2.get_left()) / 2)
        arrows[1].move_to((gate_2.get_right() + gate_3.get_left()) / 2)

        warning = Text(
            "On ne transforme pas d'abord pour vérifier le domaine ensuite.",
            font_size=30,
            color=ERROR,
            weight="SEMIBOLD",
        )
        warning.scale_to_fit_width(11.4)
        warning.next_to(gates, DOWN, buff=0.52)

        spoken = tts.ssml(
            "Cette erreur fournit une méthode générale. <bookmark mark='method_hypotheses'/> "
            "Première porte : identifier les hypothèses du théorème. <bookmark mark='method_existence'/> "
            "Deuxième porte : vérifier que toutes les expressions existent pour les valeurs considérées. "
            "<bookmark mark='method_rule'/> Troisième porte seulement : appliquer la transformation. "
            "<bookmark mark='method_warning'/> "
            "Nous ne devons pas manipuler les symboles d'abord, puis vérifier le domaine après coup."
        )
        with self.narrated(spoken):
            self.play(FadeIn(title, shift=DOWN * 0.08), run_time=0.5)
            self.wait_until_bookmark("method_hypotheses")
            self.play(Create(gate_1[0]), FadeIn(gate_1[1]), run_time=0.6)
            self.wait(0.35)
            self.wait_until_bookmark("method_existence")
            self.play(Write(arrows[0]), Create(gate_2[0]), FadeIn(gate_2[1]), run_time=0.7)
            self.wait(0.35)
            self.wait_until_bookmark("method_rule")
            self.play(Write(arrows[1]), Create(gate_3[0]), FadeIn(gate_3[1]), run_time=0.7)
            self.wait(0.7)
            self.wait_until_bookmark("method_warning")
            self.play(FadeIn(warning, shift=UP * 0.08), run_time=0.55)
            self.wait(1.0)

        self.play(FadeOut(title), FadeOut(gates), FadeOut(arrows), FadeOut(warning), run_time=0.65)

    # ------------------------------------------------------------------
    # Acte 9 — Synthèse
    # ------------------------------------------------------------------
    def _summary(self) -> None:
        self.play(FadeOut(self.header), FadeOut(self.full_statement), run_time=0.55)

        title = Text("À retenir", font_size=42, weight="SEMIBOLD", color=ACCENT)
        title.to_edge(UP, buff=0.5)

        theorem = MathTex(
            r"a\ge0,\ b\ge0",
            r"\quad\Longrightarrow\quad",
            r"\sqrt{ab}=\sqrt a\,\sqrt b",
        ).scale(1.25)
        theorem.set_color_by_tex(r"\Longrightarrow", ACCENT)
        theorem.next_to(title, DOWN, buff=0.55)
        theorem_box = SurroundingRectangle(theorem, color=GOOD, buff=0.22)

        not_universal = MathTex(
            r"\text{Cette formule n'est pas valable pour tout }(a,b)\in\mathbb R^2.",
        ).scale(0.98)
        not_universal.set_color(ERROR)
        not_universal.next_to(theorem_box, DOWN, buff=0.58)

        lesson = Text(
            "Les hypothèses font partie du théorème.",
            font_size=36,
            weight="SEMIBOLD",
        )
        lesson.next_to(not_universal, DOWN, buff=0.62)

        method = Text(
            "Vérifier les conditions  →  vérifier l'existence  →  appliquer la règle",
            font_size=29,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        method.scale_to_fit_width(11.5)
        method.next_to(lesson, DOWN, buff=0.48)

        spoken = tts.ssml(
            "Retenons l'énoncé complet. <bookmark mark='summary_theorem'/> "
            "Pour des nombres réels a et b positifs ou nuls, la racine du produit est le produit des racines. "
            "<bookmark mark='summary_scope'/> Cette formule n'est pas valable pour tous les couples de nombres réels. "
            "<bookmark mark='summary_lesson'/> Les hypothèses font partie du théorème. "
            "<bookmark mark='summary_method'/> Avant d'appliquer une règle, vérifiez ses conditions, "
            "puis l'existence des expressions, et seulement ensuite effectuez la transformation."
        )
        with self.narrated(spoken):
            self.play(FadeIn(title, shift=DOWN * 0.08), run_time=0.5)
            self.wait_until_bookmark("summary_theorem")
            self.play(Write(theorem), Create(theorem_box), run_time=0.85)
            self.wait(0.75)
            self.wait_until_bookmark("summary_scope")
            self.play(Write(not_universal), run_time=0.75)
            self.wait(0.75)
            self.wait_until_bookmark("summary_lesson")
            self.play(FadeIn(lesson, shift=UP * 0.08), run_time=0.55)
            self.wait(0.7)
            self.wait_until_bookmark("summary_method")
            self.play(FadeIn(method, shift=UP * 0.08), run_time=0.55)
            self.wait(1.25)
