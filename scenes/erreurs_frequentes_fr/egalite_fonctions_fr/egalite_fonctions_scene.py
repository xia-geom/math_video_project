from __future__ import annotations

from manim import (
    BLACK,
    BLUE_D,
    Create,
    DOWN,
    Dot,
    FadeIn,
    FadeOut,
    GREEN_D,
    LEFT,
    Line,
    MathTex,
    NumberLine,
    RED_D,
    RIGHT,
    RoundedRectangle,
    SurroundingRectangle,
    Text,
    UP,
    VGroup,
    WHITE,
    Write,
    config,
)
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService

from tools.tts import VOICE_ID, X, ssml, strip_ssml


config.background_color = WHITE
Text.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


ACCENT = BLUE_D
GOOD = GREEN_D
ERROR = RED_D


class EgaliteDeFonctionsFR(VoiceoverScene):
    """Même formule, même image, même graphe : est-ce la même fonction ?

    Objectif pédagogique
    --------------------
    Faire comprendre que l'égalité de deux fonctions ne se décide ni par
    l'apparence de leur formule, ni par leur seul ensemble de valeurs de
    sortie. Dans la convention du cours, une fonction est donnée avec son
    domaine, son ensemble d'arrivée et la valeur associée à chaque entrée.

    Progression
    -----------
    1. Deux formules différentes peuvent définir la même fonction.
    2. Deux fonctions peuvent avoir la même image sans être égales.
    3. Une même formule sur deux domaines différents donne deux fonctions
       différentes; l'une peut être une restriction de l'autre.
    4. L'ensemble d'arrivée compte aussi dans la notation f : A -> B et
       change notamment la surjectivité.
    """

    def construct(self) -> None:
        self.set_speech_service(AzureService(voice=VOICE_ID))

        self._opening_question()
        self._different_formulas_same_function()
        self._same_image_is_not_enough()
        self._same_formula_different_domain()
        self._codomain_matters()
        self._formal_criterion()
        self._summary()

        self.wait(1.2)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _function_card(
        self,
        name_tex: str,
        formula_tex: str,
        color,
        width: float = 5.25,
        height: float = 2.15,
    ) -> VGroup:
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.18,
            color=color,
            stroke_width=2.5,
            fill_color=color,
            fill_opacity=0.055,
        )
        name = MathTex(name_tex).scale(0.95)
        formula = MathTex(formula_tex).scale(1.28)
        content = VGroup(name, formula).arrange(DOWN, buff=0.28)
        content.move_to(box)
        return VGroup(box, content)

    def _value_row(
        self,
        input_tex: str,
        left_tex: str,
        right_tex: str,
        color=BLACK,
    ) -> VGroup:
        input_value = MathTex(input_tex).scale(0.92)
        arrow_1 = MathTex(r"\longmapsto").scale(0.8)
        left_value = MathTex(left_tex).scale(0.92)
        separator = MathTex(r"=").scale(0.92)
        right_value = MathTex(right_tex).scale(0.92)
        row = VGroup(
            input_value,
            arrow_1,
            left_value,
            separator,
            right_value,
        ).arrange(RIGHT, buff=0.25)
        row.set_color(color)
        return row

    def _domain_line(
        self,
        domain_label_tex: str,
        nonnegative_only: bool,
        color,
    ) -> VGroup:
        label = MathTex(domain_label_tex).scale(0.92)
        line = NumberLine(
            x_range=[-4, 4, 1],
            length=7.5,
            include_numbers=True,
            color=BLACK,
            stroke_width=2.4,
        )
        if nonnegative_only:
            active = Line(line.n2p(0), line.n2p(4), color=color, stroke_width=7)
            zero = Dot(line.n2p(0), radius=0.075, color=color)
            active.set_z_index(0)
            line.set_z_index(1)
            zero.set_z_index(2)
            domain_visual = VGroup(active, line, zero)
        else:
            active = Line(line.n2p(-4), line.n2p(4), color=color, stroke_width=7)
            active.set_z_index(0)
            line.set_z_index(1)
            domain_visual = VGroup(active, line)

        group = VGroup(label, domain_visual).arrange(DOWN, buff=0.2)
        return group

    # ------------------------------------------------------------------
    # Acte 1 — La question centrale
    # ------------------------------------------------------------------
    def _opening_question(self) -> None:
        eyebrow = Text("ERREUR CONCEPTUELLE", font_size=26, color=ACCENT)
        title = Text(
            "Qu'est-ce qui rend deux fonctions égales ?",
            font_size=46,
            weight="SEMIBOLD",
        )
        title.scale_to_fit_width(11.8)
        header = VGroup(eyebrow, title).arrange(DOWN, buff=0.22)
        header.to_edge(UP, buff=0.45)

        left_card = self._function_card(
            r"f:\mathbb{R}\to\mathbb{R}",
            r"f(x)=x^2",
            ACCENT,
        )
        right_card = self._function_card(
            r"g:\mathbb{R}\to\mathbb{R}",
            r"g(x)=|x|^2",
            GOOD,
        )
        cards = VGroup(left_card, right_card).arrange(RIGHT, buff=0.65)
        cards.move_to(DOWN * 0.15)

        question = Text(
            "Formules différentes : fonctions différentes ?",
            font_size=32,
            color=ERROR,
            weight="SEMIBOLD",
        )
        question.next_to(cards, DOWN, buff=0.55)

        spoken = ssml(
            "Deux fonctions sont-elles égales seulement lorsqu'elles ont exactement la même formule ? "
            f"Comparons {X} au carré et valeur absolue de {X}, le tout au carré. "
            "Les écritures sont différentes. Mais est-ce vraiment suffisant pour distinguer les fonctions ?"
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(eyebrow, shift=DOWN * 0.15), run_time=0.65)
            self.play(Write(title), run_time=1.05)
            self.play(FadeIn(left_card, shift=RIGHT * 0.2), run_time=0.7)
            self.play(FadeIn(right_card, shift=LEFT * 0.2), run_time=0.7)
            self.wait(0.7)
            self.play(FadeIn(question, shift=UP * 0.12), run_time=0.6)
            self.wait(1.0)

        self.play(
            header.animate.scale(0.78).to_edge(UP, buff=0.28),
            FadeOut(question),
            cards.animate.scale(0.88).move_to(UP * 1.05),
            run_time=0.8,
        )

        self.header = header
        self.first_cards = cards

    # ------------------------------------------------------------------
    # Acte 2 — Des formules différentes peuvent définir la même fonction
    # ------------------------------------------------------------------
    def _different_formulas_same_function(self) -> None:
        rows = VGroup(
            self._value_row(r"x=-2", r"f(-2)=4", r"g(-2)=4"),
            self._value_row(r"x=0", r"f(0)=0", r"g(0)=0"),
            self._value_row(r"x=3", r"f(3)=9", r"g(3)=9"),
        ).arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        rows.move_to(DOWN * 1.0)

        spoken = ssml(
            f"Testons quelques entrées. Pour {X} égale moins deux, les deux fonctions donnent quatre. "
            f"Pour zéro, elles donnent zéro. Pour trois, elles donnent neuf. Ces exemples suggèrent "
            "que les deux règles produisent toujours la même valeur."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            for row in rows:
                self.play(FadeIn(row, shift=RIGHT * 0.12), run_time=0.55)
                self.wait(0.35)
            self.wait(0.7)

        identity = MathTex(r"|x|^2=x^2\qquad\text{pour tout }x\in\mathbb{R}").scale(1.12)
        identity.set_color(ACCENT)
        identity.to_edge(DOWN, buff=0.42)
        identity_box = SurroundingRectangle(identity, color=ACCENT, buff=0.18)

        verdict = Text(
            "Même domaine + mêmes valeurs à chaque entrée",
            font_size=29,
            color=GOOD,
            weight="SEMIBOLD",
        )
        verdict.next_to(identity_box, UP, buff=0.3)

        spoken = ssml(
            f"Et cette fois, nous pouvons le prouver : pour tout réel {X}, la valeur absolue de {X} "
            f"au carré est égale à {X} au carré. Les formules ont une apparence différente, "
            "mais elles donnent la même sortie pour chaque entrée du même domaine. "
            "Elles définissent donc la même fonction."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(identity), Create(identity_box), run_time=0.9)
            self.wait(0.6)
            self.play(FadeIn(verdict, shift=UP * 0.12), run_time=0.55)
            self.wait(1.0)

        self.equal_formula_group = VGroup(rows, identity, identity_box, verdict)

    # ------------------------------------------------------------------
    # Acte 3 — La même image ne suffit pas
    # ------------------------------------------------------------------
    def _same_image_is_not_enough(self) -> None:
        self.play(
            FadeOut(self.first_cards),
            FadeOut(self.equal_formula_group),
            run_time=0.7,
        )

        section = Text(
            "Premier raccourci trompeur : « mêmes sorties possibles »",
            font_size=36,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        section.scale_to_fit_width(11.6)
        section.next_to(self.header, DOWN, buff=0.3)

        u_card = self._function_card(
            r"u:\mathbb{R}\to\mathbb{R}",
            r"u(x)=x^2",
            ACCENT,
            width=5.0,
        )
        v_card = self._function_card(
            r"v:\mathbb{R}\to\mathbb{R}",
            r"v(x)=|x|",
            GOOD,
            width=5.0,
        )
        cards = VGroup(u_card, v_card).arrange(RIGHT, buff=0.75)
        cards.move_to(UP * 0.55)

        image_u = MathTex(r"\operatorname{Im}(u)=[0,+\infty[").scale(1.0)
        image_v = MathTex(r"\operatorname{Im}(v)=[0,+\infty[").scale(1.0)
        images = VGroup(image_u, image_v).arrange(RIGHT, buff=1.0)
        images.next_to(cards, DOWN, buff=0.45)

        same_image = Text(
            "Même ensemble de valeurs atteintes",
            font_size=29,
            color=GOOD,
        )
        same_image.next_to(images, DOWN, buff=0.32)

        spoken = ssml(
            f"Prenons maintenant {X} au carré et valeur absolue de {X}. Les deux fonctions atteignent "
            "exactement tous les nombres positifs ou nuls. Elles ont donc la même image."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(section, shift=DOWN * 0.12), run_time=0.6)
            self.play(FadeIn(cards), run_time=0.7)
            self.play(Write(images), run_time=0.8)
            self.play(FadeIn(same_image, shift=UP * 0.1), run_time=0.5)
            self.wait(0.8)

        test = MathTex(
            r"x=2:",
            r"\quad u(2)=4",
            r"\qquad\text{mais}\qquad",
            r"v(2)=2",
        ).scale(1.15)
        test[1].set_color(ACCENT)
        test[3].set_color(ERROR)
        test.to_edge(DOWN, buff=0.62)
        test_box = SurroundingRectangle(test, color=ERROR, buff=0.18)

        conclusion = Text(
            "Même image ≠ même fonction",
            font_size=34,
            color=ERROR,
            weight="SEMIBOLD",
        )
        conclusion.next_to(test_box, UP, buff=0.3)

        spoken = ssml(
            f"Mais une fonction ne se contente pas d'une collection de sorties. Elle associe une sortie "
            f"précise à chaque entrée. Pour {X} égale deux, la première donne quatre, tandis que la seconde "
            "donne deux. Même image, mais associations différentes : ce ne sont pas les mêmes fonctions."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(test), Create(test_box), run_time=0.9)
            self.wait(0.55)
            self.play(FadeIn(conclusion, shift=UP * 0.12), run_time=0.55)
            self.wait(1.0)

        self.same_image_group = VGroup(section, cards, images, same_image, test, test_box, conclusion)

    # ------------------------------------------------------------------
    # Acte 4 — Une même formule sur des domaines différents
    # ------------------------------------------------------------------
    def _same_formula_different_domain(self) -> None:
        self.play(FadeOut(self.same_image_group), run_time=0.7)

        section = Text(
            "Deuxième raccourci : « même formule, donc même fonction »",
            font_size=36,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        section.scale_to_fit_width(11.5)
        section.next_to(self.header, DOWN, buff=0.3)

        f_def = MathTex(
            r"f:\mathbb{R}\to\mathbb{R},\qquad f(x)=x^2"
        ).scale(1.05)
        g_def = MathTex(
            r"g:[0,+\infty[\to\mathbb{R},\qquad g(x)=x^2"
        ).scale(1.05)

        f_line = self._domain_line(r"\operatorname{Dom}(f)=\mathbb{R}", False, ACCENT)
        g_line = self._domain_line(r"\operatorname{Dom}(g)=[0,+\infty[", True, GOOD)

        f_block = VGroup(f_def, f_line).arrange(DOWN, buff=0.28)
        g_block = VGroup(g_def, g_line).arrange(DOWN, buff=0.28)
        blocks = VGroup(f_block, g_block).arrange(DOWN, buff=0.55)
        blocks.move_to(DOWN * 0.15)

        spoken = ssml(
            f"Voici maintenant deux fonctions qui utilisent exactement la même formule, {X} au carré. "
            "Mais la première accepte tous les nombres réels, tandis que la seconde accepte seulement "
            "les nombres positifs ou nuls."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(section, shift=DOWN * 0.12), run_time=0.6)
            self.play(Write(f_def), run_time=0.65)
            self.play(FadeIn(f_line), run_time=0.75)
            self.wait(0.45)
            self.play(Write(g_def), run_time=0.65)
            self.play(FadeIn(g_line), run_time=0.75)
            self.wait(0.75)

        test_f = MathTex(r"f(-2)=4").scale(1.12).set_color(ACCENT)
        test_g = MathTex(r"g(-2)\ \text{n'existe pas}").scale(1.12).set_color(ERROR)
        test_pair = VGroup(test_f, test_g).arrange(RIGHT, buff=1.0)
        test_pair.to_edge(DOWN, buff=0.42)
        test_box = SurroundingRectangle(test_pair, color=ERROR, buff=0.2)

        spoken = ssml(
            f"L'entrée moins deux révèle la différence. La valeur f de moins deux existe et vaut quatre. "
            f"Mais g de moins deux n'existe pas, car moins deux n'appartient pas au domaine de g. "
            "La formule seule ne suffit donc pas."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(test_f), run_time=0.6)
            self.play(Write(test_g), run_time=0.7)
            self.play(Create(test_box), run_time=0.45)
            self.wait(0.9)

        restriction = MathTex(
            r"g=f\big|_{[0,+\infty[}"
        ).scale(1.15)
        restriction.set_color(GOOD)
        restriction.next_to(test_box, UP, buff=0.28)
        restriction_text = Text(
            "g est la restriction de f",
            font_size=28,
            color=GOOD,
        )
        restriction_text.next_to(restriction, RIGHT, buff=0.35)

        spoken = ssml(
            "Il existe cependant une relation précise entre elles : g est la restriction de f au domaine "
            "positif ou nul. Elle utilise la même règle, mais seulement sur une partie des entrées."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(restriction), run_time=0.65)
            self.play(FadeIn(restriction_text, shift=LEFT * 0.12), run_time=0.5)
            self.wait(1.0)

        self.domain_group = VGroup(
            section,
            blocks,
            test_pair,
            test_box,
            restriction,
            restriction_text,
        )

    # ------------------------------------------------------------------
    # Acte 5 — L'ensemble d'arrivée change ce que la fonction affirme
    # ------------------------------------------------------------------
    def _codomain_matters(self) -> None:
        self.play(FadeOut(self.domain_group), run_time=0.7)

        section = Text(
            "Et l'ensemble d'arrivée ?",
            font_size=38,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        section.next_to(self.header, DOWN, buff=0.3)

        p_def = MathTex(
            r"p:\mathbb{R}\to\mathbb{R},\qquad p(x)=x^2"
        ).scale(1.05)
        q_def = MathTex(
            r"q:\mathbb{R}\to[0,+\infty[,\qquad q(x)=x^2"
        ).scale(1.05)
        definitions = VGroup(p_def, q_def).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        definitions.move_to(UP * 0.75)

        target_p = RoundedRectangle(
            width=5.2,
            height=2.0,
            corner_radius=0.18,
            color=ACCENT,
            stroke_width=2.5,
            fill_color=ACCENT,
            fill_opacity=0.05,
        )
        target_q = RoundedRectangle(
            width=5.2,
            height=2.0,
            corner_radius=0.18,
            color=GOOD,
            stroke_width=2.5,
            fill_color=GOOD,
            fill_opacity=0.05,
        )
        target_p.move_to(LEFT * 3.0 + DOWN * 1.15)
        target_q.move_to(RIGHT * 3.0 + DOWN * 1.15)

        p_title = MathTex(r"\text{Cible de }p:\ \mathbb{R}").scale(0.95)
        p_image = MathTex(r"\operatorname{Im}(p)=[0,+\infty[").scale(0.95)
        p_status = Text("pas surjective", font_size=27, color=ERROR, weight="SEMIBOLD")
        p_content = VGroup(p_title, p_image, p_status).arrange(DOWN, buff=0.24)
        p_content.move_to(target_p)

        q_title = MathTex(r"\text{Cible de }q:\ [0,+\infty[").scale(0.95)
        q_image = MathTex(r"\operatorname{Im}(q)=[0,+\infty[").scale(0.95)
        q_status = Text("surjective", font_size=27, color=GOOD, weight="SEMIBOLD")
        q_content = VGroup(q_title, q_image, q_status).arrange(DOWN, buff=0.24)
        q_content.move_to(target_q)

        spoken = ssml(
            f"Les fonctions p et q ont le même domaine et donnent la même valeur pour chaque réel {X}. "
            "Leur graphe visible est donc identique. Pourtant, leur ensemble d'arrivée déclaré n'est pas le même."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(section, shift=DOWN * 0.12), run_time=0.6)
            self.play(Write(definitions), run_time=0.9)
            self.play(FadeIn(target_p), FadeIn(target_q), run_time=0.6)
            self.play(Write(p_title), Write(q_title), run_time=0.65)
            self.wait(0.6)

        spoken = ssml(
            "Dans les deux cas, les valeurs effectivement atteintes sont les nombres positifs ou nuls. "
            "Mais p vise tous les réels : elle n'atteint jamais les réels négatifs, donc elle n'est pas surjective. "
            "q vise seulement les nombres positifs ou nuls : elle atteint toute sa cible, donc elle est surjective."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(p_image), Write(q_image), run_time=0.7)
            self.wait(0.45)
            self.play(FadeIn(p_status, shift=UP * 0.1), run_time=0.5)
            self.play(FadeIn(q_status, shift=UP * 0.1), run_time=0.5)
            self.wait(1.0)

        convention = Text(
            "Dans ce cours, f : A → B inclut aussi l'ensemble d'arrivée B.",
            font_size=29,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        convention.scale_to_fit_width(11.4)
        convention.to_edge(DOWN, buff=0.35)
        convention_box = SurroundingRectangle(convention, color=ACCENT, buff=0.17)

        spoken = ssml(
            "C'est pourquoi, dans la convention de ce cours, la notation fonction de A vers B garde aussi "
            "l'ensemble d'arrivée. Changer B change l'objet déclaré et peut changer ses propriétés."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(convention, shift=UP * 0.12), Create(convention_box), run_time=0.75)
            self.wait(1.0)

        self.codomain_group = VGroup(
            section,
            definitions,
            target_p,
            target_q,
            p_content,
            q_content,
            convention,
            convention_box,
        )

    # ------------------------------------------------------------------
    # Acte 6 — Le critère formel
    # ------------------------------------------------------------------
    def _formal_criterion(self) -> None:
        self.play(FadeOut(self.codomain_group), run_time=0.7)

        section = Text(
            "Le critère complet",
            font_size=39,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        section.next_to(self.header, DOWN, buff=0.3)

        declarations = MathTex(
            r"f:A\to B",
            r"\qquad\text{et}\qquad",
            r"g:C\to D",
        ).scale(1.18)
        declarations.move_to(UP * 1.15)

        criterion = MathTex(
            r"f=g",
            r"\Longleftrightarrow",
            r"\begin{cases}"
            r"A=C,\\"
            r"B=D,\\"
            r"f(x)=g(x)\ \text{pour tout }x\in A."
            r"\end{cases}",
        ).scale(1.05)
        criterion[1].set_color(ACCENT)
        criterion.move_to(DOWN * 0.35)
        criterion_box = SurroundingRectangle(criterion, color=ACCENT, buff=0.24)

        spoken = ssml(
            "Nous pouvons maintenant formuler le critère. Dans la convention du cours, pour que f et g soient "
            "égales, elles doivent d'abord accepter le même ensemble d'entrées. Elles doivent annoncer le même "
            "ensemble d'arrivée. Et, pour chaque entrée autorisée, elles doivent produire exactement la même sortie."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(section, shift=DOWN * 0.12), run_time=0.6)
            self.play(Write(declarations), run_time=0.75)
            self.play(Write(criterion), run_time=1.1)
            self.play(Create(criterion_box), run_time=0.5)
            self.wait(1.0)

        warning = Text(
            "Ni la même apparence, ni la même image ne remplacent ce test.",
            font_size=31,
            color=ERROR,
            weight="SEMIBOLD",
        )
        warning.scale_to_fit_width(11.2)
        warning.to_edge(DOWN, buff=0.42)

        spoken = ssml(
            "Deux formules peuvent donc avoir l'air différentes et définir la même fonction. Inversement, deux "
            "fonctions peuvent avoir la même image, ou même la même formule visible, sans être égales."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(warning, shift=UP * 0.12), run_time=0.6)
            self.wait(1.0)

        self.formal_group = VGroup(section, declarations, criterion, criterion_box, warning)

    # ------------------------------------------------------------------
    # Acte 7 — Résumé
    # ------------------------------------------------------------------
    def _summary(self) -> None:
        self.play(FadeOut(self.formal_group), run_time=0.7)

        title = Text(
            "Avant de dire « ce sont les mêmes fonctions »",
            font_size=39,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        title.scale_to_fit_width(11.5)
        title.next_to(self.header, DOWN, buff=0.35)

        q1 = VGroup(
            MathTex(r"1.").set_color(ACCENT),
            Text("Ont-elles les mêmes entrées autorisées ?", font_size=31),
        ).arrange(RIGHT, buff=0.28)
        q2 = VGroup(
            MathTex(r"2.").set_color(ACCENT),
            Text("Donnent-elles la même sortie à chaque entrée ?", font_size=31),
        ).arrange(RIGHT, buff=0.28)
        q3 = VGroup(
            MathTex(r"3.").set_color(ACCENT),
            Text("Dans ce cours, ont-elles la même cible déclarée ?", font_size=31),
        ).arrange(RIGHT, buff=0.28)
        checklist = VGroup(q1, q2, q3).arrange(DOWN, buff=0.48, aligned_edge=LEFT)
        checklist.move_to(UP * 0.1)

        final_rule = MathTex(
            r"\text{Une fonction n'est pas seulement une formule.}"
        ).scale(1.16)
        final_rule.set_color(GOOD)
        final_rule.to_edge(DOWN, buff=0.75)
        final_box = SurroundingRectangle(final_rule, color=GOOD, buff=0.2)

        spoken = ssml(
            "Retenons trois questions. Les fonctions acceptent-elles les mêmes entrées ? Donnent-elles la même "
            "sortie à chaque entrée ? Et, dans la convention du cours, annoncent-elles le même ensemble d'arrivée ?"
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.6)
            self.play(FadeIn(q1, shift=RIGHT * 0.15), run_time=0.55)
            self.wait(0.4)
            self.play(FadeIn(q2, shift=RIGHT * 0.15), run_time=0.55)
            self.wait(0.4)
            self.play(FadeIn(q3, shift=RIGHT * 0.15), run_time=0.55)
            self.wait(0.7)

        spoken = ssml(
            "La formule est la règle de calcul. Mais la fonction complète précise aussi où cette règle agit et vers "
            "quel ensemble elle envoie ses valeurs. Une fonction n'est donc pas seulement une formule."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(final_rule), Create(final_box), run_time=0.8)
            self.wait(1.2)
