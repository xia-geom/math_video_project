from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from manim import (
    BLACK,
    BLUE_D,
    Circle,
    Create,
    DOWN,
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


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


class ImplicationEtEquivalenceFR(VoiceoverScene):

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
            self._setup_voiceover()
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
    """Pourquoi une implication ne se lit pas automatiquement à l'envers.

    Objectif pédagogique
    --------------------
    Faire comprendre qu'une implication compare deux ensembles de cas :
    tous les cas qui satisfont la première condition doivent satisfaire la
    seconde. La réciproque exige une vérification séparée. Une équivalence
    n'est légitime que lorsque les deux conditions décrivent exactement le
    même ensemble de possibilités.
    """

    def construct(self) -> None:
        self.set_speech_service(AzureService(voice=VOICE_ID))

        self._opening_question()
        self._tempting_reversal()
        self._see_the_solution_sets()
        self._formal_meaning()
        self._less_obvious_example()
        self._repair_the_reverse_direction()
        self._summary()

        self.wait(1.2)

    # ------------------------------------------------------------------
    # Acte 1 — La question centrale
    # ------------------------------------------------------------------
    def _opening_question(self) -> None:
        eyebrow = Text("ERREUR DE RAISONNEMENT", font_size=26, color=ACCENT)
        title = Text(
            "Peut-on lire une implication à l'envers ?",
            font_size=46,
            weight="SEMIBOLD",
        )
        title.scale_to_fit_width(11.9)
        header = VGroup(eyebrow, title).arrange(DOWN, buff=0.22)
        header.to_edge(UP, buff=0.45)

        forward = MathTex(r"x=2", r"\Longrightarrow", r"x^2=4").scale(1.55)
        forward[1].set_color(ACCENT)
        forward.move_to(UP * 0.25)

        reverse = MathTex(r"x^2=4", r"\Longrightarrow", r"x=2").scale(1.55)
        reverse[1].set_color(ERROR)
        reverse.move_to(DOWN * 1.05)

        question_mark = Text("?", font_size=56, color=ERROR, weight="BOLD")
        question_mark.next_to(reverse, RIGHT, buff=0.35)

        spoken = ssml(
            f"Si {X} égale deux, alors {X} au carré égale quatre. Cette phrase est vraie. "
            f"Mais peut-on retourner la flèche et conclure que, si {X} au carré vaut quatre, "
            f"alors {X} vaut forcément deux ?"
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(eyebrow, shift=DOWN * 0.15), run_time=0.65)
            self.play(Write(title), run_time=1.1)
            self.play(Write(forward), run_time=0.9)
            self.wait(0.7)
            self.play(Write(reverse), FadeIn(question_mark, scale=0.7), run_time=0.9)
            self.wait(1.0)

        self.play(
            header.animate.scale(0.78).to_edge(UP, buff=0.28),
            FadeOut(VGroup(forward, reverse, question_mark)),
            run_time=0.8,
        )

        self.header = header

    # ------------------------------------------------------------------
    # Acte 2 — Le retournement tentant
    # ------------------------------------------------------------------
    def _tempting_reversal(self) -> None:
        chain = MathTex(
            r"x=2",
            r"\Longrightarrow",
            r"x^2=4",
            r"\overset{?}{\Longrightarrow}",
            r"x=2",
        ).scale(1.35)
        chain[1].set_color(ACCENT)
        chain[3].set_color(ERROR)
        chain.move_to(UP * 1.25)

        explanation = Text(
            "La deuxième flèche est une nouvelle affirmation.",
            font_size=33,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        explanation.next_to(chain, DOWN, buff=0.55)

        counterexample = MathTex(r"x=-2", r"\quad\Longrightarrow\quad", r"x^2=4").scale(1.3)
        counterexample.move_to(DOWN * 0.75)
        counterexample_box = SurroundingRectangle(counterexample, color=ERROR, buff=0.2)

        verdict = Text(
            "Le retour est faux.",
            font_size=34,
            color=ERROR,
            weight="SEMIBOLD",
        )
        verdict.next_to(counterexample_box, DOWN, buff=0.4)

        spoken = ssml(
            "Le piège vient de la lecture. Une flèche a un sens. La retourner ne reformule "
            "pas la même phrase : on crée une deuxième affirmation, appelée la réciproque."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(chain), run_time=1.0)
            self.play(FadeIn(explanation, shift=UP * 0.12), run_time=0.65)
            self.wait(0.9)

        spoken = ssml(
            f"Pour tester cette nouvelle affirmation, cherchons un contre-exemple. Prenons "
            f"{X} égale moins deux. Son carré vaut bien quatre, mais {X} n'est pas égal à deux."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(counterexample), run_time=0.85)
            self.play(Create(counterexample_box), run_time=0.5)
            self.wait(0.75)
            self.play(FadeIn(verdict, shift=UP * 0.12), run_time=0.55)
            self.wait(1.0)

        self.tempting_group = VGroup(
            chain,
            explanation,
            counterexample,
            counterexample_box,
            verdict,
        )

    # ------------------------------------------------------------------
    # Acte 3 — Les ensembles de solutions révèlent la direction
    # ------------------------------------------------------------------
    def _point_marker(self, line: NumberLine, value: float, color) -> VGroup:
        dot = MathTex(r"\bullet", color=color).scale(1.35).move_to(line.n2p(value))
        label = MathTex(str(int(value)), color=color).scale(0.9)
        label.next_to(dot, UP, buff=0.18)
        return VGroup(dot, label)

    def _see_the_solution_sets(self) -> None:
        self.play(FadeOut(self.tempting_group), run_time=0.7)

        section_title = Text(
            "Regardons tous les cas possibles",
            font_size=38,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        section_title.next_to(self.header, DOWN, buff=0.28)

        p_label = MathTex(r"P:\quad x=2").scale(1.05)
        p_line = NumberLine(
            x_range=[-4, 4, 1],
            length=8.2,
            include_numbers=True,
            color=BLACK,
            stroke_width=2.5,
        )
        p_group = VGroup(p_label, p_line).arrange(DOWN, buff=0.2)
        p_group.move_to(UP * 0.75)
        p_two = self._point_marker(p_line, 2, ACCENT)

        q_label = MathTex(r"Q:\quad x^2=4").scale(1.05)
        q_line = NumberLine(
            x_range=[-4, 4, 1],
            length=8.2,
            include_numbers=True,
            color=BLACK,
            stroke_width=2.5,
        )
        q_group = VGroup(q_label, q_line).arrange(DOWN, buff=0.2)
        q_group.move_to(DOWN * 1.45)
        q_minus_two = self._point_marker(q_line, -2, ERROR)
        q_plus_two = self._point_marker(q_line, 2, ACCENT)

        inclusion = MathTex(r"\{2\}\subset\{-2,2\}").scale(1.15)
        inclusion.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.25)
        inclusion_box = SurroundingRectangle(inclusion, color=ACCENT, buff=0.17)

        spoken = ssml(
            f"La condition {X} égale deux ne garde qu'un seul cas sur la droite numérique : deux."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(section_title, shift=DOWN * 0.12), run_time=0.6)
            self.play(FadeIn(p_group), run_time=0.7)
            self.play(FadeIn(p_two[0]), Write(p_two[1]), run_time=0.55)
            self.wait(0.8)

        spoken = ssml(
            f"La condition {X} au carré égale quatre garde deux cas : moins deux et deux. "
            "Le premier ensemble est entièrement contenu dans le second."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(q_group), run_time=0.7)
            self.play(
                FadeIn(q_minus_two[0]),
                Write(q_minus_two[1]),
                FadeIn(q_plus_two[0]),
                Write(q_plus_two[1]),
                run_time=0.75,
            )
            self.wait(0.7)
            self.play(Write(inclusion), Create(inclusion_box), run_time=0.8)
            self.wait(0.9)

        direction = MathTex(r"P\Longrightarrow Q").scale(1.28)
        direction.set_color(ACCENT)
        direction.to_edge(DOWN, buff=0.32)

        reverse_false = MathTex(r"Q\not\Longrightarrow P").scale(1.28)
        reverse_false.set_color(ERROR)
        reverse_false.next_to(direction, RIGHT, buff=0.8)

        direction_group = VGroup(direction, reverse_false)
        direction_group.move_to(DOWN * 3.05)

        spoken = ssml(
            "C'est exactement ce que signifie l'implication : chaque cas de P est aussi un cas de Q. "
            "Mais Q contient un cas supplémentaire. On ne peut donc pas revenir de Q vers P."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(direction), run_time=0.6)
            self.wait(0.55)
            self.play(Write(reverse_false), run_time=0.7)
            self.wait(1.0)

        self.solution_sets_group = VGroup(
            section_title,
            p_group,
            p_two,
            q_group,
            q_minus_two,
            q_plus_two,
            inclusion,
            inclusion_box,
            direction_group,
        )

    # ------------------------------------------------------------------
    # Acte 4 — Sens formel, introduit après le visuel
    # ------------------------------------------------------------------
    def _formal_meaning(self) -> None:
        self.play(FadeOut(self.solution_sets_group), run_time=0.75)

        title = Text(
            "Une implication est une inclusion",
            font_size=38,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        title.next_to(self.header, DOWN, buff=0.28)

        q_box = RoundedRectangle(
            width=8.5,
            height=4.0,
            corner_radius=0.2,
            color=ACCENT,
            stroke_width=3,
            fill_color=ACCENT,
            fill_opacity=0.04,
        )
        q_box.move_to(DOWN * 0.25)
        q_text = MathTex(r"Q").scale(1.2).set_color(ACCENT)
        q_text.next_to(q_box.get_corner(UP + RIGHT), DOWN + LEFT, buff=0.22)

        p_box = RoundedRectangle(
            width=3.7,
            height=2.05,
            corner_radius=0.18,
            color=GOOD,
            stroke_width=3,
            fill_color=GOOD,
            fill_opacity=0.07,
        )
        p_box.move_to(q_box.get_center() + LEFT * 1.35)
        p_text = MathTex(r"P").scale(1.2).set_color(GOOD)
        p_text.next_to(p_box.get_corner(UP + RIGHT), DOWN + LEFT, buff=0.18)

        inside_caption = Text(
            "Tous les cas de P sont dans Q",
            font_size=31,
            weight="SEMIBOLD",
        )
        inside_caption.move_to(p_box.get_center())

        implication = MathTex(
            r"P\Longrightarrow Q",
            r"\quad\Longleftrightarrow\quad",
            r"S_P\subseteq S_Q",
        ).scale(1.15)
        implication[0].set_color(ACCENT)
        implication.to_edge(DOWN, buff=0.36)

        spoken = ssml(
            "Nous pouvons maintenant formuler l'idée générale. Dire P implique Q signifie que "
            "toute situation où P est vraie se trouve à l'intérieur des situations où Q est vraie."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.55)
            self.play(Create(q_box), Write(q_text), run_time=0.7)
            self.play(Create(p_box), Write(p_text), run_time=0.7)
            self.play(FadeIn(inside_caption), run_time=0.6)
            self.wait(0.9)

        spoken = ssml(
            "La réciproque demanderait que tous les cas de Q soient aussi dans P. Cela peut être vrai, "
            "mais ce n'est jamais garanti par la première flèche."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(implication), run_time=0.9)
            self.wait(1.0)

        self.formal_group = VGroup(
            title,
            q_box,
            q_text,
            p_box,
            p_text,
            inside_caption,
            implication,
        )

    # ------------------------------------------------------------------
    # Acte 5 — Exemple moins évident
    # ------------------------------------------------------------------
    def _open_circle(self, line: NumberLine, value: float, color) -> Circle:
        return Circle(
            radius=0.105,
            color=color,
            stroke_width=3,
            fill_color=WHITE,
            fill_opacity=1,
        ).move_to(line.n2p(value))

    def _less_obvious_example(self) -> None:
        self.play(FadeOut(self.formal_group), run_time=0.75)

        title = Text(
            "Un exemple où l'erreur est moins visible",
            font_size=37,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        title.next_to(self.header, DOWN, buff=0.28)

        statement = MathTex(r"x>2", r"\Longrightarrow", r"x^2>4").scale(1.35)
        statement[1].set_color(ACCENT)
        statement.move_to(UP * 1.85)

        p_line = NumberLine(
            x_range=[-4, 4, 1],
            length=8.3,
            include_numbers=True,
            color=BLACK,
            stroke_width=2.5,
        )
        p_line.move_to(UP * 0.35)
        p_label = MathTex(r"x>2").scale(0.95).next_to(p_line, LEFT, buff=0.35)
        p_ray = Line(p_line.n2p(2), p_line.n2p(4), color=ACCENT, stroke_width=7)
        p_ray.add_tip(tip_length=0.2)
        p_open = self._open_circle(p_line, 2, ACCENT)

        q_line = NumberLine(
            x_range=[-4, 4, 1],
            length=8.3,
            include_numbers=True,
            color=BLACK,
            stroke_width=2.5,
        )
        q_line.move_to(DOWN * 1.55)
        q_label = MathTex(r"x^2>4").scale(0.95).next_to(q_line, LEFT, buff=0.35)
        q_left_ray = Line(q_line.n2p(-2), q_line.n2p(-4), color=ERROR, stroke_width=7)
        q_left_ray.add_tip(tip_length=0.2)
        q_right_ray = Line(q_line.n2p(2), q_line.n2p(4), color=ACCENT, stroke_width=7)
        q_right_ray.add_tip(tip_length=0.2)
        q_left_open = self._open_circle(q_line, -2, ERROR)
        q_right_open = self._open_circle(q_line, 2, ACCENT)

        minus_three = MathTex(r"-3", color=ERROR).scale(1.0)
        minus_three.next_to(q_line.n2p(-3), UP, buff=0.2)
        minus_three_dot = MathTex(r"\bullet", color=ERROR).scale(1.25).move_to(q_line.n2p(-3))

        spoken = ssml(
            f"Prenons une implication vraie mais moins évidente. Si {X} est plus grand que deux, "
            f"alors son carré est plus grand que quatre."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.55)
            self.play(Write(statement), run_time=0.8)
            self.play(FadeIn(p_line), Write(p_label), run_time=0.65)
            self.play(Create(p_ray), FadeIn(p_open), run_time=0.7)
            self.wait(0.85)

        spoken = ssml(
            f"Mais la condition {X} au carré plus grand que quatre possède une deuxième région : "
            f"les nombres plus petits que moins deux."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(q_line), Write(q_label), run_time=0.65)
            self.play(Create(q_right_ray), FadeIn(q_right_open), run_time=0.55)
            self.wait(0.4)
            self.play(Create(q_left_ray), FadeIn(q_left_open), run_time=0.65)
            self.wait(0.9)

        reverse = MathTex(r"x^2>4", r"\not\Longrightarrow", r"x>2").scale(1.15)
        reverse[1].set_color(ERROR)
        reverse.to_edge(DOWN, buff=0.28)

        spoken = ssml(
            f"Par exemple, {X} égale moins trois a un carré égal à neuf, donc supérieur à quatre. "
            f"Pourtant, moins trois n'est pas supérieur à deux. Un seul contre-exemple suffit "
            f"pour détruire la réciproque."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(minus_three_dot), Write(minus_three), run_time=0.55)
            self.wait(0.55)
            self.play(Write(reverse), run_time=0.8)
            self.wait(1.0)

        self.less_obvious_group = VGroup(
            title,
            statement,
            p_line,
            p_label,
            p_ray,
            p_open,
            q_line,
            q_label,
            q_left_ray,
            q_right_ray,
            q_left_open,
            q_right_open,
            minus_three,
            minus_three_dot,
            reverse,
        )

    # ------------------------------------------------------------------
    # Acte 6 — Ajouter l'information manquante
    # ------------------------------------------------------------------
    def _repair_the_reverse_direction(self) -> None:
        self.play(FadeOut(self.less_obvious_group), run_time=0.75)

        title = Text(
            "Comment réparer la réciproque ?",
            font_size=38,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        title.next_to(self.header, DOWN, buff=0.28)

        broad_condition = MathTex(r"x^2=4").scale(1.35)
        broad_condition.move_to(UP * 1.55)

        two_candidates = MathTex(r"x=-2", r"\quad\text{ou}\quad", r"x=2").scale(1.2)
        two_candidates.move_to(UP * 0.45)

        sign_condition = MathTex(r"x\ge 0").scale(1.2).set_color(ACCENT)
        sign_condition.move_to(DOWN * 0.65)
        sign_box = SurroundingRectangle(sign_condition, color=ACCENT, buff=0.18)

        filter_arrow = MathTex(r"\Downarrow").scale(1.25).set_color(ACCENT)
        filter_arrow.next_to(sign_condition, DOWN, buff=0.28)

        survivor = MathTex(r"x=2").scale(1.4).set_color(GOOD)
        survivor.next_to(filter_arrow, DOWN, buff=0.28)
        survivor_box = SurroundingRectangle(survivor, color=GOOD, buff=0.2)

        spoken = ssml(
            f"La réciproque échouait parce que la condition {X} au carré égale quatre gardait "
            f"deux possibilités. Pour retrouver uniquement deux, il faut ajouter l'information manquante : "
            f"{X} est positif ou nul."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.55)
            self.play(Write(broad_condition), run_time=0.6)
            self.play(Write(two_candidates), run_time=0.8)
            self.wait(0.65)
            self.play(Write(sign_condition), Create(sign_box), run_time=0.65)
            self.wait(0.8)

        spoken = ssml(
            "Cette nouvelle condition élimine moins deux. Les deux descriptions donnent maintenant "
            "exactement le même ensemble de cas."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(filter_arrow), run_time=0.4)
            self.play(Write(survivor), Create(survivor_box), run_time=0.7)
            self.wait(0.9)

        equivalence = MathTex(
            r"x=2",
            r"\Longleftrightarrow",
            r"x^2=4\ \text{et}\ x\ge 0",
        ).scale(1.15)
        equivalence[1].set_color(GOOD)
        equivalence.to_edge(DOWN, buff=0.3)

        spoken = ssml(
            "On peut alors utiliser la double flèche. Une équivalence signifie que chaque direction "
            "est vraie, ou, de façon visuelle, que les deux conditions ont exactement les mêmes solutions."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(Write(equivalence), run_time=0.95)
            self.wait(1.1)

        self.repair_group = VGroup(
            title,
            broad_condition,
            two_candidates,
            sign_condition,
            sign_box,
            filter_arrow,
            survivor,
            survivor_box,
            equivalence,
        )

    # ------------------------------------------------------------------
    # Acte 7 — Synthèse
    # ------------------------------------------------------------------
    def _summary(self) -> None:
        self.play(FadeOut(self.repair_group), run_time=0.75)

        title = Text(
            "À retenir",
            font_size=42,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        title.next_to(self.header, DOWN, buff=0.34)

        row_1_math = MathTex(r"P\Longrightarrow Q").scale(1.15).set_color(ACCENT)
        row_1_text = Text(
            "Tous les cas de P sont des cas de Q.",
            font_size=30,
        )
        row_1 = VGroup(row_1_math, row_1_text).arrange(RIGHT, buff=0.55)

        row_2_math = MathTex(r"Q\Longrightarrow P\ ?").scale(1.15).set_color(ERROR)
        row_2_text = Text(
            "La réciproque doit être testée séparément.",
            font_size=30,
        )
        row_2 = VGroup(row_2_math, row_2_text).arrange(RIGHT, buff=0.55)

        row_3_math = MathTex(r"P\Longleftrightarrow Q").scale(1.15).set_color(GOOD)
        row_3_text = Text(
            "Les deux conditions ont les mêmes cas.",
            font_size=30,
        )
        row_3 = VGroup(row_3_math, row_3_text).arrange(RIGHT, buff=0.55)

        rows = VGroup(row_1, row_2, row_3).arrange(DOWN, buff=0.65, aligned_edge=LEFT)
        rows.move_to(DOWN * 0.3)

        diagnostic = Text(
            "Avant de retourner une flèche, cherchez un contre-exemple.",
            font_size=32,
            color=ACCENT,
            weight="SEMIBOLD",
        )
        diagnostic.to_edge(DOWN, buff=0.45)
        diagnostic_box = SurroundingRectangle(diagnostic, color=ACCENT, buff=0.2)

        spoken = ssml(
            "Retenons trois idées. Une implication affirme seulement que tous les cas de P sont dans Q. "
            "La réciproque est une nouvelle phrase et doit être vérifiée séparément. La double flèche "
            "n'est permise que lorsque les deux conditions décrivent exactement les mêmes cas."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.55)
            self.play(Write(row_1_math), FadeIn(row_1_text, shift=LEFT * 0.12), run_time=0.75)
            self.wait(0.45)
            self.play(Write(row_2_math), FadeIn(row_2_text, shift=LEFT * 0.12), run_time=0.75)
            self.wait(0.45)
            self.play(Write(row_3_math), FadeIn(row_3_text, shift=LEFT * 0.12), run_time=0.75)
            self.wait(0.8)

        spoken = ssml(
            "Le réflexe le plus puissant est simple : avant de retourner une flèche, cherchez un "
            "contre-exemple. S'il existe, même un seul, la réciproque est fausse."
        )
        with self.voiceover(text=spoken, subcaption=strip_ssml(spoken)):
            self.play(FadeIn(diagnostic, shift=UP * 0.12), Create(diagnostic_box), run_time=0.75)
            self.wait(1.2)
