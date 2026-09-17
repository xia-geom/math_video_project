"""Fonctions, domaine et image — merged MAT0339 foundation capsule.

This scene replaces three overlapping introductions with one progressive video.
Visual rule: one main idea per page, with at most one central diagram and one
short mathematical conclusion visible at the same time.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

import numpy as np
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


# ---------------------------------------------------------------------------
# Visual defaults
# ---------------------------------------------------------------------------
config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

ACCENT = BLUE_D
WARN = RED_D
GOOD = GREEN_D
MUTED = GRAY_D
PALE = GRAY_E
VOICE_SPEED = 0.86


# ---------------------------------------------------------------------------
# Narration
# ---------------------------------------------------------------------------
SCRIPT = [
    {
        "caption": "Qu’est-ce qu’une fonction, et que peut-elle accepter ?",
        "ssml": tts.ssml(
            "Qu'est-ce qu'une fonction ? "
            "Et, pour une fonction donnée, quelles entrées peut-on utiliser, "
            "et quelles sorties peut-on obtenir ? "
            "<break time='450ms'/>Nous allons construire ces idées une par une."
        ),
    },
    {
        "caption": "Une fonction transforme une entrée en une sortie.",
        "ssml": tts.ssml(
            "Commençons par l'idée la plus simple. "
            "<bookmark mark='machine'/>Une fonction agit comme une machine. "
            "On choisit une entrée, la règle effectue un calcul, "
            "et elle produit une sortie. "
            "<bookmark mark='send_two'/>Ici, deux donne cinq."
        ),
    },
    {
        "caption": "Chaque entrée a une seule sortie.",
        "ssml": tts.ssml(
            "Le mot fonction impose une condition essentielle. "
            "<bookmark mark='first_arrow'/>Une entrée peut mener à une sortie. "
            "<bookmark mark='second_arrow'/>Mais si cette même entrée mène aussi "
            "à une autre sortie, ce n'est plus une fonction. "
            "<bookmark mark='one_output'/>Chaque entrée doit avoir une sortie unique. "
            "<bookmark mark='shared_output'/>En revanche, deux entrées différentes "
            "peuvent très bien donner la même sortie."
        ),
    },
    {
        "caption": "Notation : f : A → B et x ↦ f(x).",
        "ssml": tts.ssml(
            "On écrit cette idée de manière compacte. "
            "<bookmark mark='formal_map'/>"
            f"{tts.char('f')} va de l'ensemble {tts.char('A')} vers l'ensemble {tts.char('B')}. "
            "<bookmark mark='formal_element'/>"
            f"Chaque {tts.char('x')} de {tts.char('A')} est envoyé vers "
            f"{tts.char('f')} de {tts.char('x')} dans {tts.char('B')}."
        ),
    },
    {
        "caption": "Domaine, codomaine et image ont trois rôles distincts.",
        "ssml": tts.ssml(
            "Prenons une petite fonction pour distinguer trois ensembles. "
            f"Elle va de zéro, un, deux vers zéro, un, deux, trois, quatre, "
            f"et sa règle est {tts.char('f')} de {tts.char('x')} égal à deux {tts.char('x')}. "
            f"<bookmark mark='pairs'/>Ainsi, zéro donne zéro, un donne deux, et deux donne quatre. "
            "<bookmark mark='domain'/>Le domaine est l'ensemble des entrées autorisées. "
            "<bookmark mark='codomain'/>Le codomaine est tout l'ensemble d'arrivée choisi. "
            "<bookmark mark='image'/>L'image ne garde que les sorties réellement atteintes. "
            "Elle peut donc être plus petite que le codomaine."
        ),
    },
    {
        "caption": "Une formule seule conduit à chercher son domaine naturel.",
        "ssml": tts.ssml(
            "Une fonction complète possède déjà un domaine. "
            "Mais lorsqu'on nous donne seulement une formule, on cherche habituellement "
            "son domaine naturel : les entrées pour lesquelles le calcul a un sens. "
            "<bookmark mark='fraction'/>Pour un sur "
            f"{tts.char('x')} moins deux, l'entrée deux crée une division par zéro. "
            "<bookmark mark='exclude_two'/>On retire donc deux du domaine naturel."
        ),
    },
    {
        "caption": "Sous une racine carrée, le contenu doit être positif ou nul.",
        "ssml": tts.ssml(
            "Une racine carrée impose une autre condition. "
            "<bookmark mark='root_formula'/>Pour la racine de "
            f"{tts.char('x')} moins trois, le contenu doit être positif ou nul. "
            "<bookmark mark='root_condition'/>On obtient "
            f"{tts.char('x')} supérieur ou égal à trois. "
            "<bookmark mark='root_line'/>Le domaine commence donc à trois, inclus."
        ),
    },
    {
        "caption": "Sur un graphe : domaine horizontal, image verticale.",
        "ssml": tts.ssml(
            "Le graphe permet de voir les deux ensembles. "
            "<bookmark mark='graph'/>Considérons le demi-cercle supérieur. "
            "<bookmark mark='horizontal'/>Horizontalement, la courbe existe de moins deux à deux : "
            "c'est le domaine. "
            "<bookmark mark='vertical'/>Verticalement, elle prend les valeurs de zéro à deux : "
            "c'est l'image."
        ),
    },
    {
        "caption": "Le test de la verticale reconnaît une fonction.",
        "ssml": tts.ssml(
            "Complétons maintenant le cercle. "
            "<bookmark mark='lower_half'/>Ce dessin représente une relation, "
            "mais pas une fonction de "
            f"{tts.char('x')} vers {tts.char('y')}. "
            "<bookmark mark='vertical_test'/>Pour une même valeur de "
            f"{tts.char('x')}, une verticale rencontre deux points. "
            "Il y aurait donc deux sorties."
        ),
    },
    {
        "caption": "Entrées permises, une sortie unique, sorties atteintes.",
        "ssml": tts.ssml(
            "À retenir. "
            "<bookmark mark='recap_one'/>Le domaine contient les entrées permises. "
            "<bookmark mark='recap_two'/>Chaque entrée du domaine possède une seule sortie. "
            "<bookmark mark='recap_three'/>L'image contient les sorties réellement atteintes, "
            "et elle est incluse dans le codomaine."
        ),
    },
]


@dataclass
class _NoVoiceTracker:
    duration: float = 0.0


BaseScene = VoiceoverScene if VoiceoverScene is not None else Scene


class FonctionsDomaineImageFR(BaseScene):
    """Merged introduction to functions, domain, codomain, and image."""

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

        self.set_speech_service(
            AzureService(
                voice=tts.VOICE_ID,
                global_speed=VOICE_SPEED,
            )
        )
        self._voiceover_enabled = True

    @contextmanager
    def narrated(self, item: dict[str, str]):
        if self._voiceover_enabled:
            with self.voiceover(
                text=item["ssml"],
                subcaption=item["caption"],
            ) as tracker:
                yield tracker
        else:
            yield _NoVoiceTracker()

    def wait_until_bookmark(self, mark: str) -> None:
        if self._voiceover_enabled:
            super().wait_until_bookmark(mark)

    def clear_page(self, *mobjects: Mobject, run_time: float = 0.65) -> None:
        visible = [mob for mob in mobjects if mob is not None]
        if visible:
            self.play(*(FadeOut(mob) for mob in visible), run_time=run_time)

    # ------------------------------------------------------------------
    # Small visual helpers
    # ------------------------------------------------------------------
    def make_heading(self, text: str) -> Text:
        heading = Text(text, font_size=36, weight=SEMIBOLD)
        if heading.width > 12.2:
            heading.scale_to_fit_width(12.2)
        return heading.to_edge(UP, buff=0.38)

    def make_machine(self, formula: str) -> VGroup:
        box = RoundedRectangle(
            width=3.65,
            height=2.05,
            corner_radius=0.18,
            stroke_color=BLACK,
            stroke_width=3,
            fill_color=ACCENT,
            fill_opacity=0.07,
        )
        formula_mob = MathTex(formula, font_size=48).move_to(box)
        input_arrow = Arrow(
            box.get_left() + LEFT * 1.75,
            box.get_left() + LEFT * 0.12,
            buff=0,
            color=BLACK,
            stroke_width=3,
        )
        output_arrow = Arrow(
            box.get_right() + RIGHT * 0.12,
            box.get_right() + RIGHT * 1.75,
            buff=0,
            color=BLACK,
            stroke_width=3,
        )
        return VGroup(box, formula_mob, input_arrow, output_arrow)

    def make_number_line(
        self,
        x_min: float,
        x_max: float,
        *,
        segments: list[tuple[float | None, float | None]],
        open_points: tuple[float, ...] = (),
        closed_points: tuple[float, ...] = (),
        length: float = 8.6,
    ) -> VGroup:
        line = NumberLine(
            x_range=[x_min, x_max, 1],
            length=length,
            include_numbers=True,
            include_tip=True,
            color=BLACK,
            stroke_width=2.2,
            font_size=27,
        )

        accepted = VGroup()
        epsilon = 0.025 * (x_max - x_min)
        for left, right in segments:
            start = x_min + epsilon if left is None else left
            end = x_max - epsilon if right is None else right
            accepted.add(
                Line(
                    line.n2p(start),
                    line.n2p(end),
                    color=ACCENT,
                    stroke_width=8,
                )
            )

        endpoints = VGroup()
        for value in closed_points:
            endpoints.add(Dot(line.n2p(value), radius=0.095, color=ACCENT))
        for value in open_points:
            endpoints.add(
                Circle(
                    radius=0.105,
                    stroke_color=ACCENT,
                    stroke_width=3,
                    fill_color=WHITE,
                    fill_opacity=1,
                ).move_to(line.n2p(value))
            )

        return VGroup(line, accepted, endpoints)

    # ------------------------------------------------------------------
    # Scene
    # ------------------------------------------------------------------
    def construct(self) -> None:
        self.camera.background_color = WHITE
        self._setup_voiceover()
        play_uqam_intro(self)

        # ==============================================================
        # PAGE 1 — Central question
        # ==============================================================
        title = Text("Fonction, domaine et image", font_size=50, weight=SEMIBOLD)
        question = Text(
            "Quelles entrées sont permises, et quelles sorties obtient-on ?",
            font_size=31,
            color=MUTED,
        )
        intro = VGroup(title, question).arrange(DOWN, buff=0.28)

        with self.narrated(SCRIPT[0]):
            self.play(Write(title), run_time=0.9)
            self.play(FadeIn(question, shift=UP * 0.15), run_time=0.65)
            self.wait(0.8)

        self.clear_page(intro)

        # ==============================================================
        # PAGE 2 — Machine intuition
        # ==============================================================
        heading = self.make_heading("Une entrée est transformée en une sortie")
        machine = self.make_machine(r"f(x)=2x+1").shift(DOWN * 0.15)

        input_token = VGroup(
            Circle(radius=0.42, color=ACCENT, stroke_width=3),
            MathTex("2", font_size=38),
        ).move_to(machine[2].get_start() + LEFT * 0.22)

        output_token = VGroup(
            Circle(radius=0.42, color=ACCENT, stroke_width=3),
            MathTex("5", font_size=38),
        ).move_to(machine[3].get_end() + RIGHT * 0.22)

        result = MathTex(r"f(2)=2\cdot2+1=5", font_size=43).to_edge(DOWN, buff=0.72)

        with self.narrated(SCRIPT[1]):
            self.play(FadeIn(heading), run_time=0.45)
            self.wait_until_bookmark("machine")
            self.play(
                Create(machine[0]),
                Write(machine[1]),
                GrowArrow(machine[2]),
                GrowArrow(machine[3]),
                run_time=1.0,
            )
            self.wait_until_bookmark("send_two")
            self.play(FadeIn(input_token, shift=RIGHT * 0.18), run_time=0.4)
            self.play(input_token.animate.move_to(machine.get_center()), run_time=0.75)
            self.play(
                FadeOut(input_token, scale=0.75),
                FadeIn(output_token, shift=RIGHT * 0.25),
                run_time=0.5,
            )
            self.play(Write(result), run_time=0.8)
            self.wait(0.7)

        self.clear_page(heading, machine, output_token, result)

        # ==============================================================
        # PAGE 3 — What breaks the function rule?
        # ==============================================================
        heading = self.make_heading("Une entrée peut-elle avoir deux sorties ?")

        source_dot = Dot(LEFT * 3.4, radius=0.075, color=BLACK)
        source_label = MathTex("2", font_size=42).next_to(source_dot, LEFT, buff=0.18)
        target_top = Dot(RIGHT * 3.4 + UP * 0.9, radius=0.075, color=BLACK)
        target_bottom = Dot(RIGHT * 3.4 + DOWN * 0.9, radius=0.075, color=BLACK)
        label_top = MathTex("5", font_size=42).next_to(target_top, RIGHT, buff=0.18)
        label_bottom = MathTex("7", font_size=42).next_to(target_bottom, RIGHT, buff=0.18)

        arrow_one = Arrow(
            source_dot.get_center() + RIGHT * 0.12,
            target_top.get_center() + LEFT * 0.12,
            buff=0.12,
            color=ACCENT,
            stroke_width=3.2,
        )
        arrow_two = Arrow(
            source_dot.get_center() + RIGHT * 0.12,
            target_bottom.get_center() + LEFT * 0.12,
            buff=0.12,
            color=WARN,
            stroke_width=3.2,
        )

        diagram_points = VGroup(
            source_dot,
            source_label,
            target_top,
            target_bottom,
            label_top,
            label_bottom,
        )
        verdict = Text(
            "Non : la sortie n’est pas unique.",
            font_size=34,
            color=WARN,
        ).to_edge(DOWN, buff=0.72)

        shared_source_top = Dot(LEFT * 3.4 + UP * 0.75, radius=0.075, color=BLACK)
        shared_source_bottom = Dot(LEFT * 3.4 + DOWN * 0.75, radius=0.075, color=BLACK)
        shared_target = Dot(RIGHT * 3.4, radius=0.075, color=BLACK)
        shared_labels = VGroup(
            MathTex("1", font_size=42).next_to(shared_source_top, LEFT, buff=0.18),
            MathTex("3", font_size=42).next_to(shared_source_bottom, LEFT, buff=0.18),
            MathTex("7", font_size=42).next_to(shared_target, RIGHT, buff=0.18),
        )
        shared_points = VGroup(
            shared_source_top,
            shared_source_bottom,
            shared_target,
            shared_labels,
        )
        shared_arrows = VGroup(
            Arrow(
                shared_source_top.get_center() + RIGHT * 0.12,
                shared_target.get_center() + LEFT * 0.12,
                buff=0.12,
                color=ACCENT,
                stroke_width=3.2,
            ),
            Arrow(
                shared_source_bottom.get_center() + RIGHT * 0.12,
                shared_target.get_center() + LEFT * 0.12,
                buff=0.12,
                color=ACCENT,
                stroke_width=3.2,
            ),
        )
        allowed = Text(
            "Oui : plusieurs entrées peuvent partager une sortie.",
            font_size=32,
            color=GOOD,
        ).to_edge(DOWN, buff=0.72)

        with self.narrated(SCRIPT[2]):
            self.play(FadeIn(heading), FadeIn(diagram_points), run_time=0.65)
            self.wait_until_bookmark("first_arrow")
            self.play(GrowArrow(arrow_one), run_time=0.7)
            self.wait(0.7)
            self.wait_until_bookmark("second_arrow")
            self.play(GrowArrow(arrow_two), run_time=0.7)
            self.wait(0.8)
            self.wait_until_bookmark("one_output")
            self.play(Write(verdict), Indicate(source_label, color=WARN), run_time=0.8)
            self.wait(0.7)

            self.wait_until_bookmark("shared_output")
            self.play(
                FadeOut(diagram_points),
                FadeOut(arrow_one),
                FadeOut(arrow_two),
                FadeOut(verdict),
                FadeIn(shared_points),
                run_time=0.65,
            )
            self.play(
                LaggedStart(*(GrowArrow(arrow) for arrow in shared_arrows), lag_ratio=0.25),
                run_time=0.9,
            )
            self.play(FadeIn(allowed, shift=UP * 0.12), run_time=0.55)
            self.wait(0.9)

        self.clear_page(heading, shared_points, shared_arrows, allowed)

        # ==============================================================
        # PAGE 4 — Formal notation
        # ==============================================================
        heading = self.make_heading("La même idée, en notation mathématique")
        formal_map = MathTex(r"f:A\longrightarrow B", font_size=62)
        formal_element = MathTex(
            r"x\in A\quad\longmapsto\quad f(x)\in B",
            font_size=48,
        )
        notation = VGroup(formal_map, formal_element).arrange(DOWN, buff=0.55)

        with self.narrated(SCRIPT[3]):
            self.play(FadeIn(heading), run_time=0.45)
            self.wait_until_bookmark("formal_map")
            self.play(Write(formal_map), run_time=0.9)
            self.wait(0.7)
            self.wait_until_bookmark("formal_element")
            self.play(Write(formal_element), run_time=0.9)
            self.wait(1.0)

        self.clear_page(heading, notation)

        # ==============================================================
        # PAGE 5 — Domain, codomain, image
        # One concept line is replaced by the next; they are not stacked.
        # ==============================================================
        heading = self.make_heading("Trois ensembles, trois rôles")
        mapping = MathTex(
            r"f:\{0,1,2\}\longrightarrow\{0,1,2,3,4\}",
            font_size=46,
        ).shift(UP * 1.18)
        rule = MathTex(r"f(x)=2x", font_size=52).shift(DOWN * 0.12)
        pairs = MathTex(
            r"0\mapsto0,\qquad 1\mapsto2,\qquad 2\mapsto4",
            font_size=46,
        ).shift(DOWN * 0.12)

        domain_line = VGroup(
            Text("Domaine", font_size=31, color=MUTED),
            MathTex(r"\operatorname{Dom}(f)=A=\{0,1,2\}", font_size=46),
        ).arrange(DOWN, buff=0.18).shift(DOWN * 0.15)

        codomain_line = VGroup(
            Text("Codomaine", font_size=31, color=MUTED),
            MathTex(r"B=\{0,1,2,3,4\}", font_size=46),
        ).arrange(DOWN, buff=0.18).shift(DOWN * 0.15)

        image_line = VGroup(
            Text("Image", font_size=31, color=MUTED),
            MathTex(r"\operatorname{Im}(f)=\{0,2,4\}\subsetneq B", font_size=46),
        ).arrange(DOWN, buff=0.18).shift(DOWN * 0.15)

        missed = Text(
            "1 et 3 appartiennent au codomaine, mais ne sont jamais atteints.",
            font_size=28,
            color=WARN,
        ).to_edge(DOWN, buff=0.68)

        with self.narrated(SCRIPT[4]):
            self.play(FadeIn(heading), Write(mapping), run_time=0.8)
            self.play(Write(rule), run_time=0.65)
            self.wait_until_bookmark("pairs")
            self.play(ReplacementTransform(rule, pairs), run_time=0.75)
            self.wait(0.8)

            self.wait_until_bookmark("domain")
            self.play(ReplacementTransform(pairs, domain_line), run_time=0.75)
            self.wait(0.8)

            self.wait_until_bookmark("codomain")
            self.play(ReplacementTransform(domain_line, codomain_line), run_time=0.75)
            self.wait(0.8)

            self.wait_until_bookmark("image")
            self.play(ReplacementTransform(codomain_line, image_line), run_time=0.75)
            self.play(FadeIn(missed, shift=UP * 0.12), run_time=0.55)
            self.wait(1.0)

        self.clear_page(heading, mapping, image_line, missed)

        # ==============================================================
        # PAGE 6 — Natural domain: denominator
        # ==============================================================
        heading = self.make_heading("Une formule peut refuser une entrée")
        fraction = MathTex(r"g(x)=\frac{1}{x-2}", font_size=58).shift(UP * 1.25)
        substitution = MathTex(r"g(2)=\frac{1}{2-2}=\frac{1}{0}", font_size=49)
        impossible = Text("division impossible", font_size=33, color=WARN)
        test_group = VGroup(substitution, impossible).arrange(DOWN, buff=0.32).shift(DOWN * 0.55)

        condition = MathTex(r"x\neq2", font_size=54).shift(UP * 0.25)
        fraction_line = self.make_number_line(
            -4,
            6,
            segments=[(None, 2), (2, None)],
            open_points=(2,),
        ).shift(DOWN * 1.05)
        fraction_domain = MathTex(
            r"\operatorname{Dom}(g)=\mathbb{R}\setminus\{2\}",
            font_size=43,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.48)

        with self.narrated(SCRIPT[5]):
            self.play(FadeIn(heading), run_time=0.45)
            self.wait_until_bookmark("fraction")
            self.play(Write(fraction), run_time=0.75)
            self.play(Write(substitution), run_time=0.8)
            self.play(FadeIn(impossible, shift=UP * 0.12), run_time=0.5)
            self.wait(0.8)

            self.wait_until_bookmark("exclude_two")
            self.play(FadeOut(test_group), FadeOut(fraction), run_time=0.5)
            self.play(Write(condition), run_time=0.55)
            self.play(
                condition.animate.shift(UP * 0.72),
                Create(fraction_line[0]),
                Create(fraction_line[1]),
                FadeIn(fraction_line[2]),
                run_time=0.9,
            )
            self.play(ReplacementTransform(condition, fraction_domain), run_time=0.65)
            self.wait(1.0)

        self.clear_page(heading, fraction_line, fraction_domain)

        # ==============================================================
        # PAGE 7 — Natural domain: square root
        # Each algebraic line replaces the previous one.
        # ==============================================================
        heading = self.make_heading("Une racine carrée crée une frontière")
        root_formula = MathTex(r"h(x)=\sqrt{x-3}", font_size=58).shift(UP * 0.95)
        root_rule = MathTex(r"x-3\geq0", font_size=54).shift(DOWN * 0.05)
        root_solution = MathTex(r"x\geq3", font_size=56, color=ACCENT).shift(DOWN * 0.05)

        root_line = self.make_number_line(
            -3,
            8,
            segments=[(3, None)],
            closed_points=(3,),
        ).shift(DOWN * 1.1)
        root_domain = MathTex(
            r"\operatorname{Dom}(h)=[3,+\infty[",
            font_size=43,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.48)

        with self.narrated(SCRIPT[6]):
            self.play(FadeIn(heading), run_time=0.45)
            self.wait_until_bookmark("root_formula")
            self.play(Write(root_formula), run_time=0.75)
            self.wait(0.6)

            self.wait_until_bookmark("root_condition")
            self.play(Write(root_rule), run_time=0.65)
            self.wait(0.65)
            self.play(ReplacementTransform(root_rule, root_solution), run_time=0.65)
            self.wait(0.65)

            self.wait_until_bookmark("root_line")
            self.play(
                FadeOut(root_formula),
                root_solution.animate.shift(UP * 0.72),
                Create(root_line[0]),
                Create(root_line[1]),
                FadeIn(root_line[2]),
                run_time=0.9,
            )
            self.play(ReplacementTransform(root_solution, root_domain), run_time=0.65)
            self.wait(1.0)

        self.clear_page(heading, root_line, root_domain)

        # ==============================================================
        # PAGE 8 — Read domain and image from a graph
        # Equal scale: 1 unit has the same length on both axes.
        # ==============================================================
        heading = self.make_heading("Le graphe montre le domaine et l’image")

        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-1, 3, 1],
            x_length=7.2,
            y_length=4.8,
            tips=False,
            axis_config={"color": BLACK, "stroke_width": 2.2},
        ).shift(DOWN * 0.25)
        axis_labels = axes.get_axis_labels(MathTex("x"), MathTex("y"))

        upper_half = axes.plot(
            lambda x: np.sqrt(max(0.0, 4 - x**2)),
            x_range=[-2, 2, 0.02],
            color=ACCENT,
            stroke_width=4,
        )
        graph_label = MathTex(
            r"y=\sqrt{4-x^2}",
            font_size=35,
        ).next_to(axes.c2p(1.2, 1.6), UR, buff=0.18)

        domain_projection = Line(
            axes.c2p(-2, 0),
            axes.c2p(2, 0),
            color=ACCENT,
            stroke_width=8,
        )
        domain_guides = VGroup(
            DashedLine(axes.c2p(-2, 0), axes.c2p(-2, 0.35), color=MUTED),
            DashedLine(axes.c2p(2, 0), axes.c2p(2, 0.35), color=MUTED),
        )
        domain_text = MathTex(
            r"\operatorname{Dom}=[-2,2]",
            font_size=40,
            color=ACCENT,
        ).to_edge(DOWN, buff=0.43)

        image_projection = Line(
            axes.c2p(0, 0),
            axes.c2p(0, 2),
            color=GOOD,
            stroke_width=8,
        )
        image_guides = VGroup(
            DashedLine(axes.c2p(0, 2), axes.c2p(0.35, 2), color=MUTED),
        )
        image_text = MathTex(
            r"\operatorname{Im}=[0,2]",
            font_size=40,
            color=GOOD,
        ).to_edge(DOWN, buff=0.43)

        with self.narrated(SCRIPT[7]):
            self.play(FadeIn(heading), run_time=0.45)
            self.wait_until_bookmark("graph")
            self.play(Create(axes), Write(axis_labels), run_time=0.9)
            self.play(Create(upper_half), FadeIn(graph_label), run_time=1.0)
            self.wait(0.7)
            self.play(FadeOut(graph_label), run_time=0.35)

            self.wait_until_bookmark("horizontal")
            self.play(
                Create(domain_projection),
                Create(domain_guides),
                FadeIn(domain_text),
                run_time=0.9,
            )
            self.wait(1.0)

            self.wait_until_bookmark("vertical")
            self.play(
                FadeOut(domain_projection),
                FadeOut(domain_guides),
                ReplacementTransform(domain_text, image_text),
                run_time=0.55,
            )
            self.play(Create(image_projection), Create(image_guides), run_time=0.75)
            self.wait(1.0)

        # Keep only the graph for the vertical-line test.
        relation_heading = self.make_heading(
            "Une relation n’est pas toujours une fonction"
        )
        self.play(
            FadeOut(image_projection),
            FadeOut(image_guides),
            FadeOut(image_text),
            FadeOut(graph_label),
            FadeOut(heading),
            run_time=0.35,
        )
        self.play(FadeIn(relation_heading), run_time=0.35)
        heading = relation_heading

        # ==============================================================
        # PAGE 9 — Vertical-line test, built from the preceding graph
        # ==============================================================
        lower_half = axes.plot(
            lambda x: -np.sqrt(max(0.0, 4 - x**2)),
            x_range=[-2, 2, 0.02],
            color=BLACK,
            stroke_width=4,
        )
        relation_label = MathTex(r"x^2+y^2=4", font_size=36).next_to(
            axes.c2p(1.15, 1.65),
            UR,
            buff=0.16,
        )

        x_test = 1.0
        test_line = Line(
            axes.c2p(x_test, -2.35),
            axes.c2p(x_test, 2.35),
            color=WARN,
            stroke_width=3,
        )
        y_hit = np.sqrt(4 - x_test**2)
        hit_points = VGroup(
            Dot(axes.c2p(x_test, y_hit), color=WARN, radius=0.09),
            Dot(axes.c2p(x_test, -y_hit), color=WARN, radius=0.09),
        )
        not_function = Text(
            "Une même entrée donne deux sorties.",
            font_size=33,
            color=WARN,
        ).to_edge(DOWN, buff=0.58)

        with self.narrated(SCRIPT[8]):
            self.wait_until_bookmark("lower_half")
            self.play(
                upper_half.animate.set_color(BLACK),
                Create(lower_half),
                FadeIn(relation_label),
                run_time=1.0,
            )
            self.wait(0.8)

            self.wait_until_bookmark("vertical_test")
            self.play(Create(test_line), run_time=0.65)
            self.play(FadeIn(hit_points, scale=1.4), run_time=0.55)
            self.play(Write(not_function), run_time=0.7)
            self.wait(1.0)

        self.clear_page(
            heading,
            axes,
            axis_labels,
            upper_half,
            lower_half,
            relation_label,
            test_line,
            hit_points,
            not_function,
        )

        # ==============================================================
        # PAGE 10 — Final recap
        # ==============================================================
        heading = Text("À retenir", font_size=46, weight=SEMIBOLD).to_edge(UP, buff=0.55)

        domain_part = MathTex(r"x\in\operatorname{Dom}(f)", font_size=44)
        map_arrow = MathTex(r"\longmapsto", font_size=44)
        image_part = MathTex(r"f(x)\in\operatorname{Im}(f)", font_size=44)
        subset = MathTex(r"\subseteq", font_size=44)
        codomain_part = MathTex(r"B", font_size=44)
        recap_formula = VGroup(
            domain_part,
            map_arrow,
            image_part,
            subset,
            codomain_part,
        ).arrange(RIGHT, buff=0.30).move_to(UP * 0.25)

        explanation_one = Text(
            "On choisit une entrée permise.",
            font_size=34,
        ).to_edge(DOWN, buff=1.0)
        explanation_two = Text(
            "Cette entrée détermine une seule sortie.",
            font_size=34,
        ).to_edge(DOWN, buff=1.0)
        explanation_three = Text(
            "Les sorties atteintes restent dans le codomaine.",
            font_size=34,
        ).to_edge(DOWN, buff=1.0)

        with self.narrated(SCRIPT[9]):
            self.play(FadeIn(heading), Write(recap_formula), run_time=0.9)

            self.wait_until_bookmark("recap_one")
            self.play(
                domain_part.animate.set_color(ACCENT),
                FadeIn(explanation_one, shift=UP * 0.12),
                run_time=0.65,
            )
            self.wait(0.8)

            self.wait_until_bookmark("recap_two")
            self.play(
                domain_part.animate.set_color(BLACK),
                map_arrow.animate.set_color(ACCENT),
                image_part.animate.set_color(ACCENT),
                FadeOut(explanation_one),
                run_time=0.35,
            )
            self.play(FadeIn(explanation_two), run_time=0.35)
            self.wait(0.8)

            self.wait_until_bookmark("recap_three")
            self.play(
                map_arrow.animate.set_color(BLACK),
                image_part.animate.set_color(BLACK),
                subset.animate.set_color(ACCENT),
                codomain_part.animate.set_color(ACCENT),
                FadeOut(explanation_two),
                run_time=0.35,
            )
            self.play(FadeIn(explanation_three), run_time=0.35)
            self.wait(1.5)
